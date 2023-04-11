import typing as t

import attrs

from pokelance.models import BaseModel
from pokelance.models.common import Effect, NamedResource

__all__: t.Tuple[str, ...] = (
    "AbilityEffectChange",
    "AbilityFlavorText",
    "AbilityPokemon",
    "PokemonSpeciesGender",
    "GrowthRateExperienceLevel",
    "NatureStatChange",
    "MoveBattleStylePreference",
    "NaturePokeathlonStatAffect",
    "NaturePokeathlonStatAffectSet",
    "PokemonMoveVersion",
    "PokemonStat",
    "PokemonType",
    "PokemonHeldItemVersion",
    "PokemonHeldItem",
    "PokemonSprite",
    "PokemonAbility",
    "PokemonMove",
    "PokemonTypePast",
    "PokemonFormType",
    "PokemonFormSprites",
    "AwesomeName",
    "PokemonSpeciesVariety",
    "PokemonSpeciesDexEntry",
    "PalParkEncounterArea",
    "Genus",
    "MoveStatAffectSets",
    "NatureStatAffectSets",
    "MoveStatEffect",
    "TypeRelations",
    "TypePokemon",
    "TypeRelationsPast",
)


@attrs.define(kw_only=True, slots=True)
class BaseSprite(BaseModel):
    """A pokemon sprite resource.

    Attributes
    ----------
    front_default: str
        The default depiction of this pokemon from the front in battle.
    front_shiny: str
        The shiny depiction of this pokemon from the front in battle.
    front_female: str
        The default depiction of female gender of this pokemon from the front in battle.
    front_shiny_female: str
        The shiny depiction of female gender of this pokemon from the front in battle.
    back_default: str
        The default depiction of this pokemon from the back in battle.
    back_shiny: str
        The shiny depiction of this pokemon from the back in battle.
    back_female: str
        The default depiction of female gender of this pokemon from the back in battle.
    back_shiny_female: str
        The shiny depiction of female gender of this pokemon from the back in battle.
    """

    back_default: str = attrs.field(factory=str)
    back_shiny: str = attrs.field(factory=str)
    back_female: str = attrs.field(factory=str)
    back_shiny_female: str = attrs.field(factory=str)
    front_default: str = attrs.field(factory=str)
    front_shiny: str = attrs.field(factory=str)
    front_female: str = attrs.field(factory=str)
    front_shiny_female: str = attrs.field(factory=str)


@attrs.define(kw_only=True, slots=True)
class Generation(BaseModel):
    """A generation resource."""

    ...


@attrs.define(kw_only=True, slots=True)
class Animated(BaseSprite):
    """A pokemon animated sprite resource."""

    @classmethod
    def from_payload(cls, payload: t.Dict[str, t.Any]) -> "Animated":
        return cls(
            back_default=payload.get("back_default", ""),
            back_shiny=payload.get("back_shiny", ""),
            back_female=payload.get("back_female", ""),
            back_shiny_female=payload.get("back_shiny_female", ""),
            front_default=payload.get("front_default", ""),
            front_shiny=payload.get("front_shiny", ""),
            front_female=payload.get("front_female", ""),
            front_shiny_female=payload.get("front_shiny_female", ""),
        )


@attrs.define(kw_only=True, slots=True)
class VersionSprite(BaseSprite):
    """A pokemon version sprite resource.

    Attributes
    ----------
    back_gray: str
        The gray depiction of this pokemon from the back in battle.
    front_gray: str
        The gray depiction of this pokemon from the front in battle.
    back_transperent: str
        The transparent depiction of this pokemon from the back in battle.
    front_transperent: str
        The transparent depiction of this pokemon from the front in battle.
    animated: Animated
        The animated depiction of this pokemon.
    """

    back_gray: str = attrs.field(factory=str)
    back_transperent: str = attrs.field(factory=str)
    back_shiny_transperent: str = attrs.field(factory=str)
    front_gray: str = attrs.field(factory=str)
    front_transperent: str = attrs.field(factory=str)
    front_shiny_transperent: str = attrs.field(factory=str)
    animated: Animated = attrs.field(factory=Animated)

    @classmethod
    def from_payload(cls, payload: t.Dict[str, t.Any]) -> "VersionSprite":
        return cls(
            back_default=payload.get("back_default", ""),
            back_gray=payload.get("back_gray", ""),
            back_shiny=payload.get("back_shiny", ""),
            back_transperent=payload.get("back_transperent", ""),
            back_shiny_transperent=payload.get("back_shiny_transperent", ""),
            back_female=payload.get("back_female", ""),
            back_shiny_female=payload.get("back_shiny_female", ""),
            front_default=payload.get("front_default", ""),
            front_shiny=payload.get("front_shiny", ""),
            front_shiny_transperent=payload.get("front_shiny_transperent", ""),
            front_female=payload.get("front_female", ""),
            front_shiny_female=payload.get("front_shiny_female", ""),
            front_gray=payload.get("front_gray", ""),
            front_transperent=payload.get("front_transperent", ""),
            animated=Animated.from_payload(payload.get("animated", {}) or {}),
        )


@attrs.define(kw_only=True, slots=True)
class GenerationI(Generation):
    """A generation I resource.

    Attributes
    ----------
    red_blue: VersionSprite
        The red-blue depiction of this pokemon.
    yellow: VersionSprite
        The yellow depiction of this pokemon.
    """

    red_blue: VersionSprite = attrs.field(factory=VersionSprite)
    yellow: VersionSprite = attrs.field(factory=VersionSprite)

    @classmethod
    def from_payload(cls, payload: t.Dict[str, t.Any]) -> "GenerationI":
        return cls(
            red_blue=VersionSprite.from_payload(payload.get("red-blue", {}) or {}),
            yellow=VersionSprite.from_payload(payload.get("yellow", {}) or {}),
        )


@attrs.define(kw_only=True, slots=True)
class GenerationII(Generation):
    """A generation II resource.

    Attributes
    ----------
    crystal: VersionSprite
        The crystal depiction of this pokemon.
    gold: VersionSprite
        The gold depiction of this pokemon.
    silver: VersionSprite
        The silver depiction of this pokemon.
    """

    crystal: VersionSprite = attrs.field(factory=VersionSprite)
    gold: VersionSprite = attrs.field(factory=VersionSprite)
    silver: VersionSprite = attrs.field(factory=VersionSprite)

    @classmethod
    def from_payload(cls, payload: t.Dict[str, t.Any]) -> "GenerationII":
        return cls(
            crystal=VersionSprite.from_payload(payload.get("crystal", {}) or {}),
            gold=VersionSprite.from_payload(payload.get("gold", {}) or {}),
            silver=VersionSprite.from_payload(payload.get("silver", {}) or {}),
        )


@attrs.define(kw_only=True, slots=True)
class GenerationIII(Generation):
    """A generation III resource.

    Attributes
    ----------
    emerald: VersionSprite
        The emerald depiction of this pokemon.
    firered_leafgreen: VersionSprite
        The firered-leafgreen depiction of this pokemon.
    ruby_sapphire: VersionSprite
        The ruby-sapphire depiction of this pokemon.
    """

    emerald: VersionSprite = attrs.field(factory=VersionSprite)
    firered_leafgreen: VersionSprite = attrs.field(factory=VersionSprite)
    ruby_sapphire: VersionSprite = attrs.field(factory=VersionSprite)

    @classmethod
    def from_payload(cls, payload: t.Dict[str, t.Any]) -> "GenerationIII":
        return cls(
            emerald=VersionSprite.from_payload(payload.get("emerald", {}) or {}),
            firered_leafgreen=VersionSprite.from_payload(payload.get("firered-leafgreen", {}) or {}),
            ruby_sapphire=VersionSprite.from_payload(payload.get("ruby-sapphire", {}) or {}),
        )


@attrs.define(kw_only=True, slots=True)
class GenerationIV(Generation):
    """A generation IV resource.

    Attributes
    ----------
    diamond_pearl: VersionSprite
        The diamond-pearl depiction of this pokemon.
    heartgold_soulsilver: VersionSprite
        The heartgold-soulsilver depiction of this pokemon.
    platinum: VersionSprite
        The platinum depiction of this pokemon.
    """

    diamond_pearl: VersionSprite = attrs.field(factory=VersionSprite)
    heartgold_soulsilver: VersionSprite = attrs.field(factory=VersionSprite)
    platinum: VersionSprite = attrs.field(factory=VersionSprite)

    @classmethod
    def from_payload(cls, payload: t.Dict[str, t.Any]) -> "GenerationIV":
        return cls(
            diamond_pearl=VersionSprite.from_payload(payload.get("diamond-pearl", {}) or {}),
            heartgold_soulsilver=VersionSprite.from_payload(payload.get("heartgold-soulsilver", {}) or {}),
            platinum=VersionSprite.from_payload(payload.get("platinum", {}) or {}),
        )


@attrs.define(kw_only=True, slots=True)
class GenerationV(Generation):
    """A generation V resource.

    Attributes
    ----------
    black_white: VersionSprite
        The black-white depiction of this pokemon.
    """

    black_white: VersionSprite = attrs.field(factory=VersionSprite)

    @classmethod
    def from_payload(cls, payload: t.Dict[str, t.Any]) -> "GenerationV":
        return cls(
            black_white=VersionSprite.from_payload(payload.get("black-white", {}) or {}),
        )


@attrs.define(kw_only=True, slots=True)
class GenerationVI(Generation):
    """A generation VI resource.

    Attributes
    ----------
    omegaruby_alphasapphire: VersionSprite
        The omegaruby-alphasapphire depiction of this pokemon.
    x_y: VersionSprite
        The x-y depiction of this pokemon.
    """

    omegaruby_alphasapphire: VersionSprite = attrs.field(factory=VersionSprite)
    x_y: VersionSprite = attrs.field(factory=VersionSprite)

    @classmethod
    def from_payload(cls, payload: t.Dict[str, t.Any]) -> "GenerationVI":
        return cls(
            omegaruby_alphasapphire=VersionSprite.from_payload(payload.get("omegaruby-alphasapphire", {}) or {}),
            x_y=VersionSprite.from_payload(payload.get("x-y", {}) or {}),
        )


@attrs.define(kw_only=True, slots=True)
class GenerationVII(Generation):
    """A generation VII resource.

    Attributes
    ----------
    icons: VersionSprite
        The icons depiction of this pokemon.
    ultra_sun_ultra_moon: VersionSprite
        The ultra-sun-ultra-moon depiction of this pokemon.
    """

    icons: VersionSprite = attrs.field(factory=VersionSprite)
    ultra_sun_ultra_moon: VersionSprite = attrs.field(factory=VersionSprite)

    @classmethod
    def from_payload(cls, payload: t.Dict[str, t.Any]) -> "GenerationVII":
        return cls(
            icons=VersionSprite.from_payload(payload.get("icons", {}) or {}),
            ultra_sun_ultra_moon=VersionSprite.from_payload(payload.get("ultra-sun-ultra-moon", {}) or {}),
        )


@attrs.define(kw_only=True, slots=True)
class GenerationVIII(Generation):
    """A generation VIII resource.

    Attributes
    ----------
    icons: VersionSprite
        The icons depiction of this pokemon.
    """

    icons: VersionSprite = attrs.field(factory=VersionSprite)

    @classmethod
    def from_payload(cls, payload: t.Dict[str, t.Any]) -> "GenerationVIII":
        return cls(
            icons=VersionSprite.from_payload(payload.get("icons", {}) or {}),
        )


@attrs.define(kw_only=True, slots=True)
class Versions(BaseModel):
    """A sprite resource for all generations.

    Attributes
    ----------
    generation_i: GenerationI
        The generation I depiction of this pokemon.
    generation_ii: GenerationII
        The generation II depiction of this pokemon.
    generation_iii: GenerationIII
        The generation III depiction of this pokemon.
    generation_iv: GenerationIV
        The generation IV depiction of this pokemon.
    generation_v: GenerationV
        The generation V depiction of this pokemon.
    generation_vi: GenerationVI
        The generation VI depiction of this pokemon.
    generation_vii: GenerationVII
        The generation VII depiction of this pokemon.
    generation_viii: GenerationVIII
        The generation VIII depiction of this pokemon.
    """

    generation_i: GenerationI = attrs.field(factory=GenerationI)
    generation_ii: GenerationII = attrs.field(factory=GenerationII)
    generation_iii: GenerationIII = attrs.field(factory=GenerationIII)
    generation_iv: GenerationIV = attrs.field(factory=GenerationIV)
    generation_v: GenerationV = attrs.field(factory=GenerationV)
    generation_vi: GenerationVI = attrs.field(factory=GenerationVI)
    generation_vii: GenerationVII = attrs.field(factory=GenerationVII)
    generation_viii: GenerationVIII = attrs.field(factory=GenerationVIII)

    @classmethod
    def from_payload(cls, payload: t.Dict[str, t.Any]) -> "Versions":
        return cls(
            generation_i=GenerationI.from_payload(payload.get("generation-i", {}) or {}),
            generation_ii=GenerationII.from_payload(payload.get("generation-ii", {}) or {}),
            generation_iii=GenerationIII.from_payload(payload.get("generation-iii", {}) or {}),
            generation_iv=GenerationIV.from_payload(payload.get("generation-iv", {}) or {}),
            generation_v=GenerationV.from_payload(payload.get("generation-v", {}) or {}),
            generation_vi=GenerationVI.from_payload(payload.get("generation-vi", {}) or {}),
            generation_vii=GenerationVII.from_payload(payload.get("generation-vii", {}) or {}),
            generation_viii=GenerationVIII.from_payload(payload.get("generation-viii", {}) or {}),
        )


@attrs.define(kw_only=True, slots=True)
class DreamWorld(BaseModel):
    """A dream world resource.

    Attributes
    ----------
    front_default: str
        The default depiction of this pokemon.
    front_female: str
        The female depiction of this pokemon.
    """

    front_default: str = attrs.field(factory=str)
    front_female: str = attrs.field(factory=str)

    @classmethod
    def from_payload(cls, payload: t.Dict[str, t.Any]) -> "DreamWorld":
        return cls(
            front_default=payload.get("front_default", ""),
            front_female=payload.get("front_female", ""),
        )


@attrs.define(kw_only=True, slots=True)
class Home(BaseModel):
    """A home resource.

    Attributes
    ----------
    front_default: str
        The default depiction of this pokemon.
    front_female: str
        The female depiction of this pokemon.
    front_shiny: str
        The shiny depiction of this pokemon.
    front_shiny_female: str
        The shiny female depiction of this pokemon.
    """

    front_default: str = attrs.field(factory=str)
    front_female: str = attrs.field(factory=str)
    front_shiny: str = attrs.field(factory=str)
    front_shiny_female: str = attrs.field(factory=str)

    @classmethod
    def from_payload(cls, payload: t.Dict[str, t.Any]) -> "Home":
        return cls(
            front_default=payload.get("front_default", ""),
            front_female=payload.get("front_female", ""),
            front_shiny=payload.get("front_shiny", ""),
            front_shiny_female=payload.get("front_shiny_female", ""),
        )


@attrs.define(kw_only=True, slots=True)
class OfficialArtwork(BaseModel):
    """Official artwork for this Pokémon from Nintendo.

    Attributes
    ----------
    front_default: str
        The default depiction of this Pokémon from the official artwork.
    front_shiny: str
        The shiny depiction of this Pokémon from the official artwork.
    """

    front_default: str = attrs.field(factory=str)
    front_shiny: str = attrs.field(factory=str)

    @classmethod
    def from_payload(cls, payload: t.Dict[str, t.Any]) -> "OfficialArtwork":
        return cls(
            front_default=payload.get("front_default", ""),
            front_shiny=payload.get("front_shiny", ""),
        )


@attrs.define(slots=True, kw_only=True)
class Other(BaseModel):
    """Other sprites for this pokemon

    Attributes
    ----------
    dream_world: DreamWorld
        The dream world sprites for this pokemon
    home: Home
        The home sprites for this pokemon
    official_artwork: OfficialArtwork
        The official artwork sprites for this pokemon
    """

    dream_world: DreamWorld = attrs.field(factory=DreamWorld)
    home: Home = attrs.field(factory=Home)
    official_artwork: OfficialArtwork = attrs.field(factory=OfficialArtwork)

    @classmethod
    def from_payload(cls, payload: t.Dict[str, t.Any]) -> "Other":
        return cls(
            dream_world=DreamWorld.from_payload(payload.get("dream_world", {}) or {}),
            home=Home.from_payload(payload.get("home", {}) or {}),
            official_artwork=OfficialArtwork.from_payload(payload.get("official-artwork", {}) or {}),
        )


@attrs.define(slots=True, kw_only=True)
class AbilityEffectChange(BaseModel):
    """An ability effect change resource.

    Attributes
    ----------
    effect_entries: t.List[Effect]
        The previous effect of this ability listed in different languages.
    version_group: NamedResource
        The version group in which the previous effect of this ability originated.
    """

    effect_entries: t.List[Effect] = attrs.field(factory=list)
    version_group: NamedResource = attrs.field(factory=NamedResource)

    @classmethod
    def from_payload(cls, payload: t.Dict[str, t.Any]) -> "AbilityEffectChange":
        return cls(
            effect_entries=[Effect.from_payload(i) for i in payload.get("effect_entries", [])],
            version_group=NamedResource.from_payload(payload.get("version_group", {}) or {}),
        )


@attrs.define(slots=True, kw_only=True)
class AbilityFlavorText(BaseModel):
    """An ability flavor text resource.

    Attributes
    ----------
    flavor_text: str
        The localized flavor text for an api resource in a specific language.
    language: NamedResource
        The language this name is in.
    version_group: NamedResource
        The version group that uses this flavor text.
    """

    flavor_text: str = attrs.field(factory=str)
    language: NamedResource = attrs.field(factory=NamedResource)
    version_group: NamedResource = attrs.field(factory=NamedResource)

    @classmethod
    def from_payload(cls, payload: t.Dict[str, t.Any]) -> "AbilityFlavorText":
        return cls(
            flavor_text=payload.get("flavor_text", ""),
            language=NamedResource.from_payload(payload.get("language", {}) or {}),
            version_group=NamedResource.from_payload(payload.get("version_group", {}) or {}),
        )


@attrs.define(slots=True, kw_only=True)
class AbilityPokemon(BaseModel):
    """An ability pokemon resource.

    Attributes
    ----------
    is_hidden: bool
        Whether or not this a hidden ability for the referenced pokemon.
    slot: int
        The slot this ability occupies in this pokemon species.
    pokemon: NamedResource
        The pokemon this ability could belong to.
    """

    is_hidden: bool = attrs.field(factory=bool)
    slot: int = attrs.field(factory=int)
    pokemon: NamedResource = attrs.field(factory=NamedResource)

    @classmethod
    def from_payload(cls, payload: t.Dict[str, t.Any]) -> "AbilityPokemon":
        return cls(
            is_hidden=payload.get("is_hidden", False),
            slot=payload.get("slot", 0),
            pokemon=NamedResource.from_payload(payload.get("pokemon", {}) or {}),
        )


@attrs.define(slots=True, kw_only=True)
class PokemonSpeciesGender(BaseModel):
    """A pokemon species gender resource.

    Attributes
    ----------
    rate: int
        The chance of a particular gender in this pokemon species.
    pokemon_species: NamedResource
        The pokemon species here.
    """

    rate: int = attrs.field(factory=int)
    pokemon_species: NamedResource = attrs.field(factory=NamedResource)

    @classmethod
    def from_payload(cls, payload: t.Dict[str, t.Any]) -> "PokemonSpeciesGender":
        return cls(
            rate=payload.get("rate", 0),
            pokemon_species=NamedResource.from_payload(payload.get("pokemon_species", {}) or {}),
        )


@attrs.define(slots=True, kw_only=True)
class GrowthRateExperienceLevel(BaseModel):
    """A growth rate experience level resource.

    Attributes
    ----------
    level: int
        The level gained.
    experience: int
        The amount of experience required to reach the referenced level.
    """

    level: int = attrs.field(factory=int)
    experience: int = attrs.field(factory=int)

    @classmethod
    def from_payload(cls, payload: t.Dict[str, t.Any]) -> "GrowthRateExperienceLevel":
        return cls(
            level=payload.get("level", 0),
            experience=payload.get("experience", 0),
        )


@attrs.define(slots=True, kw_only=True)
class NatureStatChange(BaseModel):
    """A nature stat change resource.

    Attributes
    ----------
    max_change: int
        The maximum amount of change to the referenced stat.
    pokeathlon_stat: NamedResource
        The stat being affected.
    """

    max_change: int = attrs.field(factory=int)
    pokeathlon_stat: NamedResource = attrs.field(factory=NamedResource)

    @classmethod
    def from_payload(cls, payload: t.Dict[str, t.Any]) -> "NatureStatChange":
        return cls(
            max_change=payload.get("max_change", 0),
            pokeathlon_stat=NamedResource.from_payload(payload.get("pokeathlon_stat", {}) or {}),
        )


@attrs.define(slots=True, kw_only=True)
class MoveBattleStylePreference(BaseModel):
    """A move battle style preference resource.

    Attributes
    ----------
    low_hp_preference: int
        Chance of using the move, in percent, if HP is under one half.
    high_hp_preference: int
        Chance of using the move, in percent, if HP is over one half.
    move_battle_style: NamedResource
        The move battle style.
    """

    low_hp_preference: int = attrs.field(factory=int)
    high_hp_preference: int = attrs.field(factory=int)
    move_battle_style: NamedResource = attrs.field(factory=NamedResource)

    @classmethod
    def from_payload(cls, payload: t.Dict[str, t.Any]) -> "MoveBattleStylePreference":
        return cls(
            low_hp_preference=payload.get("low_hp_preference", 0),
            high_hp_preference=payload.get("high_hp_preference", 0),
            move_battle_style=NamedResource.from_payload(payload.get("battle_style", {}) or {}),
        )


@attrs.define(slots=True, kw_only=True)
class NaturePokeathlonStatAffect(BaseModel):
    """A nature pokeathlon stat affect resource.

    Attributes
    ----------
    max_change: int
        The maximum amount of change to the referenced stat.
    nature: NamedResource
        The nature causing the change.
    """

    max_change: int = attrs.field(factory=int)
    nature: NamedResource = attrs.field(factory=NamedResource)

    @classmethod
    def from_payload(cls, payload: t.Dict[str, t.Any]) -> "NaturePokeathlonStatAffect":
        return cls(
            max_change=payload.get("max_change", 0),
            nature=NamedResource.from_payload(payload.get("nature", {}) or {}),
        )


@attrs.define(slots=True, kw_only=True)
class NaturePokeathlonStatAffectSet(BaseModel):
    """A nature pokeathlon stat affect set resource.

    Attributes
    ----------
    increase: t.List[NaturePokeathlonStatAffect]
        A list of natures and how they change the referenced pokeathlon stat.
    decrease: t.List[NaturePokeathlonStatAffect]
        A list of natures and how they change the referenced pokeathlon stat.
    """

    increase: t.List[NaturePokeathlonStatAffect] = attrs.field(factory=list)
    decrease: t.List[NaturePokeathlonStatAffect] = attrs.field(factory=list)

    @classmethod
    def from_payload(cls, payload: t.Dict[str, t.Any]) -> "NaturePokeathlonStatAffectSet":
        return cls(
            increase=[NaturePokeathlonStatAffect.from_payload(i) for i in payload.get("increase", [])],
            decrease=[NaturePokeathlonStatAffect.from_payload(i) for i in payload.get("decrease", [])],
        )


@attrs.define(slots=True, kw_only=True)
class PokemonAbility(BaseModel):
    """A pokemon ability resource.

    Attributes
    ----------
    is_hidden: bool
        Whether or not this is a hidden ability.
    slot: int
        The slot this ability occupies in this pokemon species.
    ability: NamedResource
        The ability the pokemon may have.
    """

    is_hidden: bool = attrs.field(factory=bool)
    slot: int = attrs.field(factory=int)
    ability: NamedResource = attrs.field(factory=NamedResource)

    @classmethod
    def from_payload(cls, payload: t.Dict[str, t.Any]) -> "PokemonAbility":
        return cls(
            is_hidden=payload.get("is_hidden", False),
            slot=payload.get("slot", 0),
            ability=NamedResource.from_payload(payload.get("ability", {}) or {}),
        )


@attrs.define(slots=True, kw_only=True)
class PokemonType(BaseModel):
    """A pokemon type resource.

    Attributes
    ----------
    slot: int
        The order the types are listed in.
    type: NamedResource
        The type the referenced pokemon has.
    """

    slot: int = attrs.field(factory=int)
    type: NamedResource = attrs.field(factory=NamedResource)

    @classmethod
    def from_payload(cls, payload: t.Dict[str, t.Any]) -> "PokemonType":
        return cls(
            slot=payload.get("slot", 0),
            type=NamedResource.from_payload(payload.get("type", {}) or {}),
        )


@attrs.define(slots=True, kw_only=True)
class PokemonFormType(BaseModel):
    """A pokemon form type resource.

    Attributes
    ----------
    slot: int
        The order the types are listed in.
    type: NamedResource
        The type the referenced pokemon has.
    """

    slot: int = attrs.field(factory=int)
    type: NamedResource = attrs.field(factory=NamedResource)

    @classmethod
    def from_payload(cls, payload: t.Dict[str, t.Any]) -> "PokemonFormType":
        return cls(
            slot=payload.get("slot", 0),
            type=NamedResource.from_payload(payload.get("type", {}) or {}),
        )


@attrs.define(slots=True, kw_only=True)
class PokemonTypePast(BaseModel):
    """A pokemon type past resource.

    Attributes
    ----------
    generation: NamedResource
        The generation this type was introduced in.
    types: t.List[NamedResource]
        The name of the type.
    """

    generation: NamedResource = attrs.field(factory=NamedResource)
    types: t.List[PokemonType] = attrs.field(factory=list)

    @classmethod
    def from_payload(cls, payload: t.Dict[str, t.Any]) -> "PokemonTypePast":
        return cls(
            generation=NamedResource.from_payload(payload.get("generation", {}) or {}),
            types=[PokemonType.from_payload(i) for i in payload.get("types", [])],
        )


@attrs.define(slots=True, kw_only=True)
class PokemonHeldItemVersion(BaseModel):
    """A pokemon held item version resource.

    Attributes
    ----------
    rarity: int
        How often this item is held.
    version: NamedResource
        The version this item is held in by the pokemon.
    """

    version: NamedResource = attrs.field(factory=NamedResource)
    rarity: int = attrs.field(factory=int)

    @classmethod
    def from_payload(cls, payload: t.Dict[str, t.Any]) -> "PokemonHeldItemVersion":
        return cls(
            version=NamedResource.from_payload(payload.get("version", {}) or {}),
            rarity=payload.get("rarity", 0),
        )


@attrs.define(slots=True, kw_only=True)
class PokemonHeldItem(BaseModel):
    """A pokemon held item resource.

    Attributes
    ----------
    item: NamedResource
        The item the referenced pokemon holds.
    version_details: t.List[PokemonHeldItemVersion]
        The details for the version that this item is held in by the pokemon.
    """

    item: NamedResource = attrs.field(factory=NamedResource)
    version_details: t.List[PokemonHeldItemVersion] = attrs.field(factory=list)

    @classmethod
    def from_payload(cls, payload: t.Dict[str, t.Any]) -> "PokemonHeldItem":
        return cls(
            item=NamedResource.from_payload(payload.get("item", {}) or {}),
            version_details=[PokemonHeldItemVersion.from_payload(i) for i in payload.get("version_details", [])],
        )


@attrs.define(slots=True, kw_only=True)
class PokemonMoveVersion(BaseModel):
    """A pokemon move version resource.

    Attributes
    ----------
    move_learn_method: NamedResource
        The method by which the move is learned.
    version_group: NamedResource
        The version group in which the move is learned.
    level_learned_at: int
        The minimum level to learn the move.
    """

    move_learn_method: NamedResource = attrs.field(factory=NamedResource)
    version_group: NamedResource = attrs.field(factory=NamedResource)
    level_learned_at: int = attrs.field(factory=int)

    @classmethod
    def from_payload(cls, payload: t.Dict[str, t.Any]) -> "PokemonMoveVersion":
        return cls(
            move_learn_method=NamedResource.from_payload(payload.get("move_learn_method", {}) or {}),
            version_group=NamedResource.from_payload(payload.get("version_group", {}) or {}),
            level_learned_at=payload.get("level_learned_at", 0),
        )


@attrs.define(slots=True, kw_only=True)
class PokemonMove(BaseModel):
    """A pokemon move resource.

    Attributes
    ----------
    move: NamedResource
        The move the referenced pokemon can learn.
    version_group_details: t.List[PokemonMoveVersion]
        The details for the version group that this move can be learned in.
    """

    move: NamedResource = attrs.field(factory=NamedResource)
    version_group_details: t.List[PokemonMoveVersion] = attrs.field(factory=list)

    @classmethod
    def from_payload(cls, payload: t.Dict[str, t.Any]) -> "PokemonMove":
        return cls(
            move=NamedResource.from_payload(payload.get("move", {}) or {}),
            version_group_details=[
                PokemonMoveVersion.from_payload(i) for i in payload.get("version_group_details", [])
            ],
        )


@attrs.define(slots=True, kw_only=True)
class PokemonStat(BaseModel):
    """A pokemon stat resource.

    Attributes
    ----------
    stat: NamedResource
        The stat the referenced pokemon has.
    effort: int
        The effort points (EV) the referenced pokemon has in the stat.
    base_stat: int
        The base value of the stat.
    """

    stat: NamedResource = attrs.field(factory=NamedResource)
    effort: int = attrs.field(factory=int)
    base_stat: int = attrs.field(factory=int)

    @classmethod
    def from_payload(cls, payload: t.Dict[str, t.Any]) -> "PokemonStat":
        return cls(
            stat=NamedResource.from_payload(payload.get("stat", {}) or {}),
            effort=payload.get("effort", 0),
            base_stat=payload.get("base_stat", 0),
        )


@attrs.define(slots=True, kw_only=True)
class PokemonSprite(BaseSprite):
    """A pokemon sprite resource.

    Attributes
    ----------
    other: Other
        A set of sprites used tin official artwork, home.
    versions: Versions
        A set of sprites used to depict this Pokémon in the game.
    """

    other: Other = attrs.field(factory=Other)
    versions: Versions = attrs.field(factory=Versions)

    @classmethod
    def from_payload(cls, payload: t.Dict[str, t.Any]) -> "PokemonSprite":
        return cls(
            front_default=payload.get("front_default", ""),
            front_shiny=payload.get("front_shiny", ""),
            front_female=payload.get("front_female", ""),
            front_shiny_female=payload.get("front_shiny_female", ""),
            back_default=payload.get("back_default", ""),
            back_shiny=payload.get("back_shiny", ""),
            back_female=payload.get("back_female", ""),
            back_shiny_female=payload.get("back_shiny_female", ""),
            other=Other.from_payload(payload.get("other", {}) or {}),
            versions=Versions.from_payload(payload.get("versions", {}) or {}),
        )


@attrs.define(slots=True, kw_only=True)
class PokemonFormSprites(BaseModel):
    """A pokemon form sprites resource.

    Attributes
    ----------
    front_default: str
        The default depiction of this pokemon form from the front in battle.
    front_shiny: str
        The shiny depiction of this pokemon form from the front in battle.
    back_default: str
        The default depiction of this pokemon form from the back in battle.
    back_shiny: str
        The shiny depiction of this pokemon form from the back in battle.
    """

    front_default: str = attrs.field(factory=str)
    front_shiny: str = attrs.field(factory=str)
    back_default: str = attrs.field(factory=str)
    back_shiny: str = attrs.field(factory=str)

    @classmethod
    def from_payload(cls, payload: t.Dict[str, t.Any]) -> "PokemonFormSprites":
        return cls(
            front_default=payload.get("front_default", ""),
            front_shiny=payload.get("front_shiny", ""),
            back_default=payload.get("back_default", ""),
            back_shiny=payload.get("back_shiny", ""),
        )


@attrs.define(slots=True, kw_only=True)
class AwesomeName(BaseModel):
    """An awesome name resource.

    Attributes
    ----------
    awesome_name: str
        The localized "scientific" name for an API resource in a specific language.
    language: NamedResource
        The language this "scientific" name is in.
    """

    awesome_name: str = attrs.field(factory=str)
    language: NamedResource = attrs.field(factory=NamedResource)

    @classmethod
    def from_payload(cls, payload: t.Dict[str, t.Any]) -> "AwesomeName":
        return cls(
            awesome_name=payload.get("awesome_name", ""),
            language=NamedResource.from_payload(payload.get("language", {}) or {}),
        )


@attrs.define(slots=True, kw_only=True)
class Genus(BaseModel):
    """A genus resource.

    Attributes
    ----------
    genus: str
        The localized genus for the referenced type in the specified language.
    language: NamedResource
        The language this genus is in.
    """

    genus: str = attrs.field(factory=str)
    language: NamedResource = attrs.field(factory=NamedResource)

    @classmethod
    def from_payload(cls, payload: t.Dict[str, t.Any]) -> "Genus":
        return cls(
            genus=payload.get("genus", ""),
            language=NamedResource.from_payload(payload.get("language", {}) or {}),
        )


@attrs.define(slots=True, kw_only=True)
class PokemonSpeciesDexEntry(BaseModel):
    """A pokemon species dex entry resource.

    Attributes
    ----------
    entry_number: int
        The index number within the Pokédex.
    pokedex: NamedResource
        The Pokédex the referenced Pokémon species can be found in.
    """

    entry_number: int = attrs.field(factory=int)
    pokedex: NamedResource = attrs.field(factory=NamedResource)

    @classmethod
    def from_payload(cls, payload: t.Dict[str, t.Any]) -> "PokemonSpeciesDexEntry":
        return cls(
            entry_number=payload.get("entry_number", 0),
            pokedex=NamedResource.from_payload(payload.get("pokedex", {}) or {}),
        )


@attrs.define(slots=True, kw_only=True)
class PalParkEncounterArea(BaseModel):
    """A pal park encounter area resource.

    Attributes
    ----------
    base_score: int
        The base score given to the player when the referenced Pokémon is caught during a pal park run.
    rate: int
        The base rate for encountering the referenced Pokémon in this pal park area.
    area: NamedResource
        The pal park area where this encounter happens.
    """

    base_score: int = attrs.field(factory=int)
    rate: int = attrs.field(factory=int)
    area: NamedResource = attrs.field(factory=NamedResource)

    @classmethod
    def from_payload(cls, payload: t.Dict[str, t.Any]) -> "PalParkEncounterArea":
        return cls(
            base_score=payload.get("base_score", 0),
            rate=payload.get("rate", 0),
            area=NamedResource.from_payload(payload.get("area", {}) or {}),
        )


@attrs.define(slots=True, kw_only=True)
class PokemonSpeciesVariety(BaseModel):
    """A pokemon species variety resource.

    Attributes
    ----------
    is_default: bool
        Whether this variety is the default variety.
    pokemon: NamedResource
        The Pokémon variety.
    """

    is_default: bool = attrs.field(factory=bool)
    pokemon: NamedResource = attrs.field(factory=NamedResource)

    @classmethod
    def from_payload(cls, payload: t.Dict[str, t.Any]) -> "PokemonSpeciesVariety":
        return cls(
            is_default=payload.get("is_default", False),
            pokemon=NamedResource.from_payload(payload.get("pokemon", {}) or {}),
        )


@attrs.define(slots=True, kw_only=True)
class MoveStatEffect(BaseModel):
    """A move stat effect resource.

    Attributes
    ----------
    change: int
        The maximum amount of change to the referenced stat.
    stat: NamedResource
        The stat being affected.
    """

    change: int = attrs.field(factory=int)
    stat: NamedResource = attrs.field(factory=NamedResource)

    @classmethod
    def from_payload(cls, payload: t.Dict[str, t.Any]) -> "MoveStatEffect":
        return cls(
            change=payload.get("change", 0),
            stat=NamedResource.from_payload(payload.get("stat", {}) or {}),
        )


@attrs.define(slots=True, kw_only=True)
class MoveStatAffectSets(BaseModel):
    """A move stat affect sets resource.

    Attributes
    ----------
    increase: typing.List[MoveStatAffect]
        A list of move stat affects.
    decrease: typing.List[MoveStatAffect]
        A list of move stat affects.
    """

    increase: t.List[MoveStatEffect] = attrs.field(factory=list)
    decrease: t.List[MoveStatEffect] = attrs.field(factory=list)

    @classmethod
    def from_payload(cls, payload: t.Dict[str, t.Any]) -> "MoveStatAffectSets":
        return cls(
            increase=[MoveStatEffect.from_payload(i) for i in payload.get("increase", [])],
            decrease=[MoveStatEffect.from_payload(i) for i in payload.get("decrease", [])],
        )


@attrs.define(slots=True, kw_only=True)
class NatureStatAffectSets(BaseModel):
    """A nature stat affect sets resource.

    Attributes
    ----------
    increase: typing.List[NatureStatAffect]
        A list of nature stat affects.
    decrease: typing.List[NatureStatAffect]
        A list of nature stat affects.
    """

    increase: t.List[NamedResource] = attrs.field(factory=list)
    decrease: t.List[NamedResource] = attrs.field(factory=list)

    @classmethod
    def from_payload(cls, payload: t.Dict[str, t.Any]) -> "NatureStatAffectSets":
        return cls(
            increase=[NamedResource.from_payload(i) for i in payload.get("increase", [])],
            decrease=[NamedResource.from_payload(i) for i in payload.get("decrease", [])],
        )


@attrs.define(slots=True, kw_only=True)
class TypePokemon(BaseModel):
    """A type pokemon resource.

    Attributes
    ----------
    slot: int
        The order the Pokémon's types are listed in.
    pokemon: NamedResource
        The Pokémon that has the referenced type.
    """

    slot: int = attrs.field(factory=int)
    pokemon: NamedResource = attrs.field(factory=NamedResource)

    @classmethod
    def from_payload(cls, payload: t.Dict[str, t.Any]) -> "TypePokemon":
        return cls(
            slot=payload.get("slot", 0),
            pokemon=NamedResource.from_payload(payload.get("pokemon", {}) or {}),
        )


@attrs.define(slots=True, kw_only=True)
class TypeRelations(BaseModel):
    """A type relations resource.

    Attributes
    ----------
    no_damage_to: typing.List[NamedResource]
        A list of types this type has no damage to.
    half_damage_to: typing.List[NamedResource]
        A list of types this type is half damage to.
    double_damage_to: typing.List[NamedResource]
        A list of types this type is double damage to.
    no_damage_from: typing.List[NamedResource]
        A list of types that have no damage to this type.
    half_damage_from: typing.List[NamedResource]
        A list of types that have half damage to this type.
    double_damage_from: typing.List[NamedResource]
        A list of types that have double damage to this type.
    """

    no_damage_to: t.List[NamedResource] = attrs.field(factory=list)
    half_damage_to: t.List[NamedResource] = attrs.field(factory=list)
    double_damage_to: t.List[NamedResource] = attrs.field(factory=list)
    no_damage_from: t.List[NamedResource] = attrs.field(factory=list)
    half_damage_from: t.List[NamedResource] = attrs.field(factory=list)
    double_damage_from: t.List[NamedResource] = attrs.field(factory=list)

    @classmethod
    def from_payload(cls, payload: t.Dict[str, t.Any]) -> "TypeRelations":
        return cls(
            no_damage_to=[NamedResource.from_payload(i) for i in payload.get("no_damage_to", [])],
            half_damage_to=[NamedResource.from_payload(i) for i in payload.get("half_damage_to", [])],
            double_damage_to=[NamedResource.from_payload(i) for i in payload.get("double_damage_to", [])],
            no_damage_from=[NamedResource.from_payload(i) for i in payload.get("no_damage_from", [])],
            half_damage_from=[NamedResource.from_payload(i) for i in payload.get("half_damage_from", [])],
            double_damage_from=[NamedResource.from_payload(i) for i in payload.get("double_damage_from", [])],
        )


@attrs.define(slots=True, kw_only=True)
class TypeRelationsPast(BaseModel):
    """A type relations past resource.

    Attributes
    ----------
    generation: NamedResource
        The generation of this type relation.
    damage_relations: TypeRelations
        The type relations for this generation.
    """

    generation: NamedResource = attrs.field(factory=NamedResource)
    damage_relations: TypeRelations = attrs.field(factory=TypeRelations)
