import typing as t

import attrs

from pokelance.models import BaseModel
from pokelance.models.common import (
    Description,
    FlavorText,
    GenerationGameIndex,
    Name,
    NamedResource,
    Resource,
    VerboseEffect,
    VersionEncounterDetail,
    VersionGameIndex,
)

from .showdown import ShowdownSprites
from .utils import (
    AbilityEffectChange,
    AbilityFlavorText,
    AbilityPokemon,
    AwesomeName,
    Genus,
    GrowthRateExperienceLevel,
    MoveBattleStylePreference,
    MoveStatAffectSets,
    NaturePokeathlonStatAffectSet,
    NatureStatAffectSets,
    NatureStatChange,
    PalParkEncounterArea,
    PokemonAbility,
    PokemonFormSprites,
    PokemonHeldItem,
    PokemonMove,
    PokemonSpeciesDexEntry,
    PokemonSpeciesGender,
    PokemonSpeciesVariety,
    PokemonSprite,
    PokemonStat,
    PokemonType,
    PokemonTypePast,
    TypePokemon,
    TypeRelations,
)

__all__: t.Tuple[str, ...] = (
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


@attrs.define(slots=True, kw_only=True)
class Ability(BaseModel):
    """Ability model.

    Attributes
    ----------
    id: int
        The identifier for this ability resource.
    name: str
        The name for this ability resource.
    is_main_series: bool
        Whether or not this ability originated in the main series of the video games.
    generation: NamedResource
        The generation this ability originated in.
    names: t.List[Name]
        The name of this ability listed in different languages.
    effect_entries: t.List[VerboseEffect]
        The effect of this ability listed in different languages.
    effect_changes: t.List[AbilityEffectChange]
        The list of previous effects this ability has had across version groups of the games.
    flavor_text_entries: t.List[AbilityFlavorText]
        The flavor text of this ability listed in different languages.
    pokemon: t.List[AbilityPokemon]
        A list of Pokémon that could potentially have this ability.
    """

    id: int = attrs.field(factory=int)
    name: str = attrs.field(factory=str)
    is_main_series: bool = attrs.field(factory=bool)
    generation: NamedResource = attrs.field(factory=NamedResource)
    names: t.List[Name] = attrs.field(factory=list)
    effect_entries: t.List[VerboseEffect] = attrs.field(factory=list)
    effect_changes: t.List[AbilityEffectChange] = attrs.field(factory=list)
    flavor_text_entries: t.List[AbilityFlavorText] = attrs.field(factory=list)
    pokemon: t.List[AbilityPokemon] = attrs.field(factory=list)

    @classmethod
    def from_payload(cls, payload: t.Dict[str, t.Any]) -> "Ability":
        return cls(
            id=payload.get("id", 0),
            name=payload.get("name", ""),
            is_main_series=payload.get("is_main_series", False),
            generation=NamedResource.from_payload(payload.get("generation", {}) or {}),
            names=[Name.from_payload(i) for i in payload.get("names", [])],
            effect_entries=[VerboseEffect.from_payload(i) for i in payload.get("effect_entries", [])],
            effect_changes=[AbilityEffectChange.from_payload(i) for i in payload.get("effect_changes", [])],
            flavor_text_entries=[AbilityFlavorText.from_payload(i) for i in payload.get("flavor_text_entries", [])],
            pokemon=[AbilityPokemon.from_payload(i) for i in payload.get("pokemon", [])],
        )


@attrs.define(slots=True, kw_only=True)
class Characteristic(BaseModel):
    """Characteristic model.

    Attributes
    ----------
    id: int
        The identifier for this characteristic resource.
    gene_modulo: int
        The remainder of the highest stat/IV divided by 5.
    possible_values: t.List[int]
        The possible values of the highest stat that would result in a Pokémon
         recieving this characteristic when divided by 5.

    """

    id: int = attrs.field(factory=int)
    gene_modulo: int = attrs.field(factory=int)
    possible_values: t.List[int] = attrs.field(factory=list)

    @classmethod
    def from_payload(cls, payload: t.Dict[str, t.Any]) -> "Characteristic":
        return cls(
            id=payload.get("id", 0),
            gene_modulo=payload.get("gene_modulo", 0),
            possible_values=payload.get("possible_values", []),
        )


@attrs.define(slots=True, kw_only=True)
class EggGroup(BaseModel):
    """EggGroup model.

    Attributes
    ----------
    id: int
        The identifier for this egg group resource.
    name: str
        The name for this egg group resource.
    names: t.List[Name]
        The name of this egg group listed in different languages.
    pokemon_species: t.List[NamedResource]
        A list of all Pokémon species that are members of this egg group.
    """

    id: int = attrs.field(factory=int)
    name: str = attrs.field(factory=str)
    names: t.List[Name] = attrs.field(factory=list)
    pokemon_species: t.List[NamedResource] = attrs.field(factory=list)

    @classmethod
    def from_payload(cls, payload: t.Dict[str, t.Any]) -> "EggGroup":
        return cls(
            id=payload.get("id", 0),
            name=payload.get("name", ""),
            names=[Name.from_payload(i) for i in payload.get("names", [])],
            pokemon_species=[NamedResource.from_payload(i) for i in payload.get("pokemon_species", [])],
        )


@attrs.define(slots=True, kw_only=True)
class Gender(BaseModel):
    """Gender model.

    Attributes
    ----------
    id: int
        The identifier for gender resource.
    name: str
        The name for this gender resource.
    pokemon_species_details: t.List[PokemonSpeciesGender]
        A list of Pokémon species that belong to this gender.
    """

    id: int = attrs.field(factory=int)
    name: str = attrs.field(factory=str)
    pokemon_species_details: t.List[PokemonSpeciesGender] = attrs.field(factory=list)

    @classmethod
    def from_payload(cls, payload: t.Dict[str, t.Any]) -> "Gender":
        return cls(
            id=payload.get("id", 0),
            name=payload.get("name", ""),
            pokemon_species_details=[
                PokemonSpeciesGender.from_payload(i) for i in payload.get("pokemon_species_details", [])
            ],
        )


@attrs.define(slots=True, kw_only=True)
class GrowthRate(BaseModel):
    """GrowthRate model.

    Attributes
    ----------
    id: int
        The identifier for this growth rate resource.
    name: str
        The name for this growth rate resource.
    formula: str
        The formula used to calculate the rate at which the Pokémon species gains level.
    descriptions: t.List[Description]
        The descriptions of this characteristic listed in different languages.
    levels: t.List[GrowthRateExperienceLevel]
        A list of levels and the amount of experienced needed to atain them based on this growth rate.
    pokemon_species: t.List[NamedResource]
        A list of Pokémon species that gain levels at this growth rate.
    """

    id: int = attrs.field(factory=int)
    name: str = attrs.field(factory=str)
    formula: str = attrs.field(factory=str)
    descriptions: t.List[Description] = attrs.field(factory=list)
    levels: t.List[GrowthRateExperienceLevel] = attrs.field(factory=list)
    pokemon_species: t.List[NamedResource] = attrs.field(factory=list)

    @classmethod
    def from_payload(cls, payload: t.Dict[str, t.Any]) -> "GrowthRate":
        return cls(
            id=payload.get("id", 0),
            name=payload.get("name", ""),
            formula=payload.get("formula", ""),
            descriptions=[Description.from_payload(i) for i in payload.get("descriptions", [])],
            levels=[GrowthRateExperienceLevel.from_payload(i) for i in payload.get("levels", [])],
            pokemon_species=[NamedResource.from_payload(i) for i in payload.get("pokemon_species", [])],
        )


@attrs.define(slots=True, kw_only=True)
class Nature(BaseModel):
    """Nature model.

    Attributes
    ----------
    id: int
        The identifier for this nature resource.
    name: str
        The name for this nature resource.
    decreased_stat: NamedAPIResource
        The stat decreased by 10% in Pokémon with this nature.
    increased_stat: NamedAPIResource
        The stat increased by 10% in Pokémon with this nature.
    hates_flavor: NamedAPIResource
        The flavor hated by Pokémon with this nature.
    likes_flavor: NamedAPIResource
        The flavor liked by Pokémon with this nature.
    pokeathlon_stat_changes: t.List[NatureStatChange]
        A list of Pokéathlon stats this nature effects and how much it effects them.
    move_battle_style_preferences: t.List[MoveBattleStylePreference]
        A list of battle styles and how likely a Pokémon with this nature
        is to use them in the Battle Palace or Battle Tent.
    names: t.List[Name]
        The name of this nature listed in different languages.
    """

    id: int = attrs.field(factory=int)
    name: str = attrs.field(factory=str)
    decreased_stat: NamedResource = attrs.field(factory=NamedResource)
    increased_stat: NamedResource = attrs.field(factory=NamedResource)
    hates_flavor: NamedResource = attrs.field(factory=NamedResource)
    likes_flavor: NamedResource = attrs.field(factory=NamedResource)
    pokeathlon_stat_changes: t.List[NatureStatChange] = attrs.field(factory=list)
    move_battle_style_preferences: t.List[MoveBattleStylePreference] = attrs.field(factory=list)
    names: t.List[Name] = attrs.field(factory=list)

    @classmethod
    def from_payload(cls, payload: t.Dict[str, t.Any]) -> "Nature":
        return cls(
            id=payload.get("id", 0),
            name=payload.get("name", ""),
            decreased_stat=NamedResource.from_payload(payload.get("decreased_stat", {}) or {}),
            increased_stat=NamedResource.from_payload(payload.get("increased_stat", {}) or {}),
            hates_flavor=NamedResource.from_payload(payload.get("hates_flavor", {}) or {}),
            likes_flavor=NamedResource.from_payload(payload.get("likes_flavor", {}) or {}),
            pokeathlon_stat_changes=[
                NatureStatChange.from_payload(i) for i in payload.get("pokeathlon_stat_changes", [])
            ],
            move_battle_style_preferences=[
                MoveBattleStylePreference.from_payload(i) for i in payload.get("move_battle_style_preferences", [])
            ],
            names=[Name.from_payload(i) for i in payload.get("names", [])],
        )


@attrs.define(slots=True, kw_only=True)
class PokeathlonStat(BaseModel):
    """PokeathlonStat model.

    Attributes
    ----------
    id: int
        The identifier for this resource.
    name: str
        The name for this resource.
    names: t.List[Name]
        A list of natures which affect this Pokéathlon stat positively or negatively.
    affecting_natures: NaturePokeathlonStatAffectSets
        A detail of natures which affect this Pokéathlon stat positively or negatively.
    """

    id: int = attrs.field(factory=int)
    name: str = attrs.field(factory=str)
    names: t.List[Name] = attrs.field(factory=list)
    affecting_natures: NaturePokeathlonStatAffectSet = attrs.field(factory=NaturePokeathlonStatAffectSet)

    @classmethod
    def from_payload(cls, payload: t.Dict[str, t.Any]) -> "PokeathlonStat":
        return cls(
            id=payload.get("id", 0),
            name=payload.get("name", ""),
            names=[Name.from_payload(i) for i in payload.get("names", [])],
            affecting_natures=NaturePokeathlonStatAffectSet.from_payload(payload.get("affecting_natures", {}) or {}),
        )


@attrs.define(slots=True, kw_only=True)
class Pokemon(BaseModel):
    """Pokemon model.

    Attributes
    ----------
    id: int
        The identifier for this Pokémon resource.
    name: str
        The name for this Pokémon resource.
    base_experience: int
        The base experience gained for defeating this Pokémon.
    height: int
        The height of this Pokémon in decimetres.
    is_default: bool
        Set for exactly one Pokémon used as the default for each species.
    order: int
        Order for sorting. Almost national order, except families are grouped together.
    weight: int
        The weight of this Pokémon in hectograms.
    abilities: t.List[PokemonAbility]
        A list of abilities this Pokémon could potentially have.
    forms: t.List[NamedAPIResource]
        A list of forms this Pokémon can take on.
    game_indices: t.List[VersionGameIndex]
        A list of game indices relevent to Pokémon item by generation.
    held_items: t.List[PokemonHeldItem]
        A list of items this Pokémon may be holding when encountered.
    location_area_encounters: str
        Location area encounter details for different versions.
    moves: t.List[PokemonMove]
        A list of details showing types this Pokémon has.
    species: NamedAPIResource
        The species this Pokémon belongs to.
    sprites: PokemonSprites
        A set of sprites used to depict this Pokémon in the game.
    stats: t.List[PokemonStat]
        A list of details showing all the stats this Pokémon has.
    types: t.List[PokemonType]
        A list of details showing types this Pokémon has.
    showdown: ShowdownSprites
        A set of sprites used to depict this Pokémon in the Showdown client.
    """

    id: int = attrs.field(factory=int)
    name: str = attrs.field(factory=str)
    base_experience: int = attrs.field(factory=int)
    height: int = attrs.field(factory=int)
    is_default: bool = attrs.field(factory=bool)
    order: int = attrs.field(factory=int)
    weight: int = attrs.field(factory=int)
    abilities: t.List[PokemonAbility] = attrs.field(factory=list)
    forms: t.List[NamedResource] = attrs.field(factory=list)
    game_indices: t.List[VersionGameIndex] = attrs.field(factory=list)
    held_items: t.List[PokemonHeldItem] = attrs.field(factory=list)
    location_area_encounters: str = attrs.field(factory=str)
    moves: t.List[PokemonMove] = attrs.field(factory=list)
    past_types: t.List[PokemonTypePast] = attrs.field(factory=list)
    sprites: PokemonSprite = attrs.field(factory=PokemonSprite)
    species: NamedResource = attrs.field(factory=NamedResource)
    stats: t.List[PokemonStat] = attrs.field(factory=list)
    types: t.List[PokemonType] = attrs.field(factory=list)
    showdown: ShowdownSprites = attrs.field(factory=ShowdownSprites)

    @classmethod
    def from_payload(cls, payload: t.Dict[str, t.Any]) -> "Pokemon":
        return cls(
            id=payload.get("id", 0),
            name=payload.get("name", ""),
            base_experience=payload.get("base_experience", 0),
            height=payload.get("height", 0),
            is_default=payload.get("is_default", False),
            order=payload.get("order", 0),
            weight=payload.get("weight", 0),
            abilities=[PokemonAbility.from_payload(i) for i in payload.get("abilities", [])],
            forms=[NamedResource.from_payload(i) for i in payload.get("forms", [])],
            game_indices=[VersionGameIndex.from_payload(i) for i in payload.get("game_indices", [])],
            held_items=[PokemonHeldItem.from_payload(i) for i in payload.get("held_items", [])],
            location_area_encounters=payload.get("location_area_encounters", ""),
            moves=[PokemonMove.from_payload(i) for i in payload.get("moves", [])],
            past_types=[PokemonTypePast.from_payload(i) for i in payload.get("past_types", [])],
            sprites=PokemonSprite.from_payload(payload.get("sprites", {}) or {}),
            species=NamedResource.from_payload(payload.get("species", {}) or {}),
            stats=[PokemonStat.from_payload(i) for i in payload.get("stats", [])],
            types=[PokemonType.from_payload(i) for i in payload.get("types", [])],
            showdown=ShowdownSprites.from_id(payload.get("id", 0)),
        )


@attrs.define(slots=True, kw_only=True)
class LocationAreaEncounter(BaseModel):
    """LocationAreaEncounter model.

    Attributes
    ----------
    location_area: NamedAPIResource
        The location area the referenced Pokémon can be encountered in.
    version_details: t.List[VersionEncounterDetail]
        A list of versions and encounters with the referenced Pokémon that might happen.
    """

    location_area: NamedResource = attrs.field(factory=NamedResource)
    version_details: t.List[VersionEncounterDetail] = attrs.field(factory=list)

    @classmethod
    def from_payload(cls, payload: t.Dict[str, t.Any]) -> "LocationAreaEncounter":
        return cls(
            location_area=NamedResource.from_payload(payload.get("location_area", {}) or {}),
            version_details=[VersionEncounterDetail.from_payload(i) for i in payload.get("version_details", [])],
        )


@attrs.define(slots=True, kw_only=True)
class PokemonColor(BaseModel):
    """PokemonColor model.

    Attributes
    ----------
    id: int
        The identifier for this Pokémon color resource.
    name: str
        The name for this Pokémon color resource.
    names: t.List[Name]
        The name of this Pokémon color listed in different languages.
    pokemon_species: t.List[NamedAPIResource]
        A list of the Pokémon species that have this color.
    """

    id: int = attrs.field(factory=int)
    name: str = attrs.field(factory=str)
    names: t.List[Name] = attrs.field(factory=list)
    pokemon_species: t.List[NamedResource] = attrs.field(factory=list)

    @classmethod
    def from_payload(cls, payload: t.Dict[str, t.Any]) -> "PokemonColor":
        return cls(
            id=payload.get("id", 0),
            name=payload.get("name", ""),
            names=[Name.from_payload(i) for i in payload.get("names", [])],
            pokemon_species=[NamedResource.from_payload(i) for i in payload.get("pokemon_species", [])],
        )


@attrs.define(slots=True, kw_only=True)
class PokemonForm(BaseModel):
    """PokemonForm model.

    Attributes
    ----------
    id: int
        The identifier for this Pokémon form resource.
    name: str
        The name for this Pokémon form resource.
    order: int
        The order in which forms should be sorted within all forms. Multiple forms may have equal order,
        in which case they should fall back on sorting by name.
    form_order: int
        The order in which forms should be sorted within a species' forms.
    is_default: bool
        True for exactly one form used as the default for each Pokémon.
    is_battle_only: bool
        Whether or not this form can only happen during battle.
    is_mega: bool
        Whether or not this form requires mega evolution.
    form_name: str
        The name of this form.
    pokemon: NamedAPIResource
        The Pokémon that can take on this form.
    sprites: PokemonFormSprites
        A set of sprites used to depict this Pokémon form in the game.
    version_group: NamedAPIResource
        The version group this Pokémon form was introduced in.
    names: t.List[Name]
        The form specific full name of this Pokémon form, or empty if the form does not have a specific name.
    form_names: t.List[Name]
        The form specific form name of this Pokémon form, or empty if the form does not have a specific name.
    pokemon_species: NamedAPIResource
        The Pokémon species that this form belongs to.
    """

    id: int = attrs.field(factory=int)
    name: str = attrs.field(factory=str)
    order: int = attrs.field(factory=int)
    form_order: int = attrs.field(factory=int)
    is_default: bool = attrs.field(factory=bool)
    is_battle_only: bool = attrs.field(factory=bool)
    is_mega: bool = attrs.field(factory=bool)
    form_name: str = attrs.field(factory=str)
    pokemon: NamedResource = attrs.field(factory=NamedResource)
    sprites: PokemonFormSprites = attrs.field(factory=PokemonFormSprites)
    version_group: NamedResource = attrs.field(factory=NamedResource)
    names: t.List[Name] = attrs.field(factory=list)
    form_names: t.List[Name] = attrs.field(factory=list)
    pokemon_species: NamedResource = attrs.field(factory=NamedResource)

    @classmethod
    def from_payload(cls, payload: t.Dict[str, t.Any]) -> "PokemonForm":
        return cls(
            id=payload.get("id", 0),
            name=payload.get("name", ""),
            order=payload.get("order", 0),
            form_order=payload.get("form_order", 0),
            is_default=payload.get("is_default", False),
            is_battle_only=payload.get("is_battle_only", False),
            is_mega=payload.get("is_mega", False),
            form_name=payload.get("form_name", ""),
            pokemon=NamedResource.from_payload(payload.get("pokemon", {}) or {}),
            sprites=PokemonFormSprites.from_payload(payload.get("sprites", {}) or {}),
            version_group=NamedResource.from_payload(payload.get("version_group", {}) or {}),
            names=[Name.from_payload(i) for i in payload.get("names", [])],
            form_names=[Name.from_payload(i) for i in payload.get("form_names", [])],
            pokemon_species=NamedResource.from_payload(payload.get("pokemon_species", {}) or {}),
        )


@attrs.define(slots=True, kw_only=True)
class PokemonHabitats(BaseModel):
    """PokemonHabitats model.

    Attributes
    ----------
    id: int
        The identifier for this Pokémon habitat resource.
    name: str
        The name for this Pokémon habitat resource.
    names: t.List[Name]
        The name of this Pokémon habitat listed in different languages.
    pokemon_species: t.List[NamedAPIResource]
        A list of the Pokémon species that can be found in this habitat.
    """

    id: int = attrs.field(factory=int)
    name: str = attrs.field(factory=str)
    names: t.List[Name] = attrs.field(factory=list)
    pokemon_species: t.List[NamedResource] = attrs.field(factory=list)

    @classmethod
    def from_payload(cls, payload: t.Dict[str, t.Any]) -> "PokemonHabitats":
        return cls(
            id=payload.get("id", 0),
            name=payload.get("name", ""),
            names=[Name.from_payload(i) for i in payload.get("names", [])],
            pokemon_species=[NamedResource.from_payload(i) for i in payload.get("pokemon_species", [])],
        )


@attrs.define(slots=True, kw_only=True)
class PokemonShape(BaseModel):
    """PokemonShape model.

    Attributes
    ----------
    id: int
        The identifier for this Pokémon shape resource.
    name: str
        The name for this Pokémon shape resource.
    awesome_names: t.List[AwesomeName]
        The "scientific" name of this Pokémon shape listed in different languages.
    names: t.List[Name]
        The name of this Pokémon shape listed in different languages.
    pokemon_species: t.List[NamedAPIResource]
        A list of the Pokémon species that have this shape.
    """

    id: int = attrs.field(factory=int)
    name: str = attrs.field(factory=str)
    awesome_names: t.List[AwesomeName] = attrs.field(factory=list)
    names: t.List[Name] = attrs.field(factory=list)
    pokemon_species: t.List[NamedResource] = attrs.field(factory=list)

    @classmethod
    def from_payload(cls, payload: t.Dict[str, t.Any]) -> "PokemonShape":
        return cls(
            id=payload.get("id", 0),
            name=payload.get("name", ""),
            awesome_names=[AwesomeName.from_payload(i) for i in payload.get("awesome_names", [])],
            names=[Name.from_payload(i) for i in payload.get("names", [])],
            pokemon_species=[NamedResource.from_payload(i) for i in payload.get("pokemon_species", [])],
        )


@attrs.define(slots=True, kw_only=True)
class PokemonSpecies(BaseModel):
    """PokemonSpecies model.

    Attributes
    ----------
    id: int
        The identifier for this Pokémon species resource.
    name: str
        The name for this Pokémon species resource.
    order: int
        The order in which species should be sorted. Based on National Dex order,
        except families are grouped together and sorted by stage.
    gender_rate: int
        The chance of this Pokémon being of a particular gender. Ratio is male to female. -1 for genderless.
    capture_rate: int
        The base capture rate; up to 255. The higher the number, the easier the catch.
    base_happiness: int
        The happiness when caught by a normal Pokéball; up to 255. The higher the number, the happier the Pokémon.
    is_baby: bool
        Whether or not this is a baby Pokémon.
    is_legendary: bool
        Whether or not this is a legendary Pokémon.
    is_mythical: bool
        Whether or not this is a mythical Pokémon.
    hatch_counter: int
        Initial hatch counter: one must walk 255 × (hatch_counter + 1) steps before this
        Pokémon's egg hatches, unless utilizing bonuses like Flame Body's.
    has_gender_differences: bool
        Whether or not this Pokémon has visual differences due to gender.
    forms_switchable: bool
        Whether or not this Pokémon has multiple forms and can switch between them.
    growth_rate: NamedAPIResource
        The rate at which this Pokémon species gains levels.
    pokedex_numbers: t.List[PokemonSpeciesDexEntry]
        A list of Pokedexes and the indexes reserved within them for this Pokémon species.
    egg_groups: t.List[NamedAPIResource]
        A list of egg groups this Pokémon species is a member of.
    color: NamedAPIResource
        The color of this Pokémon for Pokédex search.
    shape: NamedAPIResource
        The shape of this Pokémon for Pokédex search.
    evolves_from_species: NamedAPIResource
        The Pokémon species that evolves into this Pokemon_species.
    evolution_chain: APIResource
        The evolution chain this Pokémon species is a member of.
    habitat: NamedAPIResource
        The habitat this Pokémon species can be encountered in.
    generation: NamedAPIResource
        The generation this Pokémon species was introduced in.
    names: t.List[Name]
        The name of this Pokémon species listed in different languages.
    pal_park_encounters: t.List[PalParkEncounterArea]
        A list of encounters that can be had with this Pokémon species in pal park.
    flavor_text_entries: t.List[FlavorText]
        A list of flavor text entries for this Pokémon species.
    form_descriptions: t.List[Description]
        A list of form description for this Pokémon species.
    genera: t.List[Genus]
        A list of the genus of this Pokémon species listed in multiple languages.
    varieties: t.List[PokemonSpeciesVariety]
        A list of the Pokémon that exist within this Pokémon species.
    """

    id: int = attrs.field(factory=int)
    name: str = attrs.field(factory=str)
    order: int = attrs.field(factory=int)
    gender_rate: int = attrs.field(factory=int)
    capture_rate: int = attrs.field(factory=int)
    base_happiness: int = attrs.field(factory=int)
    is_baby: bool = attrs.field(factory=bool)
    is_legendary: bool = attrs.field(factory=bool)
    is_mythical: bool = attrs.field(factory=bool)
    hatch_counter: int = attrs.field(factory=int)
    has_gender_differences: bool = attrs.field(factory=bool)
    forms_switchable: bool = attrs.field(factory=bool)
    growth_rate: NamedResource = attrs.field(factory=NamedResource)
    pokedex_numbers: t.List[PokemonSpeciesDexEntry] = attrs.field(factory=list)
    egg_groups: t.List[NamedResource] = attrs.field(factory=list)
    color: NamedResource = attrs.field(factory=NamedResource)
    shape: NamedResource = attrs.field(factory=NamedResource)
    evolves_from_species: NamedResource = attrs.field(factory=NamedResource)
    evolution_chain: Resource = attrs.field(factory=Resource)
    habitat: NamedResource = attrs.field(factory=NamedResource)
    generation: NamedResource = attrs.field(factory=NamedResource)
    names: t.List[Name] = attrs.field(factory=list)
    pal_park_encounters: t.List[PalParkEncounterArea] = attrs.field(factory=list)
    flavor_text_entries: t.List[FlavorText] = attrs.field(factory=list)
    form_descriptions: t.List[Description] = attrs.field(factory=list)
    genera: t.List[Genus] = attrs.field(factory=list)
    varieties: t.List[PokemonSpeciesVariety] = attrs.field(factory=list)

    @classmethod
    def from_payload(cls, payload: t.Dict[str, t.Any]) -> "PokemonSpecies":
        return cls(
            id=payload.get("id", 0),
            name=payload.get("name", ""),
            order=payload.get("order", 0),
            gender_rate=payload.get("gender_rate", 0),
            capture_rate=payload.get("capture_rate", 0),
            base_happiness=payload.get("base_happiness", 0),
            is_baby=payload.get("is_baby", False),
            is_legendary=payload.get("is_legendary", False),
            is_mythical=payload.get("is_mythical", False),
            hatch_counter=payload.get("hatch_counter", 0),
            has_gender_differences=payload.get("has_gender_differences", False),
            forms_switchable=payload.get("forms_switchable", False),
            growth_rate=NamedResource.from_payload(payload.get("growth_rate", {}) or {}),
            pokedex_numbers=[PokemonSpeciesDexEntry.from_payload(i) for i in payload.get("pokedex_numbers", [])],
            egg_groups=[NamedResource.from_payload(i) for i in payload.get("egg_groups", [])],
            color=NamedResource.from_payload(payload.get("color", {}) or {}),
            shape=NamedResource.from_payload(payload.get("shape", {}) or {}),
            evolves_from_species=NamedResource.from_payload(payload.get("evolves_from_species", {}) or {}),
            evolution_chain=Resource.from_payload(payload.get("evolution_chain", {}) or {}),
            habitat=NamedResource.from_payload(payload.get("habitat", {}) or {}),
            generation=NamedResource.from_payload(payload.get("generation", {}) or {}),
            names=[Name.from_payload(i) for i in payload.get("names", [])],
            pal_park_encounters=[PalParkEncounterArea.from_payload(i) for i in payload.get("pal_park_encounters", [])],
            flavor_text_entries=[FlavorText.from_payload(i) for i in payload.get("flavor_text_entries", [])],
            form_descriptions=[Description.from_payload(i) for i in payload.get("form_descriptions", [])],
            genera=[Genus.from_payload(i) for i in payload.get("genera", [])],
            varieties=[PokemonSpeciesVariety.from_payload(i) for i in payload.get("varieties", [])],
        )


@attrs.define(slots=True, kw_only=True)
class Stat(BaseModel):
    """
    A Pokémon stat model.

    Attributes
    ----------
    id: int
        The identifier for this resource.
    name: str
        The name for this resource.
    game_index: int
        The stat order in which effects of this stat take place during battle.
    is_battle_only: bool
        Whether this stat only exists within a battle.
    affecting_moves: MoveStatAffectSets
        A detail of moves which affect this stat positively or negatively.
    affecting_natures: NatureStatAffectSets
        A detail of natures which affect this stat positively or negatively.
    characteristics: t.List[Resource]
        A list of characteristics that are set on a Pokémon when its highest base stat is this stat.
    move_damage_class: NamedResource
        The class of damage this stat is directly related to.
    names: t.List[Name]
        The name of this resource listed in different languages.
    """

    id: int = attrs.field(factory=int)
    name: str = attrs.field(factory=str)
    game_index: int = attrs.field(factory=int)
    is_battle_only: bool = attrs.field(factory=bool)
    affecting_moves: MoveStatAffectSets = attrs.field(factory=MoveStatAffectSets)
    affecting_natures: NatureStatAffectSets = attrs.field(factory=NatureStatAffectSets)
    characteristics: t.List[Resource] = attrs.field(factory=list)
    move_damage_class: NamedResource = attrs.field(factory=NamedResource)
    names: t.List[Name] = attrs.field(factory=list)

    @classmethod
    def from_payload(cls, payload: t.Dict[str, t.Any]) -> "Stat":
        return cls(
            id=payload.get("id", 0),
            name=payload.get("name", ""),
            game_index=payload.get("game_index", 0),
            is_battle_only=payload.get("is_battle_only", False),
            affecting_moves=MoveStatAffectSets.from_payload(payload.get("affecting_moves", {}) or {}),
            affecting_natures=NatureStatAffectSets.from_payload(payload.get("affecting_natures", {}) or {}),
            characteristics=[Resource.from_payload(i) for i in payload.get("characteristics", [])],
            move_damage_class=NamedResource.from_payload(payload.get("move_damage_class", {}) or {}),
            names=[Name.from_payload(i) for i in payload.get("names", [])],
        )


@attrs.define(slots=True, kw_only=True)
class Type(BaseModel):
    """
    A Pokémon type model.

    Attributes
    ----------
    id: int
        The identifier for this resource.
    name: str
        The name for this resource.
    damage_relations: TypeRelations
        A detail of how effective this type is toward others and vice versa.
    game_indices: t.List[GenerationGameIndex]
        A list of game indices relevent to this item by generation.
    generation: NamedResource
        The generation this type was introduced in.
    move_damage_class: NamedResource
        The class of damage inflicted by this type.
    names: t.List[Name]
        The name of this resource listed in different languages.
    pokemon: t.List[TypePokemon]
        A list of details of Pokémon that have this type.
    moves: t.List[NamedResource]
        A list of moves that have this type.
    """

    id: int = attrs.field(factory=int)
    name: str = attrs.field(factory=str)
    damage_relations: TypeRelations = attrs.field(factory=TypeRelations)
    game_indices: t.List[GenerationGameIndex] = attrs.field(factory=list)
    generation: NamedResource = attrs.field(factory=NamedResource)
    move_damage_class: NamedResource = attrs.field(factory=NamedResource)
    names: t.List[Name] = attrs.field(factory=list)
    pokemon: t.List[TypePokemon] = attrs.field(factory=list)
    moves: t.List[NamedResource] = attrs.field(factory=list)

    @classmethod
    def from_payload(cls, payload: t.Dict[str, t.Any]) -> "Type":
        return cls(
            id=payload.get("id", 0),
            name=payload.get("name", ""),
            damage_relations=TypeRelations.from_payload(payload.get("damage_relations", {}) or {}),
            game_indices=[GenerationGameIndex.from_payload(i) for i in payload.get("game_indices", [])],
            generation=NamedResource.from_payload(payload.get("generation", {}) or {}),
            move_damage_class=NamedResource.from_payload(payload.get("move_damage_class", {}) or {}),
            names=[Name.from_payload(i) for i in payload.get("names", [])],
            pokemon=[TypePokemon.from_payload(i) for i in payload.get("pokemon", [])],
            moves=[NamedResource.from_payload(i) for i in payload.get("moves", [])],
        )
