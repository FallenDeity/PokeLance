import typing as t

import attrs

from pokelance.models import BaseModel
from pokelance.models.common import Description, MachineVersionDetail, Name, NamedResource, Resource, VerboseEffect

from .utils import (
    AbilityEffectChange,
    ContestComboSet,
    MoveFlavorText,
    MoveMetaData,
    MoveStatChange,
    PastMoveStatValues,
)

__all__: t.Tuple[str, ...] = (
    "Move",
    "MoveAilment",
    "MoveBattleStyle",
    "MoveCategory",
    "MoveDamageClass",
    "MoveLearnMethod",
    "MoveTarget",
)


@attrs.define(slots=True, kw_only=True)
class Move(BaseModel):
    """Move model.

    Attributes
    ----------
    id: int
        The identifier for this resource.
    name: str
        The name for this resource.
    accuracy: int
        The percent value of how likely this move is to be successful.
    effect_chance: int
        The percent value of how likely it is this moves effect will take effect.
    pp: int
        Power points. The number of times this move can be used.
    priority: int
        A value between -8 and 8. Sets the order in which moves
        are executed during battle. See Bulbapedia for greater detail.
    power: int
        The base power of this move with a value of 0 if it does not have a base power.
    contest_combos: ContestComboSet
        A detail of normal and super contest combos that require this move.
    contest_type: NamedResource
        The type of appeal this move gives a Pokémon when used in a contest.
    contest_effect: Resource
        The effect the move has when used in a contest.
    damage_class: NamedResource
        The type of damage the move inflicts on the target, e.g. physical.
    effect_entries: t.List[VerboseEffect]
        The effect of this move listed in different languages.
    effect_changes: t.List[AbilityEffectChange]
        The list of previous effects this move has had across version groups of the games.
    flavor_text_entries: t.List[MoveFlavorText]
        The flavor text of this move listed in different languages.
    generation: NamedResource
        The generation in which this move was introduced.
    machines: t.List[MachineVersionDetail]
        A list of the machines that teach this move.
    meta: MoveMetaData
        Metadata about this move.
    names: t.List[Name]
        The name of this resource listed in different languages.
    past_values: t.List[PastMoveStatValues]
        A list of move resource value changes across version groups of the games.
    stat_changes: t.List[MoveStatChange]
        A list of stats this moves effects and how much it effects them.
    super_contest_effect: Resource
        The effect the move has when used in a super contest.
    target: NamedResource
        The type of target that will receive the effects of the attack.
    type: NamedResource
        The elemental type of this move.
    """

    id: int = attrs.field(factory=int)
    name: str = attrs.field(factory=str)
    accuracy: int = attrs.field(factory=int)
    effect_chance: int = attrs.field(factory=int)
    pp: int = attrs.field(factory=int)
    priority: int = attrs.field(factory=int)
    power: int = attrs.field(factory=int)
    contest_combos: ContestComboSet = attrs.field(factory=ContestComboSet)
    contest_type: NamedResource = attrs.field(factory=NamedResource)
    contest_effect: Resource = attrs.field(factory=Resource)
    damage_class: NamedResource = attrs.field(factory=NamedResource)
    effect_entries: t.List[VerboseEffect] = attrs.field(factory=list)
    effect_changes: t.List[AbilityEffectChange] = attrs.field(factory=list)
    learned_by_pokemon: t.List[NamedResource] = attrs.field(factory=list)
    flavor_text_entries: t.List[MoveFlavorText] = attrs.field(factory=list)
    generation: NamedResource = attrs.field(factory=NamedResource)
    machines: t.List[MachineVersionDetail] = attrs.field(factory=list)
    meta: MoveMetaData = attrs.field(factory=MoveMetaData)
    names: t.List[Name] = attrs.field(factory=list)
    past_values: t.List[PastMoveStatValues] = attrs.field(factory=list)
    stat_changes: t.List[MoveStatChange] = attrs.field(factory=list)
    super_contest_effect: Resource = attrs.field(factory=Resource)
    target: NamedResource = attrs.field(factory=NamedResource)
    type: NamedResource = attrs.field(factory=NamedResource)

    @classmethod
    def from_payload(cls, payload: t.Dict[str, t.Any]) -> "Move":
        return cls(
            id=payload.get("id", 0),
            name=payload.get("name", ""),
            accuracy=payload.get("accuracy", 0),
            effect_chance=payload.get("effect_chance", 0),
            pp=payload.get("pp", 0),
            priority=payload.get("priority", 0),
            power=payload.get("power", 0),
            contest_combos=ContestComboSet.from_payload(payload.get("contest_combos", {}) or {}),
            contest_type=NamedResource.from_payload(payload.get("contest_type", {}) or {}),
            contest_effect=Resource.from_payload(payload.get("contest_effect", {}) or {}),
            damage_class=NamedResource.from_payload(payload.get("damage_class", {}) or {}),
            effect_entries=[VerboseEffect.from_payload(i) for i in payload.get("effect_entries", [])],
            effect_changes=[AbilityEffectChange.from_payload(i) for i in payload.get("effect_changes", [])],
            learned_by_pokemon=[NamedResource.from_payload(i) for i in payload.get("learned_by_pokemon", [])],
            flavor_text_entries=[MoveFlavorText.from_payload(i) for i in payload.get("flavor_text_entries", [])],
            generation=NamedResource.from_payload(payload.get("generation", {}) or {}),
            machines=[MachineVersionDetail.from_payload(i) for i in payload.get("machines", [])],
            meta=MoveMetaData.from_payload(payload.get("meta", {}) or {}),
            names=[Name.from_payload(i) for i in payload.get("names", [])],
            past_values=[PastMoveStatValues.from_payload(i) for i in payload.get("past_values", [])],
            stat_changes=[MoveStatChange.from_payload(i) for i in payload.get("stat_changes", [])],
            super_contest_effect=Resource.from_payload(payload.get("super_contest_effect", {}) or {}),
            target=NamedResource.from_payload(payload.get("target", {}) or {}),
            type=NamedResource.from_payload(payload.get("type", {}) or {}),
        )


@attrs.define(slots=True, kw_only=True)
class MoveAilment(BaseModel):
    """
    MoveAilment models the data returned by the API for a move ailment.

    Attributes
    ----------
    id: int
        The identifier for this resource.
    name: str
        The name for this resource.
    moves: t.List[NamedResource]
        A list of moves that cause this ailment.
    names: t.List[Name]
        The name of this resource listed in different languages.
    """

    id: int = attrs.field(factory=int)
    name: str = attrs.field(factory=str)
    moves: t.List[NamedResource] = attrs.field(factory=list)
    names: t.List[Name] = attrs.field(factory=list)

    @classmethod
    def from_payload(cls, payload: t.Dict[str, t.Any]) -> "MoveAilment":
        return cls(
            id=payload.get("id", 0),
            name=payload.get("name", ""),
            moves=[NamedResource.from_payload(i) for i in payload.get("moves", [])],
            names=[Name.from_payload(i) for i in payload.get("names", [])],
        )


@attrs.define(slots=True, kw_only=True)
class MoveBattleStyle(BaseModel):
    """
    MoveBattleStyle models the data returned by the API for a move battle style.

    Attributes
    ----------
    id: int
        The identifier for this resource.
    name: str
        The name for this resource.
    names: t.List[Name]
        The name of this resource listed in different languages.
    """

    id: int = attrs.field(factory=int)
    name: str = attrs.field(factory=str)
    names: t.List[Name] = attrs.field(factory=list)

    @classmethod
    def from_payload(cls, payload: t.Dict[str, t.Any]) -> "MoveBattleStyle":
        return cls(
            id=payload.get("id", 0),
            name=payload.get("name", ""),
            names=[Name.from_payload(i) for i in payload.get("names", [])],
        )


@attrs.define(slots=True, kw_only=True)
class MoveCategory(BaseModel):
    """
    MoveCategory models the data returned by the API for a move category.

    Attributes
    ----------
    id: int
        The identifier for this resource.
    name: str
        The name for this resource.
    moves: t.List[NamedResource]
        A list of moves that fall into this category.
    descriptions: t.List[Description]
        The description of this resource listed in different languages.
    """

    id: int = attrs.field(factory=int)
    name: str = attrs.field(factory=str)
    moves: t.List[NamedResource] = attrs.field(factory=list)
    descriptions: t.List[Description] = attrs.field(factory=list)

    @classmethod
    def from_payload(cls, payload: t.Dict[str, t.Any]) -> "MoveCategory":
        return cls(
            id=payload.get("id", 0),
            name=payload.get("name", ""),
            moves=[NamedResource.from_payload(i) for i in payload.get("moves", [])],
            descriptions=[Description.from_payload(i) for i in payload.get("descriptions", [])],
        )


@attrs.define(slots=True, kw_only=True)
class MoveDamageClass(BaseModel):
    """
    MoveDamageClass models the data returned by the API for a move damage class.

    Attributes
    ----------
    id: int
        The identifier for this resource.
    name: str
        The name for this resource.
    descriptions: t.List[Description]
        The description of this resource listed in different languages.
    moves: t.List[NamedResource]
        A list of moves that fall into this damage class.
    names: t.List[Name]
        The name of this resource listed in different languages.
    """

    id: int = attrs.field(factory=int)
    name: str = attrs.field(factory=str)
    descriptions: t.List[Description] = attrs.field(factory=list)
    moves: t.List[NamedResource] = attrs.field(factory=list)
    names: t.List[Name] = attrs.field(factory=list)

    @classmethod
    def from_payload(cls, payload: t.Dict[str, t.Any]) -> "MoveDamageClass":
        return cls(
            id=payload.get("id", 0),
            name=payload.get("name", ""),
            descriptions=[Description.from_payload(i) for i in payload.get("descriptions", [])],
            moves=[NamedResource.from_payload(i) for i in payload.get("moves", [])],
            names=[Name.from_payload(i) for i in payload.get("names", [])],
        )


@attrs.define(slots=True, kw_only=True)
class MoveLearnMethod(BaseModel):
    """
    MoveLearnMethod models the data returned by the API for a move learn method.

    Attributes
    ----------
    id: int
        The identifier for this resource.
    name: str
        The name for this resource.
    descriptions: t.List[Description]
        The description of this resource listed in different languages.
    names: t.List[Name]
        The name of this resource listed in different languages.
    version_groups: t.List[NamedResource]
        A list of version groups where moves can be learned through this method.
    """

    id: int = attrs.field(factory=int)
    name: str = attrs.field(factory=str)
    descriptions: t.List[Description] = attrs.field(factory=list)
    names: t.List[Name] = attrs.field(factory=list)
    version_groups: t.List[NamedResource] = attrs.field(factory=list)

    @classmethod
    def from_payload(cls, payload: t.Dict[str, t.Any]) -> "MoveLearnMethod":
        return cls(
            id=payload.get("id", 0),
            name=payload.get("name", ""),
            descriptions=[Description.from_payload(i) for i in payload.get("descriptions", [])],
            names=[Name.from_payload(i) for i in payload.get("names", [])],
            version_groups=[NamedResource.from_payload(i) for i in payload.get("version_groups", [])],
        )


@attrs.define(slots=True, kw_only=True)
class MoveTarget(BaseModel):
    id: int = attrs.field(factory=int)
    name: str = attrs.field(factory=str)
    descriptions: t.List[Description] = attrs.field(factory=list)
    moves: t.List[NamedResource] = attrs.field(factory=list)
    names: t.List[Name] = attrs.field(factory=list)

    @classmethod
    def from_payload(cls, payload: t.Dict[str, t.Any]) -> "MoveTarget":
        return cls(
            id=payload.get("id", 0),
            name=payload.get("name", ""),
            descriptions=[Description.from_payload(i) for i in payload.get("descriptions", [])],
            moves=[NamedResource.from_payload(i) for i in payload.get("moves", [])],
            names=[Name.from_payload(i) for i in payload.get("names", [])],
        )
