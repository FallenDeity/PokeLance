from __future__ import annotations

import functools
import logging
import typing as t
from pathlib import Path

from typing_extensions import Self, TypeVar, Unpack

from pokelance.client._base import ClientBase, ClientConfig
from pokelance.constants import ExtensionEnum, ExtensionsL
from pokelance.http._sync import SyncHttpClient

if t.TYPE_CHECKING:
    from types import TracebackType

    import niquests

    from pokelance.ext.sync import (
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

__all__: tuple[str, ...] = ("PokeLanceSyncClient",)

logger = logging.getLogger(__name__)

BaseModelT = TypeVar(
    "BaseModelT",
    bound="BaseModel | t.Sequence[BaseModel]",
)


class PokeLanceSyncClient(ClientBase[SyncHttpClient]):
    """Main synchronous client to interact with the PokeAPI.

    Parameters
    ----------
    cache_size : int, default: 100
        The maximum cache size for the HTTP client.
    session : niquests.Session | None, default: None
        An optional custom Session to use for requests.
    **kwargs : Unpack[ClientConfig]
        Additional configuration options.

    Attributes
    ----------
    http : SyncHttpClient
        The HTTP client used to make requests to the PokeAPI.
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

    Examples
    --------
    ```python
    from pokelance import PokeLanceSyncClient

    with PokeLanceSyncClient() as client:
        pokemon = client.pokemon.get_pokemon("pikachu")
        print(f"{pokemon.name} (ID: {pokemon.id})")
    ```
    """

    EXTENSIONS: Path = Path(__file__).parent.parent / "ext" / "sync"

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
        cache_size: int = 100,
        session: niquests.Session | None = None,
        **kwargs: Unpack[ClientConfig],
    ) -> None:
        super().__init__(
            http=SyncHttpClient(client=self, session=session, cache_size=cache_size),
            **kwargs,
        )
        self._cached_get_image = functools.lru_cache(maxsize=self._image_cache_size)(self._http.load_image)
        self._cached_get_audio = functools.lru_cache(maxsize=self._audio_cache_size)(self._http.load_audio)
        self.setup_hook("pokelance.ext.sync")

    def __enter__(self) -> Self:
        return self

    def __exit__(
        self,
        exc_type: type[BaseException] | None,
        exc_val: BaseException | None,
        exc_tb: TracebackType | None,
    ) -> None:
        logger.warning("Closing session!")
        self._http.close()

    def ping(self) -> float:
        """Pings the PokeAPI and returns the latency in seconds.

        Returns
        -------
        float
            The round-trip latency in seconds.

        Examples
        --------
        ```python
        latency = client.ping()
        print(f"Latency: {latency * 1000:.1f}ms")
        ```
        """
        return self._http.ping()

    def close(self) -> None:
        """Closes the underlying HTTP client session.

        Examples
        --------
        ```python
        client.close()
        ```
        """
        logger.warning("Closing session!")
        self._http.close()

    def getch_data(
        self,
        ext: ExtensionEnum | ExtensionsL | str,
        category: str,
        id_: int | str | None = None,
    ) -> BaseModelT:  # pyright: ignore[reportInvalidTypeVarUse]
        """Looks up an object from cache first, fetching from PokeAPI if not cached.

        Parameters
        ----------
        ext : ExtensionEnum | ExtensionsL | str
            The extension name (e.g. 'pokemon', 'berry', 'item').
        category : str
            The category name within the extension (e.g. 'pokemon', 'berry').
        id_ : int | str | None, optional
            The ID or name of the resource to look up.

        Returns
        -------
        BaseModelT
            The retrieved model instance or sequence of models.

        Examples
        --------
        ```python
        from pokelance.constants import ExtensionEnum

        # Using string identifiers
        pokemon = client.getch_data("pokemon", "pokemon", "pikachu")

        # Using ExtensionEnum for type safety
        berry = client.getch_data(ExtensionEnum.Berry, "berry", 1)
        ```
        """
        ext_instance, resolved_category = self._resolve_extension_category(ext, category)
        get_ = getattr(ext_instance, f"get_{resolved_category}")
        fetch_ = getattr(ext_instance, f"fetch_{resolved_category}")
        params = (id_,) if id_ is not None else ()
        return t.cast("BaseModelT", get_(*params) or fetch_(*params))

    def from_url(self, url: str) -> BaseModelT:  # pyright: ignore[reportInvalidTypeVarUse]
        """Constructs a request from any valid PokeAPI resource URL.

        Parameters
        ----------
        url : str
            The PokeAPI resource URL (e.g. 'https://pokeapi.co/api/v2/pokemon/25/').

        Returns
        -------
        BaseModelT
            The corresponding model instance for the URL resource.

        Raises
        ------
        ValueError
            If the provided URL is not a valid PokeAPI endpoint.

        Examples
        --------
        ```python
        pokemon = client.from_url("https://pokeapi.co/api/v2/pokemon/25/")
        print(pokemon.name)  # pikachu
        ```
        """
        if params := ExtensionEnum.validate_url(url):
            return self.getch_data(params.extension, params.category, params.value)
        raise ValueError(f"Invalid URL: {url}")

    def get_image(self, url: str) -> bytes:
        """Downloads image sprite bytes from a URL with LRU caching.

        Parameters
        ----------
        url : str
            The image sprite URL.

        Returns
        -------
        bytes
            The raw image file bytes.

        Examples
        --------
        ```python
        pokemon = client.pokemon.get_pokemon("pikachu")
        if pokemon.sprites.front_default:
            image_bytes = client.get_image(pokemon.sprites.front_default)
        ```
        """
        return self._cached_get_image(url)

    def get_audio(self, url: str) -> bytes:
        """Downloads audio cry bytes from a URL with LRU caching.

        Parameters
        ----------
        url : str
            The audio cry URL.

        Returns
        -------
        bytes
            The raw audio file bytes.

        Examples
        --------
        ```python
        pokemon = client.pokemon.get_pokemon("pikachu")
        if pokemon.cries.latest:
            cry_bytes = client.get_audio(pokemon.cries.latest)
        ```
        """
        return self._cached_get_audio(url)

    def wait_until_ready(self) -> None:
        """Waits until all background endpoint caches are pre-populated.

        Examples
        --------
        ```python
        client = PokeLanceSyncClient()
        client.wait_until_ready()
        # All background caches are now loaded
        ```
        """
        self._http.connect()
        logger.info("Waiting until ready...")
        self._http.loader.wait_until_ready()
        logger.info("Ready!")
