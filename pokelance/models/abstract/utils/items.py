import typing as t

import attrs

from pokelance.models import BaseModel
from pokelance.models.common import NamedResource

__all__: t.Tuple[str, ...] = (
    "ItemSprites",
    "ItemHolderPokemon",
    "ItemHolderPokemonVersionDetail",
    "ItemPrice",
)


@attrs.define(slots=True, kw_only=True)
class ItemSprites(BaseModel):
    """An item sprites resource.

    Attributes
    ----------
    default: t.Optional[str]
        The default depiction of this item.
    """

    default: t.Optional[str] = attrs.field(default=None)

    @classmethod
    def from_payload(cls, payload: t.Dict[str, t.Any]) -> "ItemSprites":
        return cls(raw=payload, default=payload.get("default"))


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
            raw=payload,
            rarity=payload.get("rarity", 0),
            version=NamedResource.from_payload(payload.get("version", {})),
        )


@attrs.define(slots=True, kw_only=True)
class ItemHolderPokemon(BaseModel):
    """An item holder pokemon resource.

    Attributes
    ----------
    pokemon: NamedResource
        The Pokémon that holds this item.
    version_details: t.List[ItemHolderPokemonVersionDetail]
        The details for the version that this item is held in by the Pokémon.
    """

    pokemon: NamedResource = attrs.field(factory=NamedResource)
    version_details: t.List[ItemHolderPokemonVersionDetail] = attrs.field(factory=list)

    @classmethod
    def from_payload(cls, payload: t.Dict[str, t.Any]) -> "ItemHolderPokemon":
        return cls(
            raw=payload,
            pokemon=NamedResource.from_payload(payload.get("pokemon", {})),
            version_details=[
                ItemHolderPokemonVersionDetail.from_payload(version_detail)
                for version_detail in payload.get("version_details", [])
            ],
        )


@attrs.define(slots=True, kw_only=True)
class ItemPrice(BaseModel):
    """An item price resource.

    Attributes
    ----------
    currency: NamedResource
        The currency used for this price.
    purchase_price: t.Optional[int]
        The purchase price of this item in this version group. Null if the item cannot be purchased.
    sell_price: t.Optional[int]
        The sell price of this item in this version group. Null if the item cannot be sold.
    version_group: NamedResource
        The version group these prices apply to.
    """

    currency: NamedResource = attrs.field(factory=NamedResource)
    purchase_price: t.Optional[int] = attrs.field(default=None)
    sell_price: t.Optional[int] = attrs.field(default=None)
    version_group: NamedResource = attrs.field(factory=NamedResource)

    @classmethod
    def from_payload(cls, payload: t.Dict[str, t.Any]) -> "ItemPrice":
        return cls(
            raw=payload,
            currency=NamedResource.from_payload(payload.get("currency", {})),
            purchase_price=payload.get("purchase_price"),
            sell_price=payload.get("sell_price"),
            version_group=NamedResource.from_payload(payload.get("version_group", {})),
        )
