import typing as t

import attrs

from pokelance.models import BaseModel
from pokelance.models.common import Name, NamedResource

from .utils import ChainLink

__all__: t.Tuple[str, ...] = (
    "EvolutionChain",
    "EvolutionTrigger",
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
    baby_trigger_item: NamedResource = attrs.field(factory=NamedResource)
    chain: ChainLink = attrs.field(factory=ChainLink)

    @classmethod
    def from_payload(cls, payload: t.Dict[str, t.Any]) -> "EvolutionChain":
        return cls(
            id=payload.get("id", 0),
            baby_trigger_item=NamedResource.from_payload(payload.get("baby_trigger_item", {}) or {}),
            chain=ChainLink.from_payload(payload.get("chain", {}) or {}),
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
    names: t.List[Name] = attrs.field(factory=list)
    pokemon_species: t.List[NamedResource] = attrs.field(factory=list)

    @classmethod
    def from_payload(cls, payload: t.Dict[str, t.Any]) -> "EvolutionTrigger":
        return cls(
            id=payload.get("id", 0),
            name=payload.get("name", ""),
            names=[Name.from_payload(name) for name in payload.get("names", [])],
            pokemon_species=[NamedResource.from_payload(species) for species in payload.get("pokemon_species", [])],
        )
