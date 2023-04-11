import typing as t

import attrs

from pokelance.models import BaseModel

from .resources import NamedResource, Resource

__all__: t.Tuple[str, ...] = (
    "Description",
    "Effect",
    "Encounter",
    "FlavorText",
    "GenerationGameIndex",
    "MachineVersionDetail",
    "Name",
    "VerboseEffect",
    "VersionEncounterDetail",
    "VersionGameIndex",
    "VersionGroupFlavorText",
    "Language",
)


@attrs.define(slots=True, kw_only=True)
class Description(BaseModel):
    """Model for a description object

    Attributes
    ----------
    description: str
        The localized description for an API resource in a specific language.
    language: NamedResource
        The language this name is in.
    """

    description: str = attrs.field(factory=str)
    language: NamedResource = attrs.field(factory=NamedResource)

    @classmethod
    def from_payload(cls, payload: t.Dict[str, t.Any]) -> "Description":
        return cls(
            description=payload.get("description", ""),
            language=NamedResource.from_payload(payload.get("language", {}) or {}),
        )


@attrs.define(slots=True, kw_only=True)
class Effect(BaseModel):
    """Model for an effect object

    Attributes
    ----------
    effect: str
        The localized effect text for an API resource in a specific language.
    language: NamedResource
        The language this effect is in.
    """

    effect: str = attrs.field(factory=str)
    language: NamedResource = attrs.field(factory=NamedResource)

    @classmethod
    def from_payload(cls, payload: t.Dict[str, t.Any]) -> "Effect":
        return cls(
            effect=payload.get("effect", ""),
            language=NamedResource.from_payload(payload.get("language", {}) or {}),
        )


@attrs.define(slots=True, kw_only=True)
class Encounter(BaseModel):
    """Model for an encounter object

    Attributes
    ----------
    min_level: int
        The lowest level the Pokémon could be encountered at.
    max_level: int
        The highest level the Pokémon could be encountered at.
    condition_values: t.List[NamedResource]
        A list of condition values that must be in effect for this encounter to occur.
    chance: int
        The chance of the encounter to occur on a version of the game.
    method: NamedResource
        The method by which this encounter happens.
    """

    min_level: int = attrs.field(factory=int)
    max_level: int = attrs.field(factory=int)
    condition_values: t.List[Resource] = attrs.field(factory=list)
    chance: int = attrs.field(factory=int)
    method: NamedResource = attrs.field(factory=NamedResource)

    @classmethod
    def from_payload(cls, payload: t.Dict[str, t.Any]) -> "Encounter":
        return cls(
            min_level=payload.get("min_level", 0),
            max_level=payload.get("max_level", 0),
            condition_values=[Resource.from_payload(i) for i in payload.get("condition_values", [])],
            chance=payload.get("chance", 0),
            method=NamedResource.from_payload(payload.get("method", {}) or {}),
        )


@attrs.define(slots=True, kw_only=True)
class FlavorText(BaseModel):
    """Model for a flavor text object

    Attributes
    ----------
    flavor_text: str
        The localized flavor text for an API resource in a specific language.
    language: NamedResource
        The language this name is in.
    version: NamedResource
        The version that this flavor text is extracted from.
    """

    flavor_text: str = attrs.field(factory=str)
    language: NamedResource = attrs.field(factory=NamedResource)
    version: NamedResource = attrs.field(factory=NamedResource)

    @classmethod
    def from_payload(cls, payload: t.Dict[str, t.Any]) -> "FlavorText":
        return cls(
            flavor_text=payload.get("flavor_text", ""),
            language=NamedResource.from_payload(payload.get("language", {}) or {}),
            version=NamedResource.from_payload(payload.get("version", {}) or {}),
        )


@attrs.define(slots=True, kw_only=True)
class GenerationGameIndex(BaseModel):
    """Model for a generation game index object

    Attributes
    ----------
    game_index: int
        The internal id of an API resource within game data.
    generation: NamedResource
        The generation relevent to this game index.
    """

    game_index: int = attrs.field(factory=int)
    generation: NamedResource = attrs.field(factory=NamedResource)

    @classmethod
    def from_payload(cls, payload: t.Dict[str, t.Any]) -> "GenerationGameIndex":
        return cls(
            game_index=payload.get("game_index", 0),
            generation=NamedResource.from_payload(payload.get("generation", {}) or {}),
        )


@attrs.define(slots=True, kw_only=True)
class MachineVersionDetail(BaseModel):
    """Model for a machine version detail object

    Attributes
    ----------
    machine: Resource
        The machine that teaches a move from an item.
    version_group: NamedResource
        The version group of this specific machine.
    """

    machine: Resource = attrs.field(factory=Resource)
    version_group: NamedResource = attrs.field(factory=NamedResource)

    @classmethod
    def from_payload(cls, payload: t.Dict[str, t.Any]) -> "MachineVersionDetail":
        return cls(
            machine=Resource.from_payload(payload.get("machine", {}) or {}),
            version_group=NamedResource.from_payload(payload.get("version_group", {}) or {}),
        )


@attrs.define(slots=True, kw_only=True)
class Name(BaseModel):
    """Model for a name object

    Attributes
    ----------
    name: str
        The localized name for an API resource in a specific language.
    language: NamedResource
        The language this name is in.
    """

    name: str = attrs.field(factory=str)
    language: NamedResource = attrs.field(factory=NamedResource)

    @classmethod
    def from_payload(cls, payload: t.Dict[str, t.Any]) -> "Name":
        return cls(name=payload.get("name", ""), language=NamedResource.from_payload(payload.get("language", {}) or {}))


@attrs.define(slots=True, kw_only=True)
class VerboseEffect(BaseModel):
    """Model for a verbose effect object

    Attributes
    ----------
    effect: str
        The localized effect text for an API resource in a specific language.
    short_effect: str
        The localized short effect text for an API resource in a specific language.
    language: NamedResource
        The language this effect is in.
    """

    effect: str = attrs.field(factory=str)
    short_effect: str = attrs.field(factory=str)
    language: NamedResource = attrs.field(factory=NamedResource)

    @classmethod
    def from_payload(cls, payload: t.Dict[str, t.Any]) -> "VerboseEffect":
        return cls(
            effect=payload.get("effect", ""),
            short_effect=payload.get("short_effect", ""),
            language=NamedResource.from_payload(payload.get("language", {}) or {}),
        )


@attrs.define(slots=True, kw_only=True)
class VersionEncounterDetail(BaseModel):
    """Model for a version encounter detail object

    Attributes
    ----------
    max_chance: int
        The chance of an encounter to occur.
    encounter_details: t.List[Encounter]
        A list of encounters and their specifics.
    version: NamedResource
        The game version this encounter happens in.
    """

    version: NamedResource = attrs.field(factory=NamedResource)
    max_chance: int = attrs.field(factory=int)
    encounter_details: t.List[Encounter] = attrs.field(factory=list)

    @classmethod
    def from_payload(cls, payload: t.Dict[str, t.Any]) -> "VersionEncounterDetail":
        return cls(
            version=NamedResource.from_payload(payload.get("version", {}) or {}),
            max_chance=payload.get("max_chance", 0),
            encounter_details=[Encounter.from_payload(i) for i in payload.get("encounter_details", [])],
        )


@attrs.define(slots=True, kw_only=True)
class VersionGameIndex(BaseModel):
    """Model for a version game index object

    Attributes
    ----------
    game_index: int
        The internal id of an API resource within game data.
    version: NamedResource
        The version relevent to this game index.
    """

    game_index: int = attrs.field(factory=int)
    version: NamedResource = attrs.field(factory=NamedResource)

    @classmethod
    def from_payload(cls, payload: t.Dict[str, t.Any]) -> "VersionGameIndex":
        return cls(
            game_index=payload.get("game_index", 0),
            version=NamedResource.from_payload(payload.get("version", {}) or {}),
        )


@attrs.define(slots=True, kw_only=True)
class VersionGroupFlavorText(BaseModel):
    """Model for a version group flavor text object

    Attributes
    ----------
    text: str
        The localized name for an API resource in a specific language.
    language: NamedResource
        The language this name is in.
    version_group: NamedResource
        The version group which uses this flavor text.
    """

    text: str = attrs.field(factory=str)
    language: NamedResource = attrs.field(factory=NamedResource)
    version_group: NamedResource = attrs.field(factory=NamedResource)

    @classmethod
    def from_payload(cls, payload: t.Dict[str, t.Any]) -> "VersionGroupFlavorText":
        return cls(
            text=payload.get("text", ""),
            language=NamedResource.from_payload(payload.get("language", {}) or {}),
            version_group=NamedResource.from_payload(payload.get("version_group", {}) or {}),
        )


@attrs.define(slots=True, kw_only=True)
class Language(BaseModel):
    """Model for a language object

    Attributes
    ----------
    id: int
        The identifier for this resource.
    name: str
        The name for this resource.
    official: bool
        Whether or not the games are published in this language.
    iso639: str
        The two-letter code of the country where this language is spoken. Note that it is not unique.
    iso3166: str
        The two-letter code of the language. Note that it is not unique.
    names: t.List[Name]
        The name of this resource listed in different languages.
    """

    id: int = attrs.field(factory=int)
    name: str = attrs.field(factory=str)
    official: bool = attrs.field(factory=bool)
    iso639: str = attrs.field(factory=str)
    iso3166: str = attrs.field(factory=str)
    names: t.List[Name] = attrs.field(factory=list)

    @classmethod
    def from_payload(cls, payload: t.Dict[str, t.Any]) -> "Language":
        return cls(
            id=payload.get("id", 0),
            name=payload.get("name", ""),
            official=payload.get("official", False),
            iso639=payload.get("iso639", ""),
            iso3166=payload.get("iso3166", ""),
            names=[Name.from_payload(i) for i in payload.get("names", [])],
        )
