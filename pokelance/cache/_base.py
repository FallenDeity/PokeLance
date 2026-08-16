from __future__ import annotations

import typing as t

import attrs

from pokelance.http.endpoints import Route

if t.TYPE_CHECKING:
    from pokelance.cache._async import AsyncBaseCache
    from pokelance.cache.sync import SyncBaseCache
    from pokelance.client._base import _ClientBase
    from pokelance.models import BaseModel

    AnyCache = t.Union[AsyncBaseCache[Route, t.Any], SyncBaseCache[Route, t.Any]]

__all__: t.Tuple[str, ...] = (
    "CacheEndpoint",
    "BaseCacheState",
    "BaseCacheGroup",
)

_KT = t.TypeVar("_KT", bound="Route")
_VT = t.TypeVar("_VT", bound="t.Union[BaseModel, t.Sequence[BaseModel]]")
_ClientT = t.TypeVar("_ClientT", bound="_ClientBase")
_CacheT = t.TypeVar("_CacheT", bound="AnyCache")
_T = t.TypeVar("_T")


@attrs.define(kw_only=True, slots=True, frozen=True)
class CacheEndpoint:
    """Represents a cached API endpoint.

    Attributes
    ----------
    id : t.Union[str, int]
        The ID of the endpoint.
    url : str
        The URL of the endpoint.
    """

    id: t.Union[str, int] = attrs.field(factory=str)
    url: str = attrs.field(factory=str)

    def __str__(self) -> str:
        return str(self.id)


class BaseCacheState(t.MutableMapping[_KT, _VT], t.Generic[_KT, _VT, _ClientT]):
    """All in-memory operations. No I/O. No async. No events.

    Fully testable without an event loop or HTTP session.
    """

    _client: _ClientT

    def __init__(
        self,
        max_size: int = 100,
        model: t.Optional[t.Type[BaseModel]] = None,
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
        self._cache: t.Dict[_KT, _VT] = {}
        self._endpoints: t.Dict[str, CacheEndpoint] = {}
        self._endpoints_by_id: t.Dict[str, str] = {}
        self._identifiers: t.Set[str] = set()
        self._endpoints_cached: bool = False

    def from_payload(self, payload: t.Any) -> _VT:
        """Create a model instance or list of model instances from a raw payload."""
        if self._model is None:
            raise RuntimeError(f"Model class not configured for cache '{self._name}'")
        if self._is_list:
            return t.cast(_VT, [self._model.from_payload(item) for item in payload])
        return t.cast(_VT, self._model.from_payload(payload))

    def __getitem__(self, key: _KT) -> _VT:
        self._cache[key] = self._cache.pop(key)
        return self._cache[key]

    def __setitem__(self, key: _KT, value: _VT) -> None:
        if key in self._cache:
            self._cache[key] = self._cache.pop(key)
        else:
            if len(self._cache) >= self._max_size:
                self._cache.pop(list(self._cache.keys())[0])
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

    def setdefault(self, __key: _KT, __default: t.Any = ...) -> _VT:
        if __key not in self:
            self[__key] = __default
        return self[__key]

    def clear(self) -> None:
        """Clear the cached data only. The endpoint registry is left intact."""
        self._cache.clear()

    def _mark_endpoints_cached(self) -> None:
        self._identifiers = set(self._endpoints) | set(self._endpoints_by_id)
        self._endpoints_cached = True

    def reset_endpoints(self) -> None:
        """Clear the endpoint registry."""
        self._endpoints.clear()
        self._endpoints_by_id.clear()
        self._identifiers.clear()
        self._endpoints_cached = False

    def get(self, key: _KT, default: t.Union[_VT, _T, None] = None) -> t.Union[_VT, _T, None]:  # type: ignore
        """Get an item from the cache. If the exact key isn't found, attempt alias resolution."""
        if key in self:
            return self[key]
        requested = key.endpoint.split("/")[-1]
        alias = self._endpoints_by_id.get(requested) or self._endpoints.get(requested)
        if alias:
            for k, v in self.items():
                if k.endpoint.split("/")[-1] == str(alias):
                    return v
        return default

    def load_documents(self, data: t.List[t.Dict[str, str]]) -> None:
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

    def serialize(self) -> t.Dict[str, t.Any]:
        """Serialise the in-memory cache to a plain dict."""
        dummy: t.Dict[str, t.Any] = {}
        for k, v in self.items():
            dummy[k.endpoint] = [i.raw for i in v] if self._is_list and isinstance(v, list) else v.raw  # type: ignore
        return dummy

    def deserialize(self, data: t.Dict[str, t.Any]) -> None:
        """Populate the in-memory cache from a plain dict (output of serialize)."""
        self._max_size = max(self._max_size, len(data))
        for endpoint, info in data.items():
            route = Route(endpoint=endpoint)
            self.setdefault(t.cast(_KT, route), self.from_payload(info))

    @property
    def endpoints(self) -> t.Dict[str, CacheEndpoint]:
        """The endpoints that are cached."""
        return self._endpoints

    @property
    def identifiers(self) -> t.Set[str]:
        """Every valid name and id (as strings) for this category."""
        return self._identifiers

    @property
    def cache(self) -> t.Dict[_KT, _VT]:
        """The cache itself."""
        return self._cache


@attrs.define(slots=True, kw_only=True)
class BaseCacheGroup(t.Generic[_ClientT, _CacheT]):
    """Base class for all cache groups / aggregates."""

    max_size: int

    def _walk_caches(self) -> t.Iterator[_CacheT]:
        """Yield all sub-caches belonging to this cache group."""
        for field in attrs.fields(self.__class__):
            val = getattr(self, field.name)
            if isinstance(val, BaseCacheState):
                yield t.cast(_CacheT, val)

    def set_client(self, client: _ClientT) -> None:
        """Set the client for all sub-caches in this group."""
        for cache in self._walk_caches():
            cache._client = client

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
