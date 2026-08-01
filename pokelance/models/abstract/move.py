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
    accuracy: t.Optional[int]
        The percent value of how likely this move is to be successful.
    effect_chance: t.Optional[int]
        The percent value of how likely it is this moves effect will take effect.
    pp: t.Optional[int]
        Power points. The number of times this move can be used.
    priority: int
        A value between -8 and 8. Sets the order in which moves
        are executed during battle. See Bulbapedia for greater detail.
    power: t.Optional[int]
        The base power of this move with a value of 0 if it does not have a base power.
    contest_combos: t.Optional[ContestComboSet]
        A detail of normal and super contest combos that require this move.
    contest_type: t.Optional[NamedResource]
        The type of appeal this move gives a Pokémon when used in a contest.
    contest_effect: t.Optional[Resource]
        The effect the move has when used in a contest.
    damage_class: NamedResource
        The type of damage the move inflicts on the target, e.g. physical.
    effect_entries: t.List[VerboseEffect]
        The effect of this move listed in different languages.
    effect_changes: t.List[AbilityEffectChange]
        The list of previous effects this move has had across version groups of the games.
    learned_by_pokemon: t.List[NamedResource]
        A list of Pokémon that can learn this move.
    flavor_text_entries: t.List[MoveFlavorText]
        The flavor text of this move listed in different languages.
    generation: NamedResource
        The generation in which this move was introduced.
    machines: t.List[MachineVersionDetail]
        A list of the machines that teach this move.
    meta: t.Optional[MoveMetaData]
        Metadata about this move.
    names: t.List[Name]
        The name of this resource listed in different languages.
    past_values: t.List[PastMoveStatValues]
        A list of move resource value changes across version groups of the games.
    stat_changes: t.List[MoveStatChange]
        A list of stats this moves effects and how much it effects them.
    super_contest_effect: t.Optional[Resource]
        The effect the move has when used in a super contest.
    target: NamedResource
        The type of target that will receive the effects of the attack.
    type: NamedResource
        The elemental type of this move.
    """

    id: int = attrs.field(factory=int)
    name: str = attrs.field(factory=str)
    accuracy: t.Optional[int] = attrs.field(default=None)
    effect_chance: t.Optional[int] = attrs.field(default=None)
    pp: t.Optional[int] = attrs.field(default=None)
    priority: int = attrs.field(factory=int)
    power: t.Optional[int] = attrs.field(default=None)
    contest_combos: t.Optional[ContestComboSet] = attrs.field(default=None)
    contest_type: t.Optional[NamedResource] = attrs.field(default=None)
    contest_effect: t.Optional[Resource] = attrs.field(default=None)
    damage_class: NamedResource = attrs.field(factory=NamedResource)
    effect_entries: t.List[VerboseEffect] = attrs.field(factory=list)
    effect_changes: t.List[AbilityEffectChange] = attrs.field(factory=list)
    learned_by_pokemon: t.List[NamedResource] = attrs.field(factory=list)
    flavor_text_entries: t.List[MoveFlavorText] = attrs.field(factory=list)
    generation: NamedResource = attrs.field(factory=NamedResource)
    machines: t.List[MachineVersionDetail] = attrs.field(factory=list)
    meta: t.Optional[MoveMetaData] = attrs.field(default=None)
    names: t.List[Name] = attrs.field(factory=list)
    past_values: t.List[PastMoveStatValues] = attrs.field(factory=list)
    stat_changes: t.List[MoveStatChange] = attrs.field(factory=list)
    super_contest_effect: t.Optional[Resource] = attrs.field(default=None)
    target: NamedResource = attrs.field(factory=NamedResource)
    type: NamedResource = attrs.field(factory=NamedResource)

    @classmethod
    def from_payload(cls, payload: t.Dict[str, t.Any]) -> "Move":
        return cls(
            raw=payload,
            id=payload.get("id", 0),
            name=payload.get("name", ""),
            accuracy=payload.get("accuracy"),
            effect_chance=payload.get("effect_chance"),
            pp=payload.get("pp"),
            priority=payload.get("priority", 0),
            power=payload.get("power"),
            contest_combos=ContestComboSet.optional_from_payload(payload.get("contest_combos")),
            contest_type=NamedResource.optional_from_payload(payload.get("contest_type")),
            contest_effect=Resource.optional_from_payload(payload.get("contest_effect")),
            damage_class=NamedResource.from_payload(payload.get("damage_class", {})),
            effect_entries=[VerboseEffect.from_payload(i) for i in payload.get("effect_entries", [])],
            effect_changes=[AbilityEffectChange.from_payload(i) for i in payload.get("effect_changes", [])],
            learned_by_pokemon=[NamedResource.from_payload(i) for i in payload.get("learned_by_pokemon", [])],
            flavor_text_entries=[MoveFlavorText.from_payload(i) for i in payload.get("flavor_text_entries", [])],
            generation=NamedResource.from_payload(payload.get("generation", {})),
            machines=[MachineVersionDetail.from_payload(i) for i in payload.get("machines", [])],
            meta=MoveMetaData.optional_from_payload(payload.get("meta")),
            names=[Name.from_payload(i) for i in payload.get("names", [])],
            past_values=[PastMoveStatValues.from_payload(i) for i in payload.get("past_values", [])],
            stat_changes=[MoveStatChange.from_payload(i) for i in payload.get("stat_changes", [])],
            super_contest_effect=Resource.optional_from_payload(payload.get("super_contest_effect")),
            target=NamedResource.from_payload(payload.get("target", {})),
            type=NamedResource.from_payload(payload.get("type", {})),
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
            raw=payload,
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
            raw=payload,
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
            raw=payload,
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
            raw=payload,
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
            raw=payload,
            id=payload.get("id", 0),
            name=payload.get("name", ""),
            descriptions=[Description.from_payload(i) for i in payload.get("descriptions", [])],
            names=[Name.from_payload(i) for i in payload.get("names", [])],
            version_groups=[NamedResource.from_payload(i) for i in payload.get("version_groups", [])],
        )


@attrs.define(slots=True, kw_only=True)
class MoveTarget(BaseModel):
    """
    MoveTarget models the data returned by the API for a move target.

    Attributes
    ----------
    id: int
        The identifier for this resource.
    name: str
        The name for this resource.
    descriptions: t.List[Description]
        The description of this resource listed in different languages.
    moves: t.List[NamedResource]
        A list of moves that target this move target.
    names: t.List[Name]
        The name of this resource listed in different languages.
    """

    id: int = attrs.field(factory=int)
    name: str = attrs.field(factory=str)
    descriptions: t.List[Description] = attrs.field(factory=list)
    moves: t.List[NamedResource] = attrs.field(factory=list)
    names: t.List[Name] = attrs.field(factory=list)

    @classmethod
    def from_payload(cls, payload: t.Dict[str, t.Any]) -> "MoveTarget":
        return cls(
            raw=payload,
            id=payload.get("id", 0),
            name=payload.get("name", ""),
            descriptions=[Description.from_payload(i) for i in payload.get("descriptions", [])],
            moves=[NamedResource.from_payload(i) for i in payload.get("moves", [])],
            names=[Name.from_payload(i) for i in payload.get("names", [])],
        )
