from __future__ import annotations

import abc
import typing as t

from typing_extensions import TypeVar, override

from pokelance.cache.sync.manager import SyncCacheManager
from pokelance.ext._base import BaseExtension
from pokelance.http._sync import SyncHttpClient

if t.TYPE_CHECKING:
    from pokelance.cache.sync.base import SyncCacheGroup


__all__: tuple[str, ...] = ("SyncBaseExtension",)


_SyncCacheGroupT_co = TypeVar(
    "_SyncCacheGroupT_co",
    bound="SyncCacheGroup",
    default="SyncCacheGroup",
    covariant=True,
)
_BaseSyncExt = BaseExtension[SyncHttpClient, SyncCacheManager, _SyncCacheGroupT_co]


class SyncBaseExtension(
    _BaseSyncExt[_SyncCacheGroupT_co],
    t.Generic[_SyncCacheGroupT_co],
):
    """Abstract base class for synchronous extensions."""

    @abc.abstractmethod
    @override
    def setup(self) -> None:
        """Sets up the extension synchronously."""
        raise NotImplementedError
