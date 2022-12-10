import typing as t

from pokelance.http import Endpoint
from pokelance.models import Berry as BerryModel
from pokelance.models import BerryFirmness, BerryFlavor

from ._base import BaseExtension

if t.TYPE_CHECKING:
    from pokelance import PokeLance
    from pokelance.http import HttpClient


__all__: t.Tuple[str, ...] = (
    "setup",
    "Berry",
)


class Berry(BaseExtension):
    def __init__(self, client: "HttpClient") -> None:
        super().__init__(client)
        self.cache = self._cache.berry

    async def setup(self) -> None:
        data = await self._client.request(Endpoint.get_berry_endpoints())
        self._cache.load_documents(str(self.__class__.__name__), "berry", data["results"])
        data = await self._client.request(Endpoint.get_berry_flavor_endpoints())
        self._cache.load_documents(str(self.__class__.__name__), "berry_flavor", data["results"])
        data = await self._client.request(Endpoint.get_berry_firmness_endpoints())
        self._cache.load_documents(str(self.__class__.__name__), "berry_firmness", data["results"])

    def get_berry(self, name: t.Union[str, int]) -> t.Optional[BerryModel]:
        route = Endpoint.get_berry(name)
        self._validate_resource(self.cache.berry, name, route)
        return self.cache.berry.get(route, None)

    async def fetch_berry(self, name: t.Union[str, int]) -> t.Optional[BerryModel]:
        route = Endpoint.get_berry(name)
        self._validate_resource(self.cache.berry, name, route)
        data = await self._client.request(route)
        self.cache.berry[route] = BerryModel.from_payload(data)
        return self.cache.berry[route]

    def get_berry_flavor(self, name: t.Union[str, int]) -> t.Optional[BerryFlavor]:
        route = Endpoint.get_berry_flavor(name)
        self._validate_resource(self.cache.berry_flavor, name, route)
        return self.cache.berry_flavor.get(route, None)

    async def fetch_berry_flavor(self, name: t.Union[str, int]) -> t.Optional[BerryFlavor]:
        route = Endpoint.get_berry_flavor(name)
        self._validate_resource(self.cache.berry_flavor, name, route)
        data = await self._client.request(route)
        self.cache.berry_flavor[route] = BerryFlavor.from_payload(data)
        return self.cache.berry_flavor[route]

    def get_berry_firmness(self, name: t.Union[str, int]) -> t.Optional[BerryFirmness]:
        route = Endpoint.get_berry_firmness(name)
        self._validate_resource(self.cache.berry_firmness, name, route)
        return self.cache.berry_firmness.get(route, None)

    async def fetch_berry_firmness(self, name: t.Union[str, int]) -> t.Optional[BerryFirmness]:
        route = Endpoint.get_berry_firmness(name)
        self._validate_resource(self.cache.berry_firmness, name, route)
        data = await self._client.request(route)
        self.cache.berry_firmness[route] = BerryFirmness.from_payload(data)
        return self.cache.berry_firmness[route]


async def setup(lance: "PokeLance") -> None:
    await lance.add_extension("berry", Berry(lance.http))
