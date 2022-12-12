import typing as t

import attrs

from pokelance.models import BaseModel
from pokelance.models.common import Description, Name, NamedResource

from .utils import PokemonEntry

__all__: t.Tuple[str, ...] = (
    "Generation",
    "Pokedex",
    "Version",
    "VersionGroup",
)


@attrs.define(slots=True, kw_only=True)
class Generation(BaseModel):
    """Generation model.

    Attributes
    ----------
    id: int
        The identifier for this resource.
    name: str
        The name for this resource.
    abilities: t.List[NamedResource]
        A list of abilities that were introduced in this generation.
    names: t.List[Name]
        The name of this resource listed in different languages.
    main_region: NamedResource
        The main region travelled in this generation.
    moves: t.List[NamedResource]
        A list of moves that were introduced in this generation.
    pokemon_species: t.List[NamedResource]
        A list of Pokémon species that were introduced in this generation.
    types: t.List[NamedResource]
        A list of types that were introduced in this generation.
    version_groups: t.List[NamedResource]
        A list of version groups that were introduced in this generation.
    """

    id: int = attrs.field(factory=int)
    name: str = attrs.field(factory=str)
    abilities: t.List[NamedResource] = attrs.field(factory=list)
    names: t.List[Name] = attrs.field(factory=list)
    main_region: NamedResource = attrs.field(factory=NamedResource)
    moves: t.List[NamedResource] = attrs.field(factory=list)
    pokemon_species: t.List[NamedResource] = attrs.field(factory=list)
    types: t.List[NamedResource] = attrs.field(factory=list)
    version_groups: t.List[NamedResource] = attrs.field(factory=list)

    @classmethod
    def from_payload(cls, payload: t.Dict[str, t.Any]) -> "Generation":
        return cls(
            id=payload.get("id", 0),
            name=payload.get("name", ""),
            abilities=[NamedResource.from_payload(i) for i in payload.get("abilities", [])],
            names=[Name.from_payload(i) for i in payload.get("names", [])],
            main_region=NamedResource.from_payload(payload.get("main_region", {}) or {}),
            moves=[NamedResource.from_payload(i) for i in payload.get("moves", [])],
            pokemon_species=[NamedResource.from_payload(i) for i in payload.get("pokemon_species", [])],
            types=[NamedResource.from_payload(i) for i in payload.get("types", [])],
            version_groups=[NamedResource.from_payload(i) for i in payload.get("version_groups", [])],
        )


@attrs.define(slots=True, kw_only=True)
class Pokedex(BaseModel):
    """Pokedex model.

    Attributes
    ----------
    id: int
        The identifier for this resource.
    name: str
        The name for this resource.
    is_main_series: bool
        Whether or not this Pokédex originated in the main series of the video games.
    descriptions: t.List[Description]
        The description of this resource listed in different languages.
    names: t.List[Name]
        The name of this resource listed in different languages.
    pokemon_entries: t.List[PokemonEntry]
        A list of Pokémon catalogued in this Pokédex and their indexes.
    region: NamedResource
        The region this Pokédex catalogues Pokémon for.
    version_groups: t.List[NamedResource]
        A list of version groups this Pokédex is relevant to.
    """

    id: int = attrs.field(factory=int)
    name: str = attrs.field(factory=str)
    is_main_series: bool = attrs.field(factory=bool)
    descriptions: t.List[Description] = attrs.field(factory=list)
    names: t.List[Name] = attrs.field(factory=list)
    pokemon_entries: t.List[PokemonEntry] = attrs.field(factory=list)
    region: NamedResource = attrs.field(factory=NamedResource)
    version_groups: t.List[NamedResource] = attrs.field(factory=list)

    @classmethod
    def from_payload(cls, payload: t.Dict[str, t.Any]) -> "Pokedex":
        return cls(
            id=payload.get("id", 0),
            name=payload.get("name", ""),
            is_main_series=payload.get("is_main_series", False),
            descriptions=[Description.from_payload(i) for i in payload.get("descriptions", [])],
            names=[Name.from_payload(i) for i in payload.get("names", [])],
            pokemon_entries=[PokemonEntry.from_payload(i) for i in payload.get("pokemon_entries", [])],
            region=NamedResource.from_payload(payload.get("region", {}) or {}),
            version_groups=[NamedResource.from_payload(i) for i in payload.get("version_groups", [])],
        )


@attrs.define(slots=True, kw_only=True)
class Version(BaseModel):
    """Version model.

    Attributes
    ----------
    id: int
        The identifier for this resource.
    name: str
        The name for this resource.
    names: t.List[Name]
        The name of this resource listed in different languages.
    version_group: NamedResource
        The version group this version belongs to.
    """

    id: int = attrs.field(factory=int)
    name: str = attrs.field(factory=str)
    names: t.List[Name] = attrs.field(factory=list)
    version_group: NamedResource = attrs.field(factory=NamedResource)

    @classmethod
    def from_payload(cls, payload: t.Dict[str, t.Any]) -> "Version":
        return cls(
            id=payload.get("id", 0),
            name=payload.get("name", ""),
            names=[Name.from_payload(i) for i in payload.get("names", [])],
            version_group=NamedResource.from_payload(payload.get("version_group", {}) or {}),
        )


@attrs.define(slots=True, kw_only=True)
class VersionGroup(BaseModel):
    """VersionGroup model.

    Attributes
    ----------
    id: int
        The identifier for this resource.
    name: str
        The name for this resource.
    order: int
        Order for sorting. Almost by date of release, except similar versions are grouped together.
    generation: NamedResource
        The generation this version was introduced in.
    move_learn_methods: t.List[NamedResource]
        A list of methods in which Pokémon can learn moves in this version group.
    pokedexes: t.List[NamedResource]
        A list of Pokédexes introduces in this version group.
    regions: t.List[NamedResource]
        A list of regions that can be visited in this version group.
    versions: t.List[NamedResource]
        A list of versions this version group owns.
    """

    id: int = attrs.field(factory=int)
    name: str = attrs.field(factory=str)
    order: int = attrs.field(factory=int)
    generation: NamedResource = attrs.field(factory=NamedResource)
    move_learn_methods: t.List[NamedResource] = attrs.field(factory=list)
    pokedexes: t.List[NamedResource] = attrs.field(factory=list)
    regions: t.List[NamedResource] = attrs.field(factory=list)
    versions: t.List[NamedResource] = attrs.field(factory=list)

    @classmethod
    def from_payload(cls, payload: t.Dict[str, t.Any]) -> "VersionGroup":
        return cls(
            id=payload.get("id", 0),
            name=payload.get("name", ""),
            order=payload.get("order", 0),
            generation=NamedResource.from_payload(payload.get("generation", {}) or {}),
            move_learn_methods=[NamedResource.from_payload(i) for i in payload.get("move_learn_methods", [])],
            pokedexes=[NamedResource.from_payload(i) for i in payload.get("pokedexes", [])],
            regions=[NamedResource.from_payload(i) for i in payload.get("regions", [])],
            versions=[NamedResource.from_payload(i) for i in payload.get("versions", [])],
        )
