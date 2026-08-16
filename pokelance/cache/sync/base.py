from __future__ import annotations

import json
import logging
import pathlib
import threading
import typing as t

from pokelance.cache._base import Base, CacheEndpoint, CacheStateMixin
from pokelance.http.endpoints import Route

if t.TYPE_CHECKING:
    from pokelance.client.sync_client import PokeLanceSyncClient
    from pokelance.models import BaseModel

__all__: t.Tuple[str, ...] = (
    "CacheEndpoint",
    "CacheStateMixin",
    "Base",
    "SyncIOMixin",
    "SyncBaseCache",
)

logger = logging.getLogger(__name__)

_KT = t.TypeVar("_KT", bound="Route")
_VT = t.TypeVar("_VT", bound="t.Union[BaseModel, t.Sequence[BaseModel]]")


class SyncIOMixin(CacheStateMixin[_KT, _VT, "PokeLanceSyncClient"], t.Generic[_KT, _VT]):
    """Sync file I/O (save/load) and sync HTTP bulk loading.

    Uses standard open() / json.
    """

    def save(self, path: str = ".") -> None:
        """Save the cache to a JSON file."""
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
        """Load the cache from a JSON file."""
        with open(pathlib.Path(f"{path}/{self._name}.json"), "r", encoding="utf-8") as f:
            self.deserialize(json.loads(f.read()))

    def load_all(self) -> None:
        """Load all documents/data from api into the cache."""
        if not self._endpoints_cached or self._model is None:
            raise RuntimeError("Endpoints not loaded or model not set")
        logger.info(f"Loading {self._name}...")
        self._max_size = len(self._endpoints)
        for endpoint in self._endpoints.values():
            route = Route.from_raw_url(endpoint.url)
            data = self.get(t.cast(_KT, route), None)
            if not data:
                res = self._client.http.request(route)
                self.setdefault(t.cast(_KT, route), self.from_payload(res))
        logger.info(f"Loaded {self._name}.")

    def load_all_batch(self, batch_size: int = 20) -> None:
        """Load all documents from api into the cache in batches."""
        if not self._endpoints_cached or self._model is None:
            raise RuntimeError("Endpoints not loaded or model not set")
        logger.info(f"Loading {self._name} in batches...")
        self._max_size = len(self._endpoints)
        endpoints = list(self._endpoints.values())
        total_endpoints = len(endpoints)
        for i in range(0, total_endpoints, batch_size):
            batch = endpoints[i : i + batch_size]
            for ep in batch:
                route = Route.from_raw_url(ep.url)
                if not self.get(t.cast(_KT, route)):
                    res = self._client.http.request(route)
                    self.setdefault(t.cast(_KT, route), self.from_payload(res))
        logger.info(f"Loaded {self._name} - {len(self._cache)}/{total_endpoints} items.")


class SyncBaseCache(SyncIOMixin[_KT, _VT], t.Generic[_KT, _VT]):
    """Sync cache: threading.Event readiness, sync I/O."""

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
        self._endpoints_ready: threading.Event = threading.Event()

    def _mark_endpoints_cached(self) -> None:
        super()._mark_endpoints_cached()
        self._endpoints_ready.set()

    def reset_endpoints(self) -> None:
        super().reset_endpoints()
        self._endpoints_ready.clear()

    def wait_until_ready(self) -> None:
        """Wait until all endpoints are cached."""
        if self._client.cache_endpoints:
            self._endpoints_ready.wait()
