import typing as t

from pokelance.http import Endpoint
from pokelance.models import Move as MoveModel
from pokelance.models import MoveAilment, MoveBattleStyle, MoveCategory, MoveDamageClass, MoveLearnMethod, MoveTarget

from ._base import BaseExtension

if t.TYPE_CHECKING:
    from pokelance import PokeLance
    from pokelance.cache import Move as MoveCache


__all__: t.Tuple[str, ...] = (
    "setup",
    "Move",
)


class Move(BaseExtension):
    """Extension for move related endpoints.

    Attributes
    ----------
    cache: pokelance.cache.Move
        The cache for this extension.
    """

    cache: "MoveCache"

    def get_move(self, name: t.Union[str, int]) -> t.Optional[MoveModel]:
        """Gets a move from the cache.

        Parameters
        ----------
        name: t.Union[str, int]
            The id of the move.

        Returns
        -------
        typing.Optional[pokelance.models.Move]
            The move if it exists in the cache, else None.

        Raises
        ------
        pokelance.exceptions.ResourceNotFound
            If the move does not exist in the cache.

        Examples
        --------

        >>> from pokelance import PokeLance
        >>> client = PokeLance()
        >>> move = client.move.get_move(1)
        >>> move.name
        'pound'
        """
        route = Endpoint.get_move(name)
        self._validate_resource(self.cache.move, name, route)
        return self.cache.move.get(route, None)

    async def fetch_move(self, name: t.Union[str, int]) -> t.Optional[MoveModel]:
        """Fetches a move from the API.

        Parameters
        ----------
        name: t.Union[str, int]
            The id of the move.

        Returns
        -------
        typing.Optional[pokelance.models.Move]
            The move if it exists in the API, else None.

        Raises
        ------
        pokelance.exceptions.ResourceNotFound
            If the move does not exist in the API.

        Examples
        --------

        >>> from pokelance import PokeLance
        >>> import asyncio
        >>> client = PokeLance()
        >>> async def main() -> None:
        ...     move = await client.move.fetch_move(1)
        ...     print(move.name)
        ...     await client.close()
        >>> asyncio.run(main())
        pound
        """
        route = Endpoint.get_move(name)
        self._validate_resource(self.cache.move, name, route)
        data = await self._client.request(route)
        return self.cache.move.setdefault(route, MoveModel.from_payload(data))

    def get_move_ailment(self, name: t.Union[str, int]) -> t.Optional[MoveAilment]:
        """Gets a move ailment from the cache.

        Parameters
        ----------
        name: t.Union[str, int]
            The id of the move ailment.

        Returns
        -------
        typing.Optional[pokelance.models.MoveAilment]
            The move ailment if it exists in the cache, else None.

        Raises
        ------
        pokelance.exceptions.ResourceNotFound
            If the move ailment does not exist in the cache.

        Examples
        --------

        >>> from pokelance import PokeLance
        >>> client = PokeLance()
        >>> ailment = client.move.get_move_ailment(1)
        >>> ailment.name
        'paralysis'
        """
        route = Endpoint.get_move_ailment(name)
        self._validate_resource(self.cache.move_ailment, name, route)
        return self.cache.move_ailment.get(route, None)

    async def fetch_move_ailment(self, name: t.Union[str, int]) -> t.Optional[MoveAilment]:
        """Fetches a move ailment from the API.

        Parameters
        ----------
        name: t.Union[str, int]
            The id of the move ailment.

        Returns
        -------
        typing.Optional[pokelance.models.MoveAilment]
            The move ailment if it exists in the API, else None.

        Raises
        ------
        pokelance.exceptions.ResourceNotFound
            If the move ailment does not exist in the API.

        Examples
        --------

        >>> from pokelance import PokeLance
        >>> import asyncio
        >>> client = PokeLance()
        >>> async def main() -> None:
        ...     ailment = await client.move.fetch_move_ailment(1)
        ...     print(ailment.name)
        ...     await client.close()
        >>> asyncio.run(main())
        paralysis
        """
        route = Endpoint.get_move_ailment(name)
        self._validate_resource(self.cache.move_ailment, name, route)
        data = await self._client.request(route)
        return self.cache.move_ailment.setdefault(route, MoveAilment.from_payload(data))

    def get_move_battle_style(self, name: t.Union[str, int]) -> t.Optional[MoveBattleStyle]:
        """Gets a move battle style from the cache.

        Parameters
        ----------
        name: t.Union[str, int]
            The id of the move battle style.

        Returns
        -------
        typing.Optional[pokelance.models.MoveBattleStyle]
            The move battle style if it exists in the cache, else None.

        Raises
        ------
        pokelance.exceptions.ResourceNotFound
            If the move battle style does not exist in the cache.

        Examples
        --------

        >>> from pokelance import PokeLance
        >>> client = PokeLance()
        >>> style = client.move.get_move_battle_style(1)
        >>> style.name
        'attack'
        """
        route = Endpoint.get_move_battle_style(name)
        self._validate_resource(self.cache.move_battle_style, name, route)
        return self.cache.move_battle_style.get(route, None)

    async def fetch_move_battle_style(self, name: t.Union[str, int]) -> t.Optional[MoveBattleStyle]:
        """Fetches a move battle style from the API.

        Parameters
        ----------
        name: t.Union[str, int]
            The id of the move battle style.

        Returns
        -------
        typing.Optional[pokelance.models.MoveBattleStyle]
            The move battle style if it exists in the API, else None.

        Raises
        ------
        pokelance.exceptions.ResourceNotFound
            If the move battle style does not exist in the API.

        Examples
        --------

        >>> from pokelance import PokeLance
        >>> import asyncio
        >>> client = PokeLance()
        >>> async def main() -> None:
        ...     style = await client.move.fetch_move_battle_style(1)
        ...     print(style.name)
        ...     await client.close()
        >>> asyncio.run(main())
        attack
        """
        route = Endpoint.get_move_battle_style(name)
        self._validate_resource(self.cache.move_battle_style, name, route)
        data = await self._client.request(route)
        return self.cache.move_battle_style.setdefault(route, MoveBattleStyle.from_payload(data))

    def get_move_category(self, name: t.Union[str, int]) -> t.Optional[MoveCategory]:
        """Gets a move category from the cache.

        Parameters
        ----------
        name: t.Union[str, int]
            The id of the move category.

        Returns
        -------
        typing.Optional[pokelance.models.MoveCategory]
            The move category if it exists in the cache, else None.

        Raises
        ------
        pokelance.exceptions.ResourceNotFound
            If the move category does not exist in the cache.

        Examples
        --------

        >>> from pokelance import PokeLance
        >>> client = PokeLance()
        >>> category = client.move.get_move_category(1)
        >>> category.name
        'ailment'
        """
        route = Endpoint.get_move_category(name)
        self._validate_resource(self.cache.move_category, name, route)
        return self.cache.move_category.get(route, None)

    async def fetch_move_category(self, name: t.Union[str, int]) -> t.Optional[MoveCategory]:
        """Fetches a move category from the API.

        Parameters
        ----------
        name: t.Union[str, int]
            The id of the move category.

        Returns
        -------
        typing.Optional[pokelance.models.MoveCategory]
            The move category if it exists in the API, else None.

        Raises
        ------
        pokelance.exceptions.ResourceNotFound
            If the move category does not exist in the API.

        Examples
        --------

        >>> from pokelance import PokeLance
        >>> import asyncio
        >>> client = PokeLance()
        >>> async def main() -> None:
        ...     category = await client.move.fetch_move_category(1)
        ...     print(category.name)
        ...     await client.close()
        >>> asyncio.run(main())
        ailment
        """
        route = Endpoint.get_move_category(name)
        self._validate_resource(self.cache.move_category, name, route)
        data = await self._client.request(route)
        return self.cache.move_category.setdefault(route, MoveCategory.from_payload(data))

    def get_move_damage_class(self, name: t.Union[str, int]) -> t.Optional[MoveDamageClass]:
        """Gets a move damage class from the cache.

        Parameters
        ----------
        name: t.Union[str, int]
            The id of the move damage class.

        Returns
        -------
        typing.Optional[pokelance.models.MoveDamageClass]
            The move damage class if it exists in the cache, else None.

        Raises
        ------
        pokelance.exceptions.ResourceNotFound
            If the move damage class does not exist in the cache.

        Examples
        --------

        >>> from pokelance import PokeLance
        >>> client = PokeLance()
        >>> damage_class = client.move.get_move_damage_class(1)
        >>> damage_class.name
        'status'
        """
        route = Endpoint.get_move_damage_class(name)
        self._validate_resource(self.cache.move_damage_class, name, route)
        return self.cache.move_damage_class.get(route, None)

    async def fetch_move_damage_class(self, name: t.Union[str, int]) -> t.Optional[MoveDamageClass]:
        """Fetches a move damage class from the API.

        Parameters
        ----------
        name: t.Union[str, int]
            The id of the move damage class.

        Returns
        -------
        typing.Optional[pokelance.models.MoveDamageClass]
            The move damage class if it exists in the API, else None.

        Raises
        ------
        pokelance.exceptions.ResourceNotFound
            If the move damage class does not exist in the API.

        Examples
        --------

        >>> from pokelance import PokeLance
        >>> import asyncio
        >>> client = PokeLance()
        >>> async def main() -> None:
        ...     damage_class = await client.move.fetch_move_damage_class(1)
        ...     print(damage_class.name)
        ...     await client.close()
        >>> asyncio.run(main())
        status
        """
        route = Endpoint.get_move_damage_class(name)
        self._validate_resource(self.cache.move_damage_class, name, route)
        data = await self._client.request(route)
        return self.cache.move_damage_class.setdefault(route, MoveDamageClass.from_payload(data))

    def get_move_learn_method(self, name: t.Union[str, int]) -> t.Optional[MoveLearnMethod]:
        """Gets a move learn method from the cache.

        Parameters
        ----------
        name: t.Union[str, int]
            The id of the move learn method.

        Returns
        -------
        typing.Optional[pokelance.models.MoveLearnMethod]
            The move learn method if it exists in the cache, else None.

        Raises
        ------
        pokelance.exceptions.ResourceNotFound
            If the move learn method does not exist in the cache.

        Examples
        --------

        >>> from pokelance import PokeLance
        >>> client = PokeLance()
        >>> learn_method = client.move.get_move_learn_method(1)
        >>> learn_method.name
        'level-up'
        """
        route = Endpoint.get_move_learn_method(name)
        self._validate_resource(self.cache.move_learn_method, name, route)
        return self.cache.move_learn_method.get(route, None)

    async def fetch_move_learn_method(self, name: t.Union[str, int]) -> t.Optional[MoveLearnMethod]:
        """Fetches a move learn method from the API.

        Parameters
        ----------
        name: t.Union[str, int]
            The id of the move learn method.

        Returns
        -------
        typing.Optional[pokelance.models.MoveLearnMethod]
            The move learn method if it exists in the API, else None.

        Raises
        ------
        pokelance.exceptions.ResourceNotFound
            If the move learn method does not exist in the API.

        Examples
        --------

        >>> from pokelance import PokeLance
        >>> import asyncio
        >>> client = PokeLance()
        >>> async def main() -> None:
        ...     learn_method = await client.move.fetch_move_learn_method(1)
        ...     print(learn_method.name)
        ...     await client.close()
        >>> asyncio.run(main())
        level-up
        """
        route = Endpoint.get_move_learn_method(name)
        self._validate_resource(self.cache.move_learn_method, name, route)
        data = await self._client.request(route)
        return self.cache.move_learn_method.setdefault(route, MoveLearnMethod.from_payload(data))

    def get_move_target(self, name: t.Union[str, int]) -> t.Optional[MoveTarget]:
        """Gets a move target from the cache.

        Parameters
        ----------
        name: t.Union[str, int]
            The id of the move target.

        Returns
        -------
        typing.Optional[pokelance.models.MoveTarget]
            The move target if it exists in the cache, else None.

        Raises
        ------
        pokelance.exceptions.ResourceNotFound
            If the move target does not exist in the cache.

        Examples
        --------

        >>> from pokelance import PokeLance
        >>> client = PokeLance()
        >>> target = client.move.get_move_target(1)
        >>> target.name
        'specific-pokemon'
        """
        route = Endpoint.get_move_target(name)
        self._validate_resource(self.cache.move_target, name, route)
        return self.cache.move_target.get(route, None)

    async def fetch_move_target(self, name: t.Union[str, int]) -> t.Optional[MoveTarget]:
        """Fetches a move target from the API.

        Parameters
        ----------
        name: t.Union[str, int]
            The id of the move target.

        Returns
        -------
        typing.Optional[pokelance.models.MoveTarget]
            The move target if it exists in the API, else None.

        Raises
        ------
        pokelance.exceptions.ResourceNotFound
            If the move target does not exist in the API.

        Examples
        --------

        >>> from pokelance import PokeLance
        >>> import asyncio
        >>> client = PokeLance()
        >>> async def main() -> None:
        ...     target = await client.move.fetch_move_target(1)
        ...     print(target.name)
        ...     await client.close()
        >>> asyncio.run(main())
        specific-pokemon
        """
        route = Endpoint.get_move_target(name)
        self._validate_resource(self.cache.move_target, name, route)
        data = await self._client.request(route)
        return self.cache.move_target.setdefault(route, MoveTarget.from_payload(data))


def setup(lance: "PokeLance") -> None:
    """Sets up the move cog."""
    lance.add_extension("move", Move(lance.http))
