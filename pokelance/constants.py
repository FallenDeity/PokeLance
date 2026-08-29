from __future__ import annotations

import enum
import os
import re
import typing as t

import attrs
from typing_extensions import override

__all__: tuple[str, ...] = (
    "DEFAULT_BASE_URL",
    "BaseEnum",
    "BerryExtension",
    "ContestExtension",
    "EncounterExtension",
    "EvolutionExtension",
    "Extension",
    "ExtensionEnum",
    "ExtensionsL",
    "GameExtension",
    "GenderEnum",
    "ItemExtension",
    "LocationExtension",
    "MachineExtension",
    "MoveExtension",
    "PokemonExtension",
    "PokemonFormTriggerEnum",
    "RequestObject",
    "get_base_url",
    "validate_url",
)

DEFAULT_BASE_URL = "https://pokeapi.co/api/v2"

ExtensionsL = t.Literal[
    "berry", "contest", "encounter", "evolution", "game", "item", "location", "machine", "move", "pokemon"
]

# Special case subcategory /pokemon/{id}/encounters endpoint for getch_data and from_url methods,
# due to inconsistent naming in the PokéAPI specification.
_SUBCATEGORY_MAP: dict[str, str] = {"encounters": "location-area-encounter"}


def _convert_category(value: str) -> str:
    return _SUBCATEGORY_MAP.get(value, value)


@attrs.define
class RequestObject:
    extension: str
    category: str = attrs.field(converter=_convert_category)
    value: str


def get_base_url() -> str:
    return os.environ.get("POKEAPI_BASE_URL", DEFAULT_BASE_URL).rstrip("/")


def validate_url(url: str) -> re.Match[str] | None:
    pattern = re.compile(
        rf"{re.escape(get_base_url())}/(?P<category>[\w-]+)/(?P<value>[\w-]+)(?:/(?P<sub_category>[\w-]+))?/?"
    )
    return pattern.match(url)


class BaseEnum(enum.Enum):
    """
    Base enum class for all enums in the library.
    """

    def __get__(self, instance: object, owner: type[object] | None = None) -> object:
        """
        Get the value of the enum.
        """
        return self.value

    @override
    def __str__(self) -> str:
        """
        Get the string representation of the enum.
        """
        return str(self.value)


class PokemonFormTriggerEnum(BaseEnum):
    HELD_ITEM = "held-item"
    CONSUMED_ITEM = "consumed-item"
    KEY_ITEM = "key-item"
    ABILITY = "ability"
    GIGANTAMAX_FACTOR = "gigantamax-factor"
    MOVE = "move"
    UNDEFINED = "undefined"

    @classmethod
    def from_str(cls, value: str | None) -> PokemonFormTriggerEnum:
        if value is None:
            return PokemonFormTriggerEnum.UNDEFINED
        return cls(value) if value in cls._value2member_map_ else cls.UNDEFINED


class GenderEnum(BaseEnum):
    MALE = "male"
    FEMALE = "female"
    GENDERLESS = "genderless"
    UNDEFINED = "undefined"

    @classmethod
    def from_int(cls, value: int | None) -> GenderEnum | None:
        if value is None:
            return None
        convert_map: dict[int, GenderEnum] = {1: cls.FEMALE, 2: cls.MALE, 3: cls.GENDERLESS}
        return cls(convert_map.get(value, cls.UNDEFINED))


@attrs.define(slots=True, frozen=True)
class Extension:
    """
    Represents an extension.
    """

    name: str
    categories: tuple[str, ...] = attrs.field(factory=tuple)


@attrs.define(slots=True, frozen=True)
class BerryExtension(Extension):
    """Represents the berry extension.

    Attributes
    ----------
    name : str
        The name of the extension.
    categories : tuple[str, ...]
        The categories of the extension.
    """

    name: str = "berry"
    categories: tuple[str, ...] = ("berry", "berry-firmness", "berry-flavor")


@attrs.define(slots=True, frozen=True)
class ContestExtension(Extension):
    """Represents the contest extension.

    Attributes
    ----------
    name : str
        The name of the extension.
    categories : tuple[str, ...]
        The categories of the extension.
    """

    name: str = "contest"
    categories: tuple[str, ...] = ("contest-type", "contest-effect", "super-contest-effect")


@attrs.define(slots=True, frozen=True)
class EncounterExtension(Extension):
    """Represents the encounter extension.

    Attributes
    ----------
    name : str
        The name of the extension.
    categories : tuple[str, ...]
        The categories of the extension.
    """

    name: str = "encounter"
    categories: tuple[str, ...] = ("encounter-method", "encounter-condition", "encounter-condition-value")


@attrs.define(slots=True, frozen=True)
class EvolutionExtension(Extension):
    """Represents the evolution extension.

    Attributes
    ----------
    name : str
        The name of the extension.
    categories : tuple[str, ...]
        The categories of the extension.
    """

    name: str = "evolution"
    categories: tuple[str, ...] = ("evolution-chain", "evolution-trigger")


@attrs.define(slots=True, frozen=True)
class GameExtension(Extension):
    """Represents the game extension.

    Attributes
    ----------
    name : str
        The name of the extension.
    categories : tuple[str, ...]
        The categories of the extension.
    """

    name: str = "game"
    categories: tuple[str, ...] = ("generation", "pokedex", "version", "version-group")


@attrs.define(slots=True, frozen=True)
class ItemExtension(Extension):
    """Represents the item extension.

    Attributes
    ----------
    name : str
        The name of the extension.
    categories : tuple[str, ...]
        The categories of the extension.
    """

    name: str = "item"
    categories: tuple[str, ...] = (
        "currency",
        "item",
        "item-attribute",
        "item-category",
        "item-fling-effect",
        "item-pocket",
    )


@attrs.define(slots=True, frozen=True)
class LocationExtension(Extension):
    """Represents the location extension.

    Attributes
    ----------
    name : str
        The name of the extension.
    categories : tuple[str, ...]
        The categories of the extension.
    """

    name: str = "location"
    categories: tuple[str, ...] = ("location", "location-area", "pal-park-area", "region")


@attrs.define(slots=True, frozen=True)
class MachineExtension(Extension):
    """Represents the machine extension.

    Attributes
    ----------
    name : str
        The name of the extension.
    categories : tuple[str, ...]
        The categories of the extension.
    """

    name: str = "machine"
    categories: tuple[str, ...] = ("machine",)


@attrs.define(slots=True, frozen=True)
class MoveExtension(Extension):
    """Represents the move extension.

    Attributes
    ----------
    name : str
        The name of the extension.
    categories : tuple[str, ...]
        The categories of the extension.
    """

    name: str = "move"
    categories: tuple[str, ...] = (
        "move",
        "move-ailment",
        "move-battle-style",
        "move-category",
        "move-damage-class",
        "move-learn-method",
        "move-target",
    )


@attrs.define(slots=True, frozen=True)
class PokemonExtension(Extension):
    """Represents the pokemon extension.

    Attributes
    ----------
    name : str
        The name of the extension.
    categories : tuple[str, ...]
        The categories of the extension.
    """

    name: str = "pokemon"
    categories: tuple[str, ...] = (
        "ability",
        "characteristic",
        "egg-group",
        "gender",
        "growth-rate",
        "location-area-encounter",
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
    )


@attrs.define(slots=True, frozen=True)
class UtilityExtension(Extension):
    """Represents the utility extension.

    Attributes
    ----------
    name : str
        The name of the extension.
    categories : tuple[str, ...]
        The categories of the extension.
    """

    name: str = "utility"
    categories: tuple[str, ...] = ("language", "api-metadata")


class ExtensionEnum(BaseEnum):
    Berry = BerryExtension()
    Contest = ContestExtension()
    Encounter = EncounterExtension()
    Evolution = EvolutionExtension()
    Game = GameExtension()
    Item = ItemExtension()
    Location = LocationExtension()
    Machine = MachineExtension()
    Move = MoveExtension()
    Pokemon = PokemonExtension()
    Utility = UtilityExtension()

    @classmethod
    def validate_url(cls, url: str) -> RequestObject | None:
        """
        Validate the url.
        """
        if not url.startswith(get_base_url()) or not (groups := validate_url(url)):
            raise ValueError(f"Invalid url: {url}")
        category, value, subcategory = groups.groups()
        for i in cls:
            if category.lower() in i.value.categories:
                return RequestObject(extension=i.name, category=subcategory or category, value=value)
        raise ValueError(f"Invalid url: {url}")

    @classmethod
    def get_categories(cls, name: str) -> list[str]:
        return getattr(cls[name].value, "categories", [])
