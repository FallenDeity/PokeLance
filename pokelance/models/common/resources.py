import typing as t

import attrs

from pokelance.models import BaseModel

__all__: t.Tuple[str, ...] = (
    "Resource",
    "NamedResource",
)


@attrs.define(slots=True, kw_only=True)
class Resource(BaseModel):
    url: str = attrs.field(factory=str)


@attrs.define(slots=True, kw_only=True)
class NamedResource(BaseModel):
    name: str = attrs.field(factory=str)
    url: str = attrs.field(factory=str)

    @classmethod
    def from_payload(cls, payload: t.Dict[str, str]) -> "NamedResource":
        return cls(name=payload.get("name", ""), url=payload.get("url", ""))
