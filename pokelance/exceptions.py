import typing as t

from typing_extensions import override

if t.TYPE_CHECKING:
    from pokelance.endpoints import Route


__all__: tuple[str, ...] = (
    "AudioNotFound",
    "HTTPException",
    "ImageNotFound",
    "PokeLanceException",
    "ResourceNotFound",
)


class PokeLanceException(Exception):  # ruff: ignore[error-suffix-on-exception-name]
    """Base exception class for PokeLance.

    Parameters
    ----------
    message: str
        The message to display.
    route: Optional[pokelance.http.Route]
        The route that caused the exception.

    Attributes
    ----------
    message: str
        The message to display.
    route: pokelance.endpoints.Route
        The route that caused the exception.

    """

    def __init__(self, message: str, route: "Route") -> None:
        self.message = message
        self.route = route
        super().__init__(message)

    @override
    def __str__(self) -> str:
        return f"{self.message} | {self.route!s}"


class HTTPException(PokeLanceException):
    """Base exception class for HTTP exceptions.

    Parameters
    ----------
    message: str
        The message to display.
    route: pokelance.endpoints.Route
        The route that caused the exception.
    status: int
        The status code of the exception.

    Attributes
    ----------
    message: str
        The message to display.
    route: pokelance.endpoints.Route
        The route that caused the exception.
    status: int
        The status code of the exception.
    """

    def __init__(self, message: str, route: "Route", status: int) -> None:
        self.status = status
        super().__init__(message, route)

    @override
    def __str__(self) -> str:
        return f"{self.message} | {self.route!s} | {self.status}"

    def create(self) -> "HTTPException":
        """Creates an exception from the status code."""
        return get_exception(self.status)(self.message, self.route, self.status)


class BadRequest(HTTPException):
    """Exception raised when a bad request is made. [HTTP 400]"""


class Unauthorized(HTTPException):
    """Exception raised when unauthorized. [HTTP 401]"""


class Forbidden(HTTPException):
    """Exception raised when forbidden. [HTTP 403]"""


class NotFound(HTTPException):
    """Exception raised when a resource is not found. [HTTP 404]"""


class MethodNotAllowed(HTTPException):
    """Exception raised when a method is not allowed. [HTTP 405]"""


class UnknownError(HTTPException):
    """Exception raised when an unknown error occurs."""


class ResourceNotFound(NotFound):
    """Exception raised when a resource is not found.

    Parameters
    ----------
    message: str
        The message to display.
    route: pokelance.endpoints.Route
        The route that caused the exception.
    status: int
        The status code of the exception.
    suggestions: list[str] | None, optional
        Possible suggestions for the resource.
    """

    def __init__(self, message: str, route: "Route", status: int, suggestions: list[str] | None = None) -> None:
        self.suggestions = suggestions or []
        super().__init__(message, route, status)

    @override
    def __str__(self) -> str:
        message = self.message
        if self.suggestions:
            message += f" Suggestions: {', '.join(self.suggestions)}"
        return f"{message} | {self.route!s} | {self.status}"


class ImageNotFound(NotFound):
    """Exception raised when an image is not found.

    Parameters
    ----------
    message: str
        The message to display.
    route: pokelance.endpoints.Route
        The route that caused the exception.
    status: int
        The status code of the exception.
    """

    def __init__(self, message: str, route: "Route", status: int) -> None:
        super().__init__(message, route, status)

    @override
    def __str__(self) -> str:
        return f"{self.message} | {self.route!s} | {self.status}"


class AudioNotFound(NotFound):
    """Exception raised when an audio is not found.

    Parameters
    ----------
    message: str
        The message to display.
    route: pokelance.endpoints.Route
        The route that caused the exception.
    status: int
        The status code of the exception.
    """

    def __init__(self, message: str, route: "Route", status: int) -> None:
        super().__init__(message, route, status)

    @override
    def __str__(self) -> str:
        return f"{self.message} | {self.route!s} | {self.status}"


CODES: dict[int, type[HTTPException]] = {
    400: BadRequest,
    401: Unauthorized,
    403: Forbidden,
    404: ResourceNotFound,
    405: MethodNotAllowed,
}


def get_exception(status: int) -> type[HTTPException]:
    """Gets an exception from the status code.

    Parameters
    ----------
    status: int
        The status code.

    Returns
    -------
    pokelance.exceptions.HTTPException
        The exception.
    """
    return CODES.get(status, UnknownError)
