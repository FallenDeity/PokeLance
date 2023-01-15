import typing as t

if t.TYPE_CHECKING:
    from pokelance.http import Route


__all__: t.Tuple[str, ...] = (
    "PokeLanceException",
    "HTTPException",
    "ResourceNotFound",
    "ImageNotFound",
)


class PokeLanceException(Exception):
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
    route: pokelance.http.Route
        The route that caused the exception.

    """

    def __init__(self, message: str, route: "Route") -> None:
        self.message = message
        self.route = route
        super().__init__(message)

    def __str__(self) -> str:
        return f"{self.message} | {str(self.route)}"


class HTTPException(PokeLanceException):
    """Base exception class for HTTP exceptions.

    Parameters
    ----------
    message: str
        The message to display.
    route: pokelance.http.Route
        The route that caused the exception.
    status: int
        The status code of the exception.

    Attributes
    ----------
    message: str
        The message to display.
    route: pokelance.http.Route
        The route that caused the exception.
    status: int
        The status code of the exception.
    """

    def __init__(self, message: str, route: "Route", status: int) -> None:
        self.status = status
        super().__init__(message, route)

    def __str__(self) -> str:
        return f"{self.message} | {str(self.route)} | {self.status}"

    def create(self) -> "HTTPException":
        """Creates an exception from the status code."""
        return get_exception(self.status)(self.message, self.route, self.status)


class ResourceNotFound(PokeLanceException):
    """Exception raised when a resource is not found.

    Parameters
    ----------
    message: str
        The message to display.
    route: pokelance.http.Route
        The route that caused the exception.
    """

    def __init__(self, message: str, route: "Route") -> None:
        super().__init__(message, route)

    def __str__(self) -> str:
        return f"{self.message} | {str(self.route)}"


class ImageNotFound(HTTPException):
    """Exception raised when an image is not found.

    Parameters
    ----------
    message: str
        The message to display.
    route: pokelance.http.Route
        The route that caused the exception.
    status: int
        The status code of the exception.
    """

    def __init__(self, message: str, route: "Route", status: int) -> None:
        super().__init__(message, route, status)

    def __str__(self) -> str:
        return f"{self.message} | {str(self.route)} | {self.status}"


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


CODES: t.Dict[int, t.Type[HTTPException]] = {
    400: BadRequest,
    401: Unauthorized,
    403: Forbidden,
    404: NotFound,
    405: MethodNotAllowed,
}


def get_exception(status: int) -> t.Type[HTTPException]:
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
