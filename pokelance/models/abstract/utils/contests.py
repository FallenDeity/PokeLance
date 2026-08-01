import typing as t

import attrs

from pokelance.models import BaseModel
from pokelance.models.common import NamedResource

__all__: t.Tuple[str, ...] = (
    "ContestName",
    "ContestEffectFlavorText",
    "SuperContestEffectFlavorText",
)


@attrs.define(slots=True, kw_only=True)
class ContestName(BaseModel):
    """A contest name resource.

    Attributes
    ----------
    name: str
        The name for this contest.
    color: str
        The color associated with this contest's name.
    language: NamedResource
        The language that this name is in.
    """

    name: str = attrs.field(factory=str)
    color: str = attrs.field(factory=str)
    language: NamedResource = attrs.field(factory=NamedResource)

    @classmethod
    def from_payload(cls, payload: t.Dict[str, t.Any]) -> "ContestName":
        return cls(
            raw=payload,
            name=payload.get("name", ""),
            color=payload.get("color", ""),
            language=NamedResource.from_payload(payload.get("language", {})),
        )


@attrs.define(slots=True, kw_only=True)
class ContestEffectFlavorText(BaseModel):
    """A contest effect flavor text resource.

    Attributes
    ----------
    flavor_text: str
        The flavor text for this contest effect.
    language: NamedResource
        The language that this name is in.
    """

    flavor_text: str = attrs.field(factory=str)
    language: NamedResource = attrs.field(factory=NamedResource)

    @classmethod
    def from_payload(cls, payload: t.Dict[str, t.Any]) -> "ContestEffectFlavorText":
        return cls(
            raw=payload,
            flavor_text=payload.get("flavor_text", ""),
            language=NamedResource.from_payload(payload.get("language", {})),
        )


@attrs.define(slots=True, kw_only=True)
class SuperContestEffectFlavorText(BaseModel):
    """A super contest effect flavor text resource.

    Attributes
    ----------
    flavor_text: str
        The flavor text for this super contest effect.
    language: NamedResource
        The language that this name is in.
    """

    flavor_text: str = attrs.field(factory=str)
    language: NamedResource = attrs.field(factory=NamedResource)

    @classmethod
    def from_payload(cls, payload: t.Dict[str, t.Any]) -> "SuperContestEffectFlavorText":
        return cls(
            raw=payload,
            flavor_text=payload.get("flavor_text", ""),
            language=NamedResource.from_payload(payload.get("language", {})),
        )
