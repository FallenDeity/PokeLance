from __future__ import annotations

import typing as t

import attrs

from pokelance.constants import GenderEnum
from pokelance.models import BaseModel
from pokelance.models.common import NamedResource

__all__: t.Tuple[str, ...] = (
    "ChainLink",
    "EvolutionDetail",
)


@attrs.define(slots=True, kw_only=True)
class EvolutionDetail(BaseModel):
    """An evolution detail resource.

    Attributes
    ----------
    version_group: NamedResource
        The version group in which the evolution was introduced.
    is_default: bool
        Whether the evolution is considered as the expected evolution in a main series game. Each unique Pokémon variety of a line capable of evolution should have exactly one 'default' evolution. For example, the Meowth species has three default evolutions as there are three distinct varieties it can evolve into: Persian, Alolan Persian, and Perrserker.
    item: t.Optional[NamedResource]
        The item required to cause evolution this into Pokémon species.
    trigger: NamedResource
        The type of event that triggers evolution into this Pokémon species.
    gender: t.Optional[GenderEnum]
        Gender of the evolving Pokémon species must be in order to evolve.
    held_item: t.Optional[NamedResource]
        The item the evolving Pokémon species must be holding during the evolution trigger event.
    known_move: t.Optional[NamedResource]
        The move that must be known by the evolving Pokémon species during the evolution trigger event.
    known_move_type: t.Optional[NamedResource]
        The evolving Pokémon species must know a move with this type during the evolution trigger event.
    location: t.Optional[NamedResource]
        The location the evolution must be triggered at.
    min_affection: t.Optional[int]
        The minimum required level of affection the evolving Pokémon species must have.
    min_beauty: t.Optional[int]
        The minimum required level of beauty the evolving Pokémon species must have.
    min_happiness: t.Optional[int]
        The minimum required level of happiness the evolving Pokémon species must have.
    min_level: t.Optional[int]
        The minimum required level of the evolving Pokémon species.
    near_special_rock: bool
        Whether or not you need to be near a Moss Rock or Icy Rock to evolve into this Pokémon species.
    needs_multiplayer: bool
        Whether or not multiplayer link play is needed to evolve into this Pokémon species (e.g. Union Circle).
    needs_overworld_rain: bool
        Whether or not it must be raining in the overworld to cause evolution this Pokémon species.
    party_species: t.Optional[NamedResource]
        The specific Pokémon species that must be in the players party in order for the evolution to occur.
    party_type: t.Optional[NamedResource]
        The player must have a Pokémon of this type in their party during the evolution trigger event.
    relative_physical_stats: t.Optional[int]
        The required relation between the Pokémon's Attack and Defense stats.
    time_of_day: str
        The time of day the evolution must be triggered at.
    trade_species: t.Optional[NamedResource]
        The specific Pokémon species that must be traded with the evolving Pokémon species.
    turn_upside_down: bool
        Whether or not the 3DS needs to be turned upside-down as this Pokémon levels up.
    region: t.Optional[NamedResource]
        The required region in which this evolution can occur.
    base_form: t.Optional[NamedResource]
        The required form for which this evolution can occur.
    evolved_form: t.Optional[NamedResource]
        The form to which this evolution occurs.
    used_move: t.Optional[NamedResource]
        The move that must be used by the evolving Pokémon species during the evolution trigger event in order to evolve into this Pokémon species.
    min_move_count: t.Optional[int]
        The minimum number of times a move must be used in order to evolve into this Pokémon species.
    min_steps: t.Optional[int]
        The minimum number of steps that must be taken in order to evolve into this Pokémon species.
    min_damage_taken: t.Optional[int]
        The minimum amount of damage taken during the evolution trigger event in order to evolve into this Pokémon species.
    """

    version_group: NamedResource = attrs.field(factory=NamedResource)
    is_default: bool = attrs.field(factory=bool)
    item: t.Optional[NamedResource] = attrs.field(default=None)
    trigger: NamedResource = attrs.field(factory=NamedResource)
    gender: t.Optional[GenderEnum] = attrs.field(converter=GenderEnum.from_int)  # type: ignore[misc]
    held_item: t.Optional[NamedResource] = attrs.field(default=None)
    known_move: t.Optional[NamedResource] = attrs.field(default=None)
    known_move_type: t.Optional[NamedResource] = attrs.field(default=None)
    location: t.Optional[NamedResource] = attrs.field(default=None)
    min_level: t.Optional[int] = attrs.field(default=None)
    min_happiness: t.Optional[int] = attrs.field(default=None)
    min_beauty: t.Optional[int] = attrs.field(default=None)
    min_affection: t.Optional[int] = attrs.field(default=None)
    near_special_rock: bool = attrs.field(factory=bool)
    needs_overworld_rain: bool = attrs.field(factory=bool)
    needs_multiplayer: bool = attrs.field(factory=bool)
    party_species: t.Optional[NamedResource] = attrs.field(default=None)
    party_type: t.Optional[NamedResource] = attrs.field(default=None)
    relative_physical_stats: t.Optional[int] = attrs.field(default=None)
    time_of_day: str = attrs.field(factory=str)
    trade_species: t.Optional[NamedResource] = attrs.field(default=None)
    turn_upside_down: bool = attrs.field(factory=bool)
    region: t.Optional[NamedResource] = attrs.field(default=None)
    base_form: t.Optional[NamedResource] = attrs.field(default=None)
    evolved_form: t.Optional[NamedResource] = attrs.field(default=None)
    used_move: t.Optional[NamedResource] = attrs.field(default=None)
    min_move_count: t.Optional[int] = attrs.field(default=None)
    min_steps: t.Optional[int] = attrs.field(default=None)
    min_damage_taken: t.Optional[int] = attrs.field(default=None)

    @property
    def simplified_details(self) -> t.Dict[str, t.Any]:
        """Return a simplified dictionary of the evolution details.

        Prunes out any empty or None values, and only includes concrete or non-empty values.
        """
        simplified_details: t.Dict[str, t.Any] = {}
        for k, v in self.to_dict().items():
            if ((is_dict := isinstance(v, dict)) and v.get("name") and v.get("url")) or (not is_dict and v):
                simplified_details[k] = v
        return simplified_details

    @classmethod
    def from_payload(cls, payload: t.Dict[str, t.Any]) -> "EvolutionDetail":
        return cls(
            raw=payload,
            version_group=NamedResource.from_payload(payload.get("version_group", {})),
            is_default=payload.get("is_default", False),
            item=NamedResource.optional_from_payload(payload.get("item")),
            trigger=NamedResource.from_payload(payload.get("trigger", {})),
            gender=payload.get("gender", None),
            held_item=NamedResource.optional_from_payload(payload.get("held_item")),
            known_move=NamedResource.optional_from_payload(payload.get("known_move")),
            known_move_type=NamedResource.optional_from_payload(payload.get("known_move_type")),
            location=NamedResource.optional_from_payload(payload.get("location")),
            min_level=payload.get("min_level"),
            min_happiness=payload.get("min_happiness"),
            min_beauty=payload.get("min_beauty"),
            min_affection=payload.get("min_affection"),
            near_special_rock=payload.get("near_special_rock", False),
            needs_overworld_rain=payload.get("needs_overworld_rain", False),
            needs_multiplayer=payload.get("needs_multiplayer", False),
            party_species=NamedResource.optional_from_payload(payload.get("party_species")),
            party_type=NamedResource.optional_from_payload(payload.get("party_type")),
            relative_physical_stats=payload.get("relative_physical_stats"),
            time_of_day=payload.get("time_of_day", ""),
            trade_species=NamedResource.optional_from_payload(payload.get("trade_species")),
            turn_upside_down=payload.get("turn_upside_down", False),
            region=NamedResource.optional_from_payload(payload.get("region")),
            base_form=NamedResource.optional_from_payload(payload.get("base_form")),
            evolved_form=NamedResource.optional_from_payload(payload.get("evolved_form")),
            used_move=NamedResource.optional_from_payload(payload.get("used_move")),
            min_move_count=payload.get("min_move_count"),
            min_steps=payload.get("min_steps"),
            min_damage_taken=payload.get("min_damage_taken"),
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
    evolves_to: t.List[ChainLink] = attrs.field(factory=list)

    @classmethod
    def from_payload(cls, payload: t.Dict[str, t.Any]) -> "ChainLink":
        return cls(
            raw=payload,
            is_baby=payload.get("is_baby", False),
            species=NamedResource.from_payload(payload.get("species", {})),
            evolution_details=[EvolutionDetail.from_payload(detail) for detail in payload.get("evolution_details", [])],
            evolves_to=[ChainLink.from_payload(link) for link in payload.get("evolves_to", [])],
        )
