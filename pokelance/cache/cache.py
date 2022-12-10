import json
import typing as t
from collections.abc import MutableMapping

import aiofiles

if t.TYPE_CHECKING:
    from pokelance.http import Route


__all__: t.Tuple[str, ...] = ("PokemonCache", "BaseCache")


class BaseCache(MutableMapping):
    def __init__(self, max_size: int = 100) -> None:
        self._max_size = max_size
        self._cache: t.Dict[str, t.Any] = {}
        self._endpoints: t.Dict[str, int] = {}

    def __getitem__(self, key: "Route") -> t.Any:
        self._cache[key.endpoint] = self._cache.pop(key.endpoint)
        return self._cache[key.endpoint]

    def __setitem__(self, key: "Route", value: t.Any) -> None:
        if key.endpoint in self._cache:
            self._cache[key.endpoint] = self._cache.pop(key.endpoint)
        else:
            if len(self._cache) >= self._max_size:
                self._cache.pop(list(self._cache.keys())[0])
            self._cache[key.endpoint] = value

    def __delitem__(self, key: "Route") -> None:
        del self._cache[key.endpoint]

    def __len__(self) -> int:
        return len(self._cache)

    def __iter__(self) -> t.Iterator[str]:
        return iter(self._cache)

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}({self._cache})"

    def load_documents(self, data: t.List[t.Dict[str, str]]) -> None:
        for document in data:
            self._endpoints[document["name"]] = int(document["url"].split("/")[-2])

    async def save(self, path: str = "") -> None:
        async with aiofiles.open(f"{path}{self.__class__.__name__}.json", "w") as f:
            await f.write(json.dumps(self._cache, indent=4, ensure_ascii=False))

    @property
    def endpoints(self) -> t.Dict[str, int]:
        return self._endpoints

    @property
    def cache(self) -> t.Dict[str, t.Any]:
        return self._cache


class PokemonCache(BaseCache):
    pass
