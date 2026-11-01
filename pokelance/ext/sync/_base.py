from __future__ import annotations

import abc
import logging
import typing as t

from typing_extensions import TypeVar, override

from pokelance.cache.sync.manager import SyncCacheManager
from pokelance.exceptions import EndpointInitializationError
from pokelance.ext._base import BaseExtension
from pokelance.http._sync import SyncHttpClient

if t.TYPE_CHECKING:
    from pokelance.cache.sync.base import SyncCacheGroup
    from pokelance.endpoints import Route


__all__: tuple[str, ...] = ("SyncBaseExtension",)

logger = logging.getLogger(__name__)


_SyncCacheGroupT_co = TypeVar(
    "_SyncCacheGroupT_co",
    bound="SyncCacheGroup",
    default="SyncCacheGroup",
    covariant=True,
)


class SyncBaseExtension(
    BaseExtension[SyncHttpClient, SyncCacheManager, _SyncCacheGroupT_co],
    t.Generic[_SyncCacheGroupT_co],
):
    """Abstract base class for synchronous extensions."""

    def _setup_endpoints(self, routes: dict[str, Route]) -> None:
        """Load each registry independently, retaining successes when another fails."""
        errors: dict[str, Exception] = {}
        for category, route in routes.items():
            cache = getattr(self._cache_group, category)
            try:
                data = self._client.request(route)
                cache.load_documents(data["results"])
            except Exception as error:
                logger.exception("Failed loading endpoint registry %s", category)
                cache.reset_endpoints()
                cache.set_failed(error)
                errors[category] = error
        if errors:
            raise EndpointInitializationError(errors) from next(iter(errors.values()))

    @abc.abstractmethod
    @override
    def setup(self) -> None:
        """Sets up the extension synchronously."""
        raise NotImplementedError
