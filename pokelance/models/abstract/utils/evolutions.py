from __future__ import annotations

import typing as t

import attrs
from typing_extensions import override

from pokelance.constants import GenderEnum
from pokelance.models import BaseModel
from pokelance.models.common import NamedResource
from pokelance.utils import parse_rpn_expression

__all__: tuple[str, ...] = (
    "ChainLink",
    "EvolutionDetail",
)


@attrs.define(slots=True, kw_only=True)
class ConditionExpression(BaseModel):
    """A condition expression resource.

    Attributes
    ----------
    expression: str
        The reverse Polish notation (RPN) mathematical expression determining form-branching.
    percentage_chance: int
        The percentage chance that this evolution will occur.
    variables: list[NamedResource]
        The variables used in the condition expression.
    """

    expression: str = attrs.field(factory=str)
    percentage_chance: int = attrs.field(factory=int)
    variables: list[NamedResource] = attrs.field(factory=list)

    @property
    def readable_expression(self) -> str:
        """Return the condition expression parsed into human-readable infix notation."""
        return parse_rpn_expression(self.expression)

    @classmethod
    @override
    def from_payload(cls, payload: dict[str, t.Any]) -> ConditionExpression:
        return cls(
            raw=payload,
            expression=payload.get("expression", ""),
            percentage_chance=payload.get("percentage_chance", 0),
            variables=[NamedResource.from_payload(var) for var in payload.get("variables", [])],
        )


@attrs.define(slots=True, kw_only=True)
class EvolutionDetail(BaseModel):
    """An evolution detail resource.

    Attributes
    ----------
    version_group: NamedResource
        The version group in which the evolution was introduced.
    is_default: bool
        Whether the evolution is considered as the expected evolution in a main series game.
        Each unique Pokémon variety of a line capable of evolution should have exactly one 'default' evolution.
        For example, the Meowth species has three default evolutions as there are three distinct varieties it can
        evolve into: Persian, Alolan Persian, and Perrserker.
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
    required_pokemon_form: t.Optional[NamedResource]
        The specific pre-evolution form required for this evolution to occur (e.g. sinistea-antique, burmy-plant).
    evolved_pokemon_form: t.Optional[NamedResource]
        The specific form resulting from this evolution (e.g. polteageist-antique, wormadam-sandy).
    used_move: t.Optional[NamedResource]
        The move that must be used by the evolving Pokémon species during the evolution trigger event
        in order to evolve into this Pokémon species.
    min_move_count: t.Optional[int]
        The minimum number of times a move must be used in order to evolve into this Pokémon species.
    min_steps: t.Optional[int]
        The minimum number of steps that must be taken in order to evolve into this Pokémon species.
    min_damage_taken: t.Optional[int]
        The minimum amount of damage taken during the evolution trigger event in order to evolve
        into this Pokémon species.
    allowed_natures: t.Optional[t.List[NamedResource]]
        The list of allowed natures the Pokémon must have to evolve into this Pokémon species.
    condition_expression: t.Optional[ConditionExpression]
        The condition expression that must evaluate to true in order for the evolution to occur.
    """

    version_group: NamedResource = attrs.field(factory=NamedResource)
    is_default: bool = attrs.field(factory=bool)
    item: NamedResource | None = attrs.field(default=None)
    trigger: NamedResource = attrs.field(factory=NamedResource)
    gender: GenderEnum | None = attrs.field(converter=GenderEnum.from_int)
    held_item: NamedResource | None = attrs.field(default=None)
    known_move: NamedResource | None = attrs.field(default=None)
    known_move_type: NamedResource | None = attrs.field(default=None)
    location: NamedResource | None = attrs.field(default=None)
    min_level: int | None = attrs.field(default=None)
    min_happiness: int | None = attrs.field(default=None)
    min_beauty: int | None = attrs.field(default=None)
    min_affection: int | None = attrs.field(default=None)
    near_special_rock: bool = attrs.field(factory=bool)
    needs_overworld_rain: bool = attrs.field(factory=bool)
    needs_multiplayer: bool = attrs.field(factory=bool)
    party_species: NamedResource | None = attrs.field(default=None)
    party_type: NamedResource | None = attrs.field(default=None)
    relative_physical_stats: int | None = attrs.field(default=None)
    time_of_day: str = attrs.field(factory=str)
    trade_species: NamedResource | None = attrs.field(default=None)
    turn_upside_down: bool = attrs.field(factory=bool)
    region: NamedResource | None = attrs.field(default=None)
    required_pokemon_form: NamedResource | None = attrs.field(default=None)
    evolved_pokemon_form: NamedResource | None = attrs.field(default=None)
    used_move: NamedResource | None = attrs.field(default=None)
    min_move_count: int | None = attrs.field(default=None)
    min_steps: int | None = attrs.field(default=None)
    min_damage_taken: int | None = attrs.field(default=None)
    allowed_natures: list[NamedResource] | None = attrs.field(default=None)
    condition_expression: ConditionExpression | None = attrs.field(default=None)

    @property
    def simplified_details(self) -> dict[str, t.Any]:
        """Return a simplified dictionary of the evolution details.

        Prunes out any empty or None values, and only includes concrete or non-empty values.
        """
        simplified_details: dict[str, t.Any] = {}
        for k, v in self.to_dict().items():
            if isinstance(v, dict):
                if (v.get("name") and v.get("url")) or "expression" in v:
                    simplified_details[k] = v
            elif isinstance(v, list):
                if len(v) > 0:
                    simplified_details[k] = v
            elif v is not None and v is not False and v != "":
                simplified_details[k] = v
        return simplified_details

    @classmethod
    @override
    def from_payload(cls, payload: dict[str, t.Any]) -> EvolutionDetail:
        return cls(
            raw=payload,
            version_group=NamedResource.from_payload(payload.get("version_group", {})),
            is_default=payload.get("is_default", False),
            item=NamedResource.optional_from_payload(payload.get("item")),
            trigger=NamedResource.from_payload(payload.get("trigger", {})),
            gender=payload.get("gender"),
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
            required_pokemon_form=NamedResource.optional_from_payload(payload.get("required_pokemon_form")),
            evolved_pokemon_form=NamedResource.optional_from_payload(payload.get("evolved_pokemon_form")),
            used_move=NamedResource.optional_from_payload(payload.get("used_move")),
            min_move_count=payload.get("min_move_count"),
            min_steps=payload.get("min_steps"),
            min_damage_taken=payload.get("min_damage_taken"),
            allowed_natures=(
                [NamedResource.from_payload(n) for n in natures]
                if (natures := payload.get("allowed_natures"))
                else None
            ),
            condition_expression=ConditionExpression.optional_from_payload(payload.get("condition_expression")),
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
    evolution_details: list[EvolutionDetail] = attrs.field(factory=list)
    evolves_to: list[ChainLink] = attrs.field(factory=list)

    @classmethod
    @override
    def from_payload(cls, payload: dict[str, t.Any]) -> ChainLink:
        return cls(
            raw=payload,
            is_baby=payload.get("is_baby", False),
            species=NamedResource.from_payload(payload.get("species", {})),
            evolution_details=[EvolutionDetail.from_payload(detail) for detail in payload.get("evolution_details", [])],
            evolves_to=[ChainLink.from_payload(link) for link in payload.get("evolves_to", [])],
        )
