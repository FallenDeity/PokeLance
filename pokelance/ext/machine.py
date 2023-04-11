import typing as t

from pokelance.http import Endpoint
from pokelance.models import Machine as MachineModel

from ._base import BaseExtension

if t.TYPE_CHECKING:
    from pokelance import PokeLance
    from pokelance.cache import Machine as MachineCache


__all__: t.Tuple[str, ...] = (
    "setup",
    "Machine",
)


class Machine(BaseExtension):
    """Extension for machine related endpoints.

    Attributes
    ----------
    cache: pokelance.cache.Machine
        The cache for this extension.
    """

    cache: "MachineCache"

    def get_machine(self, id_: int) -> t.Optional[MachineModel]:
        """Gets a machine from the cache.

        Parameters
        ----------
        id_: int
            The id of the machine.

        Returns
        -------
        typing.Optional[pokelance.models.Machine]
            The machine if it exists in the cache, else None.

        Raises
        ------
        pokelance.exceptions.ResourceNotFound
            If the machine does not exist in the cache.

        Examples
        --------

        >>> from pokelance import PokeLance
        >>> client = PokeLance()
        >>> machine = client.machine.get_machine(1)
        >>> machine.item.name
        'tm00'
        """
        route = Endpoint.get_machine(id_)
        self._validate_resource(self.cache.machine, id_, route)
        return self.cache.machine.get(route, None)

    async def fetch_machine(self, id_: int) -> t.Optional[MachineModel]:
        """Fetches a machine from the API.

        Parameters
        ----------
        id_: int
            The id of the machine.

        Returns
        -------
        typing.Optional[pokelance.models.Machine]
            The machine if it exists in the API, else None.

        Raises
        ------
        pokelance.exceptions.ResourceNotFound
            If the machine does not exist in the API.

        Examples
        --------

        >>> from pokelance import PokeLance
        >>> import asyncio
        >>> client = PokeLance()
        >>> async def main() -> None:
        ...     machine = await client.machine.fetch_machine(1)
        ...     print(machine.item.name)
        ...     await client.close()
        >>> asyncio.run(main())
        tm00
        """
        route = Endpoint.get_machine(id_)
        self._validate_resource(self.cache.machine, id_, route)
        data = await self._client.request(route)
        return self.cache.machine.setdefault(route, MachineModel.from_payload(data))


def setup(lance: "PokeLance") -> None:
    """Sets up the machine cog."""
    lance.add_extension("machine", Machine(lance.http))
