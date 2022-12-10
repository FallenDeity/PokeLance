import time
import typing as t

import aiohttp

from pokelance.cache import Cache
from pokelance.exceptions import HTTPException

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

    __slots__: t.Tuple[str, ...] = ("_client", "_session", "_cache")

    def __init__(
        self, *, cache_size: int, client: "PokeLance", session: t.Optional[aiohttp.ClientSession] = None
    ) -> None:
        self._client = client
        self._session = session or aiohttp.ClientSession()
        self._cache = Cache(max_size=cache_size)
        if self._client.session is None:
            self._client._session = self._session

    async def request(self, route: Route) -> t.Any:
        async with self._session.request(route.method, route.url, params=route.payload) as response:
            if 300 > response.status >= 200:
                return await response.json()
            else:
                raise HTTPException(str(response.reason), route, response.status).create()

    async def ping(self) -> float:
        start = time.perf_counter()
        await self.request(Route())
        return time.perf_counter() - start

    @property
    def cache(self) -> Cache:
        return self._cache
