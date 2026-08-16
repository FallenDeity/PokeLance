from __future__ import annotations

import typing as t
from pathlib import Path

from typing_extensions import Self

from pokelance.client._base import _ClientBase
from pokelance.constants import ExtensionEnum, ExtensionsL
from pokelance.http._async import AsyncHttpClient
from pokelance.utils import alru_cache

if t.TYPE_CHECKING:
    import logging
    from types import TracebackType

    import niquests

    from pokelance.ext._async import (
        Berry,
        Contest,
        Encounter,
        Evolution,
        Game,
        Item,
        Location,
        Machine,
        Move,
        Pokemon,
        Utility,
    )
    from pokelance.models import BaseModel

__all__: tuple[str, ...] = ("PokeLanceAsyncClient",)

BaseModelT = t.TypeVar("BaseModelT", bound="BaseModel")


class PokeLanceAsyncClient(_ClientBase[AsyncHttpClient]):
    """Main asynchronous client to interact with the PokeAPI.

    Attributes
    ----------
    http : AsyncHttpClient
        The HTTP client used to make requests to the PokeAPI.
    logger : logging.Logger
        The logger used to log information about the client.
    cache_endpoints : bool
        Whether to pre-populate endpoint caches. Defaults to True.
    berry : Berry
        The berry extension.
    contest : Contest
        The contest extension.
    encounter : Encounter
        The encounter extension.
    evolution : Evolution
        The evolution extension.
    game : Game
        The game extension.
    item : Item
        The item extension.
    location : Location
        The location extension.
    machine : Machine
        The machine extension.
    move : Move
        The move extension.
    pokemon : Pokemon
        The pokemon extension.
    utility : Utility
        The utility extension.
    """

    EXTENSIONS: Path = Path(__file__).parent.parent / "ext" / "_async"

    if t.TYPE_CHECKING:
        berry: Berry
        contest: Contest
        encounter: Encounter
        evolution: Evolution
        game: Game
        item: Item
        location: Location
        machine: Machine
        move: Move
        pokemon: Pokemon
        utility: Utility

    def __init__(
        self,
        *,
        audio_cache_size: int = 128,
        image_cache_size: int = 128,
        cache_size: int = 100,
        logger: logging.Logger | None = None,
        cache_endpoints: bool = True,
        session: niquests.AsyncSession | None = None,
    ) -> None:
        http = AsyncHttpClient(client=self, session=session, cache_size=cache_size)
        self._setup_common(
            http=http,
            audio_cache_size=audio_cache_size,
            image_cache_size=image_cache_size,
            logger=logger,
            cache_endpoints=cache_endpoints,
        )
        self.get_image.set_size(image_cache_size)
        self.get_audio.set_size(audio_cache_size)
        self.setup_hook("pokelance.ext._async")

    async def __aenter__(self) -> Self:
        return self

    async def __aexit__(
        self,
        exc_type: type[BaseException] | None,
        exc_val: BaseException | None,
        exc_tb: TracebackType | None,
    ) -> None:
        self._logger.warning("Closing session!")
        await self._http.close()

    async def ping(self) -> float:
        """Pings the PokeAPI and returns the latency."""
        return await self._http.ping()

    async def close(self) -> None:
        """Closes the client session."""
        self._logger.warning("Closing session!")
        await self._http.close()

    async def getch_data(
        self,
        ext: ExtensionEnum | ExtensionsL | str,
        category: str,
        id_: int | str | None = None,
    ) -> BaseModelT:  # pyright: ignore[reportInvalidTypeVarUse]
        """A getch method that looks up the cache first, then fetches from the API if not cached."""
        ext_instance, resolved_category = self._resolve_extension_category(ext, category)
        get_ = getattr(ext_instance, f"get_{resolved_category}")
        fetch_ = getattr(ext_instance, f"fetch_{resolved_category}")
        params = (id_,) if id_ is not None else ()
        return t.cast("BaseModelT", get_(*params) or await fetch_(*params))

    async def from_url(self, url: str) -> BaseModelT:  # pyright: ignore[reportInvalidTypeVarUse]
        """Constructs a request from URLs present in API data."""
        if params := ExtensionEnum.validate_url(url):
            return await self.getch_data(params.extension, params.category, params.value)
        raise ValueError(f"Invalid URL: {url}")

    @alru_cache(maxsize=128, typed=True)
    async def get_image(self, url: str) -> bytes:
        """Gets an image from the URL asynchronously."""
        return await self._http.load_image(url)

    @alru_cache(maxsize=128, typed=True)
    async def get_audio(self, url: str) -> bytes:
        """Gets audio from the URL asynchronously."""
        return await self._http.load_audio(url)

    async def wait_until_ready(self) -> None:
        """Waits until all background endpoint caches are pre-populated."""
        await self._http.connect()
        self._logger.info("Waiting until ready...")
        await self._http.loader.wait_until_ready()
        self._logger.info("Ready!")
