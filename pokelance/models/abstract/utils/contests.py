import typing as t

import attrs

from pokelance.models import BaseModel
from pokelance.models.common import NamedResource

__all__: t.Tuple[str, ...] = ("ContestName",)


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
            name=payload.get("name", ""),
            color=payload.get("color", ""),
            language=NamedResource.from_payload(payload.get("language", {}) or {}),
        )
