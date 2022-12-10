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
)


@attrs.define(slots=True, kw_only=True)
class Description(BaseModel):
    description: str = attrs.field(factory=str)
    language: Resource = attrs.field(factory=NamedResource)


@attrs.define(slots=True, kw_only=True)
class Effect(BaseModel):
    effect: str = attrs.field(factory=str)
    language: Resource = attrs.field(factory=NamedResource)


@attrs.define(slots=True, kw_only=True)
class Encounter(BaseModel):
    min_level: int = attrs.field(factory=int)
    max_level: int = attrs.field(factory=int)
    condition_values: t.List[Resource] = attrs.field(factory=list)
    chance: int = attrs.field(factory=int)
    method: Resource = attrs.field(factory=NamedResource)


@attrs.define(slots=True, kw_only=True)
class FlavorText(BaseModel):
    flavor_text: str = attrs.field(factory=str)
    language: Resource = attrs.field(factory=NamedResource)
    version: Resource = attrs.field(factory=NamedResource)


@attrs.define(slots=True, kw_only=True)
class GenerationGameIndex(BaseModel):
    game_index: int = attrs.field(factory=int)
    generation: Resource = attrs.field(factory=NamedResource)


@attrs.define(slots=True, kw_only=True)
class MachineVersionDetail(BaseModel):
    machine: Resource = attrs.field(factory=Resource)
    version_group: Resource = attrs.field(factory=NamedResource)


@attrs.define(slots=True, kw_only=True)
class Name(BaseModel):
    name: str = attrs.field(factory=str)
    language: Resource = attrs.field(factory=NamedResource)

    @classmethod
    def from_payload(cls, payload: t.Dict[str, str]) -> "Name":
        return cls(name=payload.get("name", ""), language=payload.get("language", ""))


@attrs.define(slots=True, kw_only=True)
class VerboseEffect(BaseModel):
    effect: str = attrs.field(factory=str)
    short_effect: str = attrs.field(factory=str)
    language: Resource = attrs.field(factory=NamedResource)


@attrs.define(slots=True, kw_only=True)
class VersionEncounterDetail(BaseModel):
    version: Resource = attrs.field(factory=NamedResource)
    max_chance: int = attrs.field(factory=int)
    encounter_details: t.List[Encounter] = attrs.field(factory=list)


@attrs.define(slots=True, kw_only=True)
class VersionGameIndex(BaseModel):
    game_index: int = attrs.field(factory=int)
    version: Resource = attrs.field(factory=NamedResource)


@attrs.define(slots=True, kw_only=True)
class VersionGroupFlavorText(BaseModel):
    text: str = attrs.field(factory=str)
    language: Resource = attrs.field(factory=NamedResource)
    version_group: Resource = attrs.field(factory=NamedResource)
