import typing as t

import attrs

from .cache import BaseCache, PokemonCache

__all__: t.Tuple[str, ...] = (
    "Cache",
    "BaseCache",
)


@attrs.define(slots=True)
class Cache:
    max_size: int = 100
    pokemon: PokemonCache = PokemonCache(max_size=max_size)

    def load_documents(self, _type: str, data: t.List[t.Dict[str, str]]) -> None:
        getattr(self, _type).load_documents(data)
