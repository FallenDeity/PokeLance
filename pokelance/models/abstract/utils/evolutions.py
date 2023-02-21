import typing as t

import attrs

from pokelance.models import BaseModel
from pokelance.models.common import NamedResource

__all__: t.Tuple[str, ...] = (
    "ChainLink",
    "EvolutionDetail",
)
GENDER_MAP: t.Dict[int, str] = {1: "Female", 2: "Male", 3: "Genderless"}


@attrs.define(slots=True, kw_only=True)
class EvolutionDetail(BaseModel):
    """An evolution detail resource.

    Attributes
    ----------
    item: NamedResource
        The item required to cause evolution this into Pokémon species.
    trigger: NamedResource
        The type of event that triggers evolution into this Pokémon species.
    gender: str
        Gender of the evolving Pokémon species must be in order to evolve.
    held_item: NamedResource
        The item the evolving Pokémon species must be holding during the evolution trigger event.
    known_move: NamedResource
        The move that must be known by the evolving Pokémon species during the evolution trigger event.
    known_move_type: NamedResource
        The evolving Pokémon species must know a move with this type during the evolution trigger event.
    location: NamedResource
        The location the evolution must be triggered at.
    min_affection: int
        The minimum required level of affection the evolving Pokémon species must have.
    min_beauty: int
        The minimum required level of beauty the evolving Pokémon species must have.
    min_happiness: int
        The minimum required level of happiness the evolving Pokémon species must have.
    min_level: int
        The minimum required level of the evolving Pokémon species.
    needs_overworld_rain: bool
        Whether or not it must be raining in the overworld to cause evolution this Pokémon species.
    party_species: NamedResource
        The specific Pokémon species that must be in the players party in order for the evolution to occur.
    party_type: NamedResource
        The player must have a Pokémon of this type in their party during the evolution trigger event.
    relative_physical_stats: int
        The required relation between the Pokémon's Attack and Defense stats.
    time_of_day: str
        The time of day the evolution must be triggered at.
    trade_species: NamedResource
        The specific Pokémon species that must be traded with the evolving Pokémon species.
    turn_upside_down: bool
        Whether or not the 3DS needs to be turned upside-down as this Pokémon levels up.
    """

    item: NamedResource = attrs.field(factory=NamedResource)
    trigger: NamedResource = attrs.field(factory=NamedResource)
    gender: str = attrs.field(factory=str)
    held_item: NamedResource = attrs.field(factory=NamedResource)
    known_move: NamedResource = attrs.field(factory=NamedResource)
    known_move_type: NamedResource = attrs.field(factory=NamedResource)
    location: NamedResource = attrs.field(factory=NamedResource)
    min_level: int = attrs.field(factory=int)
    min_happiness: int = attrs.field(factory=int)
    min_beauty: int = attrs.field(factory=int)
    min_affection: int = attrs.field(factory=int)
    needs_overworld_rain: bool = attrs.field(factory=bool)
    party_species: NamedResource = attrs.field(factory=NamedResource)
    party_type: NamedResource = attrs.field(factory=NamedResource)
    relative_physical_stats: int = attrs.field(factory=int)
    time_of_day: str = attrs.field(factory=str)
    trade_species: NamedResource = attrs.field(factory=NamedResource)
    turn_upside_down: bool = attrs.field(factory=bool)

    @classmethod
    def from_payload(cls, payload: t.Dict[str, t.Any]) -> "EvolutionDetail":
        return cls(
            item=NamedResource.from_payload(payload.get("item", {}) or {}),
            trigger=NamedResource.from_payload(payload.get("trigger", {}) or {}),
            gender=GENDER_MAP.get(payload.get("gender", 0), ""),
            held_item=NamedResource.from_payload(payload.get("held_item", {}) or {}),
            known_move=NamedResource.from_payload(payload.get("known_move", {}) or {}),
            known_move_type=NamedResource.from_payload(payload.get("known_move_type", {}) or {}),
            location=NamedResource.from_payload(payload.get("location", {}) or {}),
            min_level=payload.get("min_level", 0),
            min_happiness=payload.get("min_happiness", 0),
            min_beauty=payload.get("min_beauty", 0),
            min_affection=payload.get("min_affection", 0),
            needs_overworld_rain=payload.get("needs_overworld_rain", False),
            party_species=NamedResource.from_payload(payload.get("party_species", {}) or {}),
            party_type=NamedResource.from_payload(payload.get("party_type", {}) or {}),
            relative_physical_stats=payload.get("relative_physical_stats", 0),
            time_of_day=payload.get("time_of_day", ""),
            trade_species=NamedResource.from_payload(payload.get("trade_species", {}) or {}),
            turn_upside_down=payload.get("turn_upside_down", False),
        )


@attrs.define(slots=True, kw_only=True)
class ChainLink(BaseModel):
    """A chain link resource.

    Attributes
    ----------
    is_baby: bool
        Whether or not this link is for a baby Pokémon.
    species: NamedResource
        The Pokémon species at this point in the evolution chain.
    evolution_details: t.List[EvolutionDetail]
        A list of details regarding the specific details of the referenced Pokémon species evolution.
    evolves_to: t.List[ChainLink]
        A list of chain links.
    """

    is_baby: bool = attrs.field(factory=bool)
    species: NamedResource = attrs.field(factory=NamedResource)
    evolution_details: t.List[EvolutionDetail] = attrs.field(factory=list)
    evolves_to: t.List["ChainLink"] = attrs.field(factory=list)

    @classmethod
    def from_payload(cls, payload: t.Dict[str, t.Any]) -> "ChainLink":
        return cls(
            is_baby=payload.get("is_baby", False),
            species=NamedResource.from_payload(payload.get("species", {}) or {}),
            evolution_details=[EvolutionDetail.from_payload(detail) for detail in payload.get("evolution_details", [])],
            evolves_to=[ChainLink.from_payload(link) for link in payload.get("evolves_to", [])],
        )
