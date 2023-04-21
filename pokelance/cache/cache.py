import importlib
import json
import pathlib
import typing as t
from collections.abc import MutableMapping

import aiofiles
import attrs

if t.TYPE_CHECKING:
    from pokelance import models  # noqa: F401
    from pokelance.http import HttpClient, Route  # noqa: F401
    from pokelance.models import BaseModel  # noqa: F401


__all__: t.Tuple[str, ...] = (
    "PokemonCache",
    "BaseCache",
    "BerryCache",
    "PalParkAreaCache",
    "GenderCache",
    "GamesPokedexCache",
    "GamesVersionCache",
    "GamesGenerationCache",
    "BerryFlavorCache",
    "BerryFirmnessCache",
    "ContestTypeCache",
    "PokeathlonStatCache",
    "PokemonSpeciesCache",
    "PokemonLocationAreaCache",
    "ContestEffectCache",
    "SuperContestEffectCache",
    "PokemonColorCache",
    "PokemonFormCache",
    "PokemonHabitatCache",
    "PokemonShapeCache",
    "GrowthRateCache",
    "NatureCache",
    "TypeCache",
    "GenderCache",
    "GamesVersionGroupCache",
    "EggGroupCache",
    "EvolutionChainCache",
    "EvolutionTriggerCache",
    "EncounterConditionCache",
    "EncounterConditionValueCache",
    "EncounterMethodCache",
    "ItemCache",
    "ItemAttributeCache",
    "ItemCategoryCache",
    "ItemFlingEffectCache",
    "ItemPocketCache",
    "LocationCache",
    "LocationAreaCache",
    "MachineCache",
    "MoveCache",
    "MoveAilmentCache",
    "MoveBattleStyleCache",
    "MoveCategoryCache",
    "MoveDamageClassCache",
    "MoveLearnMethodCache",
    "MoveTargetCache",
    "AbilityCache",
    "CharacteristicCache",
    "PokemonCache",
    "PokemonSpeciesCache",
    "PokemonFormCache",
    "NatureCache",
    "TypeCache",
    "GenderCache",
    "GrowthRateCache",
    "PokemonLocationAreaCache",
    "StatCache",
    "RegionCache",
)

_KT = t.TypeVar("_KT", bound="Route")
_VT = t.TypeVar("_VT", bound="BaseModel")
_T = t.TypeVar("_T")


@attrs.define(kw_only=True, slots=True, frozen=True)
class Endpoint:
    id: t.Union[str, int] = attrs.field(factory=str)
    url: str = attrs.field(factory=str)

    def __str__(self) -> str:
        return str(self.id)


class BaseCache(MutableMapping[_KT, _VT]):
    """Base class for all caches.

    Parameters
    ----------
    max_size: int
        The maximum size of the cache.

    Attributes
    ----------
    _max_size: int
        The maximum size of the cache.
    _cache: typing.Dict[_KT, _VT]
        The cache itself.
    _endpoints: typing.Dict[str, int]
        The endpoints that are cached.
    _endpoints_cached: bool
        Whether or not the endpoints are cached.

    Examples
    --------
    >>> import asyncio
    >>> from pokelance import PokeLance
    >>>
    >>> async def main():
    ...     client = PokeLance()
    ...     print(await client.ping())
    ...     await asyncio.sleep(5)  # Wait for all the endpoints to load automatically. If not just load them manually.
    ...     # from pokelance.http import Endpoint
    ...     # data = await client.http.request(Endpoint.get_berry_endpoints())
    ...     # client.berry._cache.load_documents(str(client.berry.__class__.__name__).lower(), "berry", data)
    ...     # print(client.berry.cache.berry.endpoints)
    ...     # await client.berry.cache.berry.load_all(client.http)
    ...     print(client.berry.cache.berry)
    ...     await client.berry.cache.berry.save('temp')  # Save the cache to a file.
    ...     await client.berry.cache.berry.load('temp')  # Load the cache from a file.
    ...     print(client.berry.cache.berry)
    ...     await client.close()
    >>>
    >>> asyncio.run(main())
    """

    def __init__(self, max_size: int = 100) -> None:
        self._max_size = max_size
        self._cache: t.Dict[_KT, _VT] = {}
        self._endpoints: t.Dict[str, Endpoint] = {}
        self._endpoints_cached: bool = False

    def __getitem__(self, key: _KT) -> _VT:
        self._cache[key] = self._cache.pop(key)
        return self._cache[key]

    def __setitem__(self, key: _KT, value: _VT) -> None:
        if key in self._cache:
            self._cache[key] = self._cache.pop(key)
        else:
            if len(self._cache) >= self._max_size:
                self._cache.pop(list(self._cache.keys())[0])
            self._cache[key] = value

    def __delitem__(self, key: _KT) -> None:
        del self._cache[key]

    def __len__(self) -> int:
        return len(self._cache)

    def __iter__(self) -> t.Iterator[_KT]:
        return iter(self._cache)

    def __repr__(self) -> str:
        return f"{self.__class__.__name__}({self._cache})"

    def keys(self) -> t.KeysView[_KT]:
        return self._cache.keys()

    def values(self) -> t.ValuesView[_VT]:
        return self._cache.values()

    def setdefault(self, __key: _KT, __default: t.Any = ...) -> _VT:
        if __key not in self:
            self[__key] = __default
        return self[__key]

    def clear(self) -> None:
        self._cache.clear()

    def items(self) -> t.ItemsView[_KT, _VT]:
        return self._cache.items()

    def get(self, key: _KT, /, default: t.Union[_VT, _T, None] = None) -> t.Union[_VT, _T, None]:  # type: ignore
        if key in self:
            return self[key]
        dummy: t.Dict[str, str] = {str(v): k for k, v in self._endpoints.items()}
        alias = dummy.get(key.endpoint.split("/")[-1]) or self._endpoints.get(key.endpoint.split("/")[-1])
        if alias:
            for k in self.keys():
                if k.endpoint.split("/")[-1] == str(alias):
                    return self[k]
        return default

    def load_documents(self, data: t.List[t.Dict[str, str]]) -> None:
        """Load documents into the cache.

        Parameters
        ----------
        data: typing.List[typing.Dict[str, str]]
            The data to load.
        """
        for document in data:
            self._endpoints[document["name"]] = Endpoint(url=document["url"], id=int(document["url"].split("/")[-2]))
        self._endpoints_cached = True

    async def save(self, path: str = "") -> None:
        """Save the cache to a file.

        Parameters
        ----------
        path: str
            The path to save the cache to.
        """
        pathlib.Path(path).mkdir(parents=True, exist_ok=True)
        dummy: t.Dict[str, t.Dict[str, t.Any]] = {k.endpoint: attrs.asdict(v) for k, v in self.items()}
        async with aiofiles.open(pathlib.Path(f"{path}/{self.__class__.__name__}.json"), "w") as f:
            await f.write(json.dumps(dummy, indent=4, ensure_ascii=False))

    async def load(self, path: str = "") -> None:
        """Load the cache from a file.

        Parameters
        ----------
        path: str
            The path to load the cache from.
        """
        async with aiofiles.open(pathlib.Path(f"{path}/{self.__class__.__name__}.json"), "r") as f:
            data = json.loads(await f.read())
        route_model = importlib.import_module("pokelance.http").__dict__["Route"]
        value_type = str(self.__orig_bases__[0].__args__[1]).split(".")[-1]  # type: ignore
        model: "models.BaseModel" = importlib.import_module("pokelance.models").__dict__[value_type]
        for endpoint, info in data.items():
            route = route_model(endpoint=endpoint)
            self.setdefault(route, model.from_payload(info))

    async def load_all(self, client: "HttpClient") -> None:
        """Load all documents into the cache.

        Parameters
        ----------
        client: HttpClient
            The client to use to load the documents.
        """
        if not self._endpoints_cached:
            raise RuntimeError("The endpoints have not been cached yet.")
        client._client.logger.info(f"Loading {self.__class__.__name__}...")
        route_model = importlib.import_module("pokelance.http").__dict__["Route"]
        value_type = str(self.__orig_bases__[0].__args__[1]).split(".")[-1]  # type: ignore
        model: "models.BaseModel" = importlib.import_module("pokelance.models").__dict__[value_type]
        for endpoint in self._endpoints.values():
            route = route_model(endpoint=f"/{endpoint.url.strip('/').split('/')[-2]}/{str(endpoint)}")
            self.setdefault(route, model.from_payload(await client.request(route)))
        client._client.logger.info(f"Loaded {self.__class__.__name__}.")

    @property
    def endpoints(self) -> t.Dict[str, Endpoint]:
        """The endpoints that are cached.

        Returns
        -------
        typing.Dict[str, Endpoint]
            The endpoints that are cached.
        """
        return self._endpoints

    @property
    def cache(self) -> t.Dict[_KT, _VT]:
        """The cache itself.

        Returns
        -------
        typing.Dict[_KT, _VT]
            The cache itself.
        """
        return self._cache


class SecondaryTypeCache(BaseCache[_KT, _VT]):
    """A cache for secondary types with differing endpoints."""

    def load_documents(self, data: t.List[t.Dict[str, str]]) -> None:
        """Load documents into the cache. Endpoints are different for secondary types.

        Parameters
        ----------
        data: typing.List[typing.Dict[str, str]]
            The data to load.
        """
        for document in data:
            self._endpoints[document["url"].split("/")[-2]] = Endpoint(
                url=document["url"], id=int(document["url"].split("/")[-2])
            )
        self._endpoints_cached = True


class BerryCache(BaseCache["Route", "models.Berry"]):
    """A cache for berries."""


class BerryFirmnessCache(BaseCache["Route", "models.BerryFirmness"]):
    """A cache for berry firmnesses."""


class BerryFlavorCache(BaseCache["Route", "models.BerryFlavor"]):
    """A cache for berry flavors."""


class ContestTypeCache(BaseCache["Route", "models.ContestType"]):
    """A cache for contest types."""


class PokemonCache(BaseCache["Route", "models.Pokemon"]):
    """A cache for pokemon."""


class AbilityCache(BaseCache["Route", "models.Ability"]):
    """A cache for abilities."""


class EggGroupCache(BaseCache["Route", "models.EggGroup"]):
    """A cache for egg groups."""


class GenderCache(BaseCache["Route", "models.Gender"]):
    """A cache for genders."""


class GrowthRateCache(BaseCache["Route", "models.GrowthRate"]):
    """A cache for growth rates."""


class NatureCache(BaseCache["Route", "models.Nature"]):
    """A cache for natures."""


class PokeathlonStatCache(BaseCache["Route", "models.PokeathlonStat"]):
    """A cache for pokeathlon stats."""


class PokemonColorCache(BaseCache["Route", "models.PokemonColor"]):
    """A cache for pokemon colors."""


class PokemonFormCache(BaseCache["Route", "models.PokemonForm"]):
    """A cache for pokemon forms."""


class PokemonLocationAreaCache(BaseCache["Route", "models.LocationAreaEncounter"]):
    """A cache for pokemon location areas."""


class PokemonHabitatCache(BaseCache["Route", "models.PokemonHabitats"]):
    """A cache for pokemon habitats."""


class PokemonShapeCache(BaseCache["Route", "models.PokemonShape"]):
    """A cache for pokemon shapes."""


class PokemonSpeciesCache(BaseCache["Route", "models.PokemonSpecies"]):
    """A cache for pokemon species."""


class StatCache(BaseCache["Route", "models.Stat"]):
    """A cache for stats."""


class TypeCache(BaseCache["Route", "models.Type"]):
    """A cache for types."""


class EncounterMethodCache(BaseCache["Route", "models.EncounterMethod"]):
    """A cache for encounter methods."""


class EncounterConditionCache(BaseCache["Route", "models.EncounterCondition"]):
    """A cache for encounter conditions."""


class EncounterConditionValueCache(BaseCache["Route", "models.EncounterConditionValue"]):
    """A cache for encounter condition values."""


class EvolutionTriggerCache(BaseCache["Route", "models.EvolutionTrigger"]):
    """A cache for evolution triggers."""


class GamesGenerationCache(BaseCache["Route", "models.Generation"]):
    """A cache for games generations."""


class GamesPokedexCache(BaseCache["Route", "models.Pokedex"]):
    """A cache for games pokedexes."""


class GamesVersionCache(BaseCache["Route", "models.Version"]):
    """A cache for games versions."""


class GamesVersionGroupCache(BaseCache["Route", "models.VersionGroup"]):
    """A cache for games version groups."""


class ItemCache(BaseCache["Route", "models.Item"]):
    """A cache for items."""


class ItemAttributeCache(BaseCache["Route", "models.ItemAttribute"]):
    """A cache for item attributes."""


class ItemCategoryCache(BaseCache["Route", "models.ItemCategory"]):
    """A cache for item categories."""


class ItemFlingEffectCache(BaseCache["Route", "models.ItemFlingEffect"]):
    """A cache for item fling effects."""


class ItemPocketCache(BaseCache["Route", "models.ItemPocket"]):
    """A cache for item pockets."""


class LocationCache(BaseCache["Route", "models.Location"]):
    """A cache for locations."""


class LocationAreaCache(BaseCache["Route", "models.LocationArea"]):
    """A cache for location areas."""


class PalParkAreaCache(BaseCache["Route", "models.PalParkArea"]):
    """A cache for pal park areas."""


class RegionCache(BaseCache["Route", "models.Region"]):
    """A cache for regions."""


class MoveCache(BaseCache["Route", "models.Move"]):
    """A cache for moves."""


class MoveAilmentCache(BaseCache["Route", "models.MoveAilment"]):
    """A cache for move ailments."""


class MoveBattleStyleCache(BaseCache["Route", "models.MoveBattleStyle"]):
    """A cache for move battle styles."""


class MoveCategoryCache(BaseCache["Route", "models.MoveCategory"]):
    """A cache for move categories."""


class MoveDamageClassCache(BaseCache["Route", "models.MoveDamageClass"]):
    """A cache for move damage classes."""


class MoveLearnMethodCache(BaseCache["Route", "models.MoveLearnMethod"]):
    """A cache for move learn methods."""


class MoveTargetCache(BaseCache["Route", "models.MoveTarget"]):
    """A cache for move targets."""


class MachineCache(SecondaryTypeCache["Route", "models.Machine"]):
    """A cache for machines."""


class EvolutionChainCache(SecondaryTypeCache["Route", "models.EvolutionChain"]):
    """A cache for evolution chains."""


class CharacteristicCache(SecondaryTypeCache["Route", "models.Characteristic"]):
    """A cache for characteristics."""


class ContestEffectCache(SecondaryTypeCache["Route", "models.ContestEffect"]):
    """A cache for contest effects."""


class SuperContestEffectCache(SecondaryTypeCache["Route", "models.SuperContestEffect"]):
    """A cache for super contest effects."""
