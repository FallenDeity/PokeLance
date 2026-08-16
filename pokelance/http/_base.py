from __future__ import annotations

import logging
import typing as t

from pokelance.endpoints import Route
from pokelance.exceptions import AudioNotFound, HTTPException, ImageNotFound

if t.TYPE_CHECKING:
    import niquests

    from pokelance.cache._async.manager import AsyncCacheManager
    from pokelance.cache.sync.manager import SyncCacheManager
    from pokelance.client._base import _ClientBase

    AnyCacheManager = AsyncCacheManager | SyncCacheManager

__all__: tuple[str, ...] = ("BaseHttpClient",)

logger = logging.getLogger(__name__)

_ClientT = t.TypeVar("_ClientT", bound="_ClientBase")
_SessionT = t.TypeVar("_SessionT", bound="niquests.Session | niquests.AsyncSession")
_CacheManagerT = t.TypeVar(
    "_CacheManagerT",
    bound="AsyncCacheManager | SyncCacheManager",
    default="AsyncCacheManager | SyncCacheManager",
)


class BaseHttpClient(t.Generic[_ClientT, _SessionT, _CacheManagerT]):
    """Base class containing shared HTTP logic, validation, and media checks."""

    IMAGE_FORMATS: t.ClassVar[tuple[str, ...]] = ("png", "jpg", "jpeg", "gif", "webp", "svg")
    AUDIO_FORMATS: t.ClassVar[tuple[str, ...]] = ("ogg", "wav", "mp3")

    _client: _ClientT
    session: _SessionT | None
    _cache_manager: _CacheManagerT
    _is_ready: bool
    _session_owner: bool

    def __init__(
        self,
        *,
        client: _ClientT,
        session: _SessionT | None = None,
    ) -> None:
        self._client = client
        self.session = session
        self._is_ready = False
        self._session_owner = session is None

    @property
    def cache_manager(self) -> _CacheManagerT:
        """The cache manager used by this HTTP client."""
        return self._cache_manager

    @classmethod
    def _validate_response(cls, response: niquests.Response, route: Route) -> t.Any:
        """Validate an HTTP response and return parsed JSON or raise HTTPException."""
        status = response.status_code or -1
        if 200 <= status < 300:
            logger.debug(f"Request to {route.url} was successful.")
            return response.json()
        logger.error(f"Request to {route.url} was unsuccessful with status {status}.")
        raise HTTPException(str(response.reason), route, status).create()

    @classmethod
    def _validate_image(cls, response: niquests.Response, url: str) -> bytes:
        """Validate that the response is an image and return raw bytes."""
        status = response.status_code or -1
        content_type = response.headers.get("content-type", "")
        is_image = any(f_ in content_type for f_ in cls.IMAGE_FORMATS)
        if 200 <= status < 300 and response.content and is_image:
            logger.debug(f"Request to {url} was successful.")
            return response.content
        logger.error(f"Request to {url} was unsuccessful.")
        message = f"Request to {url} was unsuccessful or the URL is not an image."
        raise ImageNotFound(f"{message} ({content_type})", Route(), status)

    @classmethod
    def _validate_audio(cls, response: niquests.Response, url: str) -> bytes:
        """Validate that the response is an audio file and return raw bytes."""
        status = response.status_code or -1
        content_type = response.headers.get("content-type", "")
        is_cry = any(f_ in content_type for f_ in cls.AUDIO_FORMATS)
        if 200 <= status < 300 and response.content and is_cry:
            logger.debug(f"Request to {url} was successful.")
            return response.content
        logger.error(f"Request to {url} was unsuccessful.")
        message = f"Request to {url} was unsuccessful or the URL is not a cry."
        raise AudioNotFound(f"{message} ({content_type})", Route(), status)
