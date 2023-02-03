import typing as t

import attrs

from pokelance.models import BaseModel
from pokelance.models.common import NamedResource

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
    use_before: NamedResource
        A detail of moves this move can be used before, i.e. leading into this move.
    use_after: NamedResource
        A detail of moves this move can be used after, i.e. result in this move being used.
    """

    use_before: t.List[NamedResource] = attrs.field(factory=list)
    use_after: t.List[NamedResource] = attrs.field(factory=list)

    @classmethod
    def from_payload(cls, payload: t.Dict[str, t.Any]) -> "ContestComboDetail":
        return cls(
            use_before=[NamedResource.from_payload(i or {}) for i in (payload.get("use_before", []) or [])],
            use_after=[NamedResource.from_payload(i or {}) for i in (payload.get("use_after", []) or [])],
        )


@attrs.define(slots=True, kw_only=True)
class ContestComboSet(BaseModel):
    """A contest combo set resource.

    Attributes
    ----------
    normal: ContestComboDetail
        A detail of normal moves in a contest combo.
    super_: ContestComboDetail
        A detail of super moves in a contest combo.
    """

    normal: ContestComboDetail = attrs.field(factory=ContestComboDetail)
    super_: ContestComboDetail = attrs.field(factory=ContestComboDetail)

    @classmethod
    def from_payload(cls, payload: t.Dict[str, t.Any]) -> "ContestComboSet":
        return cls(
            normal=ContestComboDetail.from_payload(payload.get("normal", {}) or {}),
            super_=ContestComboDetail.from_payload(payload.get("super", {}) or {}),
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
            flavor_text=payload.get("flavor_text", ""),
            language=NamedResource.from_payload(payload.get("language", {}) or {}),
            version_group=NamedResource.from_payload(payload.get("version_group", {}) or {}),
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
    min_hits: int
        The minimum number of times this move hits. Null if it always only hits once.
    max_hits: int
        The maximum number of times this move hits. Null if it always only hits once.
    min_turns: int
        The minimum number of turns this move continues to take effect. Null if it always only lasts one turn.
    max_turns: int
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
    min_hits: int = attrs.field(factory=int)
    max_hits: int = attrs.field(factory=int)
    min_turns: int = attrs.field(factory=int)
    max_turns: int = attrs.field(factory=int)
    drain: int = attrs.field(factory=int)
    healing: int = attrs.field(factory=int)
    crit_rate: int = attrs.field(factory=int)
    ailment_chance: int = attrs.field(factory=int)
    flinch_chance: int = attrs.field(factory=int)
    stat_chance: int = attrs.field(factory=int)

    @classmethod
    def from_payload(cls, payload: t.Dict[str, t.Any]) -> "MoveMetaData":
        return cls(
            ailment=NamedResource.from_payload(payload.get("ailment", {}) or {}),
            category=NamedResource.from_payload(payload.get("category", {}) or {}),
            min_hits=payload.get("min_hits", 0) or 1,
            max_hits=payload.get("max_hits", 0) or 1,
            min_turns=payload.get("min_turns", 0) or 1,
            max_turns=payload.get("max_turns", 0) or 1,
            drain=payload.get("drain", 0),
            healing=payload.get("healing", 0),
            crit_rate=payload.get("crit_rate", 0),
            ailment_chance=payload.get("ailment_chance", 0),
            flinch_chance=payload.get("flinch_chance", 0),
            stat_chance=payload.get("stat_chance", 0),
        )


@attrs.define(slots=True, kw_only=True)
class MoveStatChange(BaseModel):
    change: int = attrs.field(factory=int)
    stat: NamedResource = attrs.field(factory=NamedResource)

    @classmethod
    def from_payload(cls, payload: t.Dict[str, t.Any]) -> "MoveStatChange":
        return cls(
            change=payload.get("change", 0),
            stat=NamedResource.from_payload(payload.get("stat", {}) or {}),
        )


@attrs.define(slots=True, kw_only=True)
class PastMoveStatValues(BaseModel):
    accuracy: int = attrs.field(factory=int)
    effect_chance: int = attrs.field(factory=int)
    power: int = attrs.field(factory=int)
    pp: int = attrs.field(factory=int)
    effect_entries: t.List[NamedResource] = attrs.field(factory=list)
    type: NamedResource = attrs.field(factory=NamedResource)
    version_group: NamedResource = attrs.field(factory=NamedResource)

    @classmethod
    def from_payload(cls, payload: t.Dict[str, t.Any]) -> "PastMoveStatValues":
        return cls(
            accuracy=payload.get("accuracy", 0),
            effect_chance=payload.get("effect_chance", 0),
            power=payload.get("power", 0),
            pp=payload.get("pp", 0),
            effect_entries=[NamedResource.from_payload(i) for i in payload.get("effect_entries", [])],
            type=NamedResource.from_payload(payload.get("type", {}) or {}),
            version_group=NamedResource.from_payload(payload.get("version_group", {}) or {}),
        )
