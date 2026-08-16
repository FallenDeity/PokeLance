from __future__ import annotations

import logging
import typing as t
from pathlib import Path

if t.TYPE_CHECKING:
    from pokelance.ext._base import BaseExtension
    from pokelance.http._async import AsyncHttpClient
    from pokelance.http._sync import SyncHttpClient

    AnyHttpClient = t.Union[AsyncHttpClient, SyncHttpClient]

__all__: t.Tuple[str, ...] = ("_ClientBase",)


class _ClientBase:
    """Shared base logic for PokeLance and PokeLanceSync clients."""

    EXTENSIONS: Path
    _logger: logging.Logger
    _http: t.Any
    cache_endpoints: bool

    def _setup_common(
        self,
        *,
        audio_cache_size: int = 128,
        image_cache_size: int = 128,
        logger: t.Optional[logging.Logger] = None,
        cache_endpoints: bool = True,
    ) -> None:
        self._logger = logger or logging.getLogger("pokelance")
        self.cache_endpoints = cache_endpoints
        self._ext_tasks: t.List[t.Tuple[t.Callable[..., t.Any], str]] = []
        self._image_cache_size = image_cache_size
        self._audio_cache_size = audio_cache_size

    def setup_hook(self, ext_pkg: str) -> None:
        """Dynamically loads extensions from the specified package directory."""
        self._logger.info(f"Using cache size: {self._http.cache.max_size}")
        for extension in self.EXTENSIONS.iterdir():
            if extension.is_file() and extension.suffix == ".py" and "_" not in extension.stem:
                module = __import__(f"{ext_pkg}.{extension.stem}", fromlist=["setup"])
                module.setup(self)
        self._logger.info("Setup complete")

    def add_extension(self, name: str, extension: "BaseExtension[AnyHttpClient]") -> None:
        """Adds an extension to the client."""
        self._ext_tasks.append((extension.setup, name))
        setattr(self, name, extension)

    @property
    def logger(self) -> logging.Logger:
        """The logger used to log information about the client."""
        return self._logger

    @property
    def http(self) -> t.Any:
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
