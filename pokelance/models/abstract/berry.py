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
    growth_time: int
        Time it takes the tree to grow one stage, in hours. Berry trees go through
        four of these growth stages before they can be picked.
    max_harvest: int
        The maximum number of these berries that can grow on one tree in Generation
        IV.
    natural_gift_power: int
        The power of the move "Natural Gift" when used with this Berry.
    size: int
        Berries are actually items. This is the number of those items.
    smoothness: int
        The speed at which this Berry dries out the soil as it grows. A higher
        rate means the soil dries more quickly.
    soil_dryness: int
        The firmness of this berry, used in making Pokéblocks or Poffins.
    flavors: typing.List[BerryFlavorMap]
        A list of references to each flavor a berry can have and the potency of
        each of those flavors in regard to this berry.
    item: pokelance.models.common.NamedResource
        The item that corresponds to this berry.
    natural_gift_type: pokelance.models.common.NamedResource
        The type inherited by "Natural Gift" when used with this Berry.
    """

    id: int = attrs.field(factory=int)
    name: str = attrs.field(factory=str)
    growth_time: int = attrs.field(factory=int)
    max_harvest: int = attrs.field(factory=int)
    natural_gift_power: int = attrs.field(factory=int)
    size: int = attrs.field(factory=int)
    smoothness: int = attrs.field(factory=int)
    soil_dryness: int = attrs.field(factory=int)
    firmness: NamedResource = attrs.field(factory=NamedResource)
    flavors: t.List[BerryFlavorMap] = attrs.field(factory=list)
    item: NamedResource = attrs.field(factory=NamedResource)
    natural_gift_type: NamedResource = attrs.field(factory=NamedResource)

    @classmethod
    def from_payload(cls, data: t.Dict[str, t.Any]) -> "Berry":
        return cls(
            id=data.get("id", 0),
            name=data.get("name", ""),
            growth_time=data.get("growth_time", 0),
            max_harvest=data.get("max_harvest", 0),
            natural_gift_power=data.get("natural_gift_power", 0),
            size=data.get("size", 0),
            smoothness=data.get("smoothness", 0),
            soil_dryness=data.get("soil_dryness", 0),
            firmness=NamedResource.from_payload(data.get("firmness", {}) or {}),
            flavors=[BerryFlavorMap.from_payload(flavor) for flavor in data.get("flavors", [])],
            item=NamedResource.from_payload(data.get("item", {}) or {}),
            natural_gift_type=NamedResource.from_payload(data.get("natural_gift_type", {}) or {}),
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
    berries: typing.List[pokelance.models.common.NamedResource]
        A list of the berries with this firmness.
    names: typing.List[pokelance.models.common.Name]
        A list of the name of this berry firmness listed in different languages.
    """

    id: int = attrs.field(factory=int)
    name: str = attrs.field(factory=str)
    berries: t.List[NamedResource] = attrs.field(factory=list)
    names: t.List[Name] = attrs.field(factory=list)

    @classmethod
    def from_payload(cls, data: t.Dict[str, t.Any]) -> "BerryFirmness":
        return cls(
            id=data.get("id", 0),
            name=data.get("name", ""),
            berries=[NamedResource.from_payload(berry) for berry in data.get("berries", [])],
            names=[Name.from_payload(name) for name in data.get("names", [])],
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
    berries: typing.List[FlavorBerryMap]
        A list of the berries with this flavor.
    contest_type: pokelance.models.common.NamedResource
        The contest type that correlates with this berry flavor.
    names: typing.List[pokelance.models.common.Name]
        The name of this berry flavor listed in different languages.
    """

    id: int = attrs.field(factory=int)
    name: str = attrs.field(factory=str)
    berries: t.List[FlavorBerryMap] = attrs.field(factory=list)
    contest_type: NamedResource = attrs.field(factory=NamedResource)
    names: t.List[Name] = attrs.field(factory=list)

    @classmethod
    def from_payload(cls, data: t.Dict[str, t.Any]) -> "BerryFlavor":
        return cls(
            id=data.get("id", 0),
            name=data.get("name", ""),
            berries=[FlavorBerryMap.from_payload(berry) for berry in data.get("berries", [])],
            contest_type=NamedResource.from_payload(data.get("contest_type", {}) or {}),
            names=[Name.from_payload(name) for name in data.get("names", [])],
        )
