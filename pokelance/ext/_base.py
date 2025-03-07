import typing as t
from difflib import get_close_matches

from pokelance.exceptions import ResourceNotFound
from pokelance.http import Endpoint

if t.TYPE_CHECKING:
    from pokelance.cache import BaseCache, Cache
    from pokelance.http import HttpClient, Route
    from pokelance.models import BaseModel


__all__: t.Tuple[str, ...] = ("BaseExtension",)
_KT = t.TypeVar("_KT", bound="Route")
_VT = t.TypeVar("_VT", bound="BaseModel")


class BaseExtension:
    """The base extension class.

    Parameters
    ----------
    client: pokelance.http.HttpClient
        The client to use for requests.

    Attributes
    ----------
    _client: pokelance.http.HttpClient
        The client to use for requests.
    _cache: pokelance.cache.Cache
        The cache to use for requests.
    """

    _cache: "Cache"

    def __init__(self, client: "HttpClient") -> None:
        """Initializes the extension.

        Parameters
        ----------
        client: pokelance.http.HttpClient
            The client to use for requests.
        """
        self._client = client
        self._cache = self._client.cache
        self.cache = getattr(self._cache, self.__class__.__name__.lower())

    def _validate_resource(self, cache: "BaseCache[_KT, _VT]", resource: t.Union[str, int], route: "Route") -> None:
        """Validates a resource.

        Parameters
        ----------
        cache: pokelance.cache.BaseCache[typing.Any, typing.Any]
            The cache to use for the validation.
        resource: typing.Union[str, int]
            The resource to validate.
        route: pokelance.http.Route
            The route to use for the validation.

        Raises
        ------
        pokelance.exceptions.ResourceNotFound
            The resource was not found in the cache.
        """
        data: t.Set[str] = set(list(map(str, cache.endpoints.values())) + list(cache.endpoints.keys()))
        if data and str(resource) not in data:
            suggestions = get_close_matches(str(resource), data, n=10, cutoff=0.5)
            raise ResourceNotFound(message="Resource not found.", route=route, status=404, suggestions=suggestions)

    async def setup(self) -> None:
        """Sets up the extension."""
        for item in dir(self):
            if item.startswith("fetch_"):
                data = await self._client.request(
                    t.cast(t.Callable[[], "Route"], getattr(Endpoint, f"get_{item[6:]}_endpoints"))()
                )
                self._cache.load_documents(str(self.__class__.__name__), item[6:], data["results"])
