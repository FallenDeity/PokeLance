from __future__ import annotations

import abc
import typing as t

from typing_extensions import TypeVar, override

from pokelance.cache._async.manager import AsyncCacheManager
from pokelance.ext._base import BaseExtension
from pokelance.http._async import AsyncHttpClient

if t.TYPE_CHECKING:
    from pokelance.cache._async.base import AsyncCacheGroup

__all__: tuple[str, ...] = ("AsyncBaseExtension",)

_AsyncCacheGroupT_co = TypeVar(
    "_AsyncCacheGroupT_co",
    bound="AsyncCacheGroup",
    default="AsyncCacheGroup",
    covariant=True,
)
_BaseAsyncExt = BaseExtension[AsyncHttpClient, AsyncCacheManager, _AsyncCacheGroupT_co]


class AsyncBaseExtension(
    _BaseAsyncExt[_AsyncCacheGroupT_co],
    t.Generic[_AsyncCacheGroupT_co],
):
    """Abstract base class for asynchronous extensions."""

    @abc.abstractmethod
    @override
    async def setup(self) -> None:
        """Sets up the extension asynchronously."""
        raise NotImplementedError
