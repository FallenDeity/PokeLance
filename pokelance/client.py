import typing as t
from pathlib import Path

from .http import HttpClient
from .languages import Language
from .logger import create_logging_setup

if t.TYPE_CHECKING:
    import logging
    from types import TracebackType

    import aiohttp

    from .ext import BaseExtension, Berry

__all__: t.Tuple[str, ...] = ("PokeLance",)


class PokeLance:

    EXTENSIONS: Path = Path(__file__).parent / "ext"
    berry: "Berry"

    def __init__(
        self,
        *,
        cache_size: int = 100,
        language: str = Language.default(),
        session: t.Optional["aiohttp.ClientSession"] = None,
    ) -> None:
        self._logger = create_logging_setup("Client")
        self._language = language if language == Language.default() else Language.from_name(language)
        self._http = HttpClient(client=self, session=session, cache_size=cache_size)

    async def __aenter__(self) -> "PokeLance":
        return self

    async def __aexit__(
        self,
        exc_type: t.Optional[t.Type[BaseException]],
        exc_val: t.Optional[BaseException],
        exc_tb: t.Optional["TracebackType"],
    ) -> None:
        await self._http.session.close()

    async def setup_hook(self) -> None:
        self._logger.info(f"Using language: {self._language}")
        self._logger.info(f"Using cache size: {self._http.cache.max_size}")
        for extension in self.EXTENSIONS.iterdir():
            if extension.is_file() and extension.suffix == ".py":
                if "_" not in extension.stem:
                    module = __import__(f"pokelance.ext.{extension.stem}", fromlist=["setup"])
                    await module.setup(self)
        self._logger.info("Setup complete")

    async def add_extension(self, name: str, extension: "BaseExtension") -> None:
        self._logger.info(f"Adding extension: {name}")
        await extension.setup()
        setattr(self, name, extension)

    async def ping(self) -> float:
        return await self._http.ping()

    async def close(self) -> None:
        self._logger.info("Closing session")
        await self._http.session.close()

    @property
    def logger(self) -> "logging.Logger":
        return self._logger

    @property
    def language(self) -> str:
        return self._language

    @property
    def http(self) -> HttpClient:
        return self._http
