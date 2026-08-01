import typing as t

from pokelance.http import Endpoint
from pokelance.models import APIMetadata, Language

from ._base import BaseExtension

if t.TYPE_CHECKING:
    from pokelance import PokeLance
    from pokelance.cache import Utility as UtilityCache


__all__: t.Tuple[str, ...] = (
    "setup",
    "Utility",
)


class Utility(BaseExtension):
    """
    Extension for utility related endpoints.

    Attributes
    ----------
    cache: pokelance.cache.Utility
        The cache for this extension.
    """

    cache: "UtilityCache"

    def get_language(self, name: t.Union[str, int]) -> t.Optional[Language]:
        """Gets a language from the cache.

        Parameters
        ----------
        name: t.Union[str, int]
            The name or id of the language.

        Returns
        -------
        t.Optional[Language]
            The language if it exists in the cache, else None.

        Raises
        ------
        pokelance.exceptions.ResourceNotFound
            The name or id of the language is invalid.
        """
        route = Endpoint.get_language(name)
        self._validate_resource(self.cache.language, name, route)
        return self.cache.language.get(route, None)

    async def fetch_language(self, name: t.Union[str, int]) -> Language:
        """Fetches a language from the API.

        Parameters
        ----------
        name: t.Union[str, int]
            The name or id of the language.

        Returns
        -------
        Language
            The language.

        Raises
        ------
        pokelance.exceptions.ResourceNotFound
            The name or id of the language is invalid.
        """
        route = Endpoint.get_language(name)
        self._validate_resource(self.cache.language, name, route)
        data = await self._client.request(route)
        return self.cache.language.setdefault(route, Language.from_payload(data))

    def get_api_metadata(self) -> t.Optional[APIMetadata]:
        """Gets the API metadata from the cache.

        Returns
        -------
        t.Optional[APIMetadata]
            The API metadata if it exists in the cache, else None.
        """
        route = Endpoint.get_api_metadata()
        return self.cache.api_metadata.get(route, None)

    async def fetch_api_metadata(self) -> APIMetadata:
        """Fetches the API metadata from the API.

        Returns
        -------
        APIMetadata
            The API metadata.
        """
        route = Endpoint.get_api_metadata()
        data = await self._client.request(route)
        return self.cache.api_metadata.setdefault(route, APIMetadata.from_payload(data))


def setup(lance: "PokeLance") -> None:
    """Sets up the utility extension."""
    lance.add_extension("utility", Utility(lance.http))
