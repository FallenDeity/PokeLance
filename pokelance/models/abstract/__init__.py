import typing as t

from .berry import Berry, BerryFirmness, BerryFlavor
from .contest import ContestEffect, ContestType, SuperContestEffect
from .encounter import EncounterCondition, EncounterConditionValue, EncounterMethod
from .evolution import EvolutionChain, EvolutionTrigger
from .game import Generation, Pokedex, Version, VersionGroup
from .item import Item, ItemAttribute, ItemCategory, ItemFlingEffect, ItemPocket
from .location import Location, LocationArea, PalParkArea, Region
from .machine import Machine
from .move import Move, MoveAilment, MoveBattleStyle, MoveCategory, MoveDamageClass, MoveLearnMethod, MoveTarget
from .pokemon import (
    Ability,
    Characteristic,
    EggGroup,
    Gender,
    GrowthRate,
    LocationAreaEncounter,
    Nature,
    PokeathlonStat,
    Pokemon,
    PokemonColor,
    PokemonForm,
    PokemonHabitats,
    PokemonShape,
    PokemonSpecies,
    Stat,
    Type,
)

__all__: t.Tuple[str, ...] = (
    "Berry",
    "BerryFirmness",
    "BerryFlavor",
    "ContestEffect",
    "ContestType",
    "SuperContestEffect",
    "EncounterCondition",
    "EncounterConditionValue",
    "EncounterMethod",
    "EvolutionChain",
    "EvolutionTrigger",
    "Generation",
    "Pokedex",
    "Version",
    "VersionGroup",
    "Item",
    "ItemAttribute",
    "ItemCategory",
    "ItemFlingEffect",
    "ItemPocket",
    "Location",
    "LocationArea",
    "PalParkArea",
    "Region",
    "Machine",
    "Move",
    "MoveAilment",
    "MoveBattleStyle",
    "MoveCategory",
    "MoveDamageClass",
    "MoveLearnMethod",
    "MoveTarget",
    "Ability",
    "Characteristic",
    "Pokemon",
    "PokemonSpecies",
    "PokemonForm",
    "Nature",
    "Type",
    "Gender",
    "GrowthRate",
    "EggGroup",
    "LocationAreaEncounter",
    "PokemonColor",
    "PokeathlonStat",
    "PokemonHabitats",
    "PokemonShape",
    "Stat",
)
