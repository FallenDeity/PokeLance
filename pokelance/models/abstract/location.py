import typing as t

import attrs

from pokelance.models import BaseModel
from pokelance.models.common import GenerationGameIndex, Name, NamedResource

from .utils import EncounterMethodRate, PalParkEncounterSpecies, PokemonEncounter

__all__: t.Tuple[str, ...] = (
    "Location",
    "LocationArea",
    "PalParkArea",
    "Region",
)


@attrs.define(slots=True, kw_only=True)
class Location(BaseModel):
    """Location model.

    Attributes
    ----------
    id: int
        The identifier for this resource.
    name: str
        The name for this resource.
    region: NamedResource
        The region this location can be found in.
    names: t.List[Name]
        The name of this resource listed in different languages.
    game_indices: t.List[GenerationGameIndex]
        A list of game indices relevent to this location by generation.
    areas: t.List[NamedResource]
        A list of methods in which Pokémon may be encountered in this
        location.
    """

    id: int = attrs.field(factory=int)
    name: str = attrs.field(factory=str)
    region: NamedResource = attrs.field(factory=NamedResource)
    names: t.List[Name] = attrs.field(factory=list)
    game_indices: t.List[GenerationGameIndex] = attrs.field(factory=list)
    areas: t.List[NamedResource] = attrs.field(factory=list)

    @classmethod
    def from_payload(cls, payload: t.Dict[str, t.Any]) -> "Location":
        return cls(
            id=payload.get("id", 0),
            name=payload.get("name", ""),
            region=NamedResource.from_payload(payload.get("region", {}) or {}),
            names=[Name.from_payload(i) for i in payload.get("names", [])],
            game_indices=[GenerationGameIndex.from_payload(i) for i in payload.get("game_indices", [])],
            areas=[NamedResource.from_payload(i) for i in payload.get("areas", [])],
        )


@attrs.define(slots=True, kw_only=True)
class LocationArea(BaseModel):
    """LocationArea model.

    Attributes
    ----------
    id: int
        The identifier for this resource.
    name: str
        The name for this resource.
    game_index: int
        The internal id of an API resource within game data.
    encounter_method_rates: t.List[EncounterMethodRate]
        A list of methods in which Pokémon may be encountered in this
        area and how likely the method will occur depending on the
        version of the game.
    location: NamedResource
        The region this location can be found in.
    names: t.List[Name]
        The name of this resource listed in different languages.
    pokemon_encounters: t.List[PokemonEncounter]
        A list of Pokémon that can be encountered in this area along
        with version specific details about the encounter.
    """

    id: int = attrs.field(factory=int)
    name: str = attrs.field(factory=str)
    game_index: int = attrs.field(factory=int)
    names: t.List[Name] = attrs.field(factory=list)
    location: NamedResource = attrs.field(factory=NamedResource)
    encounter_method_rates: t.List[EncounterMethodRate] = attrs.field(factory=list)
    pokemon_encounters: t.List[PokemonEncounter] = attrs.field(factory=list)

    @classmethod
    def from_payload(cls, payload: t.Dict[str, t.Any]) -> "LocationArea":
        return cls(
            id=payload.get("id", 0),
            name=payload.get("name", ""),
            game_index=payload.get("game_index", 0),
            names=[Name.from_payload(i) for i in payload.get("names", [])],
            location=NamedResource.from_payload(payload.get("location", {}) or {}),
            encounter_method_rates=[
                EncounterMethodRate.from_payload(i) for i in payload.get("encounter_method_rates", [])
            ],
            pokemon_encounters=[PokemonEncounter.from_payload(i) for i in payload.get("pokemon_encounters", [])],
        )


@attrs.define(slots=True, kw_only=True)
class PalParkArea(BaseModel):
    """PalParkArea model.

    Attributes
    ----------
    id: int
        The identifier for this resource.
    name: str
        The name for this resource.
    names: t.List[Name]
        The name of this resource listed in different languages.
    pokemon_encounters: t.List[PalParkEncounterSpecies]
        A list of Pokémon encountered in this pal park area along with
        details.
    """

    id: int = attrs.field(factory=int)
    name: str = attrs.field(factory=str)
    names: t.List[Name] = attrs.field(factory=list)
    pokemon_encounters: t.List[PalParkEncounterSpecies] = attrs.field(factory=list)

    @classmethod
    def from_payload(cls, payload: t.Dict[str, t.Any]) -> "PalParkArea":
        return cls(
            id=payload.get("id", 0),
            name=payload.get("name", ""),
            names=[Name.from_payload(i) for i in payload.get("names", [])],
            pokemon_encounters=[PalParkEncounterSpecies.from_payload(i) for i in payload.get("pokemon_encounters", [])],
        )


@attrs.define(slots=True, kw_only=True)
class Region(BaseModel):
    """Region model.

    Attributes
    ----------
    id: int
        The identifier for this resource.
    name: str
        The name for this resource.
    locations: t.List[NamedResource]
        A list of locations that can be found in this region.
    main_generation: NamedResource
        The generation this region was introduced in.
    names: t.List[Name]
        The name of this resource listed in different languages.
    pokedexes: t.List[NamedResource]
        A list of pokédexes that catalogue Pokémon in this region.
    version_groups: t.List[NamedResource]
        A list of version groups where this region can be visited.
    """

    id: int = attrs.field(factory=int)
    name: str = attrs.field(factory=str)
    locations: t.List[NamedResource] = attrs.field(factory=list)
    main_generation: NamedResource = attrs.field(factory=NamedResource)
    names: t.List[Name] = attrs.field(factory=list)
    pokedexes: t.List[NamedResource] = attrs.field(factory=list)
    version_groups: t.List[NamedResource] = attrs.field(factory=list)

    @classmethod
    def from_payload(cls, payload: t.Dict[str, t.Any]) -> "Region":
        return cls(
            id=payload.get("id", 0),
            name=payload.get("name", ""),
            locations=[NamedResource.from_payload(i) for i in payload.get("locations", [])],
            main_generation=NamedResource.from_payload(payload.get("main_generation", {}) or {}),
            names=[Name.from_payload(i) for i in payload.get("names", [])],
            pokedexes=[NamedResource.from_payload(i) for i in payload.get("pokedexes", [])],
            version_groups=[NamedResource.from_payload(i) for i in payload.get("version_groups", [])],
        )
