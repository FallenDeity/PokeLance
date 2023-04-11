import typing as t

from pokelance.http import Endpoint
from pokelance.models import Berry as BerryModel
from pokelance.models import BerryFirmness, BerryFlavor

from ._base import BaseExtension

if t.TYPE_CHECKING:
    from pokelance import PokeLance
    from pokelance.cache import Berry as BerryCache


__all__: t.Tuple[str, ...] = (
    "setup",
    "Berry",
)


class Berry(BaseExtension):
    """
    Extension for berry related endpoints.

    Attributes
    ----------
    cache: pokelance.cache.Berry
        The cache for this extension.
    """

    cache: "BerryCache"

    def get_berry(self, name: t.Union[str, int]) -> t.Optional[BerryModel]:
        """Gets a berry from the cache.

        Parameters
        ----------
        name: typing.Union[str, int]
            The name or id of the berry.

        Returns
        -------
        typing.Optional[pokelance.models.Berry]
            The berry if it exists in the cache, else None.

        Raises
        ------
        pokelance.exceptions.ResourceNotFound
            The name or id of the berry is invalid.

        Examples
        -------
        >>> from pokelance import PokeLance
        >>> client = PokeLance()
        >>> berry = client.berry.get_berry("cheri")  # None if not cached
        >>> berry.name
        'cheri'
        """
        route = Endpoint.get_berry(name)
        self._validate_resource(self.cache.berry, name, route)
        return self.cache.berry.get(route, None)

    async def fetch_berry(self, name: t.Union[str, int]) -> t.Optional[BerryModel]:
        """Fetches a berry from the API.

        Parameters
        ----------
        name: typing.Union[str, int]
            The name or id of the berry.

        Returns
        -------
        typing.Optional[pokelance.models.Berry]
            The berry if it exists in the API, else None.

        Raises
        ------
        pokelance.exceptions.ResourceNotFound
            The name or id of the berry is invalid.

        Examples
        -------
        >>> from pokelance import PokeLance
        >>> import asyncio
        >>> client = PokeLance()
        >>> async def main() -> None:
        ...     berry = await client.berry.fetch_berry("cheri")
        ...     print(berry.name)
        ...     await client.close()
        >>> asyncio.run(main())
        cheri
        """
        route = Endpoint.get_berry(name)
        self._validate_resource(self.cache.berry, name, route)
        data = await self._client.request(route)
        return self.cache.berry.setdefault(route, BerryModel.from_payload(data))

    def get_berry_flavor(self, name: t.Union[str, int]) -> t.Optional[BerryFlavor]:
        """Gets a berry flavor from the cache.

        Parameters
        ----------
        name: typing.Union[str, int]
            The name or id of the berry flavor.

        Returns
        -------
        typing.Optional[pokelance.models.BerryFlavor]
            The berry flavor if it exists in the cache, else None.

        Raises
        ------
        pokelance.exceptions.ResourceNotFound
            The name or id of the berry flavor is invalid.

        Examples
        -------
        >>> from pokelance import PokeLance
        >>> client = PokeLance()
        >>> berry_flavor = client.berry.get_berry_flavor("spicy")  # None if not cached
        >>> berry_flavor.name
        'spicy'
        """
        route = Endpoint.get_berry_flavor(name)
        self._validate_resource(self.cache.berry_flavor, name, route)
        return self.cache.berry_flavor.get(route, None)

    async def fetch_berry_flavor(self, name: t.Union[str, int]) -> t.Optional[BerryFlavor]:
        """Fetches a berry flavor from the API.

        Parameters
        ----------
        name: typing.Union[str, int]
            The name or id of the berry flavor.

        Returns
        -------
        typing.Optional[pokelance.models.BerryFlavor]
            The berry flavor if it exists in the API, else None.

        Raises
        ------
        pokelance.exceptions.ResourceNotFound
            The name or id of the berry flavor is invalid.

        Examples
        -------
        >>> from pokelance import PokeLance
        >>> import asyncio
        >>> client = PokeLance()
        >>> async def main() -> None:
        ...     berry_flavor = await client.berry.fetch_berry_flavor("spicy")
        ...     print(berry_flavor.name)
        ...     await client.close()
        >>> asyncio.run(main())
        spicy
        """
        route = Endpoint.get_berry_flavor(name)
        self._validate_resource(self.cache.berry_flavor, name, route)
        data = await self._client.request(route)
        self.cache.berry_flavor[route] = BerryFlavor.from_payload(data)
        return self.cache.berry_flavor[route]

    def get_berry_firmness(self, name: t.Union[str, int]) -> t.Optional[BerryFirmness]:
        """Gets a berry firmness from the cache.

        Parameters
        ----------
        name: typing.Union[str, int]
            The name or id of the berry firmness.

        Returns
        -------
        typing.Optional[pokelance.models.BerryFirmness]
            The berry firmness if it exists in the cache, else None.

        Raises
        ------
        pokelance.exceptions.ResourceNotFound
            The name or id of the berry firmness is invalid.

        Examples
        -------
        >>> from pokelance import PokeLance
        >>> client = PokeLance()
        >>> berry_firmness = client.berry.get_berry_firmness("very-soft")  # None if not cached
        >>> berry_firmness.name
        'very-soft'
        """
        route = Endpoint.get_berry_firmness(name)
        self._validate_resource(self.cache.berry_firmness, name, route)
        return self.cache.berry_firmness.get(route, None)

    async def fetch_berry_firmness(self, name: t.Union[str, int]) -> t.Optional[BerryFirmness]:
        """Fetches a berry firmness from the API.

        Parameters
        ----------
        name: typing.Union[str, int]
            The name or id of the berry firmness.

        Returns
        -------
        typing.Optional[pokelance.models.BerryFirmness]
            The berry firmness if it exists in the API, else None.

        Raises
        ------
        pokelance.exceptions.ResourceNotFound
            The name or id of the berry firmness is invalid.

        Examples
        -------
        >>> from pokelance import PokeLance
        >>> import asyncio
        >>> client = PokeLance()
        >>> async def main() -> None:
        ...     berry_firmness = await client.berry.fetch_berry_firmness("very-soft")
        ...     print(berry_firmness.name)
        ...     await client.close()
        >>> asyncio.run(main())
        very-soft
        """
        route = Endpoint.get_berry_firmness(name)
        self._validate_resource(self.cache.berry_firmness, name, route)
        data = await self._client.request(route)
        self.cache.berry_firmness[route] = BerryFirmness.from_payload(data)
        return self.cache.berry_firmness[route]


def setup(lance: "PokeLance") -> None:
    """Sets up the berry cog."""
    lance.add_extension("berry", Berry(lance.http))
