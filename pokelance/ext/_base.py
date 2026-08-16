from __future__ import annotations

import abc
import typing as t
from difflib import get_close_matches

from typing_extensions import TypeVar

from pokelance.exceptions import ResourceNotFound

if t.TYPE_CHECKING:
    from pokelance.cache._async.base import AsyncCacheGroup
    from pokelance.cache._async.manager import AsyncCacheManager
    from pokelance.cache._base import BaseCacheState
    from pokelance.cache.sync.base import SyncCacheGroup
    from pokelance.cache.sync.manager import SyncCacheManager
    from pokelance.http._async import AsyncHttpClient
    from pokelance.http._base import BaseHttpClient
    from pokelance.http._sync import SyncHttpClient
    from pokelance.http.endpoints import Route

    AnyHttpClient = AsyncHttpClient | SyncHttpClient
    AnyCacheManager = AsyncCacheManager | SyncCacheManager
    AnyCacheGroup = AsyncCacheGroup | SyncCacheGroup

__all__: tuple[str, ...] = (
    "AsyncBaseExtension",
    "BaseExtension",
    "SyncBaseExtension",
)

_CacheManagerT_co = TypeVar(
    "_CacheManagerT_co",
    bound="AsyncCacheManager | SyncCacheManager",
    default="AsyncCacheManager | SyncCacheManager",
    covariant=True,
)
_HTTPClientT_co = TypeVar(
    "_HTTPClientT_co",
    bound="BaseHttpClient[t.Any, t.Any, t.Any]",
    default="BaseHttpClient[t.Any, t.Any, t.Any]",
    covariant=True,
)
_CacheGroupT_co = TypeVar(
    "_CacheGroupT_co",
    bound="AsyncCacheGroup | SyncCacheGroup",
    default="AsyncCacheGroup | SyncCacheGroup",
    covariant=True,
)
_AsyncCacheGroupT_co = TypeVar(
    "_AsyncCacheGroupT_co",
    bound="AsyncCacheGroup",
    default="AsyncCacheGroup",
    covariant=True,
)
_SyncCacheGroupT_co = TypeVar(
    "_SyncCacheGroupT_co",
    bound="SyncCacheGroup",
    default="SyncCacheGroup",
    covariant=True,
)


class BaseExtension(abc.ABC, t.Generic[_HTTPClientT_co, _CacheManagerT_co, _CacheGroupT_co]):
    """The base extension class.

    Parameters
    ----------
    client : _HTTPClientT_co
        The HTTP client to use for requests.

    Attributes
    ----------
    _client : _HTTPClientT_co
        The HTTP client to use for requests.
    _cache_manager : _CacheManagerT_co
        The top-level cache manager.
    _cache_group : _CacheGroupT_co
        The category-specific cache group.
    """

    _client: _HTTPClientT_co
    _cache_manager: _CacheManagerT_co
    _cache_group: _CacheGroupT_co

    def __init__(self, client: _HTTPClientT_co) -> None:
        self._client = client
        self._cache_manager = client.cache_manager
        self._cache_group = getattr(self._cache_manager, self.__class__.__name__.lower())

    @property
    def cache_group(self) -> _CacheGroupT_co:
        """The cache group for this extension."""
        return self._cache_group

    @property
    def cache_manager(self) -> _CacheManagerT_co:
        """The top-level cache manager."""
        return self._cache_manager

    @abc.abstractmethod
    def setup(self) -> t.Coroutine[t.Any, t.Any, None] | None:
        """Sets up the extension."""
        raise NotImplementedError

    def _validate_resource(
        self,
        cache: BaseCacheState[t.Any, t.Any, t.Any],
        resource: str | int,
        route: Route,
    ) -> None:
        """Validates a resource against cached identifiers.

        Parameters
        ----------
        cache : BaseCacheState
            The cache to check identifiers against.
        resource : t.Union[str, int]
            The resource name or ID to validate.
        route : Route
            The route associated with this resource.

        Raises
        ------
        ResourceNotFound
            If identifiers are cached and the resource is not present.
        """
        data: set[str] = cache.identifiers
        if data and str(resource) not in data:
            suggestions = get_close_matches(str(resource), data, n=10, cutoff=0.5)
            raise ResourceNotFound(
                message=f"Resource not found - {route.url}",
                route=route,
                status=404,
                suggestions=suggestions,
            )


if t.TYPE_CHECKING:
    _BaseAsyncExt = BaseExtension[AsyncHttpClient, AsyncCacheManager, _AsyncCacheGroupT_co]
    _BaseSyncExt = BaseExtension[SyncHttpClient, SyncCacheManager, _SyncCacheGroupT_co]
else:
    _BaseAsyncExt = BaseExtension
    _BaseSyncExt = BaseExtension


class AsyncBaseExtension(
    _BaseAsyncExt[_AsyncCacheGroupT_co],
    t.Generic[_AsyncCacheGroupT_co],
):
    """Abstract base class for asynchronous extensions."""

    @abc.abstractmethod
    async def setup(self) -> None:
        """Sets up the extension asynchronously."""
        raise NotImplementedError


class SyncBaseExtension(
    _BaseSyncExt[_SyncCacheGroupT_co],
    t.Generic[_SyncCacheGroupT_co],
):
    """Abstract base class for synchronous extensions."""

    @abc.abstractmethod
    def setup(self) -> None:
        """Sets up the extension synchronously."""
        raise NotImplementedError
