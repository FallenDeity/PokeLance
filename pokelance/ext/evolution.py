import typing as t

from pokelance.http import Endpoint
from pokelance.models import EvolutionChain, EvolutionTrigger

from ._base import BaseExtension

if t.TYPE_CHECKING:
    from pokelance import PokeLance
    from pokelance.cache import Evolution as EvolutionCache


__all__: t.Tuple[str, ...] = (
    "setup",
    "Evolution",
)


class Evolution(BaseExtension):
    """
    Extension for evolution related endpoints.

    Attributes
    ----------
    cache: pokelance.cache.Evolution
        The cache for this extension.
    """

    cache: "EvolutionCache"

    def get_evolution_chain(self, id_: int) -> t.Optional[EvolutionChain]:
        """Gets an evolution chain from the cache.

        Parameters
        ----------
        id_: int
            The name or id of the encounter method.

        Returns
        -------
        typing.Optional[pokelance.models.EvolutionChain]
            The evolution chain if it exists in the cache, else None.

        Raises
        ------
        pokelance.exceptions.ResourceNotFound
            The name or id of the evolution chain is invalid.

        Examples
        --------

        >>> from pokelance import PokeLance
        >>> client = PokeLance()
        >>> chain = client.evolution.get_evolution_chain(1)
        >>> chain.id
        1
        """
        route = Endpoint.get_evolution_chain(id_)
        self._validate_resource(self.cache.evolution_chain, id_, route)
        return self.cache.evolution_chain.get(route, None)

    async def fetch_evolution_chain(self, id_: int) -> t.Optional[EvolutionChain]:
        """Fetches an evolution chain from the API.

        Parameters
        ----------
        id_: int
            The name or id of the encounter method.

        Returns
        -------
        t.Optional[pokelance.models.EvolutionChain]
            The evolution chain.

        Raises
        ------
        pokelance.exceptions.ResourceNotFound
            The name or id of the evolution chain is invalid.

        Examples
        --------

        >>> from pokelance import PokeLance
        >>> import asyncio
        >>> client = PokeLance()
        >>> async def main() -> None:
        ...     chain = await client.evolution.fetch_evolution_chain(1)
        ...     print(chain.id)
        ...     await client.close()
        >>> asyncio.run(main())
        1
        """
        route = Endpoint.get_evolution_chain(id_)
        self._validate_resource(self.cache.evolution_chain, id_, route)
        data = await self._client.request(route)
        return self.cache.evolution_chain.setdefault(route, EvolutionChain.from_payload(data))

    def get_evolution_trigger(self, name: t.Union[str, int]) -> t.Optional[EvolutionTrigger]:
        """Gets an evolution trigger from the cache.

        Parameters
        ----------
        name: typing.Union[str, int]
            The name or id of the encounter method.

        Returns
        -------
        typing.Optional[pokelance.models.EvolutionTrigger]
            The evolution trigger if it exists in the cache, else None.

        Raises
        ------
        pokelance.exceptions.ResourceNotFound
            The name or id of the evolution trigger is invalid.

        Examples
        --------

        >>> from pokelance import PokeLance
        >>> client = PokeLance()
        >>> trigger = client.evolution.get_evolution_trigger(1)
        >>> trigger.name
        'level-up'
        """
        route = Endpoint.get_evolution_trigger(name)
        self._validate_resource(self.cache.evolution_trigger, name, route)
        return self.cache.evolution_trigger.get(route, None)

    async def fetch_evolution_trigger(self, name: t.Union[str, int]) -> t.Optional[EvolutionTrigger]:
        """Fetches an evolution trigger from the API.

        Parameters
        ----------
        name: typing.Union[str, int]
            The name or id of the encounter method.

        Returns
        -------
        t.Optional[pokelance.models.EvolutionTrigger]
            The evolution trigger.

        Raises
        ------
        pokelance.exceptions.ResourceNotFound
            The name or id of the evolution trigger is invalid.

        Examples
        --------

        >>> from pokelance import PokeLance
        >>> import asyncio
        >>> client = PokeLance()
        >>> async def main() -> None:
        ...     trigger = await client.evolution.fetch_evolution_trigger(1)
        ...     print(trigger.name)
        ...     await client.close()
        >>> asyncio.run(main())
        level-up
        """
        route = Endpoint.get_evolution_trigger(name)
        self._validate_resource(self.cache.evolution_trigger, name, route)
        data = await self._client.request(route)
        return self.cache.evolution_trigger.setdefault(route, EvolutionTrigger.from_payload(data))


def setup(lance: "PokeLance") -> None:
    """Sets up the evolution cog."""
    lance.add_extension("evolution", Evolution(lance.http))
