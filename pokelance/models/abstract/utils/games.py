import typing as t

import attrs
from typing_extensions import override

from pokelance.models import BaseModel
from pokelance.models.common import NamedResource

__all__: tuple[str, ...] = ("PokemonEntry",)


@attrs.define(slots=True, kw_only=True)
class PokemonEntry(BaseModel):
    """A pokemon entry resource.

    Attributes
    ----------
    entry_number: int
        The index of this Pokémon species entry within the Pokédex.
    pokemon_species: NamedResource
        The Pokémon species being encountered.
    """

    entry_number: int = attrs.field(factory=int)
    pokemon_species: NamedResource = attrs.field(factory=NamedResource)

    @classmethod
    @override
    def from_payload(cls, payload: dict[str, t.Any]) -> "PokemonEntry":
        return cls(
            raw=payload,
            entry_number=payload.get("entry_number", 0),
            pokemon_species=NamedResource.from_payload(payload.get("pokemon_species", {})),
        )
