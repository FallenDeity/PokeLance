from __future__ import annotations

import asyncio
import json
import logging
import pathlib
import typing as t

import aiofiles

from pokelance.cache._base import Base, CacheEndpoint, CacheStateMixin
from pokelance.http.endpoints import Route

if t.TYPE_CHECKING:
    from pokelance.client.async_client import PokeLanceAsyncClient
    from pokelance.models import BaseModel

__all__: t.Tuple[str, ...] = (
    "CacheEndpoint",
    "CacheStateMixin",
    "Base",
    "AsyncIOMixin",
    "AsyncBaseCache",
)

logger = logging.getLogger(__name__)

_KT = t.TypeVar("_KT", bound="Route")
_VT = t.TypeVar("_VT", bound="t.Union[BaseModel, t.Sequence[BaseModel]]")


class AsyncIOMixin(CacheStateMixin[_KT, _VT, "PokeLanceAsyncClient"], t.Generic[_KT, _VT]):
    """Async file I/O (aiofiles) and async HTTP bulk loading."""

    async def save(self, path: str = ".") -> None:
        """Save the cache to a JSON file asynchronously."""
        pathlib.Path(path).mkdir(parents=True, exist_ok=True)
        data = self.serialize()
        async with aiofiles.open(pathlib.Path(f"{path}/{self._name}.json"), "w", encoding="utf-8") as f:
            await f.write("{\n")
            for n, (k, v) in enumerate(data.items()):
                await f.write("    " + f'"{k}": {json.dumps(v, indent=4)}')
                if n != len(data) - 1:
                    await f.write(",\n")
            await f.write("\n}")

    async def load(self, path: str = ".") -> None:
        """Load the cache from a JSON file asynchronously."""
        async with aiofiles.open(pathlib.Path(f"{path}/{self._name}.json"), "r", encoding="utf-8") as f:
            self.deserialize(json.loads(await f.read()))

    async def load_all(self) -> None:
        """Load all documents/data from api into the cache asynchronously."""
        if not self._endpoints_cached or self._model is None:
            raise RuntimeError("Endpoints not loaded or model not set")
        logger.info(f"Loading {self._name}...")
        self._max_size = len(self._endpoints)
        for endpoint in self._endpoints.values():
            route = Route.from_raw_url(endpoint.url)
            data = self.get(t.cast(_KT, route), None)
            if not data:
                res = await self._client.http.request(route)
                self.setdefault(t.cast(_KT, route), self.from_payload(res))
        logger.info(f"Loaded {self._name}.")

    async def load_all_batch(self, batch_size: int = 20) -> None:
        """Load all documents/data from api into the cache in parallel batches."""
        if not self._endpoints_cached or self._model is None:
            raise RuntimeError("Endpoints not loaded or model not set")
        logger.info(f"Loading {self._name}...")
        self._max_size = len(self._endpoints)
        endpoints = list(self._endpoints.values())
        total_endpoints = len(endpoints)
        for i in range(0, total_endpoints, batch_size):
            batch = endpoints[i : i + batch_size]
            tasks = [
                self._fetch_and_cache(t.cast(_KT, Route.from_raw_url(ep.url)))
                for ep in batch
                if not self.get(t.cast(_KT, Route.from_raw_url(ep.url)))
            ]
            if tasks:
                await asyncio.gather(*tasks)
            logger.debug(
                f"Loaded batch {i // batch_size + 1}/{(total_endpoints + batch_size - 1) // batch_size} for {self._name}"
            )
        logger.info(f"Loaded {self._name} - {len(self._cache)}/{total_endpoints} items.")

    async def _fetch_and_cache(self, route: _KT) -> None:
        """Helper method to fetch and cache a single item."""
        if self._model is None:
            return
        try:
            data = await self._client.http.request(route)
            self.setdefault(route, self.from_payload(data))
        except Exception as e:
            logger.error(f"Failed to load {route}: {e}")


class AsyncBaseCache(AsyncIOMixin[_KT, _VT], t.Generic[_KT, _VT]):
    """Async cache: asyncio.Event readiness, aiofiles I/O."""

    def __init__(
        self,
        max_size: int = 100,
        model: t.Optional[t.Type[BaseModel]] = None,
        name: str = "",
        endpoint_key_is_id: bool = False,
        url_suffix: str = "",
        is_list: bool = False,
    ) -> None:
        super().__init__(
            max_size=max_size,
            model=model,
            name=name,
            endpoint_key_is_id=endpoint_key_is_id,
            url_suffix=url_suffix,
            is_list=is_list,
        )
        self._endpoints_ready: asyncio.Event = asyncio.Event()

    def _mark_endpoints_cached(self) -> None:
        super()._mark_endpoints_cached()
        self._endpoints_ready.set()

    def reset_endpoints(self) -> None:
        super().reset_endpoints()
        self._endpoints_ready.clear()

    async def wait_until_ready(self) -> None:
        """Wait until all endpoints are cached."""
        if self._client.cache_endpoints:
            await self._endpoints_ready.wait()
