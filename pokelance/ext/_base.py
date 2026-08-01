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
_VT = t.TypeVar("_VT", bound="t.Union[BaseModel, t.List[t.Any]]")


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
        cache: pokelance.cache.BaseCache[t.Any, t.Any]
            The cache to use for the validation.
        resource: t.Union[str, int]
            The resource to validate.
        route: pokelance.http.Route
            The route to use for the validation.

        Raises
        ------
        pokelance.exceptions.ResourceNotFound
            The resource was not found in the cache.
        """
        data: t.Set[str] = cache.identifiers
        if data and str(resource) not in data:
            suggestions = get_close_matches(str(resource), data, n=10, cutoff=0.5)
            raise ResourceNotFound(
                message=f"Resource not found - {route.url}", route=route, status=404, suggestions=suggestions
            )

    async def setup(self) -> None:
        """Sets up the extension."""
        for item in dir(self):
            if item.startswith("fetch_"):
                endpoint_name = f"get_{item[6:]}_endpoints"
                if not hasattr(Endpoint, endpoint_name):
                    continue
                endpoint: t.Callable[[], "Route"] = getattr(Endpoint, endpoint_name)
                data = await self._client.request(endpoint())
                self._cache.load_documents(str(self.__class__.__name__), item[6:], data["results"])
