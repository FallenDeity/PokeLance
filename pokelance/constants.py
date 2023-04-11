from __future__ import annotations

import enum
import typing as t

import attrs

__all__: t.Final[t.Tuple[str, ...]] = (
    "BaseEnum",
    "Extension",
    "BerryExtension",
    "ContestExtension",
    "EncounterExtension",
    "EvolutionExtension",
    "GameExtension",
    "ItemExtension",
    "LocationExtension",
    "MachineExtension",
    "MoveExtension",
    "PokemonExtension",
    "ExtensionEnum",
    "ExtensionsL",
)


ExtensionsL = t.Literal[
    "berry", "contest", "encounter", "evolution", "game", "item", "location", "machine", "move", "pokemon"
]


class BaseEnum(enum.Enum):
    def __get__(self, instance: t.Any, owner: t.Any) -> t.Any:
        return self.value


@attrs.define(slots=True, frozen=True)
class Extension:
    name: str
    categories: t.List[str] = attrs.field(factory=list)


@attrs.define(slots=True, frozen=True)
class BerryExtension(Extension):
    name = "berry"
    categories: t.List[str] = ["berry", "berry-firmness", "berry-flavor"]


@attrs.define(slots=True, frozen=True)
class ContestExtension(Extension):
    name = "contest"
    categories: t.List[str] = ["contest-type", "contest-effect", "super-contest-effect"]


@attrs.define(slots=True, frozen=True)
class EncounterExtension(Extension):
    name = "encounter"
    categories: t.List[str] = ["encounter-method", "encounter-condition", "encounter-condition-value"]


@attrs.define(slots=True, frozen=True)
class EvolutionExtension(Extension):
    name = "evolution"
    categories: t.List[str] = ["evolution-chain", "evolution-trigger"]


@attrs.define(slots=True, frozen=True)
class GameExtension(Extension):
    name = "game"
    categories: t.List[str] = ["generation", "pokedex", "version", "version-group"]


@attrs.define(slots=True, frozen=True)
class ItemExtension(Extension):
    name = "item"
    categories: t.List[str] = ["item", "item-attribute", "item-category", "item-fling-effect", "item-pocket"]


@attrs.define(slots=True, frozen=True)
class LocationExtension(Extension):
    name = "location"
    categories: t.List[str] = ["location", "location-area", "pal-park-area", "region"]


@attrs.define(slots=True, frozen=True)
class MachineExtension(Extension):
    name = "machine"
    categories: t.List[str] = ["machine"]


@attrs.define(slots=True, frozen=True)
class MoveExtension(Extension):
    name = "move"
    categories: t.List[str] = [
        "move",
        "move-ailment",
        "move-battle-style",
        "move-category",
        "move-damage-class",
        "move-learn-method",
        "move-target",
    ]


@attrs.define(slots=True, frozen=True)
class PokemonExtension(Extension):
    name = "pokemon"
    categories: t.List[str] = [
        "ability",
        "characteristic",
        "egg-group",
        "gender",
        "growth-rate",
        "nature",
        "pokeathlon-stat",
        "pokemon",
        "pokemon-color",
        "pokemon-form",
        "pokemon-habitat",
        "pokemon-shape",
        "pokemon-species",
        "stat",
        "type",
    ]


class ExtensionEnum(BaseEnum):
    berry = BerryExtension(name="berry")
    contest = ContestExtension(name="contest")
    encounter = EncounterExtension(name="encounter")
    evolution = EvolutionExtension(name="evolution")
    game = GameExtension(name="game")
    item = ItemExtension(name="item")
    location = LocationExtension(name="location")
    machine = MachineExtension(name="machine")
    move = MoveExtension(name="move")
    pokemon = PokemonExtension(name="pokemon")

    @classmethod
    def get_names(cls) -> t.List[str]:
        return [e.name for e in cls]

    @classmethod
    def get_categories(cls, name: str) -> t.List[str]:
        return list(getattr(cls[name].value, "categories"))
