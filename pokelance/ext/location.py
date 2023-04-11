import typing as t

from pokelance.http import Endpoint
from pokelance.models import Location as LocationModel
from pokelance.models import LocationArea, PalParkArea, Region

from ._base import BaseExtension

if t.TYPE_CHECKING:
    from pokelance import PokeLance
    from pokelance.cache import Location as LocationCache


__all__: t.Tuple[str, ...] = (
    "setup",
    "Location",
)


class Location(BaseExtension):
    """
    Extension for location related endpoints.

    Attributes
    ----------
    cache: pokelance.cache.Location
        The cache for this extension.
    """

    cache: "LocationCache"

    def get_location(self, name: t.Union[str, int]) -> t.Optional[LocationModel]:
        """Gets a location from the cache.

        Parameters
        ----------
        name: typing.Union[str, int]
            The name or id of the location.

        Returns
        -------
        typing.Optional[pokelance.models.Location]
            The location if it exists in the cache, else None.

        Raises
        ------
        pokelance.exceptions.ResourceNotFound
            The name or id of the item pocket is invalid.

        Examples
        --------

        >>> from pokelance import PokeLance
        >>> client = PokeLance()
        >>> location = client.location.get_location(1)
        >>> location.name
        'canalave-city'
        """
        route = Endpoint.get_location(name)
        self._validate_resource(self.cache.location, name, route)
        return self.cache.location.get(route, None)

    async def fetch_location(self, name: t.Union[str, int]) -> t.Optional[LocationModel]:
        """Fetches a location from the API.

        Parameters
        ----------
        name: typing.Union[str, int]
            The name or id of the location.

        Returns
        -------
        t.Optional[pokelance.models.Location]
            The location.

        Raises
        ------
        pokelance.exceptions.ResourceNotFound
            The name or id of the location is invalid.

        Examples
        --------

        >>> from pokelance import PokeLance
        >>> import asyncio
        >>> client = PokeLance()
        >>> async def main() -> None:
        ...     location = await client.location.fetch_location(1)
        ...     print(location.name)
        ...     await client.close()
        >>> asyncio.run(main())
        canalave-city
        """
        route = Endpoint.get_location(name)
        self._validate_resource(self.cache.location, name, route)
        data = await self._client.request(route)
        return self.cache.location.setdefault(route, LocationModel.from_payload(data))

    def get_location_area(self, name: t.Union[str, int]) -> t.Optional[LocationArea]:
        """Gets a location area from the cache.

        Parameters
        ----------
        name: typing.Union[str, int]
            The name or id of the location area.

        Returns
        -------
        typing.Optional[pokelance.models.LocationArea]
            The location area if it exists in the cache, else None.

        Raises
        ------
        pokelance.exceptions.ResourceNotFound
            The name or id of the location area is invalid.

        Examples
        --------

        >>> from pokelance import PokeLance
        >>> client = PokeLance()
        >>> location_area = client.location.get_location_area(1)
        >>> location_area.name
        'canalave-city-area'
        """
        route = Endpoint.get_location_area(name)
        self._validate_resource(self.cache.location_area, name, route)
        return self.cache.location_area.get(route, None)

    async def fetch_location_area(self, name: t.Union[str, int]) -> t.Optional[LocationArea]:
        """Fetches a location area from the API.

        Parameters
        ----------
        name: typing.Union[str, int]
            The name or id of the location area.

        Returns
        -------
        t.Optional[pokelance.models.LocationArea]
            The location area.

        Raises
        ------
        pokelance.exceptions.ResourceNotFound
            The name or id of the location area is invalid.

        Examples
        --------

        >>> from pokelance import PokeLance
        >>> import asyncio
        >>> client = PokeLance()
        >>> async def main() -> None:
        ...     location_area = await client.location.fetch_location_area(1)
        ...     print(location_area.name)
        ...     await client.close()
        >>> asyncio.run(main())
        canalave-city-area
        """
        route = Endpoint.get_location_area(name)
        self._validate_resource(self.cache.location_area, name, route)
        data = await self._client.request(route)
        return self.cache.location_area.setdefault(route, LocationArea.from_payload(data))

    def get_pal_park_area(self, name: t.Union[str, int]) -> t.Optional[PalParkArea]:
        """Gets a pal park area from the cache.

        Parameters
        ----------
        name: typing.Union[str, int]
            The name or id of the pal park area.

        Returns
        -------
        typing.Optional[pokelance.models.PalParkArea]
            The pal park area if it exists in the cache, else None.

        Raises
        ------
        pokelance.exceptions.ResourceNotFound
            The name or id of the pal park area is invalid.

        Examples
        --------

        >>> from pokelance import PokeLance
        >>> client = PokeLance()
        >>> pal_park_area = client.location.get_pal_park_area(1)
        >>> pal_park_area.name
        'forest'
        """
        route = Endpoint.get_pal_park_area(name)
        self._validate_resource(self.cache.pal_park_area, name, route)
        return self.cache.pal_park_area.get(route, None)

    async def fetch_pal_park_area(self, name: t.Union[str, int]) -> t.Optional[PalParkArea]:
        """Fetches a pal park area from the API.

        Parameters
        ----------
        name: typing.Union[str, int]
            The name or id of the pal park area.

        Returns
        -------
        t.Optional[pokelance.models.PalParkArea]
            The pal park area.

        Raises
        ------
        pokelance.exceptions.ResourceNotFound
            The name or id of the pal park area is invalid.

        Examples
        --------

        >>> from pokelance import PokeLance
        >>> import asyncio
        >>> client = PokeLance()
        >>> async def main() -> None:
        ...     pal_park_area = await client.location.fetch_pal_park_area(1)
        ...     print(pal_park_area.name)
        ...     await client.close()
        >>> asyncio.run(main())
        forest
        """
        route = Endpoint.get_pal_park_area(name)
        self._validate_resource(self.cache.pal_park_area, name, route)
        data = await self._client.request(route)
        return self.cache.pal_park_area.setdefault(route, PalParkArea.from_payload(data))

    def get_region(self, name: t.Union[str, int]) -> t.Optional[Region]:
        """Gets a region from the cache.

        Parameters
        ----------
        name: typing.Union[str, int]
            The name or id of the region.

        Returns
        -------
        typing.Optional[pokelance.models.Region]
            The region if it exists in the cache, else None.

        Raises
        ------
        pokelance.exceptions.ResourceNotFound
            The name or id of the region is invalid.

        Examples
        --------

        >>> from pokelance import PokeLance
        >>> client = PokeLance()
        >>> region = client.location.get_region(1)
        >>> region.name
        'kanto'
        """
        route = Endpoint.get_region(name)
        self._validate_resource(self.cache.region, name, route)
        return self.cache.region.get(route, None)

    async def fetch_region(self, name: t.Union[str, int]) -> t.Optional[Region]:
        """Fetches a region from the API.

        Parameters
        ----------
        name: typing.Union[str, int]
            The name or id of the region.

        Returns
        -------
        t.Optional[pokelance.models.Region]
            The region.

        Raises
        ------
        pokelance.exceptions.ResourceNotFound
            The name or id of the region is invalid.

        Examples
        --------

        >>> from pokelance import PokeLance
        >>> import asyncio
        >>> client = PokeLance()
        >>> async def main() -> None:
        ...     region = await client.location.fetch_region(1)
        ...     print(region.name)
        ...     await client.close()
        >>> asyncio.run(main())
        kanto
        """
        route = Endpoint.get_region(name)
        self._validate_resource(self.cache.region, name, route)
        data = await self._client.request(route)
        return self.cache.region.setdefault(route, Region.from_payload(data))


def setup(lance: "PokeLance") -> None:
    """Sets up the location cog."""
    lance.add_extension("location", Location(lance.http))
