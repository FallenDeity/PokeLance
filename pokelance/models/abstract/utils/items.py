import typing as t

import attrs

from pokelance.models import BaseModel
from pokelance.models.common import NamedResource

__all__: t.Tuple[str, ...] = (
    "ItemSprites",
    "ItemHolderPokemon",
    "ItemHolderPokemonVersionDetail",
)


@attrs.define(slots=True, kw_only=True)
class ItemSprites(BaseModel):
    """An item sprites resource.

    Attributes
    ----------
    default: str
        The default depiction of this item.
    """

    default: str = attrs.field(factory=str)

    @classmethod
    def from_payload(cls, payload: t.Dict[str, str]) -> "ItemSprites":
        return cls(default=payload.get("default", ""))


@attrs.define(slots=True, kw_only=True)
class ItemHolderPokemonVersionDetail(BaseModel):
    """An item holder pokemon version detail resource.

    Attributes
    ----------
    rarity: int
        The chance of this Pokémon holding this item in this version.
    version: NamedResource
        The version that this item is held in by the Pokémon.
    """

    rarity: int = attrs.field(factory=int)
    version: NamedResource = attrs.field(factory=NamedResource)

    @classmethod
    def from_payload(cls, payload: t.Dict[str, t.Any]) -> "ItemHolderPokemonVersionDetail":
        return cls(
            rarity=payload.get("rarity", 0),
            version=NamedResource.from_payload(payload.get("version", {}) or {}),
        )


@attrs.define(slots=True, kw_only=True)
class ItemHolderPokemon(BaseModel):
    """An item holder pokemon resource.

    Attributes
    ----------
    pokemon: str
        The Pokémon that holds this item.
    version_details: t.List[ItemHolderPokemonVersionDetail]
        The details for the version that this item is held in by the Pokémon.
    """

    pokemon: NamedResource = attrs.field(factory=NamedResource)
    version_details: t.List["ItemHolderPokemonVersionDetail"] = attrs.field(factory=list)

    @classmethod
    def from_payload(cls, payload: t.Dict[str, t.Any]) -> "ItemHolderPokemon":
        return cls(
            pokemon=NamedResource.from_payload(payload.get("pokemon", {}) or {}),
            version_details=[
                ItemHolderPokemonVersionDetail.from_payload(version_detail)
                for version_detail in payload.get("version_details", [])
            ],
        )
