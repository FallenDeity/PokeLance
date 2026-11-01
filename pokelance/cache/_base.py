from __future__ import annotations

import json
import os
import pathlib
import tempfile
import threading
import typing as t
from collections import OrderedDict

import attrs
from typing_extensions import override

from pokelance.endpoints import Route
from pokelance.exceptions import EndpointInitializationError
from pokelance.models import BaseModel

if t.TYPE_CHECKING:
    from pokelance.client._base import ClientBase

__all__: tuple[str, ...] = (
    "BaseCacheGroup",
    "BaseCacheManager",
    "BaseCacheState",
    "CacheEndpoint",
    "CacheStats",
)

_KT = t.TypeVar("_KT", bound="Route")
_VT = t.TypeVar("_VT", bound="BaseModel | t.Sequence[BaseModel]")
_ClientT = t.TypeVar("_ClientT", bound="ClientBase")
_CacheT = t.TypeVar("_CacheT", bound="BaseCacheState[t.Any, t.Any, t.Any]")
_GroupT = t.TypeVar("_GroupT", bound="BaseCacheGroup[t.Any, t.Any]")


@attrs.define(kw_only=True, slots=True, frozen=True)
class CacheEndpoint:
    """Represents a cached API endpoint identifier and URL.

    Attributes
    ----------
    id : str | int
        The numeric ID or string identifier of the endpoint.
    url : str
        The full PokeAPI resource URL for this endpoint.
    """

    id: str | int = attrs.field(factory=str)
    url: str = attrs.field(factory=str)

    @override
    def __str__(self) -> str:
        return str(self.id)


@attrs.define(slots=True, kw_only=True)
class CacheStats:
    """Statistics tracking cache hits, misses, insertions, and evictions.

    Attributes
    ----------
    hits : int
        Number of successful cache lookups.
    misses : int
        Number of failed cache lookups.
    sets : int
        Number of entries inserted or updated in the cache.
    evictions : int
        Number of entries removed due to reaching maximum cache capacity (LRU eviction).

    Examples
    --------
    ```python
    stats = client.cache.stats
    print(f"Hits: {stats.hits}, Misses: {stats.misses}")
    print(f"Hit Ratio: {stats.hit_ratio:.1%}")
    ```
    """

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
        """Resets all statistical counters to zero.

        Examples
        --------
        ```python
        client.cache.stats.reset()
        ```
        """
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
    """In-memory LRU cache state with endpoint indexing and lookup metrics.

    Manages cached items in an `OrderedDict` respecting a maximum capacity,
    tracks endpoint URLs by name and ID, and records lookup statistics.

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

    Attributes
    ----------
    stats : CacheStats
        Real-time statistics for lookups, hits, misses, and evictions on this cache.
    endpoints : dict[str, CacheEndpoint]
        Mapping from resource name (or ID) to CacheEndpoint metadata.
    identifiers : set[str]
        Set of all valid resource names and IDs known to this cache.
    cache : OrderedDict[_KT, _VT]
        The underlying OrderedDict storing cached items.
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
        if max_size <= 0:
            raise ValueError("max_size must be greater than 0")
        self._lock = threading.RLock()
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
        self._endpoint_error: Exception | None = None
        self._stats: CacheStats = CacheStats()

    @property
    def stats(self) -> CacheStats:
        """Statistics for this specific cache partition."""
        return self._stats

    def from_payload(self, payload: dict[str, t.Any] | list[dict[str, t.Any]]) -> _VT:
        """Creates a model instance or list of model instances from a raw payload dict.

        Parameters
        ----------
        payload : dict[str, t.Any] | list[dict[str, t.Any]]
            The raw JSON payload from PokéAPI.

        Returns
        -------
        BaseModel | list[BaseModel]
            The instantiated PokeLance model or list of models.
        """
        if self._model is None:
            raise RuntimeError(f"Model class not configured for cache '{self._name}'")
        if isinstance(payload, list):
            return t.cast("_VT", [self._model.from_payload(item) for item in payload])
        return t.cast("_VT", self._model.from_payload(payload))

    @override
    def __getitem__(self, key: _KT) -> _VT:
        with self._lock:
            key = self._canonicalize_key(key)
            try:
                val = self._cache[key]
                self._cache.move_to_end(key)
                self._stats.hits += 1
                return val
            except KeyError:
                self._stats.misses += 1
                raise

    @override
    def __setitem__(self, key: _KT, value: _VT) -> None:
        with self._lock:
            key = self._canonicalize_key(key)
            self._stats.sets += 1
            if key in self._cache:
                self._cache[key] = value
                self._cache.move_to_end(key)
            else:
                if len(self._cache) >= self._max_size:
                    self._cache.popitem(last=False)
                    self._stats.evictions += 1
                self._cache[key] = value

    @override
    def __delitem__(self, key: _KT) -> None:
        with self._lock:
            del self._cache[self._canonicalize_key(key)]

    @override
    def __len__(self) -> int:
        with self._lock:
            return len(self._cache)

    @override
    def __iter__(self) -> t.Iterator[_KT]:
        return iter(self._cache)

    @override
    def __repr__(self) -> str:
        return f"{self.__class__.__name__}({self._cache})"

    @override
    def keys(self) -> t.KeysView[_KT]:
        return self._cache.keys()

    @override
    def values(self) -> t.ValuesView[_VT]:
        return self._cache.values()

    @override
    def items(self) -> t.ItemsView[_KT, _VT]:
        return self._cache.items()

    @override
    def setdefault(self, __key: _KT, /, __default: _VT | None = None) -> _VT:
        """Returns the cached value for key if present, otherwise inserts default and returns it."""
        with self._lock:
            key = self._canonicalize_key(__key)
            if key not in self._cache and __default is not None:
                self[key] = __default
                return self._cache[key]
            self._stats.hits += 1
            self._cache.move_to_end(key)
            return self._cache[key]

    @override
    def clear(self) -> None:
        """Clears all cached model data while keeping the endpoint registry intact.

        Examples
        --------
        ```python
        client.cache.pokemon.pokemon.clear()
        ```
        """
        with self._lock:
            self._cache.clear()

    def _mark_endpoints_cached(self) -> None:
        self._identifiers = set(self._endpoints) | set(self._endpoints_by_id)
        if self._cache:
            entries = tuple(self._cache.items())
            self._cache.clear()
            for key, value in entries:
                key = self._canonicalize_key(key)
                if key in self._cache:
                    del self._cache[key]
                self._cache[key] = value
        self.set_ready()

    def _canonicalize_key(self, key: _KT) -> _KT:
        """Maps a registered name or ID route to its numeric-ID cache key."""
        endpoint = key.endpoint.rstrip("/")
        suffix = self._url_suffix if self._url_suffix and endpoint.endswith(self._url_suffix) else ""
        parent, _, identifier = endpoint.removesuffix(suffix).rpartition("/")
        endpoint_data = self._endpoints.get(self._endpoints_by_id.get(identifier, identifier))
        if endpoint_data is None:
            return key

        canonical_endpoint = f"{parent}/{endpoint_data.id}{suffix}"
        if canonical_endpoint == key.endpoint:
            return key
        return attrs.evolve(key, endpoint=canonical_endpoint)

    def set_ready(self) -> None:
        """Sets the cache endpoint state as ready."""
        with self._lock:
            self._endpoint_error = None
            self._endpoints_cached = True

    def set_failed(self, error: Exception) -> None:
        """Records an endpoint-loading failure without disabling model caching."""
        with self._lock:
            self._endpoint_error = error
            self._endpoints_cached = False

    def _check_endpoint_wait(self) -> None:
        if hasattr(self, "_client") and not self._client.cache_endpoints:
            raise RuntimeError("Endpoint loading is disabled (cache_endpoints=False).")

    def _raise_endpoint_error(self) -> None:
        if self._endpoint_error is not None:
            raise EndpointInitializationError({self._name: self._endpoint_error}) from self._endpoint_error

    def reset_endpoints(self) -> None:
        """Clears the endpoint registry and marks the cache as unready."""
        with self._lock:
            self._endpoints.clear()
            self._endpoints_by_id.clear()
            self._identifiers.clear()
            self._endpoints_cached = False
            self._endpoint_error = None

    def load_documents(self, data: list[dict[str, str]]) -> None:
        """Loads endpoint metadata documents into this cache partition's registry.

        Parameters
        ----------
        data : list[dict[str, str]]
            The raw list of endpoint documents containing `name` and `url`.
        """
        with self._lock:
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
        """Sets the maximum capacity of this cache partition.

        Parameters
        ----------
        size : int
            The maximum number of items allowed in the cache.

        Examples
        --------
        ```python
        client.cache.pokemon.pokemon.set_size(200)
        ```
        """
        with self._lock:
            if size <= 0:
                raise ValueError("size must be greater than 0")
            self._max_size = size
            while len(self._cache) > size:
                self._cache.popitem(last=False)
                self._stats.evictions += 1

    def serialize(self) -> dict[str, t.Any]:
        """Serializes all in-memory cached models into a raw dictionary.

        Returns
        -------
        dict[str, t.Any]
            A dictionary mapping endpoint routes to raw model payload dictionaries.

        Examples
        --------
        ```python
        data = client.cache.pokemon.pokemon.serialize()
        ```
        """
        with self._lock:
            dummy: dict[str, t.Any] = {}
            for k, v in self.items():
                dummy[k.endpoint] = v.raw if isinstance(v, BaseModel) else [i.raw for i in v]
            return dummy

    def _write(self, path: str, payload: dict[str, t.Any]) -> None:
        """Atomically write a previously serialized cache snapshot to disk."""
        directory = pathlib.Path(path)
        directory.mkdir(parents=True, exist_ok=True)
        file_path = directory / f"{self._name}.json"
        serialized = json.dumps(payload, indent=4)
        temp_path: pathlib.Path | None = None
        try:
            with tempfile.NamedTemporaryFile(
                mode="w",
                encoding="utf-8",
                dir=directory,
                prefix=f".{file_path.name}.",
                suffix=".tmp",
                delete=False,
            ) as temp_file:
                temp_path = pathlib.Path(temp_file.name)
                temp_file.write(serialized)
                temp_file.flush()
            os.replace(temp_path, file_path)
        finally:
            if temp_path is not None:
                temp_path.unlink(missing_ok=True)

    def _read(self, path: str = ".") -> dict[str, t.Any]:
        """Read and parse the saved data for this partition."""
        file_path = pathlib.Path(path) / f"{self._name}.json"
        return json.loads(file_path.read_text(encoding="utf-8"))

    def deserialize(self, data: dict[str, t.Any]) -> None:
        """Populates this cache partition from a serialized dictionary.

        Parameters
        ----------
        data : dict[str, t.Any]
            Dictionary previously generated by `serialize()`.

        Examples
        --------
        ```python
        client.cache.pokemon.pokemon.deserialize(saved_data)
        ```
        """
        with self._lock:
            self._max_size = max(self._max_size, len(data))
            for endpoint, info in data.items():
                route = Route(endpoint=endpoint)
                self.setdefault(t.cast("_KT", route), self.from_payload(info))

    @property
    def endpoints(self) -> dict[str, CacheEndpoint]:
        """Mapping from resource name (or ID) to CacheEndpoint metadata."""
        return self._endpoints

    @property
    def identifiers(self) -> set[str]:
        """Every valid resource name and ID known to this cache partition."""
        return self._identifiers

    @property
    def cache(self) -> OrderedDict[_KT, _VT]:
        """The underlying OrderedDict storing cached items."""
        return self._cache


@attrs.define(slots=True, kw_only=True)
class BaseCacheGroup(t.Generic[_ClientT, _CacheT]):
    """Base class for all category cache aggregates.

    Groups multiple related sub-caches (e.g. `berry`, `berry_firmness`, `berry_flavor`)
    under a unified namespace and provides batch management methods.

    Attributes
    ----------
    max_size : int
        Maximum cache capacity configured across sub-caches in this group.
    """

    max_size: int

    def __attrs_post_init__(self) -> None:
        if self.max_size <= 0:
            raise ValueError("max_size must be greater than 0")

    @property
    def stats(self) -> CacheStats:
        """Aggregated statistics across all sub-caches in this group.

        Examples
        --------
        ```python
        group_stats = client.cache.pokemon.stats
        print(f"Pokemon category hit ratio: {group_stats.hit_ratio:.1%}")
        ```
        """
        return sum((cache.stats for cache in self._walk_caches()), CacheStats())

    def _walk_caches(self) -> t.Iterator[_CacheT]:
        """Yield all sub-caches belonging to this cache group."""
        for field in attrs.fields(self.__class__):
            val = getattr(self, field.name)
            if isinstance(val, BaseCacheState):
                yield t.cast("_CacheT", val)

    def set_client(self, client: _ClientT) -> None:
        """Sets the parent client instance for all sub-caches in this group."""
        for cache in self._walk_caches():
            cache._client = client  # pyright: ignore[reportPrivateUsage]

    def set_size(self, max_size: int = 100) -> None:
        """Sets the maximum cache capacity for all sub-caches in this group.

        Parameters
        ----------
        max_size : int, default: 100
            The maximum number of items allowed in each sub-cache.

        Examples
        --------
        ```python
        client.cache.pokemon.set_size(250)
        ```
        """
        if max_size <= 0:
            raise ValueError("max_size must be greater than 0")
        self.max_size = max_size
        for cache in self._walk_caches():
            cache.set_size(max_size)

    def clear(self) -> None:
        """Clears all cached model data in every sub-cache in this group.

        Examples
        --------
        ```python
        client.cache.pokemon.clear()
        ```
        """
        for cache in self._walk_caches():
            cache.clear()

    def reset(self) -> None:
        """Resets all endpoint registries in every sub-cache in this group."""
        for cache in self._walk_caches():
            cache.reset_endpoints()


@attrs.define(slots=True, kw_only=True)
class BaseCacheManager(t.Generic[_ClientT, _GroupT]):
    """Base manager coordinating all category cache groups across the client.

    Provides global configuration, bulk endpoint loading, cache clearance,
    and cumulative statistics across all sub-caches.

    Attributes
    ----------
    client : ClientBase
        The parent client instance owning this cache manager.
    max_size : int, default: 100
        The default maximum capacity applied to all sub-caches.
    """

    client: _ClientT
    max_size: int = 100

    def _walk_aggregates(self) -> t.Iterator[_GroupT]:
        """Yield all child cache aggregates."""
        for field in attrs.fields(self.__class__):
            val = getattr(self, field.name)
            if isinstance(val, BaseCacheGroup):
                yield t.cast("_GroupT", val)

    def __attrs_post_init__(self) -> None:
        if self.max_size <= 0:
            raise ValueError("max_size must be greater than 0")
        for aggregate in self._walk_aggregates():
            aggregate.set_size(self.max_size)
            aggregate.set_client(self.client)

    def set_size(self, max_size: int = 100) -> None:
        """Sets the maximum cache size across all category aggregates and sub-caches.

        Parameters
        ----------
        max_size : int, default: 100
            The maximum number of items allowed in each cache partition.

        Examples
        --------
        ```python
        client.cache.set_size(500)
        ```
        """
        if max_size <= 0:
            raise ValueError("max_size must be greater than 0")
        self.max_size = max_size
        for aggregate in self._walk_aggregates():
            aggregate.set_size(max_size)

    def load_documents(self, category: str, _type: str, data: list[dict[str, str]]) -> None:
        """Loads endpoint metadata documents into the specified category sub-cache.

        Parameters
        ----------
        category : str
            The top-level category name (e.g. 'pokemon', 'berry').
        _type : str
            The specific sub-cache partition name (e.g. 'pokemon_species', 'berry_flavor').
        data : list[dict[str, str]]
            The raw list of endpoint documents.
        """
        getattr(getattr(self, category.lower()), _type).load_documents(data)

    def clear(self) -> None:
        """Clears all cached model data across all category aggregates.

        Examples
        --------
        ```python
        client.cache.clear()
        ```
        """
        for aggregate in self._walk_aggregates():
            aggregate.clear()

    def reset(self) -> None:
        """Resets all endpoint registries across all category aggregates.

        Examples
        --------
        ```python
        client.cache.reset()
        ```
        """
        for aggregate in self._walk_aggregates():
            aggregate.reset()

    @property
    def stats(self) -> CacheStats:
        """Cumulative statistics across all sub-caches in all category aggregates.

        Examples
        --------
        ```python
        total_stats = client.cache.stats
        print(f"Overall cache hits: {total_stats.hits}")
        print(f"Overall hit ratio: {total_stats.hit_ratio:.1%}")
        ```
        """
        return sum((aggregate.stats for aggregate in self._walk_aggregates()), CacheStats())
