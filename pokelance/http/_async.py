# pyright: reportUnknownMemberType=false
from __future__ import annotations

import asyncio
import logging
import time
import typing as t
from functools import partial

import niquests

from pokelance.cache._async.manager import AsyncCacheManager
from pokelance.endpoints import Route
from pokelance.exceptions import HTTPException
from pokelance.http._base import BaseEndpointLoader, BaseHttpClient

if t.TYPE_CHECKING:
    from pokelance.client.async_client import PokeLanceAsyncClient

__all__: tuple[str, ...] = ("AsyncEndpointLoader", "AsyncHttpClient")

logger = logging.getLogger(__name__)


class AsyncEndpointLoader(BaseEndpointLoader["PokeLanceAsyncClient", asyncio.Task[None]]):
    """Schedule registry setup once per connection and drain it before closing."""

    @property
    def is_ready(self) -> bool:
        """Whether every scheduled setup has completed successfully."""
        return all(task.done() and not task.cancelled() and task.exception() is None for task in self._tasks.values())

    async def wait_until_ready(self) -> None:
        """Wait for all setup results without cancelling startup if this caller cancels."""
        if not self._client.cache_endpoints:
            raise RuntimeError("Endpoint loading is disabled (cache_endpoints=False).")
        tasks = self._tasks
        await asyncio.shield(asyncio.gather(*tasks.values(), return_exceptions=True))
        self._raise_errors(tasks)

    async def schedule_tasks(self) -> None:
        """Load unfinished extensions; successful registries survive reconnects."""
        if any(not task.done() for task in self._tasks.values()):
            return
        self._tasks = {name: asyncio.create_task(setup(), name=name) for setup, name in self._prepare()}
        for name, task in self._tasks.items():
            task.add_done_callback(partial(self._task_done, name))

    async def cancel_tasks(self) -> None:
        """Cancel and await setup work, including its cancellation cleanup."""
        for task in self._tasks.values():
            if not task.done():
                task.cancel()
        await asyncio.gather(*self._tasks.values(), return_exceptions=True)


@t.final
class AsyncHttpClient(BaseHttpClient["PokeLanceAsyncClient", niquests.AsyncSession, AsyncCacheManager]):
    """The asynchronous HTTP client for PokeLance.

    Parameters
    ----------
    client: PokeLanceAsyncClient
        The client that this HTTP client is for.
    cache_size: int
        The size of the cache.
    session: niquests.AsyncSession | None, optional
        The session to use for the HTTP client. If not provided, one is created
        internally on the first request and owned by this client.
    """

    __slots__: tuple[str, ...] = (
        "_cache_manager",
        "_client",
        "_closing",
        "_is_ready",
        "_loader",
        "_session_owner",
        "session",
    )

    def __init__(
        self,
        *,
        cache_size: int,
        client: PokeLanceAsyncClient,
        session: niquests.AsyncSession | None = None,
    ) -> None:
        super().__init__(client=client, session=session)
        self._cache_manager = AsyncCacheManager(max_size=cache_size, client=self._client)
        self._loader = AsyncEndpointLoader(client=self._client)

    @property
    def loader(self) -> AsyncEndpointLoader:
        """The endpoint loader composition helper."""
        return self._loader

    async def close(self) -> None:
        """Closes the HTTP client session and cancels pending endpoint loaders."""
        if self._closing:
            return
        self._closing = True
        try:
            await self._loader.cancel_tasks()
            await asyncio.gather(self._client.get_image.cache_close(), self._client.get_audio.cache_close())
            session_to_close = self.session if self._session_owner else None
            self.session = None
            if session_to_close:
                logger.debug("Closing internal async HTTP session...")
                await session_to_close.close()
        finally:
            self._is_ready = False
            self._closing = False

    async def connect(self) -> None:
        """Connects the HTTP client and sets up the session."""
        if self._closing:
            raise RuntimeError("Cannot connect while the HTTP client is closing.")
        if self.session is None:
            logger.debug("Initializing internal async HTTP session (niquests)...")
            self.session = niquests.AsyncSession(resolver="system://", retries=self.retry_strategy)
            self._session_owner = True
        if not self._is_ready:
            self._is_ready = True
            if self._client.cache_endpoints:
                await self._loader.schedule_tasks()

    async def request(self, route: Route) -> dict[str, t.Any]:
        """Makes an asynchronous request to the PokeAPI.

        Parameters
        ----------
        route: Route
            The route to use for the request.

        Returns
        -------
        dict[str, t.Any]
            The response from the PokeAPI parsed as JSON.

        Raises
        ------
        HTTPException
            An error occurred while making the request.
        """
        logger.debug(f"Sending {route.method} request to {route.url}")
        return self._validate_response(await self._request_response(route), route)

    async def _request_response(self, route: Route) -> niquests.Response:
        if self._closing:
            raise RuntimeError("Cannot make a request while the HTTP client is closing.")

        await self.connect()

        if self.session is None:
            raise HTTPException("No session was provided.", route, -1).create()

        try:
            return await self.session.request(route.method, route.url, params=route.payload)
        except niquests.exceptions.RequestException as e:
            logger.error(f"Request failed for {route.url} ({type(e).__name__}): {e}")
            raise HTTPException(str(e), route, -1).create() from e

    async def load_image(self, url: str) -> bytes:
        """Loads an image from the url asynchronously.

        Parameters
        ----------
        url: str
            The URL to load the image from.

        Returns
        -------
        bytes
            The raw image bytes.
        """
        logger.debug(f"Fetching image from {url}")
        route = self._route_for_url(url)
        response = await self._request_response(route)
        return self._validate_image(response, url)

    async def load_audio(self, url: str) -> bytes:
        """Loads an audio from the url asynchronously.

        Parameters
        ----------
        url: str
            The URL to load the audio from.

        Returns
        -------
        bytes
            The raw audio bytes.
        """
        logger.debug(f"Fetching audio from {url}")
        route = self._route_for_url(url)
        response = await self._request_response(route)
        return self._validate_audio(response, url)

    async def ping(self) -> float:
        """Pings the PokeAPI and returns the latency."""
        start = time.perf_counter()
        await self.request(Route())
        latency = time.perf_counter() - start
        logger.debug(f"PokeAPI async ping latency: {latency:.4f}s")
        return latency
