import typing as t

import attrs

from pokelance.models import BaseModel
from pokelance.models.common import Effect, FlavorText, NamedResource

from .utils import ContestName

__all__: t.Tuple[str, ...] = (
    "ContestType",
    "ContestEffect",
    "SuperContestEffect",
)


@attrs.define(slots=True, kw_only=True)
class ContestType(BaseModel):
    """A contest type resource.

    Attributes
    ----------
    id: int
        The identifier for this contest type resource.
    name: str
        The name for this contest type resource.
    berry_flavor: pokelance.models.common.NamedResource
        The berry flavor that correlates with this contest type.
    names: typing.List[pokelance.models.common.Name]
        The name of this contest type listed in different languages.
    """

    id: int = attrs.field(factory=int)
    name: str = attrs.field(factory=str)
    berry_flavor: NamedResource = attrs.field(factory=NamedResource)
    names: t.List[ContestName] = attrs.field(factory=list)

    @classmethod
    def from_payload(cls, payload: t.Dict[str, t.Any]) -> "ContestType":
        return cls(
            id=payload.get("id", 0),
            name=payload.get("name", ""),
            berry_flavor=NamedResource.from_payload(payload.get("berry_flavor", {}) or {}),
            names=[ContestName.from_payload(name) for name in payload.get("names", [])],
        )


@attrs.define(slots=True, kw_only=True)
class ContestEffect(BaseModel):
    """A contest effect resource.

    Attributes
    ----------
    id: int
        The identifier for this contest effect resource.
    appeal: int
        The base number of hearts the user of this move gets.
    jam: int
        The base number of hearts the user's opponent loses.
    effect_entries: typing.List[pokelance.models.common.Effect]
        The result of this contest effect listed in different languages.
    flavor_text_entries: typing.List[pokelance.models.common.FlavorText]
        The flavor text of this contest effect listed in different languages.
    """

    id: int = attrs.field(factory=int)
    appeal: int = attrs.field(factory=int)
    jam: int = attrs.field(factory=int)
    effect_entries: t.List[Effect] = attrs.field(factory=list)
    flavor_text_entries: t.List[FlavorText] = attrs.field(factory=list)

    @classmethod
    def from_payload(cls, payload: t.Dict[str, t.Any]) -> "ContestEffect":
        return cls(
            id=payload.get("id", 0),
            appeal=payload.get("appeal", 0),
            jam=payload.get("jam", 0),
            effect_entries=[Effect.from_payload(effect) for effect in payload.get("effect_entries", [])],
            flavor_text_entries=[
                FlavorText.from_payload(flavor_text) for flavor_text in payload.get("flavor_text_entries", [])
            ],
        )


@attrs.define(slots=True, kw_only=True)
class SuperContestEffect(BaseModel):
    """A super contest effect resource.

    Attributes
    ----------
    id: int
        The identifier for this super contest effect resource.
    appeal: int
        The level of appeal this super contest effect has.
    flavor_text_entries: typing.List[pokelance.models.common.FlavorText]
        The flavor text of this super contest effect listed in different languages.
    moves: typing.List[pokelance.models.common.NamedResource]
        A list of moves that have the effect when used in super contests.
    """

    id: int = attrs.field(factory=int)
    appeal: int = attrs.field(factory=int)
    flavor_text_entries: t.List[FlavorText] = attrs.field(factory=list)
    moves: t.List[NamedResource] = attrs.field(factory=list)

    @classmethod
    def from_payload(cls, payload: t.Dict[str, t.Any]) -> "SuperContestEffect":
        return cls(
            id=payload.get("id", 0),
            appeal=payload.get("appeal", 0),
            flavor_text_entries=[
                FlavorText.from_payload(flavor_text) for flavor_text in payload.get("flavor_text_entries", [])
            ],
            moves=[NamedResource.from_payload(move) for move in payload.get("moves", [])],
        )
