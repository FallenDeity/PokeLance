"""Declarative registry for all extensions and cache types.

This is the SINGLE SOURCE OF TRUTH for the code generator.
Uses real Endpoint methods and Model classes for type safety and autocomplete.
"""

from __future__ import annotations

import typing as t
from dataclasses import dataclass

from pokelance import models
from pokelance.http.endpoints import Endpoint, Route


@dataclass
class CategorySpec:
    """One category endpoint within an extension."""

    name: str
    endpoint: t.Callable[..., Route]
    endpoint_list: t.Optional[t.Callable[[], Route]]
    model: t.Type[models.BaseModel]
    cache_attr: str
    endpoint_key_is_id: bool = False
    url_suffix: str = ""
    is_list: bool = False


@dataclass
class ExtensionSpec:
    """One extension (e.g. Berry, Pokemon, etc.)."""

    name: str              # Class name: "Berry"
    module_name: str       # File stem: "berry"
    doc: str
    categories: list[CategorySpec]


# ---------------------------------------------------------------------------
# Extension Registry
# ---------------------------------------------------------------------------

EXTENSIONS: list[ExtensionSpec] = [
    ExtensionSpec(
        name="Berry",
        module_name="berry",
        doc="Extension for berry related endpoints.",
        categories=[
            CategorySpec(
                name="berry",
                endpoint=Endpoint.get_berry,
                endpoint_list=Endpoint.get_berry_endpoints,
                model=models.Berry,
                cache_attr="berry",
            ),
            CategorySpec(
                name="berry_firmness",
                endpoint=Endpoint.get_berry_firmness,
                endpoint_list=Endpoint.get_berry_firmness_endpoints,
                model=models.BerryFirmness,
                cache_attr="berry_firmness",
            ),
            CategorySpec(
                name="berry_flavor",
                endpoint=Endpoint.get_berry_flavor,
                endpoint_list=Endpoint.get_berry_flavor_endpoints,
                model=models.BerryFlavor,
                cache_attr="berry_flavor",
            ),
        ],
    ),
    ExtensionSpec(
        name="Contest",
        module_name="contest",
        doc="Extension for contest related endpoints.",
        categories=[
            CategorySpec(
                name="contest_type",
                endpoint=Endpoint.get_contest_type,
                endpoint_list=Endpoint.get_contest_type_endpoints,
                model=models.ContestType,
                cache_attr="contest_type",
            ),
            CategorySpec(
                name="contest_effect",
                endpoint=Endpoint.get_contest_effect,
                endpoint_list=Endpoint.get_contest_effect_endpoints,
                model=models.ContestEffect,
                cache_attr="contest_effect",
                endpoint_key_is_id=True,
            ),
            CategorySpec(
                name="super_contest_effect",
                endpoint=Endpoint.get_super_contest_effect,
                endpoint_list=Endpoint.get_super_contest_effect_endpoints,
                model=models.SuperContestEffect,
                cache_attr="super_contest_effect",
                endpoint_key_is_id=True,
            ),
        ],
    ),
    ExtensionSpec(
        name="Encounter",
        module_name="encounter",
        doc="Extension for encounter related endpoints.",
        categories=[
            CategorySpec(
                name="encounter_method",
                endpoint=Endpoint.get_encounter_method,
                endpoint_list=Endpoint.get_encounter_method_endpoints,
                model=models.EncounterMethod,
                cache_attr="encounter_method",
            ),
            CategorySpec(
                name="encounter_condition",
                endpoint=Endpoint.get_encounter_condition,
                endpoint_list=Endpoint.get_encounter_condition_endpoints,
                model=models.EncounterCondition,
                cache_attr="encounter_condition",
            ),
            CategorySpec(
                name="encounter_condition_value",
                endpoint=Endpoint.get_encounter_condition_value,
                endpoint_list=Endpoint.get_encounter_condition_value_endpoints,
                model=models.EncounterConditionValue,
                cache_attr="encounter_condition_value",
            ),
        ],
    ),
    ExtensionSpec(
        name="Evolution",
        module_name="evolution",
        doc="Extension for evolution related endpoints.",
        categories=[
            CategorySpec(
                name="evolution_chain",
                endpoint=Endpoint.get_evolution_chain,
                endpoint_list=Endpoint.get_evolution_chain_endpoints,
                model=models.EvolutionChain,
                cache_attr="evolution_chain",
                endpoint_key_is_id=True,
            ),
            CategorySpec(
                name="evolution_trigger",
                endpoint=Endpoint.get_evolution_trigger,
                endpoint_list=Endpoint.get_evolution_trigger_endpoints,
                model=models.EvolutionTrigger,
                cache_attr="evolution_trigger",
            ),
        ],
    ),
    ExtensionSpec(
        name="Game",
        module_name="game",
        doc="Extension for game related endpoints.",
        categories=[
            CategorySpec(
                name="generation",
                endpoint=Endpoint.get_generation,
                endpoint_list=Endpoint.get_generation_endpoints,
                model=models.Generation,
                cache_attr="generation",
            ),
            CategorySpec(
                name="pokedex",
                endpoint=Endpoint.get_pokedex,
                endpoint_list=Endpoint.get_pokedex_endpoints,
                model=models.Pokedex,
                cache_attr="pokedex",
            ),
            CategorySpec(
                name="version",
                endpoint=Endpoint.get_version,
                endpoint_list=Endpoint.get_version_endpoints,
                model=models.Version,
                cache_attr="version",
            ),
            CategorySpec(
                name="version_group",
                endpoint=Endpoint.get_version_group,
                endpoint_list=Endpoint.get_version_group_endpoints,
                model=models.VersionGroup,
                cache_attr="version_group",
            ),
        ],
    ),
    ExtensionSpec(
        name="Item",
        module_name="item",
        doc="Extension for item related endpoints.",
        categories=[
            CategorySpec(
                name="item",
                endpoint=Endpoint.get_item,
                endpoint_list=Endpoint.get_item_endpoints,
                model=models.Item,
                cache_attr="item",
            ),
            CategorySpec(
                name="item_attribute",
                endpoint=Endpoint.get_item_attribute,
                endpoint_list=Endpoint.get_item_attribute_endpoints,
                model=models.ItemAttribute,
                cache_attr="item_attribute",
            ),
            CategorySpec(
                name="item_category",
                endpoint=Endpoint.get_item_category,
                endpoint_list=Endpoint.get_item_category_endpoints,
                model=models.ItemCategory,
                cache_attr="item_category",
            ),
            CategorySpec(
                name="item_fling_effect",
                endpoint=Endpoint.get_item_fling_effect,
                endpoint_list=Endpoint.get_item_fling_effect_endpoints,
                model=models.ItemFlingEffect,
                cache_attr="item_fling_effect",
            ),
            CategorySpec(
                name="item_pocket",
                endpoint=Endpoint.get_item_pocket,
                endpoint_list=Endpoint.get_item_pocket_endpoints,
                model=models.ItemPocket,
                cache_attr="item_pocket",
            ),
        ],
    ),
    ExtensionSpec(
        name="Location",
        module_name="location",
        doc="Extension for location related endpoints.",
        categories=[
            CategorySpec(
                name="location",
                endpoint=Endpoint.get_location,
                endpoint_list=Endpoint.get_location_endpoints,
                model=models.Location,
                cache_attr="location",
            ),
            CategorySpec(
                name="location_area",
                endpoint=Endpoint.get_location_area,
                endpoint_list=Endpoint.get_location_area_endpoints,
                model=models.LocationArea,
                cache_attr="location_area",
            ),
            CategorySpec(
                name="pal_park_area",
                endpoint=Endpoint.get_pal_park_area,
                endpoint_list=Endpoint.get_pal_park_area_endpoints,
                model=models.PalParkArea,
                cache_attr="pal_park_area",
            ),
            CategorySpec(
                name="region",
                endpoint=Endpoint.get_region,
                endpoint_list=Endpoint.get_region_endpoints,
                model=models.Region,
                cache_attr="region",
            ),
        ],
    ),
    ExtensionSpec(
        name="Machine",
        module_name="machine",
        doc="Extension for machine related endpoints.",
        categories=[
            CategorySpec(
                name="machine",
                endpoint=Endpoint.get_machine,
                endpoint_list=Endpoint.get_machine_endpoints,
                model=models.Machine,
                cache_attr="machine",
                endpoint_key_is_id=True,
            ),
        ],
    ),
    ExtensionSpec(
        name="Move",
        module_name="move",
        doc="Extension for move related endpoints.",
        categories=[
            CategorySpec(
                name="move",
                endpoint=Endpoint.get_move,
                endpoint_list=Endpoint.get_move_endpoints,
                model=models.Move,
                cache_attr="move",
            ),
            CategorySpec(
                name="move_ailment",
                endpoint=Endpoint.get_move_ailment,
                endpoint_list=Endpoint.get_move_ailment_endpoints,
                model=models.MoveAilment,
                cache_attr="move_ailment",
            ),
            CategorySpec(
                name="move_battle_style",
                endpoint=Endpoint.get_move_battle_style,
                endpoint_list=Endpoint.get_move_battle_style_endpoints,
                model=models.MoveBattleStyle,
                cache_attr="move_battle_style",
            ),
            CategorySpec(
                name="move_category",
                endpoint=Endpoint.get_move_category,
                endpoint_list=Endpoint.get_move_category_endpoints,
                model=models.MoveCategory,
                cache_attr="move_category",
            ),
            CategorySpec(
                name="move_damage_class",
                endpoint=Endpoint.get_move_damage_class,
                endpoint_list=Endpoint.get_move_damage_class_endpoints,
                model=models.MoveDamageClass,
                cache_attr="move_damage_class",
            ),
            CategorySpec(
                name="move_learn_method",
                endpoint=Endpoint.get_move_learn_method,
                endpoint_list=Endpoint.get_move_learn_method_endpoints,
                model=models.MoveLearnMethod,
                cache_attr="move_learn_method",
            ),
            CategorySpec(
                name="move_target",
                endpoint=Endpoint.get_move_target,
                endpoint_list=Endpoint.get_move_target_endpoints,
                model=models.MoveTarget,
                cache_attr="move_target",
            ),
        ],
    ),
    ExtensionSpec(
        name="Pokemon",
        module_name="pokemon",
        doc="Extension for pokemon related endpoints.",
        categories=[
            CategorySpec(
                name="ability",
                endpoint=Endpoint.get_ability,
                endpoint_list=Endpoint.get_ability_endpoints,
                model=models.Ability,
                cache_attr="ability",
            ),
            CategorySpec(
                name="characteristic",
                endpoint=Endpoint.get_characteristic,
                endpoint_list=Endpoint.get_characteristic_endpoints,
                model=models.Characteristic,
                cache_attr="characteristic",
                endpoint_key_is_id=True,
            ),
            CategorySpec(
                name="egg_group",
                endpoint=Endpoint.get_egg_group,
                endpoint_list=Endpoint.get_egg_group_endpoints,
                model=models.EggGroup,
                cache_attr="egg_group",
            ),
            CategorySpec(
                name="gender",
                endpoint=Endpoint.get_gender,
                endpoint_list=Endpoint.get_gender_endpoints,
                model=models.Gender,
                cache_attr="gender",
            ),
            CategorySpec(
                name="growth_rate",
                endpoint=Endpoint.get_growth_rate,
                endpoint_list=Endpoint.get_growth_rate_endpoints,
                model=models.GrowthRate,
                cache_attr="growth_rate",
            ),
            CategorySpec(
                name="nature",
                endpoint=Endpoint.get_nature,
                endpoint_list=Endpoint.get_nature_endpoints,
                model=models.Nature,
                cache_attr="nature",
            ),
            CategorySpec(
                name="pokeathlon_stat",
                endpoint=Endpoint.get_pokeathlon_stat,
                endpoint_list=Endpoint.get_pokeathlon_stat_endpoints,
                model=models.PokeathlonStat,
                cache_attr="pokeathlon_stat",
            ),
            CategorySpec(
                name="pokemon",
                endpoint=Endpoint.get_pokemon,
                endpoint_list=Endpoint.get_pokemon_endpoints,
                model=models.Pokemon,
                cache_attr="pokemon",
            ),
            CategorySpec(
                name="pokemon_color",
                endpoint=Endpoint.get_pokemon_color,
                endpoint_list=Endpoint.get_pokemon_color_endpoints,
                model=models.PokemonColor,
                cache_attr="pokemon_color",
            ),
            CategorySpec(
                name="pokemon_form",
                endpoint=Endpoint.get_pokemon_form,
                endpoint_list=Endpoint.get_pokemon_form_endpoints,
                model=models.PokemonForm,
                cache_attr="pokemon_form",
            ),
            CategorySpec(
                name="pokemon_habitat",
                endpoint=Endpoint.get_pokemon_habitat,
                endpoint_list=Endpoint.get_pokemon_habitat_endpoints,
                model=models.PokemonHabitats,
                cache_attr="pokemon_habitat",
            ),
            CategorySpec(
                name="pokemon_shape",
                endpoint=Endpoint.get_pokemon_shape,
                endpoint_list=Endpoint.get_pokemon_shape_endpoints,
                model=models.PokemonShape,
                cache_attr="pokemon_shape",
            ),
            CategorySpec(
                name="pokemon_species",
                endpoint=Endpoint.get_pokemon_species,
                endpoint_list=Endpoint.get_pokemon_species_endpoints,
                model=models.PokemonSpecies,
                cache_attr="pokemon_species",
            ),
            CategorySpec(
                name="stat",
                endpoint=Endpoint.get_stat,
                endpoint_list=Endpoint.get_stat_endpoints,
                model=models.Stat,
                cache_attr="stat",
            ),
            CategorySpec(
                name="type",
                endpoint=Endpoint.get_type,
                endpoint_list=Endpoint.get_type_endpoints,
                model=models.Type,
                cache_attr="type",
            ),
            CategorySpec(
                name="location_area_encounter",
                endpoint=Endpoint.get_location_area_encounter,
                endpoint_list=Endpoint.get_location_area_encounter_endpoints,
                model=models.LocationAreaEncounter,
                cache_attr="location_area_encounter",
                url_suffix="/encounters",
                is_list=True,
            ),
        ],
    ),
    ExtensionSpec(
        name="Utility",
        module_name="utility",
        doc="Extension for utility related endpoints.",
        categories=[
            CategorySpec(
                name="language",
                endpoint=Endpoint.get_language,
                endpoint_list=Endpoint.get_language_endpoints,
                model=models.Language,
                cache_attr="language",
                endpoint_key_is_id=True,
            ),
            CategorySpec(
                name="api_metadata",
                endpoint=Endpoint.get_api_metadata,
                endpoint_list=None,
                model=models.APIMetadata,
                cache_attr="api_metadata",
                endpoint_key_is_id=True,
            ),
        ],
    ),
]
