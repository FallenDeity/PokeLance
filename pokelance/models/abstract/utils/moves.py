import typing as t

import attrs

from pokelance.models import BaseModel
from pokelance.models.common import NamedResource, VerboseEffect

__all__: t.Tuple[str, ...] = (
    "ContestComboSet",
    "ContestComboDetail",
    "MoveFlavorText",
    "MoveMetaData",
    "MoveStatChange",
    "PastMoveStatValues",
)


@attrs.define(slots=True, kw_only=True)
class ContestComboDetail(BaseModel):
    """A contest combo detail resource.

    Attributes
    ----------
    use_before: t.Optional[t.List[NamedResource]]
        A detail of moves this move can be used before, i.e. leading into this move.
    use_after: t.Optional[t.List[NamedResource]]
        A detail of moves this move can be used after, i.e. result in this move being used.
    """

    use_before: t.Optional[t.List[NamedResource]] = attrs.field(default=None)
    use_after: t.Optional[t.List[NamedResource]] = attrs.field(default=None)

    @classmethod
    def from_payload(cls, payload: t.Dict[str, t.Any]) -> "ContestComboDetail":
        return cls(
            raw=payload,
            use_before=[NamedResource.from_payload(i) for i in ub] if (ub := payload.get("use_before")) else None,
            use_after=[NamedResource.from_payload(i) for i in ua] if (ua := payload.get("use_after")) else None,
        )


@attrs.define(slots=True, kw_only=True)
class ContestComboSet(BaseModel):
    """A contest combo set resource.

    Attributes
    ----------
    normal: ContestComboDetail
        A detail of normal moves in a contest combo.
    super: ContestComboDetail
        A detail of super moves in a contest combo.
    """

    normal: ContestComboDetail = attrs.field(factory=ContestComboDetail)
    super: ContestComboDetail = attrs.field(factory=ContestComboDetail)

    @classmethod
    def from_payload(cls, payload: t.Dict[str, t.Any]) -> "ContestComboSet":
        return cls(
            raw=payload,
            normal=ContestComboDetail.from_payload(payload.get("normal", {})),
            super=ContestComboDetail.from_payload(payload.get("super", {})),
        )


@attrs.define(slots=True, kw_only=True)
class MoveFlavorText(BaseModel):
    """A move flavor text resource.

    Attributes
    ----------
    flavor_text: str
        The localized flavor text for an api resource in a specific language.
    language: NamedResource
        The language this name is in.
    version_group: NamedResource
        The version group that uses this flavor text.
    """

    flavor_text: str = attrs.field(factory=str)
    language: NamedResource = attrs.field(factory=NamedResource)
    version_group: NamedResource = attrs.field(factory=NamedResource)

    @classmethod
    def from_payload(cls, payload: t.Dict[str, t.Any]) -> "MoveFlavorText":
        return cls(
            raw=payload,
            flavor_text=payload.get("flavor_text", ""),
            language=NamedResource.from_payload(payload.get("language", {})),
            version_group=NamedResource.from_payload(payload.get("version_group", {})),
        )


@attrs.define(slots=True, kw_only=True)
class MoveMetaData(BaseModel):
    """A move meta data resource.

    Attributes
    ----------
    ailment: NamedResource
        The status ailment this move inflicts on its target.
    category: NamedResource
        The category of move this move falls under, e.g. damage or ailment.
    min_hits: t.Optional[int]
        The minimum number of times this move hits. Null if it always only hits once.
    max_hits: t.Optional[int]
        The maximum number of times this move hits. Null if it always only hits once.
    min_turns: t.Optional[int]
        The minimum number of turns this move continues to take effect. Null if it always only lasts one turn.
    max_turns: t.Optional[int]
        The maximum number of turns this move continues to take effect. Null if it always only lasts one turn.
    drain: int
        HP drain (if positive) or Recoil damage (if negative), in percent of damage done.
    healing: int
        The amount of hp gained by the attacking Pokemon, in percent of it's maximum HP.
    crit_rate: int
        Critical hit rate bonus.
    ailment_chance: int
        The likelihood this attack will cause an ailment.
    flinch_chance: int
        The likelihood this attack will cause the target Pokémon to flinch.
    stat_chance: int
        The likelihood this attack will cause a stat change in the target Pokémon.
    """

    ailment: NamedResource = attrs.field(factory=NamedResource)
    category: NamedResource = attrs.field(factory=NamedResource)
    min_hits: t.Optional[int] = attrs.field(default=None)
    max_hits: t.Optional[int] = attrs.field(default=None)
    min_turns: t.Optional[int] = attrs.field(default=None)
    max_turns: t.Optional[int] = attrs.field(default=None)
    drain: int = attrs.field(factory=int)
    healing: int = attrs.field(factory=int)
    crit_rate: int = attrs.field(factory=int)
    ailment_chance: int = attrs.field(factory=int)
    flinch_chance: int = attrs.field(factory=int)
    stat_chance: int = attrs.field(factory=int)

    @classmethod
    def from_payload(cls, payload: t.Dict[str, t.Any]) -> "MoveMetaData":
        return cls(
            raw=payload,
            ailment=NamedResource.from_payload(payload.get("ailment", {})),
            category=NamedResource.from_payload(payload.get("category", {})),
            min_hits=payload.get("min_hits"),
            max_hits=payload.get("max_hits"),
            min_turns=payload.get("min_turns"),
            max_turns=payload.get("max_turns"),
            drain=payload.get("drain", 0),
            healing=payload.get("healing", 0),
            crit_rate=payload.get("crit_rate", 0),
            ailment_chance=payload.get("ailment_chance", 0),
            flinch_chance=payload.get("flinch_chance", 0),
            stat_chance=payload.get("stat_chance", 0),
        )


@attrs.define(slots=True, kw_only=True)
class MoveStatChange(BaseModel):
    """A move stat change resource.

    Attributes
    ----------
    change: int
        The amount of change.
    stat: NamedResource
        The stat being affected.
    """

    change: int = attrs.field(factory=int)
    stat: NamedResource = attrs.field(factory=NamedResource)

    @classmethod
    def from_payload(cls, payload: t.Dict[str, t.Any]) -> "MoveStatChange":
        return cls(
            raw=payload,
            change=payload.get("change", 0),
            stat=NamedResource.from_payload(payload.get("stat", {})),
        )


@attrs.define(slots=True, kw_only=True)
class PastMoveStatValues(BaseModel):
    """A past move stat values resource.

    Attributes
    ----------
    accuracy: t.Optional[int]
        The accuracy of this move.
    effect_chance: t.Optional[int]
        The chance of this move causing an effect.
    power: t.Optional[int]
        The power of this move.
    pp: t.Optional[int]
        The amount of PP this move has.
    effect_entries: t.List[VerboseEffect]
        The effect of this move listed in different languages.
    type: t.Optional[NamedResource]
        The type of this move.
    version_group: NamedResource
        The version group in which these move stat values were in effect.
    """

    accuracy: t.Optional[int] = attrs.field(default=None)
    effect_chance: t.Optional[int] = attrs.field(default=None)
    power: t.Optional[int] = attrs.field(default=None)
    pp: t.Optional[int] = attrs.field(default=None)
    effect_entries: t.List[VerboseEffect] = attrs.field(factory=list)
    type: t.Optional[NamedResource] = attrs.field(default=None)
    version_group: NamedResource = attrs.field(factory=NamedResource)

    @classmethod
    def from_payload(cls, payload: t.Dict[str, t.Any]) -> "PastMoveStatValues":
        return cls(
            raw=payload,
            accuracy=payload.get("accuracy"),
            effect_chance=payload.get("effect_chance"),
            power=payload.get("power"),
            pp=payload.get("pp"),
            effect_entries=[VerboseEffect.from_payload(i) for i in payload.get("effect_entries", [])],
            type=NamedResource.optional_from_payload(payload.get("type")),
            version_group=NamedResource.from_payload(payload.get("version_group", {})),
        )
