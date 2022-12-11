import typing as t

import attrs

from pokelance.models import BaseModel

__all__: t.Tuple[str, ...] = (
    "Resource",
    "NamedResource",
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
    def from_payload(cls, payload: t.Dict[str, t.Any]) -> "Resource":
        return cls(
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
    def from_payload(cls, payload: t.Dict[str, str]) -> "NamedResource":
        return cls(name=payload.get("name", ""), url=payload.get("url", ""))
