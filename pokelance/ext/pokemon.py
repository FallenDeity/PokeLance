import typing as t

from pokelance.http import Endpoint
from pokelance.models import (
    Ability,
    Characteristic,
    EggGroup,
    Gender,
    GrowthRate,
    LocationAreaEncounter,
    Nature,
    PokeathlonStat,
)
from pokelance.models import Pokemon as PokemonModel
from pokelance.models import PokemonColor, PokemonForm, PokemonHabitats, PokemonShape, PokemonSpecies, Stat, Type

from ._base import BaseExtension

if t.TYPE_CHECKING:
    from pokelance import PokeLance
    from pokelance.cache import Pokemon as PokemonCache


__all__: t.Tuple[str, ...] = (
    "setup",
    "Pokemon",
)


class Pokemon(BaseExtension):
    """Extension for pokemon related endpoints.

    Attributes
    ----------
    cache: pokelance.cache.Pokemon
        The cache for this extension.
    """

    cache: "PokemonCache"

    def get_ability(self, name: t.Union[str, int]) -> t.Optional[Ability]:
        """Get an ability by name or id.

        Parameters
        ----------
        name: Union[str, int]
            The name or id of the ability.

        Returns
        -------
        Optional[Ability]
            The ability if found, else None.

        Raises
        ------
        pokelance.exceptions.ResourceNotFound
            If the ability was not found.

        Examples
        --------

        >>> from pokelance import PokeLance
        >>> client = PokeLance()
        >>> ability = client.pokemon.get_ability("stench")
        >>> ability.id
        1
        """
        route = Endpoint.get_ability(name)
        self._validate_resource(self.cache.ability, name, route)
        return self.cache.ability.get(route, None)

    async def fetch_ability(self, name: t.Union[str, int]) -> t.Optional[Ability]:
        """Fetch an ability by name or id.

        Parameters
        ----------
        name: Union[str, int]
            The name or id of the ability.

        Returns
        -------
        Optional[Ability]
            The ability if found, else None.

        Raises
        ------
        pokelance.exceptions.ResourceNotFound
            If the ability was not found.

        Examples
        --------

        >>> from pokelance import PokeLance
        >>> import asyncio
        >>> client = PokeLance()
        >>> async def main() -> None:
        ...     ability = await client.pokemon.fetch_ability("stench")
        ...     print(ability.id)
        ...     await client.close()
        >>> asyncio.run(main())
        1
        """
        route = Endpoint.get_ability(name)
        self._validate_resource(self.cache.ability, name, route)
        data = await self._client.request(route)
        return self.cache.ability.setdefault(route, Ability.from_payload(data))

    def get_characteristic(self, id_: int) -> t.Optional[Characteristic]:
        """Get a characteristic by id.

        Parameters
        ----------
        id_: int
            The id of the characteristic.

        Returns
        -------
        Optional[Characteristic]
            The characteristic if found, else None.

        Raises
        ------
        pokelance.exceptions.ResourceNotFound
            If the characteristic was not found.

        Examples
        --------

        >>> from pokelance import PokeLance
        >>> client = PokeLance()
        >>> characteristic = client.pokemon.get_characteristic(1)
        >>> characteristic.gene_modulo
        0
        """
        route = Endpoint.get_characteristic(id_)
        self._validate_resource(self.cache.characteristic, id_, route)
        return self.cache.characteristic.get(route, None)

    async def fetch_characteristic(self, id_: int) -> t.Optional[Characteristic]:
        """Fetch a characteristic by id.

        Parameters
        ----------
        id_: int
            The id of the characteristic.

        Returns
        -------
        Optional[Characteristic]
            The characteristic if found, else None.

        Raises
        ------
        pokelance.exceptions.ResourceNotFound
            If the characteristic was not found.

        Examples
        --------

        >>> from pokelance import PokeLance
        >>> import asyncio
        >>> client = PokeLance()
        >>> async def main() -> None:
        ...     characteristic = await client.pokemon.fetch_characteristic(1)
        ...     print(characteristic.gene_modulo)
        ...     await client.close()
        >>> asyncio.run(main())
        0
        """
        route = Endpoint.get_characteristic(id_)
        self._validate_resource(self.cache.characteristic, id_, route)
        data = await self._client.request(route)
        return self.cache.characteristic.setdefault(route, Characteristic.from_payload(data))

    def get_egg_group(self, name: t.Union[str, int]) -> t.Optional[EggGroup]:
        """Get an egg group by name or id.

        Parameters
        ----------
        name: Union[str, int]
            The name or id of the egg group.

        Returns
        -------
        Optional[EggGroup]
            The egg group if found, else None.

        Raises
        ------
        pokelance.exceptions.ResourceNotFound
            If the egg group was not found.

        Examples
        --------

        >>> from pokelance import PokeLance
        >>> client = PokeLance()
        >>> egg_group = client.pokemon.get_egg_group("monster")
        >>> egg_group.id
        1
        """
        route = Endpoint.get_egg_group(name)
        self._validate_resource(self.cache.egg_group, name, route)
        return self.cache.egg_group.get(route, None)

    async def fetch_egg_group(self, name: t.Union[str, int]) -> t.Optional[EggGroup]:
        """Fetch an egg group by name or id.

        Parameters
        ----------
        name: Union[str, int]
            The name or id of the egg group.

        Returns
        -------
        Optional[EggGroup]
            The egg group if found, else None.

        Raises
        ------
        pokelance.exceptions.ResourceNotFound
            If the egg group was not found.

        Examples
        --------

        >>> from pokelance import PokeLance
        >>> import asyncio
        >>> client = PokeLance()
        >>> async def main() -> None:
        ...     egg_group = await client.pokemon.fetch_egg_group("monster")
        ...     print(egg_group.id)
        ...     await client.close()
        >>> asyncio.run(main())
        1
        """
        route = Endpoint.get_egg_group(name)
        self._validate_resource(self.cache.egg_group, name, route)
        data = await self._client.request(route)
        return self.cache.egg_group.setdefault(route, EggGroup.from_payload(data))

    def get_gender(self, name: t.Union[str, int]) -> t.Optional[Gender]:
        """
        Get gender from cache.

        Parameters
        ----------
        name: Union[str, int]
            The name or id of the gender.

        Returns
        -------
        t.Optional[Gender]
            Gender model if found, else None.

        Raises
        ------
        pokelance.exceptions.ResourceNotFound
            if gender was not found.

        Examples
        --------

        >>> from pokelance import PokeLance
        >>> client = PokeLance()
        >>> gender = client.pokemon.get_gender(1)
        >>> gender.name
        'female'
        """
        route = Endpoint.get_gender(name)
        self._validate_resource(self.cache.gender, name, route)
        return self.cache.gender.get(route, None)

    async def fetch_gender(self, name: t.Union[str, int]) -> t.Optional[Gender]:
        """
        Fetches a gender model by name or id.

        Parameters
        ----------
        name: Union[str, int]
            The name or id of the

        Returns
        -------
        t.Optional[Gender]
            Gender model if found, else None.

        Raises
        ------
        pokelance.exceptions.ResourceNotFound
            if gender was not found.

        Examples
        --------

        >>> from pokelance import PokeLance
        >>> import asyncio
        >>> client = PokeLance()
        >>> async def main() -> None:
        ...    gender = await client.pokemon.fetch_gender(1)
        ...    print(gender.name)
        ...    await client.close()
        >>> asyncio.run(main())
        female
        """
        route = Endpoint.get_gender(name)
        self._validate_resource(self.cache.gender, name, route)
        data = await self._client.request(route)
        return self.cache.gender.setdefault(route, Gender.from_payload(data))

    def get_growth_rate(self, name: t.Union[str, int]) -> t.Optional[GrowthRate]:
        """
        Get growth rate from cache.

        Parameters
        ----------
        name: Union[str, int]
            The name or id of the growth rate.

        Returns
        -------
        t.Optional[GrowthRate]
            Growth rate model if found, else None.

        Raises
        ------
        pokelance.exceptions.ResourceNotFound
            if growth rate was not found.

        Examples
        --------

        >>> from pokelance import PokeLance
        >>> client = PokeLance()
        >>> growth_rate = client.pokemon.get_growth_rate(1)
        >>> growth_rate.name
        'slow'
        """
        route = Endpoint.get_growth_rate(name)
        self._validate_resource(self.cache.growth_rate, name, route)
        return self.cache.growth_rate.get(route, None)

    async def fetch_growth_rate(self, name: t.Union[str, int]) -> t.Optional[GrowthRate]:
        """
        Fetches a growth rate model by name or id.

        Parameters
        ----------
        name: Union[str, int]
            The name or id of the

        Returns
        -------
        t.Optional[GrowthRate]
            Growth rate model if found, else None.

        Raises
        ------
        pokelance.exceptions.ResourceNotFound
            if growth rate was not found.

        Examples
        --------

        >>> from pokelance import PokeLance
        >>> import asyncio
        >>> client = PokeLance()
        >>> async def main() -> None:
        ...    growth_rate = await client.pokemon.fetch_growth_rate(1)
        ...    print(growth_rate.name)
        ...    await client.close()
        >>> asyncio.run(main())
        slow
        """
        route = Endpoint.get_growth_rate(name)
        self._validate_resource(self.cache.growth_rate, name, route)
        data = await self._client.request(route)
        return self.cache.growth_rate.setdefault(route, GrowthRate.from_payload(data))

    def get_nature(self, name: t.Union[str, int]) -> t.Optional[Nature]:
        """
        Get nature from cache.

        Parameters
        ----------
        name: Union[str, int]
            The name or id of the nature.

        Returns
        -------
        t.Optional[Nature]
            Nature model if found, else None.

        Raises
        ------
        pokelance.exceptions.ResourceNotFound
            if nature was not found.

        Examples
        --------

        >>> from pokelance import PokeLance
        >>> client = PokeLance()
        >>> nature = client.pokemon.get_nature(1)
        >>> nature.name
        'hardy'
        """
        route = Endpoint.get_nature(name)
        self._validate_resource(self.cache.nature, name, route)
        return self.cache.nature.get(route, None)

    async def fetch_nature(self, name: t.Union[str, int]) -> t.Optional[Nature]:
        """
        Fetches a nature model by name or id.

        Parameters
        ----------
        name: Union[str, int]
            The name or id of the

        Returns
        -------
        t.Optional[Nature]
            Nature model if found, else None.

        Raises
        ------
        pokelance.exceptions.ResourceNotFound
            if nature was not found.

        Examples
        --------

        >>> from pokelance import PokeLance
        >>> import asyncio
        >>> client = PokeLance()
        >>> async def main() -> None:
        ...    nature = await client.pokemon.fetch_nature(1)
        ...    print(nature.name)
        ...    await client.close()
        >>> asyncio.run(main())
        hardy
        """
        route = Endpoint.get_nature(name)
        self._validate_resource(self.cache.nature, name, route)
        data = await self._client.request(route)
        return self.cache.nature.setdefault(route, Nature.from_payload(data))

    def get_pokeathlon_stat(self, name: t.Union[str, int]) -> t.Optional[PokeathlonStat]:
        """
        Get pokeathlon stat from cache.

        Parameters
        ----------
        name: Union[str, int]
            The name or id of the pokeathlon stat.

        Returns
        -------
        t.Optional[PokeathlonStat]
            Pokeathlon stat model if found, else None.

        Raises
        ------
        pokelance.exceptions.ResourceNotFound
            if pokeathlon stat was not found.

        Examples
        --------

        >>> from pokelance import PokeLance
        >>> client = PokeLance()
        >>> pokeathlon_stat = client.pokemon.get_pokeathlon_stat(1)
        >>> pokeathlon_stat.name
        'speed'
        """
        route = Endpoint.get_pokeathlon_stat(name)
        self._validate_resource(self.cache.pokeathlon_stat, name, route)
        return self.cache.pokeathlon_stat.get(route, None)

    async def fetch_pokeathlon_stat(self, name: t.Union[str, int]) -> t.Optional[PokeathlonStat]:
        """
        Fetches a pokeathlon stat model by name or id.

        Parameters
        ----------
        name: Union[str, int]
            The name or id of the

        Returns
        -------
        t.Optional[PokeathlonStat]
            Pokeathlon stat model if found, else None.

        Raises
        ------
        pokelance.exceptions.ResourceNotFound
            if pokeathlon stat was not found.

        Examples
        --------

        >>> from pokelance import PokeLance
        >>> import asyncio
        >>> client = PokeLance()
        >>> async def main() -> None:
        ...    pokeathlon_stat = await client.pokemon.fetch_pokeathlon_stat(1)
        ...    print(pokeathlon_stat.name)
        ...    await client.close()
        >>> asyncio.run(main())
        speed
        """
        route = Endpoint.get_pokeathlon_stat(name)
        self._validate_resource(self.cache.pokeathlon_stat, name, route)
        data = await self._client.request(route)
        return self.cache.pokeathlon_stat.setdefault(route, PokeathlonStat.from_payload(data))

    def get_location_area_encounter(self, name: t.Union[str, int]) -> t.Optional[LocationAreaEncounter]:
        """
        Get location area encounter from cache.
        It gets areas where a pokemon can be found.

        Parameters
        ----------
        name: Union[str, int]
            The name or id of the location area encounter.

        Returns
        -------
        t.Optional[LocationAreaEncounter]
            Location area encounter model if found, else None.

        Raises
        ------
        pokelance.exceptions.ResourceNotFound
            if location area encounter was not found.

        Examples
        --------

        >>> from pokelance import PokeLance
        >>> client = PokeLance()
        >>> location_area_encounter = client.pokemon.get_location_area_encounter(1)
        >>> location_area_encounter.location_area.name
        'cerulean-city-area'
        """
        route = Endpoint.get_location_area_encounter(name)
        self._validate_resource(self.cache.location_area_encounter, name, route)
        return self.cache.location_area_encounter.get(route, None)

    async def fetch_location_area_encounter(self, name: t.Union[str, int]) -> t.Optional[LocationAreaEncounter]:
        """
        Fetches a location area encounter model by name or id.

        Parameters
        ----------
        name: Union[str, int]
            The name or id of the

        Returns
        -------
        t.Optional[LocationAreaEncounter]
            Location area encounter model if found, else None.

        Raises
        ------
        pokelance.exceptions.ResourceNotFound
            if location area encounter was not found.

        Examples
        --------

        >>> from pokelance import PokeLance
        >>> import asyncio
        >>> client = PokeLance()
        >>> async def main() -> None:
        ...    location_area_encounter = await client.pokemon.fetch_location_area_encounter(1)
        ...    print(location_area_encounter.location_area.name)
        ...    await client.close()
        >>> asyncio.run(main())
        cerulean-city-area
        """
        route = Endpoint.get_location_area_encounter(name)
        self._validate_resource(self.cache.location_area_encounter, name, route)
        data = await self._client.request(route)
        return self.cache.location_area_encounter.setdefault(route, LocationAreaEncounter.from_payload(data[0]))

    def get_pokemon(self, name: t.Union[str, int]) -> t.Optional[PokemonModel]:
        """
        Get pokemon from cache.

        Parameters
        ----------
        name: Union[str, int]
            The name or id of the pokemon.

        Returns
        -------
        t.Optional[PokemonModel]
            Pokemon model if found, else None.

        Raises
        ------
        pokelance.exceptions.ResourceNotFound
            if pokemon was not found.

        Examples
        --------

        >>> from pokelance import PokeLance
        >>> client = PokeLance()
        >>> pokemon = client.pokemon.get_pokemon(1)
        >>> pokemon.name
        'bulbasaur'
        """
        route = Endpoint.get_pokemon(name)
        self._validate_resource(self.cache.pokemon, name, route)
        return self.cache.pokemon.get(route, None)

    async def fetch_pokemon(self, name: t.Union[str, int]) -> t.Optional[PokemonModel]:
        """
        Fetches a pokemon model by name or id.

        Parameters
        ----------
        name: Union[str, int]
            The name or id of the

        Returns
        -------
        t.Optional[PokemonModel]
            Pokemon model if found, else None.

        Raises
        ------
        pokelance.exceptions.ResourceNotFound
            if pokemon was not found.

        Examples
        --------

        >>> from pokelance import PokeLance
        >>> import asyncio
        >>> client = PokeLance()
        >>> async def main() -> None:
        ...    pokemon = await client.pokemon.fetch_pokemon(1)
        ...    print(pokemon.name)
        ...    await client.close()
        >>> asyncio.run(main())
        bulbasaur
        """
        route = Endpoint.get_pokemon(name)
        self._validate_resource(self.cache.pokemon, name, route)
        data = await self._client.request(route)
        return self.cache.pokemon.setdefault(route, PokemonModel.from_payload(data))

    def get_pokemon_color(self, name: t.Union[str, int]) -> t.Optional[PokemonColor]:
        """
        Get pokemon color from cache.

        Parameters
        ----------
        name: Union[str, int]
            The name or id of the pokemon color.

        Returns
        -------
        t.Optional[PokemonColor]
            Pokemon color model if found, else None.

        Raises
        ------
        pokelance.exceptions.ResourceNotFound
            if pokemon color was not found.

        Examples
        --------

        >>> from pokelance import PokeLance
        >>> client = PokeLance()
        >>> pokemon_color = client.pokemon.get_pokemon_color(1)
        >>> pokemon_color.name
        'black'
        """
        route = Endpoint.get_pokemon_color(name)
        self._validate_resource(self.cache.pokemon_color, name, route)
        return self.cache.pokemon_color.get(route, None)

    async def fetch_pokemon_color(self, name: t.Union[str, int]) -> t.Optional[PokemonColor]:
        """
        Fetches a pokemon color model by name or id.

        Parameters
        ----------
        name: Union[str, int]
            The name or id of the

        Returns
        -------
        t.Optional[PokemonColor]
            Pokemon color model if found, else None.

        Raises
        ------
        pokelance.exceptions.ResourceNotFound
            if pokemon color was not found.

        Examples
        --------

        >>> from pokelance import PokeLance
        >>> import asyncio
        >>> client = PokeLance()
        >>> async def main() -> None:
        ...    pokemon_color = await client.pokemon.fetch_pokemon_color(1)
        ...    print(pokemon_color.name)
        ...    await client.close()
        >>> asyncio.run(main())
        black
        """
        route = Endpoint.get_pokemon_color(name)
        self._validate_resource(self.cache.pokemon_color, name, route)
        data = await self._client.request(route)
        return self.cache.pokemon_color.setdefault(route, PokemonColor.from_payload(data))

    def get_pokemon_form(self, name: t.Union[str, int]) -> t.Optional[PokemonForm]:
        """
        Get pokemon form from cache.

        Parameters
        ----------
        name: Union[str, int]
            The name or id of the pokemon form.

        Returns
        -------
        t.Optional[PokemonForm]
            Pokemon form model if found, else None.

        Raises
        ------
        pokelance.exceptions.ResourceNotFound
            if pokemon form was not found.

        Examples
        --------

        >>> from pokelance import PokeLance
        >>> client = PokeLance()
        >>> pokemon_form = client.pokemon.get_pokemon_form(1)
        >>> pokemon_form.name
        'bulbasaur'
        """
        route = Endpoint.get_pokemon_form(name)
        self._validate_resource(self.cache.pokemon_form, name, route)
        return self.cache.pokemon_form.get(route, None)

    async def fetch_pokemon_form(self, name: t.Union[str, int]) -> t.Optional[PokemonForm]:
        """
        Fetches a pokemon form model by name or id.

        Parameters
        ----------
        name: Union[str, int]
            The name or id of the

        Returns
        -------
        t.Optional[PokemonForm]
            Pokemon form model if found, else None.

        Raises
        ------
        pokelance.exceptions.ResourceNotFound
            if pokemon form was not found.

        Examples
        --------

        >>> from pokelance import PokeLance
        >>> import asyncio
        >>> client = PokeLance()
        >>> async def main() -> None:
        ...    pokemon_form = await client.pokemon.fetch_pokemon_form(1)
        ...    print(pokemon_form.name)
        ...    await client.close()
        >>> asyncio.run(main())
        bulbasaur
        """
        route = Endpoint.get_pokemon_form(name)
        self._validate_resource(self.cache.pokemon_form, name, route)
        data = await self._client.request(route)
        return self.cache.pokemon_form.setdefault(route, PokemonForm.from_payload(data))

    def get_pokemon_habitat(self, name: t.Union[str, int]) -> t.Optional[PokemonHabitats]:
        """
        Get pokemon habitat from cache.

        Parameters
        ----------
        name: Union[str, int]
            The name or id of the pokemon habitat.

        Returns
        -------
        t.Optional[PokemonHabitats]
            Pokemon habitat model if found, else None.

        Raises
        ------
        pokelance.exceptions.ResourceNotFound
            if pokemon habitat was not found.

        Examples
        --------

        >>> from pokelance import PokeLance
        >>> client = PokeLance()
        >>> pokemon_habitat = client.pokemon.get_pokemon_habitat(1)
        >>> pokemon_habitat.name
        'cave'
        """
        route = Endpoint.get_pokemon_habitat(name)
        self._validate_resource(self.cache.pokemon_habitat, name, route)
        return self.cache.pokemon_habitat.get(route, None)

    async def fetch_pokemon_habitat(self, name: t.Union[str, int]) -> t.Optional[PokemonHabitats]:
        """
        Fetches a pokemon habitat model by name or id.

        Parameters
        ----------
        name: Union[str, int]
            The name or id of the

        Returns
        -------
        t.Optional[PokemonHabitats]
            Pokemon habitat model if found, else None.

        Raises
        ------
        pokelance.exceptions.ResourceNotFound
            if pokemon habitat was not found.

        Examples
        --------

        >>> from pokelance import PokeLance
        >>> import asyncio
        >>> client = PokeLance()
        >>> async def main() -> None:
        ...    pokemon_habitat = await client.pokemon.fetch_pokemon_habitat(1)
        ...    print(pokemon_habitat.name)
        ...    await client.close()
        >>> asyncio.run(main())
        cave
        """
        route = Endpoint.get_pokemon_habitat(name)
        self._validate_resource(self.cache.pokemon_habitat, name, route)
        data = await self._client.request(route)
        return self.cache.pokemon_habitat.setdefault(route, PokemonHabitats.from_payload(data))

    def get_pokemon_shape(self, name: t.Union[str, int]) -> t.Optional[PokemonShape]:
        """
        Get pokemon shape from cache.

        Parameters
        ----------
        name: Union[str, int]
            The name or id of the pokemon shape.

        Returns
        -------
        t.Optional[PokemonShape]
            Pokemon shape model if found, else None.

        Raises
        ------
        pokelance.exceptions.ResourceNotFound
            if pokemon shape was not found.

        Examples
        --------

        >>> from pokelance import PokeLance
        >>> client = PokeLance()
        >>> pokemon_shape = client.pokemon.get_pokemon_shape(1)
        >>> pokemon_shape.name
        'ball'
        """
        route = Endpoint.get_pokemon_shape(name)
        self._validate_resource(self.cache.pokemon_shape, name, route)
        return self.cache.pokemon_shape.get(route, None)

    async def fetch_pokemon_shape(self, name: t.Union[str, int]) -> t.Optional[PokemonShape]:
        """
        Fetches a pokemon shape model by name or id.

        Parameters
        ----------
        name: Union[str, int]
            The name or id of the

        Returns
        -------
        t.Optional[PokemonShape]
            Pokemon shape model if found, else None.

        Raises
        ------
        pokelance.exceptions.ResourceNotFound
            if pokemon shape was not found.

        Examples
        --------

        >>> from pokelance import PokeLance
        >>> import asyncio
        >>> client = PokeLance()
        >>> async def main() -> None:
        ...    pokemon_shape = await client.pokemon.fetch_pokemon_shape(1)
        ...    print(pokemon_shape.name)
        ...    await client.close()
        >>> asyncio.run(main())
        ball
        """
        route = Endpoint.get_pokemon_shape(name)
        self._validate_resource(self.cache.pokemon_shape, name, route)
        data = await self._client.request(route)
        return self.cache.pokemon_shape.setdefault(route, PokemonShape.from_payload(data))

    def get_pokemon_species(self, name: t.Union[str, int]) -> t.Optional[PokemonSpecies]:
        """
        Get pokemon species from cache.

        Parameters
        ----------
        name: Union[str, int]
            The name or id of the pokemon species.

        Returns
        -------
        t.Optional[PokemonSpecies]
            Pokemon species model if found, else None.

        Raises
        ------
        pokelance.exceptions.ResourceNotFound
            if pokemon species was not found.

        Examples
        --------

        >>> from pokelance import PokeLance
        >>> client = PokeLance()
        >>> pokemon_species = client.pokemon.get_pokemon_species(1)
        >>> pokemon_species.name
        'bulbasaur'
        """
        route = Endpoint.get_pokemon_species(name)
        self._validate_resource(self.cache.pokemon_species, name, route)
        return self.cache.pokemon_species.get(route, None)

    async def fetch_pokemon_species(self, name: t.Union[str, int]) -> t.Optional[PokemonSpecies]:
        """
        Fetches a pokemon species model by name or id.

        Parameters
        ----------
        name: Union[str, int]
            The name or id of the

        Returns
        -------
        t.Optional[PokemonSpecies]
            Pokemon species model if found, else None.

        Raises
        ------
        pokelance.exceptions.ResourceNotFound
            if pokemon species was not found.

        Examples
        --------

        >>> from pokelance import PokeLance
        >>> import asyncio
        >>> client = PokeLance()
        >>> async def main() -> None:
        ...    pokemon_species = await client.pokemon.fetch_pokemon_species(1)
        ...    print(pokemon_species.name)
        ...    await client.close()
        >>> asyncio.run(main())
        bulbasaur
        """
        route = Endpoint.get_pokemon_species(name)
        self._validate_resource(self.cache.pokemon_species, name, route)
        data = await self._client.request(route)
        return self.cache.pokemon_species.setdefault(route, PokemonSpecies.from_payload(data))

    def get_stat(self, name: t.Union[str, int]) -> t.Optional[Stat]:
        """
        Get stat from cache.

        Parameters
        ----------
        name: Union[str, int]
            The name or id of the stat.

        Returns
        -------
        t.Optional[Stat]
            Stat model if found, else None.

        Raises
        ------
        pokelance.exceptions.ResourceNotFound
            if stat was not found.

        Examples
        --------

        >>> from pokelance import PokeLance
        >>> client = PokeLance()
        >>> stat = client.pokemon.get_stat(1)
        >>> stat.name
        'hp'
        """
        route = Endpoint.get_stat(name)
        self._validate_resource(self.cache.stat, name, route)
        return self.cache.stat.get(route, None)

    async def fetch_stat(self, name: t.Union[str, int]) -> t.Optional[Stat]:
        """
        Fetches a stat model by name or id.

        Parameters
        ----------
        name: Union[str, int]
            The name or id of the

        Returns
        -------
        t.Optional[Stat]
            Stat model if found, else None.

        Raises
        ------
        pokelance.exceptions.ResourceNotFound
            if stat was not found.

        Examples
        --------

        >>> from pokelance import PokeLance
        >>> import asyncio
        >>> client = PokeLance()
        >>> async def main() -> None:
        ...    stat = await client.pokemon.fetch_stat(1)
        ...    print(stat.name)
        ...    await client.close()
        >>> asyncio.run(main())
        hp
        """
        route = Endpoint.get_stat(name)
        self._validate_resource(self.cache.stat, name, route)
        data = await self._client.request(route)
        return self.cache.stat.setdefault(route, Stat.from_payload(data))

    def get_type(self, name: t.Union[str, int]) -> t.Optional[Type]:
        """
        Get type from cache.

        Parameters
        ----------
        name: Union[str, int]
            The name or id of the type.

        Returns
        -------
        t.Optional[Type]
            Type model if found, else None.

        Raises
        ------
        pokelance.exceptions.ResourceNotFound
            if type was not found.

        Examples
        --------

        >>> from pokelance import PokeLance
        >>> client = PokeLance()
        >>> type_ = client.pokemon.get_type(1)
        >>> type_.name
        'normal'
        """
        route = Endpoint.get_type(name)
        self._validate_resource(self.cache.type, name, route)
        return self.cache.type.get(route, None)

    async def fetch_type(self, name: t.Union[str, int]) -> t.Optional[Type]:
        """
        Fetches a type model by name or id.

        Parameters
        ----------
        name: Union[str, int]
            The name or id of the

        Returns
        -------
        t.Optional[Type]
            Type model if found, else None.

        Raises
        ------
        pokelance.exceptions.ResourceNotFound
            if type was not found.

        Examples
        --------

        >>> from pokelance import PokeLance
        >>> import asyncio
        >>> client = PokeLance()
        >>> async def main() -> None:
        ...    type_ = await client.pokemon.fetch_type(1)
        ...    print(type_.name)
        ...    await client.close()
        >>> asyncio.run(main())
        normal
        """
        route = Endpoint.get_type(name)
        self._validate_resource(self.cache.type, name, route)
        data = await self._client.request(route)
        return self.cache.type.setdefault(route, Type.from_payload(data))

    @property
    def all_pokemons(self) -> t.Optional[t.List[str]]:
        """
        Returns a list of all pokemon names.

        Returns
        -------
        t.Optional[t.List[str]]
            List of all pokemon names. None if not cached yet.
        """
        data = list(self.cache.pokemon.endpoints.keys())
        return data if data else None


def setup(lance: "PokeLance") -> None:
    """Setup the pokemon cog."""
    lance.add_extension("pokemon", Pokemon(lance.http))
