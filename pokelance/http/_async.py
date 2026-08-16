from __future__ import annotations

import asyncio
import logging
import time
import typing as t

import niquests

from pokelance.cache._async.manager import AsyncCacheManager
from pokelance.exceptions import HTTPException
from pokelance.http._base import BaseHttpClient
from pokelance.http.endpoints import Route

if t.TYPE_CHECKING:
    from pokelance.client.async_client import PokeLanceAsyncClient

    _BaseHttpClient = BaseHttpClient[PokeLanceAsyncClient, niquests.AsyncSession, AsyncCacheManager]
else:
    _BaseHttpClient = BaseHttpClient

__all__: tuple[str, ...] = ("AsyncEndpointLoader", "AsyncHttpClient")

logger = logging.getLogger(__name__)


class AsyncEndpointLoader:
    """Composition helper for scheduling and tracking async endpoint pre-population tasks."""

    def __init__(self, client: PokeLanceAsyncClient) -> None:
        self._client = client
        self._tasks: set[asyncio.Task[None]] = set()
        self._remaining: int = 0
        self._ready_event: asyncio.Event = asyncio.Event()
        self._ready_event.set()

    @property
    def is_ready(self) -> bool:
        """Whether all background loading tasks have finished."""
        return self._ready_event.is_set()

    async def wait_until_ready(self) -> None:
        """Wait until all background endpoint tasks have completed."""
        await self._ready_event.wait()

    async def _load_ext(self, coroutine: t.Callable[[], t.Coroutine[t.Any, t.Any, None]], message: str) -> None:
        """Load an extension's resources asynchronously."""
        logger.debug(f"Loading {message}")
        try:
            await coroutine()
        finally:
            self._remaining -= 1
            if self._remaining <= 0:
                self._ready_event.set()
        logger.info(f"Loaded {message}")

    async def schedule_tasks(self) -> None:
        """Schedules background endpoint-loading tasks using asyncio.create_task."""
        self._ready_event.clear()
        if not self._client.cache_endpoints:
            self._ready_event.set()
            self._client.ext_tasks.clear()
            return
        total = len(self._client.ext_tasks)
        self._remaining = total
        for num, (coroutine, name) in enumerate(self._client.ext_tasks):
            message = f"Extension {name} endpoints ({num + 1}/{total})"
            task = asyncio.create_task(coro=self._load_ext(coroutine, message), name=name)
            self._tasks.add(task)
            task.add_done_callback(self._tasks.discard)
        self._client.ext_tasks.clear()
        if self._remaining == 0:
            self._ready_event.set()

    async def cancel_tasks(self) -> None:
        """Cancels and awaits all in-flight endpoint loading tasks."""
        for task in list(self._tasks):
            if not task.done():
                task.cancel()
                logger.warning(f"Cancelled task {task.get_name()}")
        if self._tasks:
            await asyncio.gather(*self._tasks, return_exceptions=True)


@t.final
class AsyncHttpClient(_BaseHttpClient):
    """The asynchronous HTTP client for PokeLance.

    Parameters
    ----------
    client: PokeLanceAsyncClient
        The client that this HTTP client is for.
    cache_size: int
        The size of the cache.
    session: t.Optional[niquests.AsyncSession]
        The session to use for the HTTP client. If not provided, one is created
        internally on the first request and owned by this client.
    """

    __slots__: tuple[str, ...] = (
        "_cache_manager",
        "_client",
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
        """Closes the HTTP client and cancels pending endpoint loaders."""
        await self._loader.cancel_tasks()
        if self.session and self._session_owner:
            await self.session.close()
        elif self.session:
            logger.debug("Session was provided externally, not closing it.")

    async def connect(self) -> None:
        """Connects the HTTP client and sets up the session."""
        if self.session is None:
            self.session = niquests.AsyncSession(resolver="system://")
            self._session_owner = True
        if not self._is_ready:
            if self._client.cache_endpoints:
                await self._loader.schedule_tasks()
            self._is_ready = True

    async def request(self, route: Route) -> t.Any:
        """Makes an asynchronous request to the PokeAPI.

        Parameters
        ----------
        route: Route
            The route to use for the request.

        Returns
        -------
        t.Any
            The response from the PokeAPI parsed as JSON.

        Raises
        ------
        HTTPException
            An error occurred while making the request.
        """
        await self.connect()
        if self.session is not None:
            response = await self.session.request(route.method, route.url, params=route.payload)
            return self._validate_response(response, route)
        raise HTTPException("No session was provided.", route, -1).create()

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
        await self.connect()
        if self.session is not None:
            response = await self.session.get(url)
            return self._validate_image(response, url)
        return b""

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
        await self.connect()
        if self.session is not None:
            response = await self.session.get(url)
            return self._validate_audio(response, url)
        return b""

    async def ping(self) -> float:
        """Pings the PokeAPI and returns the latency."""
        start = time.perf_counter()
        await self.request(Route())
        return time.perf_counter() - start
