import typing as t

import attrs

from pokelance.models import BaseModel
from pokelance.models.common import Name, NamedResource

from .utils import BerryFlavorMap, FlavorBerryMap

__all__: t.Tuple[str, ...] = (
    "Berry",
    "BerryFirmness",
    "BerryFlavor",
)


@attrs.define(slots=True, kw_only=True)
class Berry(BaseModel):
    """A berry resource.

    Attributes
    ----------
    id: int
        The identifier for this berry resource.
    name: str
        The name for this berry resource.
    growth_time: t.Optional[int]
        Time it takes the tree to grow one stage, in hours. Berry trees go through
        four of these growth stages before they can be picked.
    max_harvest: t.Optional[int]
        The maximum number of these berries that can grow on one tree in Generation
        IV.
    natural_gift_power: t.Optional[int]
        The power of the move "Natural Gift" when used with this Berry.
    size: t.Optional[int]
        Berries are actually items. This is the number of those items.
    smoothness: t.Optional[int]
        The speed at which this Berry dries out the soil as it grows. A higher
        rate means the soil dries more quickly.
    soil_dryness: t.Optional[int]
        The firmness of this berry, used in making Pokéblocks or Poffins.
    firmness: t.Optional[NamedResource]
        The firmness of this berry.
    flavors: t.List[BerryFlavorMap]
        A list of references to each flavor a berry can have and the potency of
        each of those flavors in regard to this berry.
    item: NamedResource
        The item that corresponds to this berry.
    natural_gift_type: t.Optional[NamedResource]
        The type inherited by "Natural Gift" when used with this Berry.
    """

    id: int = attrs.field(factory=int)
    name: str = attrs.field(factory=str)
    growth_time: t.Optional[int] = attrs.field(default=None)
    max_harvest: t.Optional[int] = attrs.field(default=None)
    natural_gift_power: t.Optional[int] = attrs.field(default=None)
    size: t.Optional[int] = attrs.field(default=None)
    smoothness: t.Optional[int] = attrs.field(default=None)
    soil_dryness: t.Optional[int] = attrs.field(default=None)
    firmness: t.Optional[NamedResource] = attrs.field(default=None)
    flavors: t.List[BerryFlavorMap] = attrs.field(factory=list)
    item: NamedResource = attrs.field(factory=NamedResource)
    natural_gift_type: t.Optional[NamedResource] = attrs.field(default=None)

    @classmethod
    def from_payload(cls, payload: t.Dict[str, t.Any]) -> "Berry":
        return cls(
            raw=payload,
            id=payload.get("id", 0),
            name=payload.get("name", ""),
            growth_time=payload.get("growth_time"),
            max_harvest=payload.get("max_harvest"),
            natural_gift_power=payload.get("natural_gift_power"),
            size=payload.get("size"),
            smoothness=payload.get("smoothness"),
            soil_dryness=payload.get("soil_dryness"),
            firmness=NamedResource.optional_from_payload(payload.get("firmness")),
            flavors=[BerryFlavorMap.from_payload(flavor) for flavor in payload.get("flavors", [])],
            item=NamedResource.from_payload(payload.get("item", {})),
            natural_gift_type=NamedResource.optional_from_payload(payload.get("natural_gift_type")),
        )


@attrs.define(slots=True, kw_only=True)
class BerryFirmness(BaseModel):
    """A berry firmness resource.

    Attributes
    ----------
    id: int
        The identifier for this berry firmness resource.
    name: str
        The name for this berry firmness resource.
    berries: t.List[NamedResource]
        A list of the berries with this firmness.
    names: t.List[Name]
        A list of the name of this berry firmness listed in different languages.
    """

    id: int = attrs.field(factory=int)
    name: str = attrs.field(factory=str)
    berries: t.List[NamedResource] = attrs.field(factory=list)
    names: t.List[Name] = attrs.field(factory=list)

    @classmethod
    def from_payload(cls, payload: t.Dict[str, t.Any]) -> "BerryFirmness":
        return cls(
            raw=payload,
            id=payload.get("id", 0),
            name=payload.get("name", ""),
            berries=[NamedResource.from_payload(berry) for berry in payload.get("berries", [])],
            names=[Name.from_payload(name) for name in payload.get("names", [])],
        )


@attrs.define(slots=True, kw_only=True)
class BerryFlavor(BaseModel):
    """A berry flavor resource.

    Attributes
    ----------
    id: int
        The identifier for this berry flavor resource.
    name: str
        The name for this berry flavor resource.
    berries: t.List[FlavorBerryMap]
        A list of the berries with this flavor.
    contest_type: NamedResource
        The contest type that correlates with this berry flavor.
    names: t.List[Name]
        The name of this berry flavor listed in different languages.
    """

    id: int = attrs.field(factory=int)
    name: str = attrs.field(factory=str)
    berries: t.List[FlavorBerryMap] = attrs.field(factory=list)
    contest_type: NamedResource = attrs.field(factory=NamedResource)
    names: t.List[Name] = attrs.field(factory=list)

    @classmethod
    def from_payload(cls, payload: t.Dict[str, t.Any]) -> "BerryFlavor":
        return cls(
            raw=payload,
            id=payload.get("id", 0),
            name=payload.get("name", ""),
            berries=[FlavorBerryMap.from_payload(berry) for berry in payload.get("berries", [])],
            contest_type=NamedResource.from_payload(payload.get("contest_type", {})),
            names=[Name.from_payload(name) for name in payload.get("names", [])],
        )
