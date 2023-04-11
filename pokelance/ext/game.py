import typing as t

from pokelance.http import Endpoint
from pokelance.models import Generation, Pokedex, Version, VersionGroup

from ._base import BaseExtension

if t.TYPE_CHECKING:
    from pokelance import PokeLance
    from pokelance.cache import Game as GameCache


__all__: t.Tuple[str, ...] = (
    "setup",
    "Game",
)


class Game(BaseExtension):
    """
    Extension for game related endpoints.

    Attributes
    ----------
    cache: pokelance.cache.Game
        The cache to use for caching resources.

    """

    cache: "GameCache"

    def get_generation(self, name: t.Union[str, int]) -> t.Optional[Generation]:
        """Gets a generation from the cache.

        Parameters
        ----------
        name: typing.Union[str, int]
            The name or id of the generation.

        Returns
        -------
        typing.Optional[pokelance.models.Generation]
            The generation if it exists in the cache, else None.

        Raises
        ------
        pokelance.exceptions.ResourceNotFound
            The name or id of the generation is invalid.

        Examples
        --------

        >>> from pokelance import PokeLance
        >>> client = PokeLance()
        >>> generation = client.game.get_generation(1)
        >>> generation.id
        1
        """
        route = Endpoint.get_generation(name)
        self._validate_resource(self.cache.generation, name, route)
        return self.cache.generation.get(route, None)

    async def fetch_generation(self, name: t.Union[str, int]) -> t.Optional[Generation]:
        """Fetches a generation from the API.

        Parameters
        ----------
        name: typing.Union[str, int]
            The name or id of the generation.

        Raises
        ------
        pokelance.exceptions.ResourceNotFound
            The name or id of the generation is invalid.

        Examples
        --------

        >>> from pokelance import PokeLance
        >>> import asyncio
        >>> client = PokeLance()
        >>> async def main() -> None:
        ...     generation = await client.game.fetch_generation(1)
        ...     print(generation.id)
        ...     await client.close()
        >>> asyncio.run(main())
        1
        """
        route = Endpoint.get_generation(name)
        self._validate_resource(self.cache.generation, name, route)
        data = await self._client.request(route)
        return self.cache.generation.setdefault(route, Generation.from_payload(data))

    def get_pokedex(self, name: t.Union[str, int]) -> t.Optional[Pokedex]:
        """Gets a pokedex from the cache.

        Parameters
        ----------
        name: typing.Union[str, int]
            The name or id of the pokedex.

        Returns
        -------
        typing.Optional[pokelance.models.Pokedex]
            The pokedex if it exists in the cache, else None.

        Raises
        ------
        pokelance.exceptions.ResourceNotFound
            The name or id of the pokedex is invalid.

        Examples
        --------

        >>> from pokelance import PokeLance
        >>> client = PokeLance()
        >>> pokedex = client.game.get_pokedex(1)
        >>> pokedex.region
        None
        """
        route = Endpoint.get_pokedex(name)
        self._validate_resource(self.cache.pokedex, name, route)
        return self.cache.pokedex.get(route, None)

    async def fetch_pokedex(self, name: t.Union[str, int]) -> t.Optional[Pokedex]:
        """Fetches a pokedex from the API.

        Parameters
        ----------
        name: typing.Union[str, int]
            The name or id of the pokedex.

        Raises
        ------
        pokelance.exceptions.ResourceNotFound
            The name or id of the pokedex is invalid.

        Examples
        --------

        >>> from pokelance import PokeLance
        >>> import asyncio
        >>> client = PokeLance()
        >>> async def main() -> None:
        ...     pokedex = await client.game.fetch_pokedex(1)
        ...     print(pokedex.region)
        ...     await client.close()
        >>> asyncio.run(main())
        None
        """
        route = Endpoint.get_pokedex(name)
        self._validate_resource(self.cache.pokedex, name, route)
        data = await self._client.request(route)
        return self.cache.pokedex.setdefault(route, Pokedex.from_payload(data))

    def get_version(self, name: t.Union[str, int]) -> t.Optional[Version]:
        """Gets a version from the cache.

        Parameters
        ----------
        name: typing.Union[str, int]
            The name or id of the version.

        Returns
        -------
        typing.Optional[pokelance.models.Version]
            The version if it exists in the cache, else None.

        Raises
        ------
        pokelance.exceptions.ResourceNotFound
            The name or id of the version is invalid.

        Examples
        --------

        >>> from pokelance import PokeLance
        >>> client = PokeLance()
        >>> version = client.game.get_version(1)
        >>> version.name
        'red'
        """
        route = Endpoint.get_version(name)
        self._validate_resource(self.cache.version, name, route)
        return self.cache.version.get(route, None)

    async def fetch_version(self, name: t.Union[str, int]) -> t.Optional[Version]:
        """Fetches a version from the API.

        Parameters
        ----------
        name: typing.Union[str, int]
            The name or id of the version.

        Raises
        ------
        pokelance.exceptions.ResourceNotFound
            The name or id of the version is invalid.

        Examples
        --------

        >>> from pokelance import PokeLance
        >>> import asyncio
        >>> client = PokeLance()
        >>> async def main() -> None:
        ...     version = await client.game.fetch_version(1)
        ...     print(version.name)
        ...     await client.close()
        >>> asyncio.run(main())
        red
        """
        route = Endpoint.get_version(name)
        self._validate_resource(self.cache.version, name, route)
        data = await self._client.request(route)
        return self.cache.version.setdefault(route, Version.from_payload(data))

    def get_version_group(self, name: t.Union[str, int]) -> t.Optional[VersionGroup]:
        """Gets a version group from the cache.

        Parameters
        ----------
        name: typing.Union[str, int]
            The name or id of the version group.

        Returns
        -------
        typing.Optional[pokelance.models.VersionGroup]
            The version group if it exists in the cache, else None.

        Raises
        ------
        pokelance.exceptions.ResourceNotFound
            The name or id of the version group is invalid.

        Examples
        --------

        >>> from pokelance import PokeLance
        >>> client = PokeLance()
        >>> version_group = client.game.get_version_group(1)
        >>> version_group.id
        1
        """
        route = Endpoint.get_version_group(name)
        self._validate_resource(self.cache.version_group, name, route)
        return self.cache.version_group.get(route, None)

    async def fetch_version_group(self, name: t.Union[str, int]) -> t.Optional[VersionGroup]:
        """Fetches a version group from the API.

        Parameters
        ----------
        name: typing.Union[str, int]
            The name or id of the version group.

        Raises
        ------
        pokelance.exceptions.ResourceNotFound
            The name or id of the version group is invalid.

        Examples
        --------

        >>> from pokelance import PokeLance
        >>> import asyncio
        >>> client = PokeLance()
        >>> async def main() -> None:
        ...     version_group = await client.game.fetch_version_group(1)
        ...     print(version_group.id)
        ...     await client.close()
        >>> asyncio.run(main())
        1
        """
        route = Endpoint.get_version_group(name)
        self._validate_resource(self.cache.version_group, name, route)
        data = await self._client.request(route)
        return self.cache.version_group.setdefault(route, VersionGroup.from_payload(data))


def setup(lance: "PokeLance") -> None:
    """Sets up the game cog."""
    lance.add_extension("game", Game(lance.http))
