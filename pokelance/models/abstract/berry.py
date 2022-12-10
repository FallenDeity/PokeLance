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
            firmness=NamedResource.from_payload(data.get("firmness", {})),
            flavors=[BerryFlavorMap.from_payload(flavor) for flavor in data.get("flavors", [])],
            item=NamedResource.from_payload(data.get("item", {})),
            natural_gift_type=NamedResource.from_payload(data.get("natural_gift_type", {})),
        )


@attrs.define(slots=True, kw_only=True)
class BerryFirmness(BaseModel):
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
            contest_type=NamedResource.from_payload(data.get("contest_type", {})),
            names=[Name.from_payload(name) for name in data.get("names", [])],
        )
