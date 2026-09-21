import typing as t

import attrs
from typing_extensions import override

from pokelance.models import BaseModel
from pokelance.models.common import Description, Name, NamedResource

from .utils import ChainLink

__all__: tuple[str, ...] = (
    "ChainLink",
    "EvolutionChain",
    "EvolutionTrigger",
    "EvolutionVariable",
)


@attrs.define(slots=True, kw_only=True)
class EvolutionChain(BaseModel):
    """Evolution chain model.

    Attributes
    ----------
    id: int
        The identifier for this resource.
    baby_trigger_item: t.Optional[NamedResource]
        The item that a Pokémon would be holding when mating that would trigger the egg hatching a baby
         Pokémon rather than a basic Pokémon.
    chain: ChainLink
        The base chain link object. Each link contains evolution details for a Pokémon in the chain.
         Each link references the next Pokémon in the natural evolution order.
    """

    id: int = attrs.field(factory=int)
    baby_trigger_item: NamedResource | None = attrs.field(default=None)
    chain: ChainLink = attrs.field(factory=ChainLink)

    @classmethod
    @override
    def from_payload(cls, payload: dict[str, t.Any]) -> "EvolutionChain":
        return cls(
            raw=payload,
            id=payload.get("id", 0),
            baby_trigger_item=NamedResource.optional_from_payload(payload.get("baby_trigger_item")),
            chain=ChainLink.from_payload(payload.get("chain", {})),
        )


@attrs.define(slots=True, kw_only=True)
class EvolutionTrigger(BaseModel):
    """Evolution trigger model.

    Attributes
    ----------
    id: int
        The identifier for this resource.
    name: str
        The name for this resource.
    names: t.List[Name]
        A list of name and language pairs for this resource.
    pokemon_species: t.List[NamedResource]
        A list of pokemon species that result from this evolution trigger.
    """

    id: int = attrs.field(factory=int)
    name: str = attrs.field(factory=str)
    names: list[Name] = attrs.field(factory=list)
    pokemon_species: list[NamedResource] = attrs.field(factory=list)

    @classmethod
    @override
    def from_payload(cls, payload: dict[str, t.Any]) -> "EvolutionTrigger":
        return cls(
            raw=payload,
            id=payload.get("id", 0),
            name=payload.get("name", ""),
            names=[Name.from_payload(name) for name in payload.get("names", [])],
            pokemon_species=[NamedResource.from_payload(species) for species in payload.get("pokemon_species", [])],
        )


@attrs.define(slots=True, kw_only=True)
class EvolutionVariable(BaseModel):
    """Evolution variable model.

    Attributes
    ----------
    id: int
        The identifier for this resource.
    name: str
        The name for this resource.
    symbol: str
        The short mathematical symbol for this variable (e.g. 'EC', 'PID').
    data_type: str
        The data type of the variable (e.g. 'uint32').
    version_group: NamedResource
        The version group in which this variable was introduced.
    names: list[Name]
        A list of name and language pairs for this resource.
    descriptions: list[Description]
        A list of descriptions for this resource in various languages.
    """

    id: int = attrs.field(factory=int)
    name: str = attrs.field(factory=str)
    symbol: str = attrs.field(factory=str)
    data_type: str = attrs.field(factory=str)
    version_group: NamedResource = attrs.field(factory=NamedResource)
    names: list[Name] = attrs.field(factory=list)
    descriptions: list[Description] = attrs.field(factory=list)

    @classmethod
    @override
    def from_payload(cls, payload: dict[str, t.Any]) -> "EvolutionVariable":
        return cls(
            raw=payload,
            id=payload.get("id", 0),
            name=payload.get("name", ""),
            symbol=payload.get("symbol", ""),
            data_type=payload.get("data_type", ""),
            version_group=NamedResource.from_payload(payload.get("version_group", {})),
            names=[Name.from_payload(name) for name in payload.get("names", [])],
            descriptions=[Description.from_payload(desc) for desc in payload.get("descriptions", [])],
        )
