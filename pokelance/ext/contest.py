import typing as t

from pokelance.http import Endpoint
from pokelance.models import ContestEffect, ContestType, SuperContestEffect

from ._base import BaseExtension

if t.TYPE_CHECKING:
    from pokelance import PokeLance
    from pokelance.cache import Contest as ContestCache


__all__: t.Tuple[str, ...] = (
    "setup",
    "Contest",
)


class Contest(BaseExtension):
    """
    Extension for contest related endpoints.

    Attributes
    ----------
    cache: pokelance.cache.Contest
        The cache for this extension.
    """

    cache: "ContestCache"

    def get_contest_type(self, name: t.Union[str, int]) -> t.Optional[ContestType]:
        """Gets a contest type from the cache.

        Parameters
        ----------
        name: typing.Union[str, int]
            The name or id of the contest type.

        Returns
        -------
        typing.Optional[pokelance.models.ContestType]
            The contest type if it exists in the cache, else None.

        Raises
        ------
        pokelance.exceptions.ResourceNotFound
            The name or id of the contest type is invalid.

        Examples
        --------

        >>> from pokelance import PokeLance
        >>> client = PokeLance()
        >>> type_ = client.contest.get_contest_type("cool")  # None if not cached
        >>> type_.name
        'cool'
        """
        route = Endpoint.get_contest_type(name)
        self._validate_resource(self.cache.contest_type, name, route)
        return self.cache.contest_type.get(route, None)

    async def fetch_contest_type(self, name: t.Union[str, int]) -> t.Optional[ContestType]:
        """Fetches a contest type from the API.

        Parameters
        ----------
        name: typing.Union[str, int]
            The name or id of the contest type.

        Returns
        -------
        typing.Optional[pokelance.models.ContestType]
            The contest type if it exists in the API, else None.

        Raises
        ------
        pokelance.exceptions.ResourceNotFound
            The name or id of the contest type is invalid.

        Examples
        --------

        >>> from pokelance import PokeLance
        >>> import asyncio
        >>> client = PokeLance()
        >>> async def main() -> None:
        ...     type_ = await client.contest.fetch_contest_type("cool")
        ...     print(type_.name)
        ...     await client.close()
        >>> asyncio.run(main())
        cool
        """
        route = Endpoint.get_contest_type(name)
        self._validate_resource(self.cache.contest_type, name, route)
        data = await self._client.request(route)
        return self.cache.contest_type.setdefault(route, ContestType.from_payload(data))

    def get_contest_effect(self, id_: int) -> t.Optional[ContestEffect]:
        """Gets a contest effect from the cache.

        Parameters
        ----------
        id_: int
            The name or id of the contest effect.

        Returns
        -------
        typing.Optional[pokelance.models.ContestEffect]
            The contest effect if it exists in the cache, else None.

        Raises
        ------
        pokelance.exceptions.ResourceNotFound
            The name or id of the contest effect is invalid.

        Examples
        --------

        >>> from pokelance import PokeLance
        >>> client = PokeLance()
        >>> effect = client.contest.get_contest_effect(1)  # None if not cached
        >>> effect.appeal
        4
        """
        route = Endpoint.get_contest_effect(id_)
        self._validate_resource(self.cache.contest_effect, id_, route)
        return self.cache.contest_effect.get(route, None)

    async def fetch_contest_effect(self, id_: int) -> t.Optional[ContestEffect]:
        """Fetches a contest effect from the API.

        Parameters
        ----------
        id_: int
            The name or id of the contest effect.

        Returns
        -------
        typing.Optional[pokelance.models.ContestEffect]
            The contest effect if it exists in the API, else None.

        Raises
        ------
        pokelance.exceptions.ResourceNotFound
            The name or id of the contest effect is invalid.

        Examples
        --------

        >>> from pokelance import PokeLance
        >>> import asyncio
        >>> client = PokeLance()
        >>> async def main() -> None:
        ...     effect = await client.contest.fetch_contest_effect(1)
        ...     print(effect.appeal)
        ...     await client.close()
        >>> asyncio.run(main())
        4
        """
        route = Endpoint.get_contest_effect(id_)
        self._validate_resource(self.cache.contest_effect, id_, route)
        data = await self._client.request(route)
        return self.cache.contest_effect.setdefault(route, ContestEffect.from_payload(data))

    def get_super_contest_effect(self, id_: int) -> t.Optional[SuperContestEffect]:
        """Gets a super contest effect from the cache.

        Parameters
        ----------
        id_: int
            The name or id of the super contest effect.

        Returns
        -------
        typing.Optional[pokelance.models.SuperContestEffect]
            The super contest effect if it exists in the cache, else None.

        Raises
        ------
        pokelance.exceptions.ResourceNotFound
            The name or id of the super contest effect is invalid.

        Examples
        --------

        >>> from pokelance import PokeLance
        >>> client = PokeLance()
        >>> effect = client.contest.get_super_contest_effect(1)
        >>> effect.appeal
        2
        """
        route = Endpoint.get_super_contest_effect(id_)
        self._validate_resource(self.cache.super_contest_effect, id_, route)
        return self.cache.super_contest_effect.get(route, None)

    async def fetch_super_contest_effect(self, id_: int) -> t.Optional[SuperContestEffect]:
        """Fetches a super contest effect from the API.

        Parameters
        ----------
        id_: int
            The name or id of the super contest effect.

        Returns
        -------
        typing.Optional[pokelance.models.SuperContestEffect]
            The super contest effect if it exists in the API, else None.

        Raises
        ------
        pokelance.exceptions.ResourceNotFound
            The name or id of the super contest effect is invalid.

        Examples
        --------

        >>> from pokelance import PokeLance
        >>> import asyncio
        >>> client = PokeLance()
        >>> async def main() -> None:
        ...     effect = await client.contest.fetch_super_contest_effect(1)
        ...     print(effect.appeal)
        ...     await client.close()
        >>> asyncio.run(main())
        2
        """
        route = Endpoint.get_super_contest_effect(id_)
        self._validate_resource(self.cache.super_contest_effect, id_, route)
        data = await self._client.request(route)
        return self.cache.super_contest_effect.setdefault(route, SuperContestEffect.from_payload(data))


def setup(lance: "PokeLance") -> None:
    """Sets up the contest cog."""
    lance.add_extension("contest", Contest(lance.http))
