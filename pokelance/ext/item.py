import typing as t

from pokelance.http import Endpoint
from pokelance.models import Item as ItemModel
from pokelance.models import ItemAttribute, ItemCategory, ItemFlingEffect, ItemPocket

from ._base import BaseExtension

if t.TYPE_CHECKING:
    from pokelance import PokeLance
    from pokelance.cache import Item as ItemCache


__all__: t.Tuple[str, ...] = (
    "setup",
    "Item",
)


class Item(BaseExtension):
    """
    Extension for item related endpoints.

    Attributes
    ----------
    cache: pokelance.cache.Item
        The cache for this extension.
    """

    cache: "ItemCache"

    def get_item(self, name: t.Union[str, int]) -> t.Optional[ItemModel]:
        """Gets an item from the cache.

        Parameters
        ----------
        name: typing.Union[str, int]
            The name or id of the item.

        Returns
        -------
        typing.Optional[pokelance.models.Item]
            The item if it exists in the cache, else None.

        Raises
        ------
        pokelance.exceptions.ResourceNotFound
            The name or id of the item is invalid.

        Examples
        --------

        >>> from pokelance import PokeLance
        >>> client = PokeLance()
        >>> item = client.item.get_item("potion")
        >>> item.id
        17
        """
        route = Endpoint.get_item(name)
        self._validate_resource(self.cache.item, name, route)
        return self.cache.item.get(route, None)

    async def fetch_item(self, name: t.Union[str, int]) -> t.Optional[ItemModel]:
        """Fetches an item from the API.

        Parameters
        ----------
        name: typing.Union[str, int]
            The name or id of the item.

        Returns
        -------
        t.Optional[pokelance.models.Item]
            The item.

        Raises
        ------
        pokelance.exceptions.ResourceNotFound
            The name or id of the item is invalid.

        Examples
        --------

        >>> from pokelance import PokeLance
        >>> import asyncio
        >>> client = PokeLance()
        >>> async def main() -> None:
        ...     item = await client.item.fetch_item("potion")
        ...     print(item.id)
        ...     await client.close()
        >>> asyncio.run(main())
        17
        """
        route = Endpoint.get_item(name)
        self._validate_resource(self.cache.item, name, route)
        data = await self._client.request(route)
        return self.cache.item.setdefault(route, ItemModel.from_payload(data))

    def get_item_attribute(self, name: t.Union[str, int]) -> t.Optional[ItemAttribute]:
        """Gets an item attribute from the cache.

        Parameters
        ----------
        name: typing.Union[str, int]
            The name or id of the item attribute.

        Returns
        -------
        typing.Optional[pokelance.models.ItemAttribute]
            The item attribute if it exists in the cache, else None.

        Raises
        ------
        pokelance.exceptions.ResourceNotFound
            The name or id of the item attribute is invalid.

        Examples
        --------

        >>> from pokelance import PokeLance
        >>> client = PokeLance()
        >>> item_attribute = client.item.get_item_attribute("holdable")
        >>> item_attribute.id
        5
        """
        route = Endpoint.get_item_attribute(name)
        self._validate_resource(self.cache.item_attribute, name, route)
        return self.cache.item_attribute.get(route, None)

    async def fetch_item_attribute(self, name: t.Union[str, int]) -> t.Optional[ItemAttribute]:
        """Fetches an item attribute from the API.

        Parameters
        ----------
        name: typing.Union[str, int]
            The name or id of the item attribute.

        Returns
        -------
        t.Optional[pokelance.models.ItemAttribute]
            The item attribute.

        Raises
        ------
        pokelance.exceptions.ResourceNotFound
            The name or id of the item attribute is invalid.

        Examples
        --------

        >>> from pokelance import PokeLance
        >>> import asyncio
        >>> client = PokeLance()
        >>> async def main() -> None:
        ...     item_attribute = await client.item.fetch_item_attribute("holdable")
        ...     print(item_attribute.id)
        ...     await client.close()
        >>> asyncio.run(main())
        5
        """
        route = Endpoint.get_item_attribute(name)
        self._validate_resource(self.cache.item_attribute, name, route)
        data = await self._client.request(route)
        return self.cache.item_attribute.setdefault(route, ItemAttribute.from_payload(data))

    def get_item_category(self, name: t.Union[str, int]) -> t.Optional[ItemCategory]:
        """Gets an item category from the cache.

        Parameters
        ----------
        name: typing.Union[str, int]
            The name or id of the item category.

        Returns
        -------
        typing.Optional[pokelance.models.ItemCategory]
            The item category if it exists in the cache, else None.

        Raises
        ------
        pokelance.exceptions.ResourceNotFound
            The name or id of the item category is invalid.

        Examples
        --------

        >>> from pokelance import PokeLance
        >>> client = PokeLance()
        >>> item_category = client.item.get_item_category(1)
        >>> item_category.name
        'stat-boosts'
        """
        route = Endpoint.get_item_category(name)
        self._validate_resource(self.cache.item_category, name, route)
        return self.cache.item_category.get(route, None)

    async def fetch_item_category(self, name: t.Union[str, int]) -> t.Optional[ItemCategory]:
        """Fetches an item category from the API.

        Parameters
        ----------
        name: typing.Union[str, int]
            The name or id of the item category.

        Returns
        -------
        t.Optional[pokelance.models.ItemCategory]
            The item category.

        Raises
        ------
        pokelance.exceptions.ResourceNotFound
            The name or id of the item category is invalid.

        Examples
        --------

        >>> from pokelance import PokeLance
        >>> import asyncio
        >>> client = PokeLance()
        >>> async def main() -> None:
        ...     item_category = await client.item.fetch_item_category(1)
        ...     print(item_category.name)
        ...     await client.close()
        >>> asyncio.run(main())
        stat-boosts
        """
        route = Endpoint.get_item_category(name)
        self._validate_resource(self.cache.item_category, name, route)
        data = await self._client.request(route)
        return self.cache.item_category.setdefault(route, ItemCategory.from_payload(data))

    def get_item_fling_effect(self, name: t.Union[str, int]) -> t.Optional[ItemFlingEffect]:
        """Gets an item fling effect from the cache.

        Parameters
        ----------
        name: typing.Union[str, int]
            The name or id of the item fling effect.

        Returns
        -------
        typing.Optional[pokelance.models.ItemFlingEffect]
            The item fling effect if it exists in the cache, else None.

        Raises
        ------
        pokelance.exceptions.ResourceNotFound
            The name or id of the item fling effect is invalid.

        Examples
        --------

        >>> from pokelance import PokeLance
        >>> client = PokeLance()
        >>> item_fling_effect = client.item.get_item_fling_effect(1)
        >>> item_fling_effect.name
        'badly-poison'
        """
        route = Endpoint.get_item_fling_effect(name)
        self._validate_resource(self.cache.item_fling_effect, name, route)
        return self.cache.item_fling_effect.get(route, None)

    async def fetch_item_fling_effect(self, name: t.Union[str, int]) -> t.Optional[ItemFlingEffect]:
        """Fetches an item fling effect from the API.

        Parameters
        ----------
        name: typing.Union[str, int]
            The name or id of the item fling effect.

        Returns
        -------
        t.Optional[pokelance.models.ItemFlingEffect]
            The item fling effect.

        Raises
        ------
        pokelance.exceptions.ResourceNotFound
            The name or id of the item fling effect is invalid.

        Examples
        --------

        >>> from pokelance import PokeLance
        >>> import asyncio
        >>> client = PokeLance()
        >>> async def main() -> None:
        ...     item_fling_effect = await client.item.fetch_item_fling_effect(1)
        ...     print(item_fling_effect.name)
        ...     await client.close()
        >>> asyncio.run(main())
        badly-poison
        """
        route = Endpoint.get_item_fling_effect(name)
        self._validate_resource(self.cache.item_fling_effect, name, route)
        data = await self._client.request(route)
        return self.cache.item_fling_effect.setdefault(route, ItemFlingEffect.from_payload(data))

    def get_item_pocket(self, name: t.Union[str, int]) -> t.Optional[ItemPocket]:
        """Gets an item pocket from the cache.

        Parameters
        ----------
        name: typing.Union[str, int]
            The name or id of the item pocket.

        Returns
        -------
        typing.Optional[pokelance.models.ItemPocket]
            The item pocket if it exists in the cache, else None.

        Raises
        ------
        pokelance.exceptions.ResourceNotFound
            The name or id of the item pocket is invalid.

        Examples
        --------

        >>> from pokelance import PokeLance
        >>> client = PokeLance()
        >>> item_pocket = client.item.get_item_pocket(1)
        >>> item_pocket.name
        'misc'
        """
        route = Endpoint.get_item_pocket(name)
        self._validate_resource(self.cache.item_pocket, name, route)
        return self.cache.item_pocket.get(route, None)

    async def fetch_item_pocket(self, name: t.Union[str, int]) -> t.Optional[ItemPocket]:
        """Fetches an item pocket from the API.

        Parameters
        ----------
        name: typing.Union[str, int]
            The name or id of the item pocket.

        Returns
        -------
        t.Optional[pokelance.models.ItemPocket]
            The item pocket.

        Raises
        ------
        pokelance.exceptions.ResourceNotFound
            The name or id of the item pocket is invalid.

        Examples
        --------

        >>> from pokelance import PokeLance
        >>> import asyncio
        >>> client = PokeLance()
        >>> async def main() -> None:
        ...     item_pocket = await client.item.fetch_item_pocket(1)
        ...     print(item_pocket.name)
        ...     await client.close()
        >>> asyncio.run(main())
        misc
        """
        route = Endpoint.get_item_pocket(name)
        self._validate_resource(self.cache.item_pocket, name, route)
        data = await self._client.request(route)
        return self.cache.item_pocket.setdefault(route, ItemPocket.from_payload(data))


def setup(lance: "PokeLance") -> None:
    """Sets up the item cog."""
    lance.add_extension("item", Item(lance.http))
