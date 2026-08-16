from __future__ import annotations

import concurrent.futures
import logging
import threading
import time
import typing as t

import niquests

from pokelance.cache.sync.manager import SyncCacheManager
from pokelance.exceptions import HTTPException
from pokelance.http._base import BaseHttpClient
from pokelance.http.endpoints import Route

if t.TYPE_CHECKING:
    from pokelance.client.sync_client import PokeLanceSyncClient

__all__: t.Tuple[str, ...] = ("SyncHttpClient", "SyncEndpointLoader")

logger = logging.getLogger(__name__)


class SyncEndpointLoader:
    """Composition helper for scheduling and tracking sync endpoint pre-population tasks via thread pool."""

    def __init__(self, client: "PokeLanceSyncClient") -> None:
        self._client = client
        self._executor: t.Optional[concurrent.futures.ThreadPoolExecutor] = None
        self._futures: t.Set[concurrent.futures.Future[None]] = set()
        self._remaining: int = 0
        self._lock = threading.Lock()
        self._ready_event = threading.Event()
        self._ready_event.set()

    @property
    def is_ready(self) -> bool:
        """Whether all background loading tasks have finished."""
        return self._ready_event.is_set()

    def wait_until_ready(self) -> None:
        """Wait until all background endpoint tasks have completed."""
        self._ready_event.wait()

    def _load_ext(self, fn: t.Callable[[], None], message: str) -> None:
        """Load an extension's resources synchronously in a thread."""
        logger.debug(f"Loading {message}")
        try:
            fn()
        finally:
            with self._lock:
                self._remaining -= 1
                if self._remaining <= 0:
                    self._ready_event.set()
        logger.info(f"Loaded {message}")

    def schedule_tasks(self) -> None:
        """Schedules the background endpoint-loading tasks on a thread pool."""
        self._ready_event.clear()
        if not self._client.cache_endpoints:
            self._ready_event.set()
            self._client.ext_tasks.clear()
            return
        total = len(self._client.ext_tasks)
        self._remaining = total
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
        for future in list(self._futures):
            future.cancel()
        if self._executor is not None:
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
    session: t.Optional[niquests.Session]
        The session to use for the HTTP client. If not provided, one is created
        internally on the first request and owned by this client.
    """

    __slots__: t.Tuple[str, ...] = (
        "_client",
        "session",
        "_cache",
        "_is_ready",
        "_loader",
        "_session_owner",
    )

    def __init__(
        self,
        *,
        cache_size: int,
        client: "PokeLanceSyncClient",
        session: t.Optional[niquests.Session] = None,
    ) -> None:
        super().__init__(client=client, session=session)
        self._cache = SyncCacheManager(max_size=cache_size, client=self._client)
        self._loader = SyncEndpointLoader(client=self._client)

    @property
    def loader(self) -> SyncEndpointLoader:
        """The endpoint loader composition helper."""
        return self._loader

    def close(self) -> None:
        """Closes the HTTP client and shuts down the endpoint loader thread pool."""
        self._loader.shutdown()
        if self.session and self._session_owner:
            self.session.close()
        elif self.session:
            logger.debug("Session was provided externally, not closing it.")

    def connect(self) -> None:
        """Connects the HTTP client and sets up the session."""
        if self.session is None:
            self.session = niquests.Session(resolver="system://")
            self._session_owner = True
        if not self._is_ready:
            if self._client.cache_endpoints:
                self._loader.schedule_tasks()
            self._is_ready = True

    def request(self, route: Route) -> t.Any:
        """Makes a synchronous request to the PokeAPI.

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
        self.connect()
        if self.session is not None:
            response = self.session.request(route.method, route.url, params=route.payload)
            return self._validate_response(response, route)
        raise HTTPException("No session was provided.", route, -1).create()

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
            response = self.session.get(url)
            return self._validate_audio(response, url)
        return b""

    def ping(self) -> float:
        """Pings the PokeAPI and returns the latency."""
        start = time.perf_counter()
        self.request(Route())
        return time.perf_counter() - start
