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

    __slots__: t.Tuple[str, ...] = (
        "_client",
        "session",
        "_cache",
        "_is_ready",
    )

    def __init__(
        self, *, cache_size: int, client: "PokeLance", session: t.Optional[aiohttp.ClientSession] = None
    ) -> None:
        self._client = client
        self.session = session
        self._is_ready = False
        self._cache = Cache(max_size=cache_size)

    async def connect(self) -> None:
        if not self._is_ready:
            if self.session is None:
                self.session = aiohttp.ClientSession()
                await self._client.setup_hook()
            self._is_ready = True

    async def request(self, route: Route) -> t.Any:
        await self.connect()
        async with self.session.request(route.method, route.url, params=route.payload) as response:
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
