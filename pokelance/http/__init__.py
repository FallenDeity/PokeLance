import asyncio
import time
import typing as t

import aiohttp

from pokelance.cache import Cache
from pokelance.exceptions import HTTPException, ImageNotFound

from .endpoints import Endpoint, Route

if t.TYPE_CHECKING:
    from pokelance import PokeLance


__all__: t.Tuple[str, ...] = (
    "HttpClient",
    "Route",
    "Endpoint",
)


@t.final
class HttpClient:
    """The HTTP client for PokeLance.

    Parameters
    ----------
    client: pokelance.PokeLance
        The client that this HTTP client is for.
    cache_size: int
        The size of the cache.
    session: aiohttp.ClientSession
        The session to use for the HTTP client.

    Attributes
    ----------
    session: aiohttp.ClientSession
        The session to use for the HTTP client.
    _is_ready: bool
        Whether the HTTP client is ready.
    _cache: pokelance.cache.Cache
        The cache to use for the HTTP client.
    _client: pokelance.PokeLance
        The client that this HTTP client is for.
    _tasks_queue: typing.List[asyncio.Task]
        The queue for the tasks.
    """

    __slots__: t.Tuple[str, ...] = (
        "_client",
        "session",
        "_cache",
        "_is_ready",
        "_tasks_queue",
    )

    def __init__(
        self, *, cache_size: int, client: "PokeLance", session: t.Optional[aiohttp.ClientSession] = None
    ) -> None:
        """Initializes the HTTP client.

        Parameters
        ----------
        cache_size: int
            The size of the cache.
        client: pokelance.PokeLance
            The client that this HTTP client is for.
        session: aiohttp.ClientSession
            The session to use for the HTTP client.

        Returns
        -------
        pokelance.http.HttpClient
            The HTTP client.
        """
        self._client = client
        self.session = session
        self._is_ready = False
        self._cache = Cache(max_size=cache_size, client=self._client)
        self._tasks_queue: t.List[asyncio.Task[None]] = []

    async def _load_ext(self, coroutine: t.Callable[[], t.Coroutine[t.Any, t.Any, None]], message: str) -> None:
        """
        Load an extension's resources.

        Parameters
        ----------
        coroutine: typing.Coroutine
            The coroutine to load.
        message: str
            The message to log.
        """
        task: t.Optional[asyncio.Task[None]] = asyncio.current_task()
        self._client.logger.debug(f"Loading {message}")
        await coroutine()
        if task is not None:
            self._tasks_queue.remove(task)
        self._client.logger.info(f"Loaded {message}")

    async def _schedule_tasks(self) -> None:
        """Schedules the tasks for the HTTP client."""
        total = len(self._client.ext_tasks)
        for num, (coroutine, name) in enumerate(self._client.ext_tasks):
            message = f"Extension {name} endpoints ({num + 1}/{total})"
            task = asyncio.create_task(coro=self._load_ext(coroutine, message), name=name)
            self._tasks_queue.append(task)
        self._client.ext_tasks.clear()

    async def close(self) -> None:
        """Closes the HTTP client."""
        for task in self._tasks_queue:
            if not task.done():
                task.cancel()
                self._client.logger.warning(f"Cancelled task {task.get_name()}")
        if self.session:
            await self.session.close()

    async def connect(self) -> None:
        """Connects the HTTP client."""
        if self.session is None:
            self.session = self.session or aiohttp.ClientSession()
        if not self._is_ready:
            if self._client.cache_endpoints:
                await self._schedule_tasks()
            self._is_ready = True

    async def request(self, route: Route) -> t.Any:
        """Makes a request to the PokeAPI.

        Parameters
        ----------
        route: pokelance.http.Route
            The route to use for the request.

        Returns
        -------
        t.Any
            The response from the PokeAPI.

        Raises
        ------
        pokelance.exceptions.HTTPException
            An error occurred while making the request.
        """
        await self.connect()
        if self.session is not None:
            async with self.session.request(route.method, route.url, params=route.payload) as response:
                if 300 > response.status >= 200:
                    self._client.logger.debug(f"Request to {route.url} was successful.")
                    return await response.json()
                else:
                    self._client.logger.error(f"Request to {route.url} was unsuccessful.")
                    raise HTTPException(str(response.reason), route, response.status).create()
        else:
            raise HTTPException("No session was provided.", route, -1).create()

    async def load_image(self, url: str) -> bytes:
        """Loads an image from the url.

        Parameters
        ----------
        url: str
            The URL to load the image from.

        Returns
        -------
        bytes
            The image.

        Raises
        ------
        pokelance.exceptions.ImageNotFound
            The image was not found.
        """
        await self.connect()
        _image_formats = ("png", "jpg", "jpeg", "gif", "webp", "svg")
        if self.session is not None:
            async with self.session.get(url) as response:
                is_image = any(f_ in response.content_type for f_ in _image_formats)
                if 300 > response.status >= 200 and is_image:
                    self._client.logger.debug(f"Request to {url} was successful.")
                    return await response.read()
                else:
                    self._client.logger.error(f"Request to {url} was unsuccessful.")
                    message = f"Request to {url} was unsuccessful or the URL is not an image."
                    raise ImageNotFound(f"{message} ({response.content_type})", Route(), response.status)
        return b""

    async def ping(self) -> float:
        """Pings the PokeAPI and returns the latency.

        Returns
        -------
        float
            The latency of the PokeAPI.
        """
        start = time.perf_counter()
        await self.request(Route())
        return time.perf_counter() - start

    @property
    def cache(self) -> Cache:
        """The cache to use for the HTTP client.

        Returns
        -------
        pokelance.cache.Cache
            The cache.
        """
        return self._cache
