import json
import typing as t
from collections.abc import MutableMapping

import aiofiles

if t.TYPE_CHECKING:
    from pokelance.http import Route  # noqa: F401
    from pokelance.models import Ability  # noqa: F401
    from pokelance.models import Berry  # noqa: F401
    from pokelance.models import BerryFirmness  # noqa: F401
    from pokelance.models import BerryFlavor  # noqa: F401
    from pokelance.models import Characteristic  # noqa: F401
    from pokelance.models import ContestEffect  # noqa: F401
    from pokelance.models import ContestType  # noqa: F401
    from pokelance.models import EggGroup  # noqa: F401
    from pokelance.models import EncounterCondition  # noqa: F401
    from pokelance.models import EncounterConditionValue  # noqa: F401
    from pokelance.models import EncounterMethod  # noqa: F401
    from pokelance.models import EvolutionChain  # noqa: F401
    from pokelance.models import EvolutionTrigger  # noqa: F401
    from pokelance.models import Gender  # noqa: F401
    from pokelance.models import Generation  # noqa: F401
    from pokelance.models import GrowthRate  # noqa: F401
    from pokelance.models import Item  # noqa: F401
    from pokelance.models import ItemAttribute  # noqa: F401
    from pokelance.models import ItemCategory  # noqa: F401
    from pokelance.models import ItemFlingEffect  # noqa: F401
    from pokelance.models import ItemPocket  # noqa: F401
    from pokelance.models import Location  # noqa: F401
    from pokelance.models import LocationArea  # noqa: F401
    from pokelance.models import LocationAreaEncounter  # noqa: F401
    from pokelance.models import Machine  # noqa: F401
    from pokelance.models import Move  # noqa: F401
    from pokelance.models import MoveAilment  # noqa: F401
    from pokelance.models import MoveBattleStyle  # noqa: F401
    from pokelance.models import MoveCategory  # noqa: F401
    from pokelance.models import MoveDamageClass  # noqa: F401
    from pokelance.models import MoveLearnMethod  # noqa: F401
    from pokelance.models import MoveTarget  # noqa: F401
    from pokelance.models import Nature  # noqa: F401
    from pokelance.models import PalParkArea  # noqa: F401
    from pokelance.models import PokeathlonStat  # noqa: F401
    from pokelance.models import Pokedex  # noqa: F401
    from pokelance.models import Pokemon  # noqa: F401
    from pokelance.models import PokemonColor  # noqa: F401
    from pokelance.models import PokemonForm  # noqa: F401
    from pokelance.models import PokemonHabitats  # noqa: F401
    from pokelance.models import PokemonShape  # noqa: F401
    from pokelance.models import PokemonSpecies  # noqa: F401
    from pokelance.models import Region  # noqa: F401
    from pokelance.models import Stat  # noqa: F401
    from pokelance.models import SuperContestEffect  # noqa: F401
    from pokelance.models import Type  # noqa: F401
    from pokelance.models import Version  # noqa: F401
    from pokelance.models import VersionGroup  # noqa: F401; noqa: F401


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

_KT = t.TypeVar("_KT")
_VT = t.TypeVar("_VT")


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
    """

    def __init__(self, max_size: int = 100) -> None:
        self._max_size = max_size
        self._cache: t.Dict[_KT, _VT] = {}
        self._endpoints: t.Dict[str, int] = {}

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

    def setdefault(self, __key: _KT, __default: t.Any = ...) -> _VT:
        item = self._cache.setdefault(__key, __default)
        if item is __default:
            self._cache[__key] = self._cache.pop(__key)
        return item

    def load_documents(self, data: t.List[t.Dict[str, str]]) -> None:
        """Load documents into the cache.

        Parameters
        ----------
        data: typing.List[typing.Dict[str, str]]
            The data to load.
        """
        for document in data:
            self._endpoints[document["name"]] = int(document["url"].split("/")[-2])

    async def save(self, path: str = "") -> None:
        """Save the cache to a file.

        Parameters
        ----------
        path: str
            The path to save the cache to.
        """
        async with aiofiles.open(f"{path}{self.__class__.__name__}.json", "w") as f:
            await f.write(json.dumps(self._cache, indent=4, ensure_ascii=False))

    @property
    def endpoints(self) -> t.Dict[str, int]:
        """The endpoints that are cached.

        Returns
        -------
        typing.Dict[str, int]
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
            self._endpoints[document["url"].split("/")[-2]] = int(document["url"].split("/")[-2])


class BerryCache(BaseCache["Route", "Berry"]):
    """A cache for berries."""


class BerryFirmnessCache(BaseCache["Route", "BerryFirmness"]):
    """A cache for berry firmnesses."""


class BerryFlavorCache(BaseCache["Route", "BerryFlavor"]):
    """A cache for berry flavors."""


class ContestTypeCache(BaseCache["Route", "ContestType"]):
    """A cache for contest types."""


class PokemonCache(BaseCache["Route", "Pokemon"]):
    """A cache for pokemon."""


class AbilityCache(BaseCache["Route", "Ability"]):
    """A cache for abilities."""


class EggGroupCache(BaseCache["Route", "EggGroup"]):
    """A cache for egg groups."""


class GenderCache(BaseCache["Route", "Gender"]):
    """A cache for genders."""


class GrowthRateCache(BaseCache["Route", "GrowthRate"]):
    """A cache for growth rates."""


class NatureCache(BaseCache["Route", "Nature"]):
    """A cache for natures."""


class PokeathlonStatCache(BaseCache["Route", "PokeathlonStat"]):
    """A cache for pokeathlon stats."""


class PokemonColorCache(BaseCache["Route", "PokemonColor"]):
    """A cache for pokemon colors."""


class PokemonFormCache(BaseCache["Route", "PokemonForm"]):
    """A cache for pokemon forms."""


class PokemonLocationAreaCache(BaseCache["Route", "LocationAreaEncounter"]):
    """A cache for pokemon location areas."""


class PokemonHabitatCache(BaseCache["Route", "PokemonHabitats"]):
    """A cache for pokemon habitats."""


class PokemonShapeCache(BaseCache["Route", "PokemonShape"]):
    """A cache for pokemon shapes."""


class PokemonSpeciesCache(BaseCache["Route", "PokemonSpecies"]):
    """A cache for pokemon species."""


class StatCache(BaseCache["Route", "Stat"]):
    """A cache for stats."""


class TypeCache(BaseCache["Route", "Type"]):
    """A cache for types."""


class EncounterMethodCache(BaseCache["Route", "EncounterMethod"]):
    """A cache for encounter methods."""


class EncounterConditionCache(BaseCache["Route", "EncounterCondition"]):
    """A cache for encounter conditions."""


class EncounterConditionValueCache(BaseCache["Route", "EncounterConditionValue"]):
    """A cache for encounter condition values."""


class EvolutionTriggerCache(BaseCache["Route", "EvolutionTrigger"]):
    """A cache for evolution triggers."""


class GamesGenerationCache(BaseCache["Route", "Generation"]):
    """A cache for games generations."""


class GamesPokedexCache(BaseCache["Route", "Pokedex"]):
    """A cache for games pokedexes."""


class GamesVersionCache(BaseCache["Route", "Version"]):
    """A cache for games versions."""


class GamesVersionGroupCache(BaseCache["Route", "VersionGroup"]):
    """A cache for games version groups."""


class ItemCache(BaseCache["Route", "Item"]):
    """A cache for items."""


class ItemAttributeCache(BaseCache["Route", "ItemAttribute"]):
    """A cache for item attributes."""


class ItemCategoryCache(BaseCache["Route", "ItemCategory"]):
    """A cache for item categories."""


class ItemFlingEffectCache(BaseCache["Route", "ItemFlingEffect"]):
    """A cache for item fling effects."""


class ItemPocketCache(BaseCache["Route", "ItemPocket"]):
    """A cache for item pockets."""


class LocationCache(BaseCache["Route", "Location"]):
    """A cache for locations."""


class LocationAreaCache(BaseCache["Route", "LocationArea"]):
    """A cache for location areas."""


class PalParkAreaCache(BaseCache["Route", "PalParkArea"]):
    """A cache for pal park areas."""


class RegionCache(BaseCache["Route", "Region"]):
    """A cache for regions."""


class MoveCache(BaseCache["Route", "Move"]):
    """A cache for moves."""


class MoveAilmentCache(BaseCache["Route", "MoveAilment"]):
    """A cache for move ailments."""


class MoveBattleStyleCache(BaseCache["Route", "MoveBattleStyle"]):
    """A cache for move battle styles."""


class MoveCategoryCache(BaseCache["Route", "MoveCategory"]):
    """A cache for move categories."""


class MoveDamageClassCache(BaseCache["Route", "MoveDamageClass"]):
    """A cache for move damage classes."""


class MoveLearnMethodCache(BaseCache["Route", "MoveLearnMethod"]):
    """A cache for move learn methods."""


class MoveTargetCache(BaseCache["Route", "MoveTarget"]):
    """A cache for move targets."""


class MachineCache(SecondaryTypeCache["Route", "Machine"]):
    """A cache for machines."""


class EvolutionChainCache(SecondaryTypeCache["Route", "EvolutionChain"]):
    """A cache for evolution chains."""


class CharacteristicCache(SecondaryTypeCache["Route", "Characteristic"]):
    """A cache for characteristics."""


class ContestEffectCache(SecondaryTypeCache["Route", "ContestEffect"]):
    """A cache for contest effects."""


class SuperContestEffectCache(SecondaryTypeCache["Route", "SuperContestEffect"]):
    """A cache for super contest effects."""
