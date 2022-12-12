import typing as t

import attrs

from pokelance.models import BaseModel
from pokelance.models.common import NamedResource

__all__: t.Tuple[str, ...] = ("Machine",)


@attrs.define(slots=True, kw_only=True)
class Machine(BaseModel):
    """Machine model.

    Attributes
    ----------
    id: int
        The identifier for this resource.
    item: NamedResource
        The item that is required to use the TM or HM.
    move: NamedResource
        The move that is taught by the TM or HM.
    version_group: NamedResource
        The version group that this machine applies to.
    """

    id: int = attrs.field(factory=int)
    item: NamedResource = attrs.field(factory=NamedResource)
    move: NamedResource = attrs.field(factory=NamedResource)
    version_group: NamedResource = attrs.field(factory=NamedResource)

    @classmethod
    def from_payload(cls, payload: t.Dict[str, t.Any]) -> "Machine":
        return cls(
            id=payload.get("id", 0),
            item=NamedResource.from_payload(payload.get("item", {}) or {}),
            move=NamedResource.from_payload(payload.get("move", {}) or {}),
            version_group=NamedResource.from_payload(payload.get("version_group", {}) or {}),
        )
