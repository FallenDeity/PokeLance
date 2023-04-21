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
    """
    Base enum class for all enums in the library.
    """

    def __get__(self, instance: t.Any, owner: t.Any) -> t.Any:
        """
        Get the value of the enum.
        """
        return self.value


@attrs.define(slots=True, frozen=True)
class Extension:
    """
    Represents an extension.
    """

    name: str
    categories: t.List[str] = attrs.field(factory=list)


@attrs.define(slots=True, frozen=True)
class BerryExtension(Extension):
    """
    Represents the berry extension.

    Attributes
    ----------
    name : str
        The name of the extension.
    categories : t.List[str]
        The categories of the extension.
    """

    name = "berry"
    categories: t.List[str] = ["berry", "berry-firmness", "berry-flavor"]


@attrs.define(slots=True, frozen=True)
class ContestExtension(Extension):
    """
    Represents the contest extension.

    Attributes
    ----------
    name : str
        The name of the extension.
    categories : t.List[str]
        The categories of the extension.
    """

    name = "contest"
    categories: t.List[str] = ["contest-type", "contest-effect", "super-contest-effect"]


@attrs.define(slots=True, frozen=True)
class EncounterExtension(Extension):
    """
    Represents the encounter extension.

    Attributes
    ----------
    name : str
        The name of the extension.
    categories : t.List[str]
        The categories of the extension.
    """

    name = "encounter"
    categories: t.List[str] = ["encounter-method", "encounter-condition", "encounter-condition-value"]


@attrs.define(slots=True, frozen=True)
class EvolutionExtension(Extension):
    """
    Represents the evolution extension.

    Attributes
    ----------
    name : str
        The name of the extension.
    categories : t.List[str]
        The categories of the extension.
    """

    name = "evolution"
    categories: t.List[str] = ["evolution-chain", "evolution-trigger"]


@attrs.define(slots=True, frozen=True)
class GameExtension(Extension):
    """
    Represents the game extension.

    Attributes
    ----------
    name : str
        The name of the extension.
    categories : t.List[str]
        The categories of the extension.
    """

    name = "game"
    categories: t.List[str] = ["generation", "pokedex", "version", "version-group"]


@attrs.define(slots=True, frozen=True)
class ItemExtension(Extension):
    """
    Represents the item extension.

    Attributes
    ----------
    name : str
        The name of the extension.
    categories : t.List[str]
        The categories of the extension.
    """

    name = "item"
    categories: t.List[str] = ["item", "item-attribute", "item-category", "item-fling-effect", "item-pocket"]


@attrs.define(slots=True, frozen=True)
class LocationExtension(Extension):
    """
    Represents the location extension.

    Attributes
    ----------
    name : str
        The name of the extension.
    categories : t.List[str]
        The categories of the extension.
    """

    name = "location"
    categories: t.List[str] = ["location", "location-area", "pal-park-area", "region"]


@attrs.define(slots=True, frozen=True)
class MachineExtension(Extension):
    """
    Represents the machine extension.

    Attributes
    ----------
    name : str
        The name of the extension.
    categories : t.List[str]
        The categories of the extension.
    """

    name = "machine"
    categories: t.List[str] = ["machine"]


@attrs.define(slots=True, frozen=True)
class MoveExtension(Extension):
    """
    Represents the move extension.

    Attributes
    ----------
    name : str
        The name of the extension.
    categories : t.List[str]
        The categories of the extension.
    """

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
    """
    Represents the pokemon extension.

    Attributes
    ----------
    name : str
        The name of the extension.
    categories : t.List[str]
        The categories of the extension.
    """

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
    Berry = BerryExtension(name="berry")
    Contest = ContestExtension(name="contest")
    Encounter = EncounterExtension(name="encounter")
    Evolution = EvolutionExtension(name="evolution")
    Game = GameExtension(name="game")
    Item = ItemExtension(name="item")
    Location = LocationExtension(name="location")
    Machine = MachineExtension(name="machine")
    Move = MoveExtension(name="move")
    Pokemon = PokemonExtension(name="pokemon")

    @classmethod
    def get_categories(cls, name: str) -> t.List[str]:
        return [i.replace("-", "_") for i in getattr(cls[name].value, "categories", [])]
