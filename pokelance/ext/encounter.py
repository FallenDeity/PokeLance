import typing as t

from pokelance.http import Endpoint
from pokelance.models import EncounterCondition, EncounterConditionValue, EncounterMethod

from ._base import BaseExtension

if t.TYPE_CHECKING:
    from pokelance import PokeLance
    from pokelance.http import HttpClient


__all__: t.Tuple[str, ...] = (
    "setup",
    "Encounter",
)


class Encounter(BaseExtension):
    def __init__(self, client: "HttpClient") -> None:
        super().__init__(client)
        self.cache = self._cache.encounter

    async def setup(self) -> None:
        data = await self._client.request(Endpoint.get_encounter_condition_endpoints())
        self._cache.load_documents(str(self.__class__.__name__), "encounter_condition", data["results"])
        data = await self._client.request(Endpoint.get_encounter_method_endpoints())
        self._cache.load_documents(str(self.__class__.__name__), "encounter_method", data["results"])
        data = await self._client.request(Endpoint.get_encounter_condition_value_endpoints())
        self._cache.load_documents(str(self.__class__.__name__), "encounter_condition_value", data["results"])

    def get_encounter_condition(self, name: t.Union[str, int]) -> t.Optional[EncounterCondition]:
        """Gets an encounter condition from the cache.

        Parameters
        ----------
        name: typing.Union[str, int]
            The name or id of the encounter condition.

        Returns
        -------
        typing.Optional[pokelance.models.EncounterCondition]
            The encounter condition if it exists in the cache, else None.

        Raises
        ------
        pokelance.exceptions.ResourceNotFound
            The name or id of the encounter condition is invalid.

        Examples
        --------

        >>> from pokelance import PokeLance
        >>> client = PokeLance()
        >>> condition = client.encounter.get_encounter_condition("swarm")
        >>> condition.name
        'swarm'
        """
        route = Endpoint.get_encounter_condition(name)
        self._validate_resource(self.cache.encounter_condition, name, route)
        return self.cache.encounter_condition.get(route, None)

    async def fetch_encounter_condition(self, name: t.Union[str, int]) -> t.Optional[EncounterCondition]:
        """Fetches an encounter condition from the API.

        Parameters
        ----------
        name: typing.Union[str, int]
            The name or id of the encounter condition.

        Returns
        -------
        typing.Optional[pokelance.models.EncounterCondition]
            The encounter condition if it exists in the API, else None.

        Raises
        ------
        pokelance.exceptions.ResourceNotFound
            The name or id of the encounter condition is invalid.

        Examples
        --------

        >>> from pokelance import PokeLance
        >>> import asyncio
        >>> client = PokeLance()
        >>> async def main() -> None:
        ...     condition = await client.encounter.fetch_encounter_condition("swarm")
        ...     print(condition.name)
        ...     await client.close()
        >>> asyncio.run(main())
        swarm
        """
        route = Endpoint.get_encounter_condition(name)
        self._validate_resource(self.cache.encounter_condition, name, route)
        data = await self._client.request(route)
        return self.cache.encounter_condition.setdefault(route, EncounterCondition.from_payload(data))

    def get_encounter_condition_value(self, name: t.Union[str, int]) -> t.Optional[EncounterConditionValue]:
        """Gets an encounter condition value from the cache.

        Parameters
        ----------
        name: typing.Union[str, int]
            The name or id of the encounter condition value.

        Returns
        -------
        typing.Optional[pokelance.models.EncounterConditionValue]
            The encounter condition value if it exists in the cache, else None.

        Raises
        ------
        pokelance.exceptions.ResourceNotFound
            The name or id of the encounter condition value is invalid.

        Examples
        --------

        >>> from pokelance import PokeLance
        >>> client = PokeLance()
        >>> condition = client.encounter.get_encounter_condition_value("swarm-yes")
        >>> condition.name
        'swarm-yes'
        """
        route = Endpoint.get_encounter_condition_value(name)
        self._validate_resource(self.cache.encounter_condition_value, name, route)
        return self.cache.encounter_condition_value.get(route, None)

    async def fetch_encounter_condition_value(self, name: t.Union[str, int]) -> t.Optional[EncounterConditionValue]:
        """Fetches an encounter condition value from the API.

        Parameters
        ----------
        name: typing.Union[str, int]
            The name or id of the encounter condition value.

        Returns
        -------
        typing.Optional[pokelance.models.EncounterConditionValue]
            The encounter condition value if it exists in the API, else None.

        Raises
        ------
        pokelance.exceptions.ResourceNotFound
            The name or id of the encounter condition value is invalid.

        Examples
        --------

        >>> from pokelance import PokeLance
        >>> import asyncio
        >>> client = PokeLance()
        >>> async def main() -> None:
        ...     condition = await client.encounter.fetch_encounter_condition_value("swarm-yes")
        ...     print(condition.name)
        ...     await client.close()
        >>> asyncio.run(main())
        swarm-yes
        """
        route = Endpoint.get_encounter_condition_value(name)
        self._validate_resource(self.cache.encounter_condition_value, name, route)
        data = await self._client.request(route)
        return self.cache.encounter_condition_value.setdefault(route, EncounterConditionValue.from_payload(data))

    def get_encounter_method(self, name: t.Union[str, int]) -> t.Optional[EncounterMethod]:
        """Gets an encounter method from the cache.

        Parameters
        ----------
        name: typing.Union[str, int]
            The name or id of the encounter method.

        Returns
        -------
        typing.Optional[pokelance.models.EncounterMethod]
            The encounter method if it exists in the cache, else None.

        Raises
        ------
        pokelance.exceptions.ResourceNotFound
            The name or id of the encounter method is invalid.

        Examples
        --------

        >>> from pokelance import PokeLance
        >>> client = PokeLance()
        >>> method = client.encounter.get_encounter_method("walk")
        >>> method.name
        'walk'
        """
        route = Endpoint.get_encounter_method(name)
        self._validate_resource(self.cache.encounter_method, name, route)
        return self.cache.encounter_method.get(route, None)

    async def fetch_encounter_method(self, name: t.Union[str, int]) -> t.Optional[EncounterMethod]:
        """Fetches an encounter method from the API.

        Parameters
        ----------
        name: typing.Union[str, int]
            The name or id of the encounter method.

        Returns
        -------
        typing.Optional[pokelance.models.EncounterMethod]
            The encounter method if it exists in the API, else None.

        Raises
        ------
        pokelance.exceptions.ResourceNotFound
            The name or id of the encounter method is invalid.

        Examples
        --------

        >>> from pokelance import PokeLance
        >>> import asyncio
        >>> client = PokeLance()
        >>> async def main() -> None:
        ...     method = await client.encounter.fetch_encounter_method("walk")
        ...     print(method.name)
        ...     await client.close()
        >>> asyncio.run(main())
        walk
        """
        route = Endpoint.get_encounter_method(name)
        self._validate_resource(self.cache.encounter_method, name, route)
        data = await self._client.request(route)
        return self.cache.encounter_method.setdefault(route, EncounterMethod.from_payload(data))


async def setup(lance: "PokeLance") -> None:
    """Sets up the encounter cog."""
    await lance.add_extension("encounter", Encounter(lance.http))