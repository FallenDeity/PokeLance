import typing as t

import attrs

from .cache import BaseCache, BerryCache, BerryFirmnessCache, BerryFlavorCache

__all__: t.Tuple[str, ...] = (
    "Cache",
    "BaseCache",
)


@attrs.define(slots=True, kw_only=True)
class Berry:
    max_size: int = 100
    berry: BerryCache = attrs.field(default=BerryCache(max_size=max_size))
    berry_firmness: BerryFirmnessCache = attrs.field(default=BerryFirmnessCache(max_size=max_size))
    berry_flavor: BerryFlavorCache = attrs.field(default=BerryFlavorCache(max_size=max_size))


@attrs.define(slots=True)
class Cache:
    max_size: int = 100
    berry: Berry = attrs.field(default=Berry(max_size=max_size))

    def load_documents(self, category: str, _type: str, data: t.List[t.Dict[str, str]]) -> None:
        getattr(getattr(self, category.lower()), _type).load_documents(data)
