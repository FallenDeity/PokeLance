import typing as t

import attrs

__all__: t.Tuple[str, ...] = ("Endpoint", "Route")


@attrs.define(repr=True, slots=True, kw_only=True)
class Route:
    endpoint: str = attrs.field(factory=str)
    _url: str = "https://pokeapi.co/api/v2{endpoint}"
    _api_version: int = 2
    method: str = "GET"
    payload: t.Optional[t.Dict[str, t.Any]] = None

    @property
    def url(self) -> str:
        return self._url.format(endpoint=self.endpoint)


class Endpoint:
    @classmethod
    def get_pokemon_enpoints(cls) -> Route:
        return Route(endpoint="/pokemon", payload={"limit": 10000})

    @classmethod
    def get_pokemon(cls, name: t.Union[str, int]) -> Route:
        return Route(endpoint=f"/pokemon/{name}")
