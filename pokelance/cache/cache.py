import asyncio
import importlib
import json
import pathlib
import typing as t

import aiofiles
import attrs

from pokelance.models import BaseModel

if t.TYPE_CHECKING:
    from pokelance import PokeLance, models  # noqa: F401
    from pokelance.http import Route  # noqa: F401


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
    "LanguageCache",
    "APIMetadataCache",
    "CacheEndpoint",
)

_KT = t.TypeVar("_KT", bound="Route")
_VT = t.TypeVar("_VT", bound="t.Union[BaseModel, t.List[t.Any]]")
_T = t.TypeVar("_T")


@attrs.define(kw_only=True, slots=True, frozen=True)
class CacheEndpoint:
    """Represents a cached API endpoint.

    Attributes
    ----------
    id : t.Union[str, int]
        The ID of the endpoint.
    url : str
        The URL of the endpoint.
    """

    id: t.Union[str, int] = attrs.field(factory=str)
    url: str = attrs.field(factory=str)

    def __str__(self) -> str:
        return str(self.id)


class BaseCache(t.MutableMapping[_KT, _VT]):
    """Base class for all caches.

    Parameters
    ----------
    max_size: int
        The maximum size of the cache.

    Attributes
    ----------
    _max_size: int
        The maximum size of the cache.
    _cache: t.Dict[_KT, _VT]
        The cache itself.
    _endpoints: t.Dict[str, CacheEndpoint]
        The endpoints that are cached.
    _endpoints_by_id: t.Dict[str, str]
        Reverse lookup of id (as a string) to CacheEndpoint, for alias resolution.
    _identifiers: t.Set[str]
        The union of every valid name and id (as strings) for this category.
    _endpoints_cached: bool
        Whether or not the endpoints are cached.
    _client: pokelance.PokeLance
        The client that this cache is for.

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

    _client: "PokeLance"

    def __init__(self, max_size: int = 100) -> None:
        self._max_size = max_size
        self._cache: t.Dict[_KT, _VT] = {}
        self._endpoints: t.Dict[str, CacheEndpoint] = {}
        self._endpoints_by_id: t.Dict[str, str] = {}
        self._identifiers: t.Set[str] = set()
        self._endpoints_cached: bool = False
        self._endpoints_ready: asyncio.Event = asyncio.Event()

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
        """Clear the cached data only. The endpoint registry is left intact
        so that a previously-fetched list of names/ids does not need to be
        re-fetched just to repopulate the data cache."""
        self._cache.clear()

    def _mark_endpoints_cached(self) -> None:
        self._identifiers = set(self._endpoints) | set(self._endpoints_by_id)
        self._endpoints_cached = True
        self._endpoints_ready.set()

    def reset_endpoints(self) -> None:
        """Clear the endpoint registry and re-arm the per-cache ready event.

        After this call, ``wait_until_ready()`` on this cache will block
        again until ``_mark_endpoints_cached()`` is invoked by the new load.
        """
        self._endpoints.clear()
        self._endpoints_by_id.clear()
        self._identifiers.clear()
        self._endpoints_cached = False
        self._endpoints_ready.clear()

    def items(self) -> t.ItemsView[_KT, _VT]:
        return self._cache.items()

    def get(self, key: _KT, default: t.Union[_VT, _T, None] = None) -> t.Union[_VT, _T, None]:  # type: ignore
        """Get an item from the cache. If the exact key isn't found, it will attempt to resolve an alias (e.g. numeric id vs. name).

        Parameters
        ----------
        key: _KT
            The key to get.
        default: t.Union[_VT, _T, None]
            The default value to return if the key isn't found.
        """
        if key in self:
            return self[key]
        requested = key.endpoint.split("/")[-1]
        alias = self._endpoints_by_id.get(requested) or self._endpoints.get(requested)
        if alias:
            for k, v in self.items():
                if k.endpoint.split("/")[-1] == str(alias):
                    return v
        return default

    def load_documents(self, data: t.List[t.Dict[str, str]]) -> None:
        """Load documents into the cache.

        Parameters
        ----------
        data: t.List[t.Dict[str, str]]
            The data to load.
        """
        self.reset_endpoints()
        for document in data:
            id_ = int(document["url"].split("/")[-2])
            self._endpoints[document["name"]] = CacheEndpoint(url=document["url"], id=id_)
            self._endpoints_by_id[str(id_)] = document["name"]
        self._mark_endpoints_cached()

    def set_size(self, size: int) -> None:
        """Set the size of the cache.

        Parameters
        ----------
        size: int
            The size of the cache.
        """
        self._max_size = size

    async def wait_until_ready(self) -> None:
        """Wait until the all the endpoints are cached."""
        await self._client.http.connect()
        if self._client.cache_endpoints:
            await self._endpoints_ready.wait()

    async def save(self, path: str = ".") -> None:
        """Save the cache to a file.

        Parameters
        ----------
        path: str
            The path to save the cache to.
        """
        pathlib.Path(path).mkdir(parents=True, exist_ok=True)
        dummy: t.Dict[str, t.Union[t.Dict[str, t.Any], t.List[t.Dict[str, t.Any]]]] = {
            k.endpoint: ([i.raw for i in v] if isinstance(v, list) else v.raw) for k, v in self.items()  # type: ignore
        }
        async with aiofiles.open(pathlib.Path(f"{path}/{self.__class__.__name__}.json"), "w") as f:
            await f.write("{\n")
            for n, (k, v) in enumerate(dummy.items()):
                await f.write("\n".join([4 * " " + i for i in f'"{k}": {json.dumps(v, indent=4)}'.split("\n")]))
                if n != len(dummy) - 1:
                    await f.write(",\n")
            await f.write("\n}")

    async def load(self, path: str = ".") -> None:
        """Load the cache from a file.

        Parameters
        ----------
        path: str
            The path to load the cache from.
        """
        async with aiofiles.open(pathlib.Path(f"{path}/{self.__class__.__name__}.json"), "r") as f:
            data = json.loads(await f.read())

        self._max_size = len(data)
        route_model = importlib.import_module("pokelance.http").__dict__["Route"]
        value_type = str(self.__orig_bases__[0].__args__[1]).split(".")[-1].strip("[]")  # type: ignore

        model = importlib.import_module("pokelance.models").__dict__[value_type]
        if not issubclass(model, BaseModel):
            raise TypeError(f"Expected a subclass of BaseModel, got {type(model)}")

        for endpoint, info in data.items():
            route = route_model(endpoint=endpoint)
            self.setdefault(
                route, [model.from_payload(i) for i in info] if isinstance(info, list) else model.from_payload(info)
            )

    async def load_all_batch(self, batch_size: int = 20) -> None:
        """
        Load all documents/data from api into the cache in parallel. (Endpoints must be cached first)

        Parameters
        ----------
        batch_size: int
            The number of documents to load at once. Default is 20 to avoid overwhelming the API.
        """
        if not self._endpoints_cached:
            raise RuntimeError("The endpoints have not been cached yet.")

        self._client.logger.info(f"Loading {self.__class__.__name__}...")
        route_model = importlib.import_module("pokelance.http").__dict__["Route"]
        value_type = str(self.__orig_bases__[0].__args__[1]).split(".")[-1].strip("[]")  # type: ignore

        model = importlib.import_module("pokelance.models").__dict__[value_type]
        if not issubclass(model, BaseModel):
            raise TypeError(f"Expected a subclass of BaseModel, got {type(model)}")

        self._max_size = len(self._endpoints)
        endpoints = list(self._endpoints.values())
        total_endpoints = len(endpoints)
        for i in range(0, total_endpoints, batch_size):
            batch = endpoints[i : i + batch_size]
            tasks = []
            for endpoint in batch:
                route = route_model.from_raw_url(endpoint.url)
                data = self.get(route, None)
                if data:
                    self.setdefault(route, data)
                    self._client.logger.info(f"Cached {route} - existing data used.")
                else:
                    tasks.append(self._fetch_and_cache(route, model))
            if tasks:
                await asyncio.gather(*tasks)
            self._client.logger.debug(
                f"Loaded batch {i//batch_size + 1}/{(total_endpoints + batch_size - 1)//batch_size} for {self.__class__.__name__}"
            )
        self._client.logger.info(f"Loaded {self.__class__.__name__} - {len(self._cache)}/{total_endpoints} items.")

    async def _fetch_and_cache(self, route: "_KT", model: t.Type["_VT"]) -> None:
        """Helper method to fetch and cache a single item"""
        if not issubclass(model, BaseModel):
            raise TypeError(f"Expected a subclass of BaseModel, got {type(model)}")
        try:
            data = await self._client.http.request(route)
            self.setdefault(
                route, [model.from_payload(i) for i in data] if isinstance(data, list) else model.from_payload(data)
            )
        except Exception as e:
            self._client.logger.error(f"Failed to load {route}: {e}")

    async def load_all(self) -> None:
        """
        Load all documents/data from api into the cache. (Endpoints must be cached first)
        """
        if not self._endpoints_cached:
            raise RuntimeError("The endpoints have not been cached yet.")
        self._client.logger.info(f"Loading {self.__class__.__name__}...")
        route_model = importlib.import_module("pokelance.http").__dict__["Route"]
        value_type = str(self.__orig_bases__[0].__args__[1]).split(".")[-1].strip("[]")  # type: ignore
        model: "models.BaseModel" = importlib.import_module("pokelance.models").__dict__[value_type]
        self._max_size = len(self._endpoints)
        for endpoint in self._endpoints.values():
            route = route_model.from_raw_url(endpoint.url)
            data = self.get(route, None)
            self.setdefault(route, data if data else model.from_payload(await self._client.http.request(route)))
        self._client.logger.info(f"Loaded {self.__class__.__name__}.")

    @property
    def endpoints(self) -> t.Dict[str, CacheEndpoint]:
        """The endpoints that are cached.

        Returns
        -------
        t.Dict[str, CacheEndpoint]
            The endpoints that are cached.
        """
        return self._endpoints

    @property
    def identifiers(self) -> t.Set[str]:
        """Every valid name and id (as strings) for this category.

        Built once when the registry loads so all identifiers/aliases can be validated
        without needing to rebuild the set on every `get_*`/`fetch_*` call.

        Returns
        -------
        t.Set[str]
            The set of valid identifiers.
        """
        return self._identifiers

    @property
    def cache(self) -> t.Dict[_KT, _VT]:
        """The cache itself.

        Returns
        -------
        t.Dict[_KT, _VT]
            The cache itself.
        """
        return self._cache


class SecondaryTypeCache(BaseCache[_KT, _VT]):
    """A cache for secondary types with differing endpoints."""

    def load_documents(self, data: t.List[t.Dict[str, str]]) -> None:
        """Load documents into the cache. Endpoints are different for secondary types.

        Parameters
        ----------
        data: t.List[t.Dict[str, str]]
            The data to load.
        """
        self.reset_endpoints()
        for document in data:
            id_ = int(document["url"].split("/")[-2])
            self._endpoints[str(id_)] = CacheEndpoint(url=document["url"], id=id_)
            self._endpoints_by_id[str(id_)] = str(id_)
        self._mark_endpoints_cached()


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


class PokemonLocationAreaCache(BaseCache["Route", "t.List[models.LocationAreaEncounter]"]):
    """A cache for pokemon location areas."""

    def load_documents(self, data: t.List[t.Dict[str, str]]) -> None:
        self.reset_endpoints()
        for document in data:
            encounter_url = f"{document['url'].strip('/')}/encounters"
            id_ = int(encounter_url.split("/")[-2])
            self._endpoints[document["name"]] = CacheEndpoint(url=encounter_url, id=id_)
            self._endpoints_by_id[str(id_)] = document["name"]
        self._mark_endpoints_cached()


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


class LanguageCache(SecondaryTypeCache["Route", "models.Language"]):
    """A cache for languages."""


class APIMetadataCache(SecondaryTypeCache["Route", "models.APIMetadata"]):
    """A cache for API metadata."""
