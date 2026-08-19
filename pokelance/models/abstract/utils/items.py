import typing as t

import attrs
from typing_extensions import override

from pokelance.models import BaseModel
from pokelance.models.common import NamedResource

__all__: tuple[str, ...] = (
    "ItemHolderPokemon",
    "ItemHolderPokemonVersionDetail",
    "ItemPrice",
    "ItemSprites",
)


@attrs.define(slots=True, kw_only=True)
class ItemSprites(BaseModel):
    """An item sprites resource.

    Attributes
    ----------
    default: t.Optional[str]
        The default depiction of this item.
    """

    default: str | None = attrs.field(default=None)

    @classmethod
    @override
    def from_payload(cls, payload: dict[str, t.Any]) -> "ItemSprites":
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
    @override
    def from_payload(cls, payload: dict[str, t.Any]) -> "ItemHolderPokemonVersionDetail":
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
    version_details: list[ItemHolderPokemonVersionDetail] = attrs.field(factory=list)

    @classmethod
    @override
    def from_payload(cls, payload: dict[str, t.Any]) -> "ItemHolderPokemon":
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
    purchase_price: int | None = attrs.field(default=None)
    sell_price: int | None = attrs.field(default=None)
    version_group: NamedResource = attrs.field(factory=NamedResource)

    @classmethod
    @override
    def from_payload(cls, payload: dict[str, t.Any]) -> "ItemPrice":
        return cls(
            raw=payload,
            currency=NamedResource.from_payload(payload.get("currency", {})),
            purchase_price=payload.get("purchase_price"),
            sell_price=payload.get("sell_price"),
            version_group=NamedResource.from_payload(payload.get("version_group", {})),
        )
