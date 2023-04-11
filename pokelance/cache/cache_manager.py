import typing as t

import attrs

from .cache import (
    AbilityCache,
    BaseCache,
    BerryCache,
    BerryFirmnessCache,
    BerryFlavorCache,
    CharacteristicCache,
    ContestEffectCache,
    ContestTypeCache,
    EggGroupCache,
    EncounterConditionCache,
    EncounterConditionValueCache,
    EncounterMethodCache,
    EvolutionChainCache,
    EvolutionTriggerCache,
    GamesGenerationCache,
    GamesPokedexCache,
    GamesVersionCache,
    GamesVersionGroupCache,
    GenderCache,
    GrowthRateCache,
    ItemAttributeCache,
    ItemCache,
    ItemCategoryCache,
    ItemFlingEffectCache,
    ItemPocketCache,
    LocationAreaCache,
    LocationCache,
    MachineCache,
    MoveAilmentCache,
    MoveBattleStyleCache,
    MoveCache,
    MoveCategoryCache,
    MoveDamageClassCache,
    MoveLearnMethodCache,
    MoveTargetCache,
    NatureCache,
    PalParkAreaCache,
    PokeathlonStatCache,
    PokemonCache,
    PokemonColorCache,
    PokemonFormCache,
    PokemonHabitatCache,
    PokemonLocationAreaCache,
    PokemonShapeCache,
    PokemonSpeciesCache,
    RegionCache,
    StatCache,
    SuperContestEffectCache,
    TypeCache,
)

__all__: t.Tuple[str, ...] = (
    "Cache",
    "Base",
    "BaseCache",
    "Berry",
    "Contest",
    "Encounter",
    "Evolution",
    "Game",
    "Item",
    "Location",
    "Machine",
    "Move",
    "Pokemon",
)


@attrs.define(slots=True, kw_only=True)
class Base:
    """Base class for all caches.

    Attributes
    ----------
    max_size: int
        The maximum cache size.
    """

    max_size: int

    def set_size(self, max_size: int = 100) -> None:
        """Set the maximum cache size.

        Parameters
        ----------
        max_size: int
            The maximum cache size.
        """
        self.max_size = max_size
        obj: attrs.Attribute[BaseCache[t.Any, t.Any]]
        for obj in self.__attrs_attrs__:  # type: ignore
            if isinstance(obj.default, BaseCache) and obj.default is not None:
                obj.default._max_size = max_size


@attrs.define(slots=True, kw_only=True)
class Encounter(Base):
    """Cache for encounter related endpoints.

    Attributes
    ----------
    max_size: int
        The maximum cache size.
    encounter_method: EncounterMethodCache
        The method in which the encounter happens.
    encounter_condition: EncounterConditionCache
        The condition in which the encounter happens.
    encounter_condition_value: EncounterConditionValueCache
        The condition value in which the encounter happens.
    """

    max_size: int = 100
    encounter_method: EncounterMethodCache = attrs.field(default=EncounterMethodCache(max_size=max_size))
    encounter_condition: EncounterConditionCache = attrs.field(default=EncounterConditionCache(max_size=max_size))
    encounter_condition_value: EncounterConditionValueCache = attrs.field(
        default=EncounterConditionValueCache(max_size=max_size)
    )


@attrs.define(slots=True, kw_only=True)
class Evolution(Base):
    """Cache for evolution related endpoints.

    Attributes
    ----------
    max_size: int
        The maximum cache size.
    evolution_chain: EvolutionChainCache
        The evolution chain of a Pokemon.
    evolution_trigger: EvolutionTriggerCache
        The trigger in which the evolution happens.
    """

    max_size: int = 100
    evolution_chain: EvolutionChainCache = attrs.field(default=EvolutionChainCache(max_size=max_size))
    evolution_trigger: EvolutionTriggerCache = attrs.field(default=EvolutionTriggerCache(max_size=max_size))


@attrs.define(slots=True, kw_only=True)
class Machine(Base):
    """Cache for machine related endpoints.

    Attributes
    ----------
    max_size: int
        The maximum cache size.
    machine: MachineCache
        The machine that teaches a move.
    """

    max_size: int = 100
    machine: MachineCache = attrs.field(default=MachineCache(max_size=max_size))


@attrs.define(slots=True, kw_only=True)
class Game(Base):
    """Cache for game related endpoints.

    Attributes
    ----------
    max_size: int
        The maximum cache size.
    generation: GamesGenerationCache
        The generation of a game.
    pokedex: GamesPokedexCache
        The pokedex of a game.
    version: GamesVersionCache
        The version of a game.
    version_group: GamesVersionGroupCache
        The version group of a game.
    """

    max_size: int = 100
    generation: GamesGenerationCache = attrs.field(default=GamesGenerationCache(max_size=max_size))
    pokedex: GamesPokedexCache = attrs.field(default=GamesPokedexCache(max_size=max_size))
    version: GamesVersionCache = attrs.field(default=GamesVersionCache(max_size=max_size))
    version_group: GamesVersionGroupCache = attrs.field(default=GamesVersionGroupCache(max_size=max_size))


@attrs.define(slots=True, kw_only=True)
class Item(Base):
    """Cache for item related endpoints.

    Attributes
    ----------
    max_size: int
        The maximum cache size.
    item: ItemCache
        The item.
    item_attribute: ItemAttributeCache
        The attribute of an item.
    item_category: ItemCategoryCache
        The category of an item.
    item_fling_effect: ItemFlingEffectCache
        The fling effect of an item.
    item_pocket: ItemPocketCache
        The pocket of an item.
    """

    max_size: int = 100
    item: ItemCache = attrs.field(default=ItemCache(max_size=max_size))
    item_attribute: ItemAttributeCache = attrs.field(default=ItemAttributeCache(max_size=max_size))
    item_category: ItemCategoryCache = attrs.field(default=ItemCategoryCache(max_size=max_size))
    item_fling_effect: ItemFlingEffectCache = attrs.field(default=ItemFlingEffectCache(max_size=max_size))
    item_pocket: ItemPocketCache = attrs.field(default=ItemPocketCache(max_size=max_size))


@attrs.define(slots=True, kw_only=True)
class Location(Base):
    """Cache for location related endpoints.

    Attributes
    ----------
    max_size: int
        The maximum cache size.
    location: LocationCache
        The location.
    location_area: LocationAreaCache
        The location area.
    """

    max_size: int = 100
    location: LocationCache = attrs.field(default=LocationCache(max_size=max_size))
    location_area: LocationAreaCache = attrs.field(default=LocationAreaCache(max_size=max_size))
    pal_park_area: PalParkAreaCache = attrs.field(default=PalParkAreaCache(max_size=max_size))
    region: RegionCache = attrs.field(default=RegionCache(max_size=max_size))


@attrs.define(slots=True, kw_only=True)
class Move(Base):
    """Cache for move related endpoints.

    Attributes
    ----------
    max_size: int
        The maximum cache size.
    move: MoveCache
        The move.
    move_ailment: MoveAilmentCache
        The ailment of a move.
    move_battle_style: MoveBattleStyleCache
        The battle style of a move.
    move_category: MoveCategoryCache
        The category of a move.
    move_damage_class: MoveDamageClassCache
        The damage class of a move.
    move_learn_method: MoveLearnMethodCache
        The learn method of a move.
    move_target: MoveTargetCache
        The target of a move.
    """

    max_size: int = 100
    move: MoveCache = attrs.field(default=MoveCache(max_size=max_size))
    move_ailment: MoveAilmentCache = attrs.field(default=MoveAilmentCache(max_size=max_size))
    move_battle_style: MoveBattleStyleCache = attrs.field(default=MoveBattleStyleCache(max_size=max_size))
    move_category: MoveCategoryCache = attrs.field(default=MoveCategoryCache(max_size=max_size))
    move_damage_class: MoveDamageClassCache = attrs.field(default=MoveDamageClassCache(max_size=max_size))
    move_learn_method: MoveLearnMethodCache = attrs.field(default=MoveLearnMethodCache(max_size=max_size))
    move_target: MoveTargetCache = attrs.field(default=MoveTargetCache(max_size=max_size))


@attrs.define(slots=True, kw_only=True)
class Pokemon(Base):
    """Cache for pokemon related endpoints.

    Attributes
    ----------
    max_size: int
        The maximum cache size.
    ability: AbilityCache
        The ability.
    characteristic: CharacteristicCache
        The characteristic.
    egg_group: EggGroupCache
        The egg group.
    gender: GenderCache
        The gender cache.
    growth_rate: GrowthRateCache
        The growth rate.
    nature: NatureCache
        The nature.
    pokeathlon_stat: PokeathlonStatCache
        The pokeathlon stat.
    pokemon: PokemonCache
        The pokemon.
    pokemon_color: PokemonColorCache
        The color of a pokemon.
    pokemon_form: PokemonFormCache
        The form of a pokemon.
    pokemon_habitat: PokemonHabitatCache
        The habitat of a pokemon.
    pokemon_shape: PokemonShapeCache
        The shape of a pokemon.
    pokemon_species: PokemonSpeciesCache
        The species of a pokemon.
    stat: StatCache
        The stat.
    type: TypeCache
        The type.
    """

    max_size: int = 100
    ability: AbilityCache = attrs.field(default=AbilityCache(max_size=max_size))
    characteristic: CharacteristicCache = attrs.field(default=CharacteristicCache(max_size=max_size))
    egg_group: EggGroupCache = attrs.field(default=EggGroupCache(max_size=max_size))
    gender: GenderCache = attrs.field(default=GenderCache(max_size=max_size))
    growth_rate: GrowthRateCache = attrs.field(default=GrowthRateCache(max_size=max_size))
    location_area_encounter: PokemonLocationAreaCache = attrs.field(default=PokemonLocationAreaCache(max_size=max_size))
    nature: NatureCache = attrs.field(default=NatureCache(max_size=max_size))
    pokeathlon_stat: PokeathlonStatCache = attrs.field(default=PokeathlonStatCache(max_size=max_size))
    pokemon: PokemonCache = attrs.field(default=PokemonCache(max_size=max_size))
    pokemon_color: PokemonColorCache = attrs.field(default=PokemonColorCache(max_size=max_size))
    pokemon_form: PokemonFormCache = attrs.field(default=PokemonFormCache(max_size=max_size))
    pokemon_habitat: PokemonHabitatCache = attrs.field(default=PokemonHabitatCache(max_size=max_size))
    pokemon_shape: PokemonShapeCache = attrs.field(default=PokemonShapeCache(max_size=max_size))
    pokemon_species: PokemonSpeciesCache = attrs.field(default=PokemonSpeciesCache(max_size=max_size))
    stat: StatCache = attrs.field(default=StatCache(max_size=max_size))
    type: TypeCache = attrs.field(default=TypeCache(max_size=max_size))


@attrs.define(slots=True, kw_only=True)
class Contest(Base):
    """Cache for contest related endpoints.

    Attributes
    ----------
    max_size: int
        The maximum cache size.
    contest_type: ContestTypeCache
        The contest type.
    contest_effect: ContestEffectCache
        The contest effect.
    super_contest_effect: SuperContestEffectCache
        The super contest effect.
    """

    max_size: int = 100
    contest_effect: ContestEffectCache = attrs.field(default=ContestEffectCache(max_size=max_size))
    contest_type: ContestTypeCache = attrs.field(default=ContestTypeCache(max_size=max_size))
    super_contest_effect: SuperContestEffectCache = attrs.field(default=SuperContestEffectCache(max_size=max_size))


@attrs.define(slots=True, kw_only=True)
class Berry(Base):
    """Cache for berry related endpoints.

    Attributes
    ----------
    max_size: int
        The maximum cache size.
    berry: BerryCache
        The berry.
    berry_firmness: BerryFirmnessCache
        The berry firmness.
    berry_flavor: BerryFlavorCache
        The berry flavor.
    """

    max_size: int = 100
    berry: BerryCache = attrs.field(default=BerryCache(max_size=max_size))
    berry_firmness: BerryFirmnessCache = attrs.field(default=BerryFirmnessCache(max_size=max_size))
    berry_flavor: BerryFlavorCache = attrs.field(default=BerryFlavorCache(max_size=max_size))


@attrs.define(slots=True, kw_only=True)
class Cache:
    """Cache for all endpoints.

    Attributes
    ----------
    max_size: int
        The maximum cache size.
    berry: Berry
        The berry cache.
    contest: Contest
        The contest cache.
    encounter: Encounter
        The encounter cache.
    evolution: Evolution
        The evolution cache.
    game: Game
        The game cache.
    item: Item
        The item cache.
    location: Location
        The location cache.
    machine: Machine
        The machine cache.
    move: Move
        The move cache.
    pokemon: Pokemon
        The pokemon cache.
    """

    max_size: int = 100
    berry: Berry = attrs.field(default=Berry(max_size=max_size))
    contest: Contest = attrs.field(default=Contest(max_size=max_size))
    encounter: Encounter = attrs.field(default=Encounter(max_size=max_size))
    evolution: Evolution = attrs.field(default=Evolution(max_size=max_size))
    game: Game = attrs.field(default=Game(max_size=max_size))
    item: Item = attrs.field(default=Item(max_size=max_size))
    location: Location = attrs.field(default=Location(max_size=max_size))
    machine: Machine = attrs.field(default=Machine(max_size=max_size))
    move: Move = attrs.field(default=Move(max_size=max_size))
    pokemon: Pokemon = attrs.field(default=Pokemon(max_size=max_size))

    def __attrs_post_init__(self) -> None:
        obj: attrs.Attribute[Base]
        for obj in self.__attrs_attrs__:  # type: ignore
            if isinstance(obj.default, Base) and obj.default and obj.default.max_size != self.max_size:
                obj.default.set_size(self.max_size)

    def load_documents(self, category: str, _type: str, data: t.List[t.Dict[str, str]]) -> None:
        """Loads the endpoint data into the cache.

        Parameters
        ----------
        category: str
            The category of the endpoint.
        _type: str
            The type of the endpoint.
        data: typing.List[Dict[str, str]]
            The data to load.
        """
        getattr(getattr(self, category.lower()), _type).load_documents(data)
