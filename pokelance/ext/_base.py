import typing as t
from difflib import get_close_matches

from pokelance.exceptions import ResourceNotFound

if t.TYPE_CHECKING:
    from pokelance.cache import BaseCache, Cache
    from pokelance.http import HttpClient, Route


__all__: t.Tuple[str, ...] = ("BaseExtension",)


class BaseExtension:
    _cache: "Cache"

    def __init__(self, client: "HttpClient") -> None:
        self._client = client
        self._cache = self._client.cache

    def validate_resource(self, cache: "BaseCache", resource: t.Union[str, int], route: "Route") -> None:
        data: t.List[str] = list(map(str, cache.endpoints.values())) + list(cache.endpoints.keys())
        if resource not in data:
            raise ResourceNotFound(self.get_message(str(resource), data), route)

    @staticmethod
    def get_message(case: str, data: t.List[str]) -> str:
        matches = get_close_matches(case, data, n=10, cutoff=0.5)
        if matches:
            return f"Resource not found. Did you mean {', '.join(matches)}?"
        return "Resource not found."

    async def setup(self) -> None:
        ...
