import typing as t

import attrs

from pokelance.constants import ShowdownEnum
from pokelance.models import BaseModel

__all__: t.Tuple[str, ...] = ("ShowdownSprites",)


@attrs.define(kw_only=True, slots=True)
class ShowdownSprites(BaseModel):
    """Showdown sprites.

    Attributes
    ----------
    back_default: str
        The default back sprite.
    front_default: str
        The default front sprite.
    back_shiny: str
        The shiny back sprite.
    front_shiny: str
        The shiny front sprite.
    """

    front_default: str = attrs.field(factory=str)
    front_shiny: str = attrs.field(factory=str)
    back_default: str = attrs.field(factory=str)
    back_shiny: str = attrs.field(factory=str)

    @classmethod
    def from_id(cls, id_: int) -> "ShowdownSprites":
        return cls(
            front_default=str(ShowdownEnum["front_default".upper()]).format(id_),
            front_shiny=str(ShowdownEnum["front_shiny".upper()]).format(id_),
            back_shiny=str(ShowdownEnum["back_shiny".upper()]).format(id_),
            back_default=str(ShowdownEnum["back_default".upper()]).format(id_),
        )
