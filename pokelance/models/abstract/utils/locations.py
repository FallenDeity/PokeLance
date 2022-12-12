import typing as t

import attrs

from pokelance.models import BaseModel
from pokelance.models.common import NamedResource

__all__: t.Tuple[str, ...] = (
    "EncounterVersionDetails",
    "EncounterMethodRate",
    "PokemonEncounter",
    "PalParkEncounterSpecies",
)


@attrs.define(slots=True, kw_only=True)
class EncounterVersionDetails(BaseModel):
    """An encounter version details resource.

    Attributes
    ----------
    rate: int
        The chance of an encounter to occur.
    version: NamedResource
        The version of this encounter.
    """

    rate: int = attrs.field(factory=int)
    version: NamedResource = attrs.field(factory=NamedResource)

    @classmethod
    def from_payload(cls, payload: t.Dict[str, t.Any]) -> "EncounterVersionDetails":
        return cls(
            rate=payload.get("rate", 0),
            version=NamedResource.from_payload(payload.get("version", {}) or {}),
        )


@attrs.define(slots=True, kw_only=True)
class EncounterMethodRate(BaseModel):
    """An encounter method rate resource.

    Attributes
    ----------
    encounter_method: NamedResource
        The method in which Pokémon may be encountered in an area.
    version_details: t.List[EncounterVersionDetails]
        A list of version details for the encounter.
    """

    encounter_method: NamedResource = attrs.field(factory=NamedResource)
    version_details: t.List[EncounterVersionDetails] = attrs.field(factory=list)

    @classmethod
    def from_payload(cls, payload: t.Dict[str, t.Any]) -> "EncounterMethodRate":
        return cls(
            encounter_method=NamedResource.from_payload(payload.get("encounter_method", {}) or {}),
            version_details=[EncounterVersionDetails.from_payload(i) for i in payload.get("version_details", [])],
        )


@attrs.define(slots=True, kw_only=True)
class PokemonEncounter(BaseModel):
    """A pokemon encounter resource.

    Attributes
    ----------
    pokemon: NamedResource
        The Pokémon being encountered.
    version_details: t.List[EncounterVersionDetails]
        A list of versions and encounters with Pokémon that might happen.
    """

    pokemon: NamedResource = attrs.field(factory=NamedResource)
    version_details: t.List[EncounterVersionDetails] = attrs.field(factory=list)

    @classmethod
    def from_payload(cls, payload: t.Dict[str, t.Any]) -> "PokemonEncounter":
        return cls(
            pokemon=NamedResource.from_payload(payload.get("pokemon", {}) or {}),
            version_details=[EncounterVersionDetails.from_payload(i) for i in payload.get("version_details", [])],
        )


@attrs.define(slots=True, kw_only=True)
class PalParkEncounterSpecies(BaseModel):
    """A pal park encounter species resource.

    Attributes
    ----------
    base_score: int
        The base score given to the player when this Pokémon is caught during a pal park run.
    rate: int
        The base rate for encountering this Pokémon in pal park.
    pokemon_species: NamedResource
        The Pokémon species being encountered.
    """

    base_score: int = attrs.field(factory=int)
    rate: int = attrs.field(factory=int)
    pokemon_species: NamedResource = attrs.field(factory=NamedResource)

    @classmethod
    def from_payload(cls, payload: t.Dict[str, t.Any]) -> "PalParkEncounterSpecies":
        return cls(
            base_score=payload.get("base_score", 0),
            rate=payload.get("rate", 0),
            pokemon_species=NamedResource.from_payload(payload.get("pokemon_species", {}) or {}),
        )
