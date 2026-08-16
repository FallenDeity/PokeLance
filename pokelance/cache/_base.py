from __future__ import annotations

import typing as t
from collections import OrderedDict

import attrs

from pokelance.endpoints import Route
from pokelance.models import BaseModel

if t.TYPE_CHECKING:
    from pokelance.cache._async import AsyncCache
    from pokelance.cache.sync import SyncCache
    from pokelance.client._base import _ClientBase

    AnyCache = AsyncCache[Route, t.Any] | SyncCache[Route, t.Any]

__all__: tuple[str, ...] = (
    "BaseCacheGroup",
    "BaseCacheManager",
    "BaseCacheState",
    "CacheEndpoint",
    "CacheStats",
)

_KT = t.TypeVar("_KT", bound="Route")
_VT = t.TypeVar("_VT", bound="BaseModel | t.Sequence[BaseModel]")
_ClientT = t.TypeVar("_ClientT", bound="_ClientBase")
_CacheT = t.TypeVar("_CacheT", bound="AnyCache")
_GroupT = t.TypeVar("_GroupT", bound="BaseCacheGroup[t.Any, t.Any]")


@attrs.define(kw_only=True, slots=True, frozen=True)
class CacheEndpoint:
    """Represents a cached API endpoint.

    Attributes
    ----------
    id : str | int
        The ID of the endpoint.
    url : str
        The URL of the endpoint.
    """

    id: str | int = attrs.field(factory=str)
    url: str = attrs.field(factory=str)

    def __str__(self) -> str:
        return str(self.id)


@attrs.define(slots=True, kw_only=True)
class CacheStats:
    """Statistics tracking cache hits, misses, insertions, and evictions."""

    hits: int = 0
    misses: int = 0
    sets: int = 0
    evictions: int = 0

    @property
    def total_lookups(self) -> int:
        """Total number of cache lookup requests (hits + misses)."""
        return self.hits + self.misses

    @property
    def hit_ratio(self) -> float:
        """Ratio of cache hits to total lookups (0.0 - 1.0)."""
        total = self.total_lookups
        return (self.hits / total) if total > 0 else 0.0

    def reset(self) -> None:
        """Reset all statistical counters."""
        self.hits = 0
        self.misses = 0
        self.sets = 0
        self.evictions = 0

    def __add__(self, other: object) -> CacheStats:
        if not isinstance(other, CacheStats):
            raise TypeError(f"Cannot add CacheStats with {type(other).__name__}")
        return CacheStats(
            hits=self.hits + other.hits,
            misses=self.misses + other.misses,
            sets=self.sets + other.sets,
            evictions=self.evictions + other.evictions,
        )

    def __radd__(self, other: object) -> CacheStats:
        return self.__add__(other)


class BaseCacheState(t.MutableMapping[_KT, _VT], t.Generic[_KT, _VT, _ClientT]):
    """All in-memory operations. No I/O. No async. No events.

    Fully testable without an event loop or HTTP session.
    """

    _client: _ClientT

    def __init__(
        self,
        max_size: int = 100,
        model: type[BaseModel] | None = None,
        name: str = "",
        endpoint_key_is_id: bool = False,
        url_suffix: str = "",
        is_list: bool = False,
    ) -> None:
        self._max_size = max_size
        self._model = model
        self._name = name or self.__class__.__name__
        self._endpoint_key_is_id = endpoint_key_is_id
        self._url_suffix = url_suffix
        self._is_list = is_list
        self._cache: OrderedDict[_KT, _VT] = OrderedDict()
        self._endpoints: dict[str, CacheEndpoint] = {}
        self._endpoints_by_id: dict[str, str] = {}
        self._identifiers: set[str] = set()
        self._endpoints_cached: bool = False
        self._stats: CacheStats = CacheStats()

    @property
    def stats(self) -> CacheStats:
        """Statistics for this specific cache."""
        return self._stats

    def from_payload(self, payload: dict[str, t.Any] | list[dict[str, t.Any]]) -> _VT:
        """Create a model instance or list of model instances from a raw payload."""
        if self._model is None:
            raise RuntimeError(f"Model class not configured for cache '{self._name}'")
        if isinstance(payload, list):
            return t.cast("_VT", [self._model.from_payload(item) for item in payload])
        return t.cast("_VT", self._model.from_payload(payload))

    def __getitem__(self, key: _KT) -> _VT:
        try:
            val = self._cache[key]
            self._cache.move_to_end(key)
            self._stats.hits += 1
            return val
        except KeyError:
            self._stats.misses += 1
            raise

    def __setitem__(self, key: _KT, value: _VT) -> None:
        self._stats.sets += 1
        if key in self._cache:
            self._cache[key] = value
            self._cache.move_to_end(key)
        else:
            if len(self._cache) >= self._max_size:
                self._cache.popitem(last=False)
                self._stats.evictions += 1
            self._cache[key] = value

    def __delitem__(self, key: _KT) -> None:
        del self._cache[key]

    def __len__(self) -> int:
        return len(self._cache)

    def __iter__(self) -> t.Iterator[_KT]:
        return iter(self._cache)

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}({self._cache})"

    def keys(self) -> t.KeysView[_KT]:
        return self._cache.keys()

    def values(self) -> t.ValuesView[_VT]:
        return self._cache.values()

    def items(self) -> t.ItemsView[_KT, _VT]:
        return self._cache.items()

    def setdefault(self, __key: _KT, /, __default: _VT | None = None) -> _VT:
        if __key not in self._cache and __default is not None:
            self[__key] = __default
            return self._cache[__key]
        self._stats.hits += 1
        self._cache.move_to_end(__key)
        return self._cache[__key]

    def clear(self) -> None:
        """Clear the cached data only. The endpoint registry is left intact."""
        self._cache.clear()

    def _mark_endpoints_cached(self) -> None:
        self._identifiers = set(self._endpoints) | set(self._endpoints_by_id)
        self.set_ready()

    def set_ready(self) -> None:
        """Set the cache endpoint state as ready."""
        self._endpoints_cached = True

    def reset_endpoints(self) -> None:
        """Clear the endpoint registry."""
        self._endpoints.clear()
        self._endpoints_by_id.clear()
        self._identifiers.clear()
        self._endpoints_cached = False

    def get(self, key: _KT, default: _VT | None = None) -> _VT | None:  # pyright: ignore[reportIncompatibleMethodOverride]
        """Get an item from the cache. If the exact key isn't found, attempt alias resolution."""
        if key in self._cache:
            self._stats.hits += 1
            self._cache.move_to_end(key)
            return self._cache[key]
        requested = key.endpoint.split("/")[-1]
        alias = self._endpoints_by_id.get(requested) or self._endpoints.get(requested)
        if alias:
            for k, v in self.items():
                if k.endpoint.split("/")[-1] == str(alias):
                    self._stats.hits += 1
                    self._cache.move_to_end(k)
                    return v
        self._stats.misses += 1
        return default

    def load_documents(self, data: list[dict[str, str]]) -> None:
        """Abstracted to handle standard, secondary, and location area endpoints."""
        self.reset_endpoints()
        for document in data:
            original_url = document["url"]
            id_ = int(original_url.split("/")[-2])

            key = str(id_) if self._endpoint_key_is_id else document["name"]
            url = f"{original_url.strip('/')}{self._url_suffix}" if self._url_suffix else original_url

            self._endpoints[key] = CacheEndpoint(url=url, id=id_)
            self._endpoints_by_id[str(id_)] = key

        self._mark_endpoints_cached()

    def set_size(self, size: int) -> None:
        """Set the max size of the cache."""
        self._max_size = size

    def serialize(self) -> dict[str, t.Any]:
        """Serialise the in-memory cache to a plain dict."""
        dummy: dict[str, t.Any] = {}
        for k, v in self.items():
            dummy[k.endpoint] = v.raw if isinstance(v, BaseModel) else [i.raw for i in v]
        return dummy

    def deserialize(self, data: dict[str, t.Any]) -> None:
        """Populate the in-memory cache from a plain dict (output of serialize)."""
        self._max_size = max(self._max_size, len(data))
        for endpoint, info in data.items():
            route = Route(endpoint=endpoint)
            self.setdefault(t.cast("_KT", route), self.from_payload(info))

    @property
    def endpoints(self) -> dict[str, CacheEndpoint]:
        """The endpoints that are cached."""
        return self._endpoints

    @property
    def identifiers(self) -> set[str]:
        """Every valid name and id (as strings) for this category."""
        return self._identifiers

    @property
    def cache(self) -> OrderedDict[_KT, _VT]:
        """The cache itself."""
        return self._cache


@attrs.define(slots=True, kw_only=True)
class BaseCacheGroup(t.Generic[_ClientT, _CacheT]):
    """Base class for all cache groups / aggregates."""

    max_size: int

    @property
    def stats(self) -> CacheStats:
        """Aggregated statistics across all sub-caches in this group."""
        return sum((cache.stats for cache in self._walk_caches()), CacheStats())

    def _walk_caches(self) -> t.Iterator[_CacheT]:
        """Yield all sub-caches belonging to this cache group."""
        for field in attrs.fields(self.__class__):
            val = getattr(self, field.name)
            if isinstance(val, BaseCacheState):
                yield t.cast("_CacheT", val)

    def set_client(self, client: _ClientT) -> None:
        """Set the client for all sub-caches in this group."""
        for cache in self._walk_caches():
            cache._client = client  # pyright: ignore[reportPrivateUsage, reportAttributeAccessIssue]

    def set_size(self, max_size: int = 100) -> None:
        """Set the maximum cache size for this group and its sub-caches."""
        self.max_size = max_size
        for cache in self._walk_caches():
            cache.set_size(max_size)

    def clear(self) -> None:
        """Clear all data in this cache group."""
        for cache in self._walk_caches():
            cache.clear()

    def reset(self) -> None:
        """Reset all endpoint registries in this cache group."""
        for cache in self._walk_caches():
            cache.reset_endpoints()


@attrs.define(slots=True, kw_only=True)
class BaseCacheManager(t.Generic[_ClientT, _GroupT]):
    """Base class for cache managers (sync and async)."""

    client: _ClientT
    max_size: int = 100

    def _walk_aggregates(self) -> t.Iterator[_GroupT]:
        """Yield all child cache aggregates."""
        for field in attrs.fields(self.__class__):
            val = getattr(self, field.name)
            if isinstance(val, BaseCacheGroup):
                yield t.cast("_GroupT", val)

    def __attrs_post_init__(self) -> None:
        for aggregate in self._walk_aggregates():
            aggregate.set_size(self.max_size)
            aggregate.set_client(self.client)

    def set_size(self, max_size: int = 100) -> None:
        """Set max cache size across all aggregates."""
        self.max_size = max_size
        for aggregate in self._walk_aggregates():
            aggregate.set_size(max_size)

    def load_documents(self, category: str, _type: str, data: list[dict[str, str]]) -> None:
        """Load endpoint documents into the specified category subcache."""
        getattr(getattr(self, category.lower()), _type).load_documents(data)

    def clear(self) -> None:
        """Clear all cached data in all aggregates."""
        for aggregate in self._walk_aggregates():
            aggregate.clear()

    def reset(self) -> None:
        """Reset all endpoint registries in all aggregates."""
        for aggregate in self._walk_aggregates():
            aggregate.reset()

    @property
    def stats(self) -> CacheStats:
        """Aggregate statistics across all sub-caches in all aggregates."""
        return sum((aggregate.stats for aggregate in self._walk_aggregates()), CacheStats())
