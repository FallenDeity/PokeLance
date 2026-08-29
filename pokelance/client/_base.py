from __future__ import annotations

import logging
import typing as t

from typing_extensions import TypeVar, Unpack

from pokelance.constants import Extension, ExtensionEnum, ExtensionsL
from pokelance.logger import setup_logging

if t.TYPE_CHECKING:
    from pathlib import Path

    from pokelance.ext._base import BaseExtension
    from pokelance.http._async import AsyncHttpClient
    from pokelance.http._sync import SyncHttpClient

__all__: tuple[str, ...] = ("ClientConfig", "_ClientBase")

logger = logging.getLogger(__name__)

_HTTPClientT_co = TypeVar(
    "_HTTPClientT_co",
    bound="AsyncHttpClient | SyncHttpClient",
    covariant=True,
    default="AsyncHttpClient | SyncHttpClient",
)


class ClientConfig(t.TypedDict, total=False):
    """Configuration options for PokeLance clients."""

    audio_cache_size: int
    image_cache_size: int
    cache_endpoints: bool
    setup_logging: bool
    log_level: int
    structured_logging: bool
    file_logging: bool
    log_dir: str | Path
    set_excepthook: bool


class _ClientBase(t.Generic[_HTTPClientT_co]):
    """Shared base logic for PokeLanceAsyncClient and PokeLanceSyncClient."""

    EXTENSIONS: Path
    _http: _HTTPClientT_co
    cache_endpoints: bool
    _ext_tasks: list[tuple[t.Callable[..., t.Any], str]]
    _image_cache_size: int
    _audio_cache_size: int

    def __init__(
        self,
        *,
        http: _HTTPClientT_co,
        **kwargs: Unpack[ClientConfig],
    ) -> None:
        if kwargs.get("setup_logging", True):
            setup_logging(
                log_level=kwargs.get("log_level", logging.INFO),
                structured=kwargs.get("structured_logging", False),
                file_logging=kwargs.get("file_logging", False),
                log_dir=kwargs.get("log_dir", "logs"),
                set_excepthook=kwargs.get("set_excepthook", True),
            )
        self._http = http
        self.cache_endpoints = kwargs.get("cache_endpoints", True)
        self._ext_tasks = []
        self._image_cache_size = kwargs.get("image_cache_size", 128)
        self._audio_cache_size = kwargs.get("audio_cache_size", 128)

    def setup_hook(self, ext_pkg: str) -> None:
        """Dynamically loads extensions from the specified package directory."""
        logger.info(f"Using cache size: {self._http.cache_manager.max_size}")
        if not self.EXTENSIONS.exists():
            logger.warning(f"Extensions directory '{self.EXTENSIONS}' does not exist.")
            return
        for extension in self.EXTENSIONS.iterdir():
            if extension.is_file() and extension.suffix == ".py" and "_" not in extension.stem:
                module = __import__(f"{ext_pkg}.{extension.stem}", fromlist=["setup"])
                module.setup(self)
                logger.debug(f"Loaded extension module: {extension.stem}")
        logger.info("Setup complete")

    def add_extension(self, name: str, extension: BaseExtension[_HTTPClientT_co]) -> None:
        """Adds an extension to the client."""
        self._ext_tasks.append((extension.setup, name))
        setattr(self, name, extension)
        logger.debug(f"Registered extension '{name}'")

    def _resolve_extension_category(self, ext: ExtensionEnum | ExtensionsL | str, category: str) -> tuple[t.Any, str]:
        """Validates extension and category inputs and returns the extension instance and resolved category."""
        if isinstance(ext, str):
            ext_title = ext.title()
            if ext_title not in ExtensionEnum.__members__:
                raise ValueError(f"Invalid extension: {ext}")
            ext = getattr(ExtensionEnum, ext_title)

        extension = t.cast("Extension", ext)
        categories = extension.categories
        ext_instance = getattr(self, extension.name.lower())

        normalized_category = category.lower().replace("_", "-")
        if normalized_category not in categories:
            raise ValueError(f"Invalid category: {category}, valid categories: {categories}")

        resolved_category = normalized_category.replace("-", "_")
        logger.debug(f"Resolved extension '{extension.name}' category '{category}' -> {resolved_category}")
        return ext_instance, resolved_category

    @property
    def http(self) -> _HTTPClientT_co:
        """The HTTP client used to make requests to the PokeAPI."""
        return self._http

    @property
    def ext_tasks(self) -> list[tuple[t.Callable[..., t.Any], str]]:
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
