import typing as t
from pathlib import Path

from .http import HttpClient
from .languages import Language
from .logger import create_logging_setup

if t.TYPE_CHECKING:
    from types import TracebackType

    import aiohttp
    import logging

    from .ext import BaseExtension, Pokemon

__all__: t.Tuple[str, ...] = ("PokeLance",)


class PokeLance:

    EXTENSIONS: Path = Path(__file__).parent / "ext"
    pokemon: "Pokemon"

    def __init__(
        self,
        *,
        cache_size: int = 100,
        language: str = Language.default(),
        session: t.Optional["aiohttp.ClientSession"] = None,
    ) -> None:
        self._session = session
        self._logger = create_logging_setup("Client")
        self._language = language if language == Language.default() else Language.from_name(language)
        self._client = HttpClient(client=self, session=self._session, cache_size=cache_size)

    async def _async_setup_hook(self) -> None:
        await self.setup_hook()
        self._logger.info("Setup complete")
        self._logger.info(f"Using language: {self._language}")
        self._logger.info(f"Using cache size: {self._client.cache.max_size}")

    async def __aenter__(self) -> "PokeLance":
        return self

    async def __aexit__(
        self,
        exc_type: t.Optional[t.Type[BaseException]],
        exc_val: t.Optional[BaseException],
        exc_tb: t.Optional["TracebackType"],
    ) -> None:
        if self._session is not None:
            await self._session.close()

    async def setup_hook(self) -> None:
        for extension in self.EXTENSIONS.iterdir():
            if extension.is_file() and extension.suffix == ".py":
                if "_" not in extension.stem:
                    module = __import__(f"pokelance.ext.{extension.stem}", fromlist=["setup"])
                    await module.setup(self)

    async def add_extension(self, name: str, extension: "BaseExtension") -> None:
        self._logger.info(f"Adding extension: {name}")
        await extension.setup()
        setattr(self, name, extension)

    async def ping(self) -> float:
        return await self._client.ping()

    @property
    def session(self) -> "aiohttp.ClientSession":
        return self._client._session

    @property
    def logger(self) -> "logging.Logger":
        return self._logger

    @property
    def language(self) -> str:
        return self._language

    @property
    def http(self) -> HttpClient:
        return self._client
