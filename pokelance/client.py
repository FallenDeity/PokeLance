import typing as t
from functools import lru_cache
from pathlib import Path

from .constants import ExtensionEnum, ExtensionsL
from .http import HttpClient
from .logger import Logger

if t.TYPE_CHECKING:
    import logging
    from types import TracebackType

    import aiohttp

    from .ext import BaseExtension, Berry, Contest, Encounter, Evolution, Game, Item, Location, Machine, Move, Pokemon
    from .models import BaseModel  # noqa: F401


__all__: t.Tuple[str, ...] = ("PokeLance",)


BaseType = t.TypeVar("BaseType", bound="BaseModel")


class PokeLance:
    """
    Main class to interact with the PokeAPI.


    Attributes
    ----------
    _http : HttpClient
        The HTTP client used to make requests to the PokeAPI.
    _logger : logging.Logger
        The logger used to log information about the client.
    _loaders : t.List[t.Tuple[t.Coroutine[t.Any, t.Any, None], str]]
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
        image_cache_size: int = 128,
        cache_size: int = 100,
        logger: t.Optional["logging.Logger"] = None,
        file_logging: bool = False,
        session: t.Optional["aiohttp.ClientSession"] = None,
    ) -> None:
        """
        Parameters
        ----------
        image_cache_size : int
            The size of the image cache. Defaults to 128.
        cache_size : int
            The size of the cache to use for the HTTP client.
        logger : logging.Logger
            The logger to use. If not provided, a new logger will be created.
        file_logging : bool
            Whether to log to a file. Defaults to False.
        session : typing.Optional[aiohttp.ClientSession]
            The session to use for the HTTP client. It is recommended to use the default.

        Returns
        -------
        PokeLance
            The client.
        """
        self._logger = logger or Logger(name="pokelance", file_logging=file_logging)
        self._http = HttpClient(client=self, session=session, cache_size=cache_size)
        self._loaders: t.List[t.Tuple[t.Coroutine[t.Any, t.Any, None], str]] = []
        self._image_cache_size = image_cache_size
        lru_cache(maxsize=self._image_cache_size)(self.get_image_async)
        self.setup_hook()

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

    def setup_hook(self) -> None:
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
                    module.setup(self)
        self._logger.info("Setup complete")

    def add_extension(self, name: str, extension: "BaseExtension") -> None:
        """
        Adds an extension to the client. This is called automatically when an extension is loaded.

        Parameters
        ----------
        name : str
            The name of the extension.
        extension : BaseExtension
            The extension to add.
        """
        self._loaders.append((extension.setup(), name))
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

    async def getch_data(
        self, ext: t.Union[ExtensionEnum, ExtensionsL], category: str, id_: t.Union[int, str]
    ) -> BaseType:
        """
        A getch method that looks up the cache for the data first then gets it from the API if it is not found.

        Parameters
        ----------
        ext : Union[ExtensionEnum, ExtensionsL]
            The extension to get the data from.
        category : str
            The category to get the data from.
        id_ : Union[int, str]
            The ID of the data to get.

        Returns
        -------
        BaseType
            The data.

        Raises
        ------
        ValueError
            If the extension or category is invalid.
        HTTPException
            If the data is not found.

        Examples
        --------
        >>> import pokelance
        >>> import asyncio
        >>> from pokelance.models import Pokemon
        >>> client = pokelance.PokeLance()
        >>> async def main() -> None:
        ...     pokemon: Pokemon = await client.getch_data("pokemon", "pokemon", 1)
        ...     print(pokemon.name)
        ...     await client.close()
        >>> asyncio.run(main())
        bulbasaur
        """
        if isinstance(ext, str) and ext.lower() not in ExtensionEnum.__members__:
            raise ValueError(f"Invalid extension: {ext}")
        categories = ExtensionEnum.get_categories(ext) if isinstance(ext, str) else ext.categories  # type: ignore
        if category not in categories:
            raise ValueError(f"Invalid category: {category}")
        ext_ = getattr(self, ext.lower()) if isinstance(ext, str) else getattr(self, ext.name.lower())
        get_, fetch_ = getattr(ext_, f"get_{category}"), getattr(ext_, f"fetch_{category}")
        return t.cast(BaseType, get_(id_) or await fetch_(id_))

    async def get_image_async(self, url: str) -> bytes:
        """
        Gets an image from the url asynchronously.

        Parameters
        ----------
        url : str
            The URL to get the image from.

        Returns
        -------
        bytes
            The image data.
        """
        return await self._http.load_image(url)

    @property
    def loaders(self) -> t.List[t.Tuple[t.Coroutine[t.Any, t.Any, None], str]]:
        """
        The list of loaders for the extensions.

        Returns
        -------
        typing.List[typing.Tuple[typing.Coroutine[typing.Any, typing.Any, None], str]]
            The list of loaders.
        """
        return self._loaders

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

    @property
    def image_cache_size(self) -> int:
        """
        The size of the image cache.

        Returns
        -------
        int
            The size of the image cache.
        """
        return self._image_cache_size

    @image_cache_size.setter
    def image_cache_size(self, value: int) -> None:
        self._image_cache_size = value
        lru_cache(maxsize=self._image_cache_size)(self.get_image_async)
