import typing as t

import attrs

from pokelance.models import BaseModel
from pokelance.models.common import Name, NamedResource

__all__: t.Tuple[str, ...] = (
    "EncounterMethod",
    "EncounterCondition",
    "EncounterConditionValue",
)


@attrs.define(slots=True, kw_only=True)
class EncounterMethod(BaseModel):
    """An encounter method resource.

    Attributes
    ----------
    id: int
        The identifier for this encounter method resource.
    name: str
        The name for this encounter method resource.
    order: int
        A good value for sorting.
    names: typing.List[pokelance.models.common.Name]
        The name of this encounter method listed in different languages.
    """

    id: int = attrs.field(factory=int)
    name: str = attrs.field(factory=str)
    order: int = attrs.field(factory=int)
    names: t.List[Name] = attrs.field(factory=list)

    @classmethod
    def from_payload(cls, payload: t.Dict[str, t.Any]) -> "EncounterMethod":
        return cls(
            id=payload.get("id", 0),
            name=payload.get("name", ""),
            order=payload.get("order", 0),
            names=[Name.from_payload(name) for name in payload.get("names", [])],
        )


@attrs.define(slots=True, kw_only=True)
class EncounterCondition(BaseModel):
    """An encounter condition resource.

    Attributes
    ----------
    id: int
        The identifier for this encounter condition resource.
    name: str
        The name for this encounter condition resource.
    names: typing.List[pokelance.models.common.Name]
        The name of this encounter condition listed in different languages.
    values: typing.List[pokelance.models.common.NamedResource]
        A list of possible values for this encounter condition.
    """

    id: int = attrs.field(factory=int)
    name: str = attrs.field(factory=str)
    names: t.List[Name] = attrs.field(factory=list)
    values: t.List[NamedResource] = attrs.field(factory=list)

    @classmethod
    def from_payload(cls, payload: t.Dict[str, t.Any]) -> "EncounterCondition":
        return cls(
            id=payload.get("id", 0),
            name=payload.get("name", ""),
            names=[Name.from_payload(name) for name in payload.get("names", [])],
            values=[NamedResource.from_payload(value) for value in payload.get("values", [])],
        )


@attrs.define(slots=True, kw_only=True)
class EncounterConditionValue(BaseModel):
    """An encounter condition value resource.

    Attributes
    ----------
    id: int
        The identifier for this encounter condition value resource.
    name: str
        The name for this encounter condition value resource.
    condition: pokelance.models.common.NamedResource
        The condition this encounter condition value pertains to.
    names: typing.List[pokelance.models.common.Name]
        The name of this encounter condition value listed in different languages.
    """

    id: int = attrs.field(factory=int)
    name: str = attrs.field(factory=str)
    condition: NamedResource = attrs.field(factory=NamedResource)
    names: t.List[Name] = attrs.field(factory=list)

    @classmethod
    def from_payload(cls, payload: t.Dict[str, t.Any]) -> "EncounterConditionValue":
        return cls(
            id=payload.get("id", 0),
            name=payload.get("name", ""),
            condition=NamedResource.from_payload(payload.get("condition", {}) or {}),
            names=[Name.from_payload(name) for name in payload.get("names", [])],
        )
