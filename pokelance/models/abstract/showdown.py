import typing as t

import attrs

from pokelance.models import BaseModel

__all__: t.Tuple[str, ...] = ("ShowdownSprites",)
PATH: str = "https://raw.githubusercontent.com/PokeAPI/sprites/master/sprites/pokemon/other/showdown/"


SHOWDOWN_MAP: t.Dict[str, str] = {
    "front_default": PATH + "{}.gif",
    "front_shiny": PATH + "shiny/{}.gif",
    "back_default": PATH + "back/{}.gif",
    "back_shiny": PATH + "/back/shiny/{}.gif",
}


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
            front_default=SHOWDOWN_MAP["front_default"].format(id_),
            front_shiny=SHOWDOWN_MAP["front_shiny"].format(id_),
            back_shiny=SHOWDOWN_MAP["back_shiny"].format(id_),
            back_default=SHOWDOWN_MAP["back_default"].format(id_),
        )
