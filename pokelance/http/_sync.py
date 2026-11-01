# pyright: reportUnknownMemberType=false
from __future__ import annotations

import concurrent.futures
import contextlib
import logging
import threading
import time
import typing as t
from functools import partial

import niquests

from pokelance.cache.sync.manager import SyncCacheManager
from pokelance.endpoints import Route
from pokelance.exceptions import HTTPException
from pokelance.http._base import BaseEndpointLoader, BaseHttpClient

if t.TYPE_CHECKING:
    from pokelance.client.sync_client import PokeLanceSyncClient

__all__: tuple[str, ...] = ("SyncEndpointLoader", "SyncHttpClient")

logger = logging.getLogger(__name__)


class SyncEndpointLoader(BaseEndpointLoader["PokeLanceSyncClient", concurrent.futures.Future[None]]):
    """Run registry setup in workers and retain their results for readiness."""

    def __init__(self, client: PokeLanceSyncClient) -> None:
        super().__init__(client)
        self._executor: concurrent.futures.ThreadPoolExecutor | None = None
        self._lock = threading.RLock()

    @property
    def is_ready(self) -> bool:
        """Whether every scheduled setup has completed successfully."""
        return all(task.done() and not task.cancelled() and task.exception() is None for task in self._tasks.values())

    def wait_until_ready(self) -> None:
        """Finish every setup before reporting initialization failures."""
        if not self._client.cache_endpoints:
            raise RuntimeError("Endpoint loading is disabled (cache_endpoints=False).")
        with self._lock:
            tasks = self._tasks
        # Report all failures together after every worker finishes.
        for task in tasks.values():
            with contextlib.suppress(Exception):
                task.result()
        self._raise_errors(tasks)

    def schedule_tasks(self) -> None:
        """Load unfinished extensions; successful registries survive reconnects."""
        with self._lock:
            if any(not task.done() for task in self._tasks.values()):
                return
            pending = self._prepare()
            if not pending:
                self._tasks = {}
                return
            if self._executor is None:
                self._executor = concurrent.futures.ThreadPoolExecutor(
                    max_workers=min(32, max(4, len(pending))),
                    thread_name_prefix="PokeLance-EndpointLoader",
                )
            self._tasks = {name: self._executor.submit(setup) for setup, name in pending}
            for name, task in self._tasks.items():
                task.add_done_callback(partial(self._task_done, name))

    def shutdown(self) -> None:
        """Cancel queued work and drain running workers before their session closes."""
        with self._lock:
            tasks = tuple(self._tasks.values())
            executor = self._executor
            self._executor = None
        for task in tasks:
            task.cancel()
        if executor is not None:
            executor.shutdown(wait=True, cancel_futures=True)


@t.final
class SyncHttpClient(BaseHttpClient["PokeLanceSyncClient", niquests.Session, SyncCacheManager]):
    """The synchronous HTTP client for PokeLance.

    Parameters
    ----------
    client: PokeLanceSyncClient
        The client that this HTTP client is for.
    cache_size: int
        The size of the cache.
    session: niquests.Session | None, optional
        The session to use for the HTTP client. If not provided, one is created
        internally on the first request and owned by this client.
    """

    __slots__: tuple[str, ...] = (
        "_cache_manager",
        "_client",
        "_closing",
        "_is_ready",
        "_loader",
        "_lock",
        "_session_owner",
        "session",
    )

    def __init__(
        self,
        *,
        cache_size: int,
        client: PokeLanceSyncClient,
        session: niquests.Session | None = None,
    ) -> None:
        super().__init__(client=client, session=session)
        self._cache_manager = SyncCacheManager(max_size=cache_size, client=self._client)
        self._loader = SyncEndpointLoader(client=self._client)
        self._lock = threading.Lock()

    @property
    def loader(self) -> SyncEndpointLoader:
        """The endpoint loader composition helper."""
        return self._loader

    def close(self) -> None:
        """Closes the HTTP client and shuts down the endpoint loader thread pool."""
        with self._lock:
            if self._closing:
                return
            self._closing = True
        try:
            self._loader.shutdown()
            session_to_close = self.session if self._session_owner else None
            self.session = None
            if session_to_close:
                logger.debug("Closing internal sync HTTP session...")
                session_to_close.close()
        finally:
            with self._lock:
                self._is_ready = False
                self._closing = False

    def connect(self) -> None:
        """Connects the HTTP client and sets up the session."""
        with self._lock:
            if self._closing:
                raise RuntimeError("Cannot connect while the HTTP client is closing.")
            if self.session is None:
                logger.debug("Initializing internal sync HTTP session (niquests)...")
                self.session = niquests.Session(resolver="system://", retries=self.retry_strategy)
                self._session_owner = True
            if not self._is_ready:
                self._is_ready = True
                if self._client.cache_endpoints:
                    self._loader.schedule_tasks()

    def request(self, route: Route) -> dict[str, t.Any]:
        """Makes a synchronous request to the PokeAPI.

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
        return self._validate_response(self._request_response(route), route)

    def _request_response(self, route: Route) -> niquests.Response:
        if self._closing:
            raise RuntimeError("Cannot make a request while the HTTP client is closing.")

        self.connect()

        if self.session is None:
            raise HTTPException("No session was provided.", route, -1).create()

        try:
            return self.session.request(route.method, route.url, params=route.payload)
        except niquests.RequestException as e:
            logger.error(f"Request failed for {route.url} ({type(e).__name__}): {e}")
            raise HTTPException(str(e), route, -1).create() from e

    def load_image(self, url: str) -> bytes:
        """Loads an image from the url synchronously.

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
        response = self._request_response(route)
        return self._validate_image(response, url)

    def load_audio(self, url: str) -> bytes:
        """Loads an audio from the url synchronously.

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
        response = self._request_response(route)
        return self._validate_audio(response, url)

    def ping(self) -> float:
        """Pings the PokeAPI and returns the latency."""
        start = time.perf_counter()
        self.request(Route())
        latency = time.perf_counter() - start
        logger.debug(f"PokeAPI sync ping latency: {latency:.4f}s")
        return latency
