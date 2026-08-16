from __future__ import annotations

import logging
import typing as t
from pathlib import Path
from typing_extensions import TypeVar

from pokelance.constants import Extension, ExtensionEnum, ExtensionsL

if t.TYPE_CHECKING:
    from pokelance.ext._base import BaseExtension
    from pokelance.http._async import AsyncHttpClient
    from pokelance.http._sync import SyncHttpClient

__all__: t.Tuple[str, ...] = ("_ClientBase",)

_HTTPClientT = TypeVar(
    "_HTTPClientT",
    bound="t.Union[AsyncHttpClient, SyncHttpClient]",
    covariant=True,
    default="t.Union[AsyncHttpClient, SyncHttpClient]",
)


class _ClientBase(t.Generic[_HTTPClientT]):
    """Shared base logic for PokeLanceAsyncClient and PokeLanceSyncClient."""

    EXTENSIONS: Path
    _logger: logging.Logger
    _http: _HTTPClientT
    cache_endpoints: bool
    _ext_tasks: t.List[t.Tuple[t.Callable[..., t.Any], str]]
    _image_cache_size: int
    _audio_cache_size: int

    def _setup_common(
        self,
        *,
        http: _HTTPClientT,  # type: ignore
        audio_cache_size: int = 128,
        image_cache_size: int = 128,
        logger: t.Optional[logging.Logger] = None,
        cache_endpoints: bool = True,
    ) -> None:
        self._logger = logger or logging.getLogger("pokelance")
        self._http = http
        self.cache_endpoints = cache_endpoints
        self._ext_tasks = []
        self._image_cache_size = image_cache_size
        self._audio_cache_size = audio_cache_size

    def setup_hook(self, ext_pkg: str) -> None:
        """Dynamically loads extensions from the specified package directory."""
        self._logger.info(f"Using cache size: {self._http.cache.max_size}")
        if not self.EXTENSIONS.exists():
            return
        for extension in self.EXTENSIONS.iterdir():
            if extension.is_file() and extension.suffix == ".py" and "_" not in extension.stem:
                module = __import__(f"{ext_pkg}.{extension.stem}", fromlist=["setup"])
                module.setup(self)
        self._logger.info("Setup complete")

    def add_extension(self, name: str, extension: "BaseExtension[_HTTPClientT]") -> None:
        """Adds an extension to the client."""
        self._ext_tasks.append((extension.setup, name))
        setattr(self, name, extension)

    def _resolve_extension_category(
        self, ext: t.Union[ExtensionEnum, ExtensionsL, str], category: str
    ) -> t.Tuple[t.Any, str]:
        """Validates extension and category inputs and returns the extension instance and resolved category."""
        if isinstance(ext, str):
            ext_title = ext.title()
            if ext_title not in ExtensionEnum.__members__:
                raise ValueError(f"Invalid extension: {ext}")
            ext = getattr(ExtensionEnum, ext_title)

        extension = t.cast(Extension, ext)
        categories = extension.categories
        ext_instance = getattr(self, extension.name.lower())

        normalized_category = category.lower().replace("_", "-")
        if normalized_category not in categories:
            raise ValueError(f"Invalid category: {category}, valid categories: {categories}")

        resolved_category = normalized_category.replace("-", "_")
        return ext_instance, resolved_category

    @property
    def logger(self) -> logging.Logger:
        """The logger used to log information about the client."""
        return self._logger

    @property
    def http(self) -> _HTTPClientT:
        """The HTTP client used to make requests to the PokeAPI."""
        return self._http

    @property
    def ext_tasks(self) -> t.List[t.Tuple[t.Callable[..., t.Any], str]]:
        """A list of setup callables/coroutines to load extension data."""
        return self._ext_tasks

    @property
    def image_cache_size(self) -> int:
        """The size of the image cache."""
        return self._image_cache_size

    @property
    def audio_cache_size(self) -> int:
        """The size of the audio cache."""
        return self._audio_cache_size
