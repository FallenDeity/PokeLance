from __future__ import annotations

import json
import logging
import pathlib
import threading
import typing as t

import attrs

from pokelance.cache._base import BaseCacheGroup, BaseCacheState, CacheEndpoint
from pokelance.endpoints import Route
from pokelance.exceptions import HTTPException

_KT = t.TypeVar("_KT", bound="Route")
_VT = t.TypeVar("_VT", bound="BaseModel | t.Sequence[BaseModel]")

if t.TYPE_CHECKING:
    from pokelance.cache.sync import SyncCache
    from pokelance.client.sync_client import PokeLanceSyncClient
    from pokelance.models import BaseModel

    _BaseCacheState = BaseCacheState[_KT, _VT, PokeLanceSyncClient]
    _BaseCacheGroup = BaseCacheGroup[PokeLanceSyncClient, SyncCache[Route, t.Any]]
else:
    _BaseCacheState = BaseCacheState
    _BaseCacheGroup = BaseCacheGroup

__all__: tuple[str, ...] = (
    "BaseCacheGroup",
    "BaseCacheState",
    "CacheEndpoint",
    "SyncCache",
    "SyncCacheGroup",
)

logger = logging.getLogger(__name__)


class SyncCache(_BaseCacheState[_KT, _VT], t.Generic[_KT, _VT]):
    """Sync cache: threading.Event readiness, synchronous file I/O, and sync HTTP bulk loading."""

    _ready: threading.Event

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
        self._ready = threading.Event()

    @property
    def is_ready(self) -> bool:
        """Whether the cache is ready."""
        return self._ready.is_set()

    def wait_until_ready(self) -> None:
        """Wait until the cache is ready."""
        self._ready.wait()

    def set_ready(self) -> None:
        """Set the cache as ready."""
        super().set_ready()
        self._ready.set()

    def reset_endpoints(self) -> None:
        """Reset endpoints and clear readiness."""
        super().reset_endpoints()
        self._ready.clear()

    def save(self, path: str = ".") -> None:
        """Save the cache to a JSON file synchronously."""
        pathlib.Path(path).mkdir(parents=True, exist_ok=True)
        data = self.serialize()
        with open(pathlib.Path(f"{path}/{self._name}.json"), "w", encoding="utf-8") as f:
            f.write("{\n")
            for n, (k, v) in enumerate(data.items()):
                f.write("    " + f'"{k}": {json.dumps(v, indent=4)}')
                if n != len(data) - 1:
                    f.write(",\n")
            f.write("\n}")

    def load(self, path: str = ".") -> None:
        """Load the cache from a JSON file synchronously."""
        data = pathlib.Path(f"{path}/{self._name}.json").read_text(encoding="utf-8")
        self.deserialize(json.loads(data))

    def load_all(self) -> None:
        """Load all documents/data from api into the cache synchronously."""
        if not self._endpoints_cached or self._model is None:
            raise RuntimeError("Endpoints not loaded or model not set")
        logger.info(f"Loading {self._name}...")
        self._max_size = len(self._endpoints)
        for endpoint in self._endpoints.values():
            route = Route.from_raw_url(endpoint.url)
            data = self.get(t.cast("_KT", route), None)
            if not data:
                res = self._client.http.request(route)
                self.setdefault(t.cast("_KT", route), self.from_payload(res))
        logger.info(f"Loaded {self._name}.")

    def load_all_batch(self, batch_size: int = 20) -> None:
        """Load all documents/data from api into the cache in batches."""
        if not self._endpoints_cached or self._model is None:
            raise RuntimeError("Endpoints not loaded or model not set")
        logger.info(f"Loading {self._name}...")
        self._max_size = len(self._endpoints)
        endpoints = list(self._endpoints.values())
        total_endpoints = len(endpoints)
        for i in range(0, total_endpoints, batch_size):
            batch = endpoints[i : i + batch_size]
            for ep in batch:
                route = t.cast("_KT", Route.from_raw_url(ep.url))
                if not self.get(route):
                    self._fetch_and_cache(route)
            current_batch = i // batch_size + 1
            total_batches = (total_endpoints + batch_size - 1) // batch_size
            logger.debug(f"Loaded batch {current_batch}/{total_batches} for {self._name}")
        logger.info(f"Loaded {self._name} - {len(self._cache)}/{total_endpoints} items.")

    def _fetch_and_cache(self, route: _KT) -> None:
        """Helper method to fetch and cache a single item synchronously."""
        if self._model is None:
            return
        try:
            data = self._client.http.request(route)
            self.setdefault(route, self.from_payload(data))
        except (HTTPException, KeyError, ValueError, TypeError) as e:
            logger.error(f"Failed to load {route}: {e}")


@attrs.define(slots=True, kw_only=True)
class SyncCacheGroup(_BaseCacheGroup):
    """Base class for sync cache groups."""

    def wait_until_ready(self) -> None:
        """Wait for all sub-caches in this group to be ready."""
        for cache in self._walk_caches():
            cache.wait_until_ready()
