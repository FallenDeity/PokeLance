# pyright: reportUnknownMemberType=false
from __future__ import annotations

import concurrent.futures
import logging
import threading
import time
import typing as t

import niquests

from pokelance.cache.sync.manager import SyncCacheManager
from pokelance.endpoints import Route
from pokelance.exceptions import HTTPException
from pokelance.http._base import BaseHttpClient

if t.TYPE_CHECKING:
    from pokelance.client.sync_client import PokeLanceSyncClient

__all__: tuple[str, ...] = ("SyncEndpointLoader", "SyncHttpClient")

logger = logging.getLogger(__name__)


class SyncEndpointLoader:
    """Composition helper for scheduling and tracking sync endpoint pre-population tasks via thread pool."""

    def __init__(self, client: PokeLanceSyncClient) -> None:
        self._client = client
        self._executor: concurrent.futures.ThreadPoolExecutor | None = None
        self._futures: set[concurrent.futures.Future[None]] = set()
        self._remaining: int = 0
        self._lock = threading.Lock()
        self._ready_event = threading.Event()
        self._ready_event.set()
        self._scheduled: bool = False

    @property
    def is_ready(self) -> bool:
        """Whether all background loading tasks have finished."""
        return self._ready_event.is_set()

    def wait_until_ready(self) -> None:
        """Wait until all background endpoint tasks have completed."""
        awaiting = not self._ready_event.is_set()
        if awaiting:
            logger.info("Waiting for endpoint loading to complete...")
        self._ready_event.wait()
        if awaiting:
            logger.info("Endpoint loading complete.")

    def _load_ext(self, fn: t.Callable[[], None], message: str) -> None:
        """Load an extension's resources synchronously in a thread."""
        logger.debug(f"Loading {message}...")
        try:
            fn()
        except Exception:
            if self._client.http.is_closing:
                logger.debug(f"Extension loading aborted due to client closing: {message}")
                return
            logger.exception(f"Failed loading {message}")
            raise
        finally:
            with self._lock:
                self._remaining -= 1
                remaining = self._remaining
                if remaining <= 0:
                    self._ready_event.set()
        logger.info(f"Loaded {message} ({remaining} remaining)")

    def schedule_tasks(self) -> None:
        """Schedules the background endpoint-loading tasks on a thread pool."""
        with self._lock:
            if self._scheduled:
                return
            self._scheduled = True
            self._ready_event.clear()
            if not self._client.cache_endpoints:
                self._ready_event.set()
                self._client.ext_tasks.clear()
                return
            total = len(self._client.ext_tasks)
            self._remaining = total
            logger.info(f"Scheduling {total} endpoint pre-population task(s)...")
            if self._executor is None:
                self._executor = concurrent.futures.ThreadPoolExecutor(
                    max_workers=min(32, max(4, total)),
                    thread_name_prefix="PokeLance-EndpointLoader",
                )
            for num, (fn, name) in enumerate(self._client.ext_tasks):
                message = f"Extension {name} endpoints ({num + 1}/{total})"
                future = self._executor.submit(self._load_ext, fn, message)
                self._futures.add(future)
                future.add_done_callback(self._futures.discard)
            self._client.ext_tasks.clear()
            if self._remaining == 0:
                self._ready_event.set()

    def shutdown(self) -> None:
        """Cancels and shuts down the loader thread pool."""
        with self._lock:
            count = sum(1 for f in self._futures if not f.done())
            if count > 0:
                logger.warning(f"Cancelling {count} in-flight endpoint loading tasks...")
            for future in list(self._futures):
                future.cancel()
            if self._executor is not None:
                logger.debug("Shutting down endpoint loader thread pool...")
                self._executor.shutdown(wait=False, cancel_futures=True)
                self._executor = None


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
                session_to_close = self.session if self._session_owner else None
                self.session = None
                if session_to_close:
                    logger.debug("Closing internal sync HTTP session...")
                    session_to_close.close()
                self._loader.shutdown()
            finally:
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
        if self._closing:
            raise RuntimeError("Cannot make a request while the HTTP client is closing.")

        self.connect()

        if self.session is None:
            raise HTTPException("No session was provided.", route, -1).create()

        try:
            logger.debug(f"Sending {route.method} request to {route.url}")
            response = self.session.request(route.method, route.url, params=route.payload)
            return self._validate_response(response, route)
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
        self.connect()
        if self.session is not None:
            logger.debug(f"Fetching image from {url}")
            response = self.session.get(url)
            return self._validate_image(response, url)
        return b""

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
        self.connect()
        if self.session is not None:
            logger.debug(f"Fetching audio from {url}")
            response = self.session.get(url)
            return self._validate_audio(response, url)
        return b""

    def ping(self) -> float:
        """Pings the PokeAPI and returns the latency."""
        start = time.perf_counter()
        self.request(Route())
        latency = time.perf_counter() - start
        logger.debug(f"PokeAPI sync ping latency: {latency:.4f}s")
        return latency
