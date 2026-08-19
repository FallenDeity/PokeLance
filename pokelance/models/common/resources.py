import typing as t

import attrs
from typing_extensions import override

from pokelance.models import BaseModel

__all__: tuple[str, ...] = (
    "NamedResource",
    "Resource",
)


@attrs.define(slots=True, kw_only=True)
class Resource(BaseModel):
    """Model for a resource object

    Attributes
    ----------
    url: str
        The URL of the referenced resource.
    """

    url: str = attrs.field(factory=str)

    @classmethod
    @override
    def from_payload(cls, payload: dict[str, t.Any]) -> "Resource":
        return cls(
            raw=payload,
            url=payload.get("url", ""),
        )


@attrs.define(slots=True, kw_only=True)
class NamedResource(BaseModel):
    """Model for a named resource object

    Attributes
    ----------
    name: str
        The name of the referenced resource.
    url: str
        The URL of the referenced resource.
    """

    name: str = attrs.field(factory=str)
    url: str = attrs.field(factory=str)

    @classmethod
    @override
    def from_payload(cls, payload: dict[str, str]) -> "NamedResource":
        return cls(raw=payload, name=payload.get("name", ""), url=payload.get("url", ""))
