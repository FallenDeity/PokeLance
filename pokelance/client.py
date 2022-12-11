import asyncio
import typing as t
from pathlib import Path

from .http import HttpClient
from .logger import create_logging_setup

if t.TYPE_CHECKING:
    import logging
    from types import TracebackType

    import aiohttp

    from .ext import BaseExtension, Berry, Contest, Encounter, Evolution, Game, Item, Location, Machine, Move, Pokemon

__all__: t.Tuple[str, ...] = ("PokeLance",)


class PokeLance:
    """
    Main class to interact with the PokeAPI.


    Attributes
    ----------
    _http : HttpClient
        The HTTP client used to make requests to the PokeAPI.
    _logger : logging.Logger
        The logger used to log information about the client.
    _auto_load : bool
        Whether or not to automatically load extension data on setup.
    _loaders : typing.List[typing.Coroutine[t.Any, t.Any, None]]
        A list of coroutines to load extension data.
    EXTENSIONS : Path
        The path to the extensions directory.
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

    Examples
    --------

    >>> import pokelance
    >>> import asyncio
    >>> client = pokelance.PokeLance()
    >>> async def main() -> None:
    ...     print(await client.ping())
    ...     await client.close()
    >>> asyncio.run(main())
    """

    EXTENSIONS: Path = Path(__file__).parent / "ext"
    berry: "Berry"
    contest: "Contest"
    evolution: "Evolution"
    game: "Game"
    item: "Item"
    location: "Location"
    machine: "Machine"
    move: "Move"
    pokemon: "Pokemon"
    encounter: "Encounter"

    def __init__(
        self,
        *,
        cache_size: int = 100,
        session: t.Optional["aiohttp.ClientSession"] = None,
        load: bool = True,
    ) -> None:
        """
        Parameters
        ----------
        cache_size : int
            The size of the cache to use for the HTTP client.
        session : typing.Optional[aiohttp.ClientSession]
            The session to use for the HTTP client. It is recommended to use the default.
        load : bool
            Whether or not to automatically load extension data on setup.

        Returns
        -------
        PokeLance
            The client.
        """
        self._logger = create_logging_setup("Client")
        self._http = HttpClient(client=self, session=session, cache_size=cache_size)
        self._auto_load = load
        self._loaders: t.List[t.Coroutine[t.Any, t.Any, None]] = []

    async def __aenter__(self) -> "PokeLance":
        return self

    async def __aexit__(
        self,
        exc_type: t.Optional[t.Type[BaseException]],
        exc_val: t.Optional[BaseException],
        exc_tb: t.Optional["TracebackType"],
    ) -> None:
        if self._http.session is not None:
            await self._http.session.close()

    async def setup_hook(self) -> None:
        """
        The setup hook to be called after the client is created.
        This is called automatically when the client is created.
        It is not recommended to call this manually.
        """
        self._logger.info(f"Using cache size: {self._http.cache.max_size}")
        for extension in self.EXTENSIONS.iterdir():
            if extension.is_file() and extension.suffix == ".py":
                if "_" not in extension.stem:
                    module = __import__(f"pokelance.ext.{extension.stem}", fromlist=["setup"])
                    await module.setup(self)
        if not self._auto_load:
            [asyncio.create_task(loader) for loader in self._loaders]
            self._logger.info("Lazy loading extension data.")
        else:
            self._logger.info("Loading extension data complete.")
        self._logger.info("Setup complete")

    async def add_extension(self, name: str, extension: "BaseExtension") -> None:
        """
        Adds an extension to the client. This is called automatically when an extension is loaded.

        Parameters
        ----------
        name : str
            The name of the extension.
        extension : BaseExtension
            The extension to add.
        """
        self._logger.info(f"Adding extension: {name}")
        if not self._auto_load:
            self._loaders.append(extension.setup())
        else:
            await extension.setup()
        setattr(self, name, extension)

    async def ping(self) -> float:
        """
        Pings the PokeAPI and returns the latency.

        Returns
        -------
        float
            The latency of the PokeAPI.
        """
        return await self._http.ping()

    async def close(self) -> None:
        """
        Closes the client session. Recommended to use this when the client is no longer needed.
        Not needed if the client is used in a context manager.
        """
        self._logger.info("Closing session")
        if self._http.session is not None:
            await self._http.session.close()

    @property
    def logger(self) -> "logging.Logger":
        """
        The logger used to log information about the client.

        Returns
        -------
        logging.Logger
            The logger.
        """
        return self._logger

    @property
    def http(self) -> HttpClient:
        """
        The HTTP client used to make requests to the PokeAPI.

        Returns
        -------
        HttpClient
            The HTTP client.
        """
        return self._http
