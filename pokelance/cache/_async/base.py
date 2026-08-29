from __future__ import annotations

import asyncio
import json
import logging
import pathlib
import typing as t

import aiofiles
import attrs
from typing_extensions import override

from pokelance.cache._base import BaseCacheGroup, BaseCacheState
from pokelance.endpoints import Route
from pokelance.exceptions import HTTPException

_KT = t.TypeVar("_KT", bound="Route")
_VT = t.TypeVar("_VT", bound="BaseModel | t.Sequence[BaseModel]")

if t.TYPE_CHECKING:
    from pokelance.client.async_client import PokeLanceAsyncClient  # ruff: ignore[unused-import]
    from pokelance.models import BaseModel

__all__: tuple[str, ...] = (
    "AsyncCache",
    "AsyncCacheGroup",
)

logger = logging.getLogger(__name__)


class AsyncCache(BaseCacheState[_KT, _VT, "PokeLanceAsyncClient"], t.Generic[_KT, _VT]):
    """Asynchronous cache partition supporting async readiness, non-blocking I/O, and batch loading.

    Extends `BaseCacheState` with an `asyncio.Event` readiness signal, async JSON serialization
    via `aiofiles`, and asynchronous batch network pre-fetching.

    Parameters
    ----------
    max_size : int, default: 100
        Maximum number of items to keep in memory before evicting least recently used items.
    model : type[BaseModel] | None, optional
        The PokeLance model class to instantiate when deserializing payloads.
    name : str, optional
        The name of this cache partition (e.g. 'pokemon', 'berry').
    endpoint_key_is_id : bool, default: False
        Whether the primary key for endpoints in this cache is the numeric ID rather than the name.
    url_suffix : str, default: ""
        URL suffix to append when building endpoint URLs (e.g. '/encounters').
    is_list : bool, default: False
        Whether this cache stores lists of models rather than single model instances.

    Examples
    --------
    ```python
    # Wait until the pokemon cache has pre-loaded all endpoint metadata
    await client.cache.pokemon.pokemon.wait_until_ready()

    # Save cached pokemon to disk asynchronously
    await client.cache.pokemon.pokemon.save("./cache_backup")

    # Load cached pokemon from disk asynchronously
    await client.cache.pokemon.pokemon.load("./cache_backup")
    ```
    """

    _ready: asyncio.Event

    def __init__(
        self,
        max_size: int = 100,
        model: type[BaseModel] | None = None,
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
        self._ready = asyncio.Event()

    @property
    def is_ready(self) -> bool:
        """Whether this cache partition has finished loading its endpoint identifiers."""
        return self._ready.is_set()

    async def wait_until_ready(self) -> None:
        """Waits asynchronously until this cache partition has loaded its endpoint identifiers.

        Examples
        --------
        ```python
        await client.cache.pokemon.pokemon.wait_until_ready()
        ```
        """
        await self._ready.wait()

    @override
    def set_ready(self) -> None:
        """Sets this cache partition as ready and unblocks any waiting tasks."""
        super().set_ready()
        self._ready.set()

    @override
    def reset_endpoints(self) -> None:
        """Clears endpoint registries and resets the readiness event."""
        super().reset_endpoints()
        self._ready.clear()

    async def save(self, path: str = ".") -> None:
        """Saves all cached data in this partition to a JSON file asynchronously.

        Parameters
        ----------
        path : str, default: "."
            Directory where `{name}.json` will be saved.

        Examples
        --------
        ```python
        await client.cache.pokemon.pokemon.save("./cache")
        ```
        """
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
        """Loads cached data into this partition from a JSON file asynchronously.

        Parameters
        ----------
        path : str, default: "."
            Directory containing `{name}.json`.

        Examples
        --------
        ```python
        await client.cache.pokemon.pokemon.load("./cache")
        ```
        """
        async with aiofiles.open(pathlib.Path(f"{path}/{self._name}.json"), encoding="utf-8") as f:
            self.deserialize(json.loads(await f.read()))

    async def load_all(self) -> None:
        """Fetches and caches all known resources for this endpoint sequentially.

        Raises
        ------
        RuntimeError
            If endpoints have not yet been registered or no model class is configured.

        Examples
        --------
        ```python
        await client.cache.berry.berry_firmness.load_all()
        ```
        """
        if not self._endpoints_cached or self._model is None:
            raise RuntimeError("Endpoints not loaded or model not set")
        logger.info(f"Loading {self._name}...")
        self._max_size = len(self._endpoints)
        for endpoint in self._endpoints.values():
            route = Route.from_raw_url(endpoint.url)
            data = self.get(t.cast("_KT", route), None)
            if not data:
                res = await self._client.http.request(route)
                self.setdefault(t.cast("_KT", route), self.from_payload(res))
        logger.info(f"Loaded {self._name}.")

    async def load_all_batch(self, batch_size: int = 20) -> None:
        """Fetches and caches all known resources for this endpoint in concurrent batches.

        Parameters
        ----------
        batch_size : int, default: 20
            The number of parallel HTTP requests to send in each batch.

        Raises
        ------
        RuntimeError
            If endpoints have not yet been registered or no model class is configured.

        Examples
        --------
        ```python
        await client.cache.berry.berry.load_all_batch(batch_size=15)
        ```
        """
        if not self._endpoints_cached or self._model is None:
            raise RuntimeError("Endpoints not loaded or model not set")
        logger.info(f"Loading {self._name}...")
        self._max_size = len(self._endpoints)
        endpoints = list(self._endpoints.values())
        total_endpoints = len(endpoints)
        for i in range(0, total_endpoints, batch_size):
            batch = endpoints[i : i + batch_size]
            tasks = [
                self._fetch_and_cache(t.cast("_KT", Route.from_raw_url(ep.url)))
                for ep in batch
                if not self.get(t.cast("_KT", Route.from_raw_url(ep.url)))
            ]
            if tasks:
                await asyncio.gather(*tasks)
            current_batch = i // batch_size + 1
            total_batches = (total_endpoints + batch_size - 1) // batch_size
            logger.debug(f"Loaded batch {current_batch}/{total_batches} for {self._name}")
        logger.info(f"Loaded {self._name} - {len(self._cache)}/{total_endpoints} items.")

    async def _fetch_and_cache(self, route: _KT) -> None:
        """Helper method to fetch and cache a single item."""
        if self._model is None:
            return
        try:
            data = await self._client.http.request(route)
            self.setdefault(route, self.from_payload(data))
        except (HTTPException, KeyError, ValueError, TypeError) as e:
            logger.error(f"Failed to load {route}: {e}")


@attrs.define(slots=True, kw_only=True)
class AsyncCacheGroup(BaseCacheGroup["PokeLanceAsyncClient", AsyncCache[Route, t.Any]]):
    """Category cache aggregate grouping multiple asynchronous sub-caches.

    Examples
    --------
    ```python
    # Wait until all pokemon category sub-caches are ready
    await client.cache.pokemon.wait_until_ready()

    # Clear all cached pokemon category models
    client.cache.pokemon.clear()
    ```
    """

    async def wait_until_ready(self) -> None:
        """Waits asynchronously until all sub-caches in this group are ready.

        Examples
        --------
        ```python
        await client.cache.pokemon.wait_until_ready()
        ```
        """
        tasks = [cache.wait_until_ready() for cache in self._walk_caches()]
        await asyncio.gather(*tasks)
