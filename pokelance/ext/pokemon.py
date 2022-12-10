import typing as t

from pokelance.http import Endpoint

from ._base import BaseExtension

if t.TYPE_CHECKING:
    from pokelance import PokeLance
    from pokelance.http import HttpClient


class Pokemon(BaseExtension):
    def __init__(self, client: "HttpClient") -> None:
        super().__init__(client)

    async def setup(self) -> None:
        data = await self._client.request(Endpoint.get_pokemon_enpoints())
        self._cache.load_documents("pokemon", data["results"])

    def get_pokemon(self, name: t.Union[str, int]) -> t.Any:
        route = Endpoint.get_pokemon(name)
        self.validate_resource(self._cache.pokemon, name, route)
        return self._cache.pokemon.get(route, None)

    async def fetch_pokemon(self, name: t.Union[str, int]) -> t.Any:
        route = Endpoint.get_pokemon(name)
        data = await self._client.request(route)
        self._cache.pokemon[route] = data
        return data


async def setup(lance: "PokeLance") -> None:
    await lance.add_extension("pokemon", Pokemon(lance.http))
