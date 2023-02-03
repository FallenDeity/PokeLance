import typing as t

import attrs

from pokelance.models import BaseModel
from pokelance.models.common import NamedResource

__all__: t.Tuple[str, ...] = (
    "BerryFlavorMap",
    "FlavorBerryMap",
)


@attrs.define(slots=True, kw_only=True)
class BerryFlavorMap(BaseModel):
    """Represents a berry flavor map.

    Attributes
    ----------
    potency: int
        The potency of the referenced flavor for this berry.
    flavor: NamedResource
        The referenced berry flavor.
    """

    potency: int = attrs.field(factory=int)
    flavor: NamedResource = attrs.field(factory=NamedResource)

    @classmethod
    def from_payload(cls, payload: t.Dict[str, t.Any]) -> "BerryFlavorMap":
        return cls(
            potency=payload.get("potency", 0),
            flavor=NamedResource.from_payload(payload.get("flavor", {}) or {}),
        )


@attrs.define(slots=True, kw_only=True)
class FlavorBerryMap(BaseModel):
    """Represents a flavor berry map.

    Attributes
    ----------
    potency: int
        The potency of the referenced berry for this flavor.
    berry: NamedResource
        The referenced berry.
    """

    potency: int = attrs.field(factory=int)
    berry: NamedResource = attrs.field(factory=NamedResource)

    @classmethod
    def from_payload(cls, payload: t.Dict[str, t.Any]) -> "FlavorBerryMap":
        return cls(
            potency=payload.get("potency", 0),
            berry=NamedResource.from_payload(payload.get("berry", {}) or {}),
        )
