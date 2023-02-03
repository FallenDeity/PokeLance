import typing as t

import attrs

from pokelance.models import BaseModel
from pokelance.models.common import (
    Description,
    Effect,
    GenerationGameIndex,
    MachineVersionDetail,
    Name,
    NamedResource,
    VerboseEffect,
    VersionGroupFlavorText,
)

from .utils import ItemHolderPokemon, ItemSprites

__all__: t.Tuple[str, ...] = ("Item", "ItemAttribute", "ItemCategory", "ItemFlingEffect", "ItemPocket")


@attrs.define(slots=True, kw_only=True)
class Item(BaseModel):
    """Item model.

    Attributes
    ----------
    id: int
        The identifier for this resource.
    name: str
        The name for this resource.
    cost: int
        The price of this item in stores.
    fling_power: int
        The power of the move Fling when used with this item.
    fling_effect: NamedResource
        The effect of the move Fling when used with this item.
    attributes: t.List[NamedResource]
        A list of attributes this item has.
    category: NamedResource
        The category of items this item falls into.
    effect_entries: t.List[Effect]
        The effect of this ability listed in different languages.
    flavor_text_entries: t.List[VersionGroupFlavorText]
        The flavor text of this ability listed in different languages.
    game_indices: t.List[GenerationGameIndex]
        A list of game indices relevent to this item by generation.
    names: t.List[Name]
        The name of this resource listed in different languages.
    sprites: ItemSprites
        A set of sprites used to depict this item in the game.
    held_by_pokemon: t.List[ItemHolderPokemon]
        A list of Pokémon that might be found in the wild holding this item.
    baby_trigger_for: NamedResource
        An evolution chain this item requires to produce a bay during mating.
    machines: t.List[MachineVersionDetail]
        A list of the machines related to this item.
    """

    id: int = attrs.field(factory=int)
    name: str = attrs.field(factory=str)
    cost: int = attrs.field(factory=int)
    fling_power: int = attrs.field(factory=int)
    fling_effect: NamedResource = attrs.field(factory=NamedResource)
    attributes: t.List[NamedResource] = attrs.field(factory=list)
    category: NamedResource = attrs.field(factory=NamedResource)
    effect_entries: t.List[VerboseEffect] = attrs.field(factory=list)
    flavor_text_entries: t.List[VersionGroupFlavorText] = attrs.field(factory=list)
    game_indices: t.List[GenerationGameIndex] = attrs.field(factory=list)
    names: t.List[Name] = attrs.field(factory=list)
    sprites: ItemSprites = attrs.field(factory=ItemSprites)
    held_by_pokemon: t.List[ItemHolderPokemon] = attrs.field(factory=list)
    baby_trigger_for: NamedResource = attrs.field(factory=NamedResource)
    machines: t.List[MachineVersionDetail] = attrs.field(factory=list)

    @classmethod
    def from_payload(cls, payload: t.Dict[str, t.Any]) -> "Item":
        return cls(
            id=payload.get("id", 0),
            name=payload.get("name", ""),
            cost=payload.get("cost", 0),
            fling_power=payload.get("fling_power", 0),
            fling_effect=NamedResource.from_payload(payload.get("fling_effect", {}) or {}),
            attributes=[NamedResource.from_payload(attribute) for attribute in payload.get("attributes", [])],
            category=NamedResource.from_payload(payload.get("category", {}) or {}),
            effect_entries=[VerboseEffect.from_payload(effect) for effect in payload.get("effect_entries", [])],
            flavor_text_entries=[
                VersionGroupFlavorText.from_payload(flavor_text)
                for flavor_text in payload.get("flavor_text_entries", [])
            ],
            game_indices=[
                GenerationGameIndex.from_payload(game_index) for game_index in payload.get("game_indices", [])
            ],
            names=[Name.from_payload(name) for name in payload.get("names", [])],
            sprites=ItemSprites.from_payload(payload.get("sprites", {}) or {}),
            held_by_pokemon=[
                ItemHolderPokemon.from_payload(held_by_pokemon)
                for held_by_pokemon in payload.get("held_by_pokemon", [])
            ],
            baby_trigger_for=NamedResource.from_payload(payload.get("baby_trigger_for", {}) or {}),
            machines=[MachineVersionDetail.from_payload(machine) for machine in payload.get("machines", [])],
        )


@attrs.define(slots=True, kw_only=True)
class ItemAttribute(BaseModel):
    """ItemAttribute model.

    Attributes
    ----------
    id: int
        The identifier for this resource.
    name: str
        The name for this resource.
    items: t.List[NamedResource]
        A list of items that have this attribute.
    names: t.List[Name]
        The name of this resource listed in different languages.
    """

    id: int = attrs.field(factory=int)
    name: str = attrs.field(factory=str)
    items: t.List[NamedResource] = attrs.field(factory=list)
    names: t.List[Name] = attrs.field(factory=list)
    descriptions: t.List[Description] = attrs.field(factory=list)

    @classmethod
    def from_payload(cls, payload: t.Dict[str, t.Any]) -> "ItemAttribute":
        return cls(
            id=payload.get("id", 0),
            name=payload.get("name", ""),
            items=[NamedResource.from_payload(item) for item in payload.get("items", [])],
            names=[Name.from_payload(name) for name in payload.get("names", [])],
            descriptions=[Description.from_payload(description) for description in payload.get("descriptions", [])],
        )


@attrs.define(slots=True, kw_only=True)
class ItemCategory(BaseModel):
    """ItemCategory model.

    Attributes
    ----------
    id: int
        The identifier for this resource.
    name: str
        The name for this resource.
    items: t.List[NamedResource]
        A list of items that are a part of this category.
    names: t.List[Name]
        The name of this resource listed in different languages.
    """

    id: int = attrs.field(factory=int)
    name: str = attrs.field(factory=str)
    items: t.List[NamedResource] = attrs.field(factory=list)
    names: t.List[Name] = attrs.field(factory=list)
    pocket: NamedResource = attrs.field(factory=NamedResource)

    @classmethod
    def from_payload(cls, payload: t.Dict[str, t.Any]) -> "ItemCategory":
        return cls(
            id=payload.get("id", 0),
            name=payload.get("name", ""),
            items=[NamedResource.from_payload(item) for item in payload.get("items", [])],
            names=[Name.from_payload(name) for name in payload.get("names", [])],
            pocket=NamedResource.from_payload(payload.get("pocket", {}) or {}),
        )


@attrs.define(slots=True, kw_only=True)
class ItemFlingEffect(BaseModel):
    """ItemFlingEffect model.

    Attributes
    ----------
    id: int
        The identifier for this resource.
    name: str
        The name for this resource.
    effect_entries: t.List[Effect]
        The result of this fling effect listed in different languages.
    items: t.List[NamedResource]
        A list of items that have this fling effect.
    """

    id: int = attrs.field(factory=int)
    name: str = attrs.field(factory=str)
    effect_entries: t.List[Effect] = attrs.field(factory=list)
    items: t.List[NamedResource] = attrs.field(factory=list)

    @classmethod
    def from_payload(cls, payload: t.Dict[str, t.Any]) -> "ItemFlingEffect":
        return cls(
            id=payload.get("id", 0),
            name=payload.get("name", ""),
            effect_entries=[Effect.from_payload(effect) for effect in payload.get("effect_entries", [])],
            items=[NamedResource.from_payload(item) for item in payload.get("items", [])],
        )


@attrs.define(slots=True, kw_only=True)
class ItemPocket(BaseModel):
    """ItemPocket model.

    Attributes
    ----------
    id: int
        The identifier for this resource.
    name: str
        The name for this resource.
    categories: t.List[NamedResource]
        A list of item categories that are relevant to this item pocket.
    names: t.List[Name]
        The name of this resource listed in different languages.
    """

    id: int = attrs.field(factory=int)
    name: str = attrs.field(factory=str)
    categories: t.List[NamedResource] = attrs.field(factory=list)
    names: t.List[Name] = attrs.field(factory=list)

    @classmethod
    def from_payload(cls, payload: t.Dict[str, t.Any]) -> "ItemPocket":
        return cls(
            id=payload.get("id", 0),
            name=payload.get("name", ""),
            categories=[NamedResource.from_payload(category) for category in payload.get("categories", [])],
            names=[Name.from_payload(name) for name in payload.get("names", [])],
        )
