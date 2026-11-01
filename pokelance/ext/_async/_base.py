from __future__ import annotations

import abc
import asyncio
import logging
import typing as t
from itertools import starmap

from typing_extensions import TypeVar, override

from pokelance.cache._async.manager import AsyncCacheManager
from pokelance.exceptions import EndpointInitializationError
from pokelance.ext._base import BaseExtension
from pokelance.http._async import AsyncHttpClient

if t.TYPE_CHECKING:
    from pokelance.cache._async.base import AsyncCacheGroup
    from pokelance.endpoints import Route

__all__: tuple[str, ...] = ("AsyncBaseExtension",)

logger = logging.getLogger(__name__)

_AsyncCacheGroupT_co = TypeVar(
    "_AsyncCacheGroupT_co",
    bound="AsyncCacheGroup",
    default="AsyncCacheGroup",
    covariant=True,
)


class AsyncBaseExtension(
    BaseExtension[AsyncHttpClient, AsyncCacheManager, _AsyncCacheGroupT_co],
    t.Generic[_AsyncCacheGroupT_co],
):
    """Abstract base class for asynchronous extensions."""

    async def _setup_endpoints(self, routes: dict[str, Route]) -> None:
        """Finish every registry request and retain successful metadata on failure."""
        errors: dict[str, Exception] = {}

        async def load(category: str, route: Route) -> None:
            cache = getattr(self._cache_group, category)
            try:
                data = await self._client.request(route)
                cache.load_documents(data["results"])
            except Exception as error:
                logger.exception("Failed loading endpoint registry %s", category)
                cache.reset_endpoints()
                cache.set_failed(error)
                errors[category] = error

        await asyncio.gather(*starmap(load, routes.items()))
        if errors:
            raise EndpointInitializationError(errors) from next(iter(errors.values()))

    @abc.abstractmethod
    @override
    async def setup(self) -> None:
        """Sets up the extension asynchronously."""
        raise NotImplementedError
