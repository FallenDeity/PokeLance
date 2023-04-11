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
    """

    __slots__: t.Tuple[str, ...] = (
        "_client",
        "session",
        "_cache",
        "_is_ready",
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
        self._cache = Cache(max_size=cache_size)

    def _load_endpoints(self) -> None:
        """Loads the endpoints for the HTTP client."""
        for num, (coro, name) in enumerate(self._client.loaders):
            task = asyncio.create_task(coro)
            task.add_done_callback(
                lambda _: self._client.logger.info(f"Loaded {self._client.loaders.pop(0)[1]} endpoints.")
            )
        self._is_ready = True

    async def connect(self) -> None:
        """Connects the HTTP client."""
        if not self._is_ready and self.session is None:
            self.session = aiohttp.ClientSession()
            self._load_endpoints()

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
        if self.session is None:
            await self.connect()
        if not self._is_ready and self._client.loaders:
            self._load_endpoints()
        if self.session is not None:
            async with self.session.request(route.method, route.url, params=route.payload) as response:
                if 300 > response.status >= 200:
                    return await response.json()
                else:
                    raise HTTPException(str(response.reason), route, response.status).create()
        else:
            raise HTTPException("No session was provided.", route, 0).create()

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
        """
        if self.session is None:
            await self.connect()
        if self.session is not None:
            async with self.session.get(url) as response:
                if 300 > response.status >= 200:
                    data: bytes = await response.read()
                    return data
                else:
                    raise ImageNotFound(str(response.reason), Route(), response.status).create()
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
