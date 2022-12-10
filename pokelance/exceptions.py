import typing as t

if t.TYPE_CHECKING:
    from pokelance.http import Route


__all__: t.Tuple[str, ...] = (
    "PokeLanceException",
    "HTTPException",
    "ResourceNotFound",
)


class PokeLanceException(Exception):
    def __init__(self, message: str, route: "Route") -> None:
        self.message = message
        self.route = route
        super().__init__(message)

    def __str__(self) -> str:
        return f"{self.message} | {self.route}"


class HTTPException(PokeLanceException):
    def __init__(self, message: str, route: "Route", status: int) -> None:
        self.status = status
        super().__init__(message, route)

    def __str__(self) -> str:
        return f"{self.message} | {self.route} | {self.status}"

    def create(self) -> "HTTPException":
        return get_exception(self.status)(self.message, self.route, self.status)


class ResourceNotFound(PokeLanceException):
    def __init__(self, message: str, route: "Route") -> None:
        super().__init__(message, route)

    def __str__(self) -> str:
        return f"{self.message} | {self.route}"


class BadRequest(HTTPException):
    ...


class Unauthorized(HTTPException):
    ...


class Forbidden(HTTPException):
    ...


class NotFound(HTTPException):
    ...


class MethodNotAllowed(HTTPException):
    ...


class UnknownError(HTTPException):
    ...


CODES: t.Dict[int, t.Type[HTTPException]] = {
    400: BadRequest,
    401: Unauthorized,
    403: Forbidden,
    404: NotFound,
    405: MethodNotAllowed,
}


def get_exception(status: int) -> t.Type[HTTPException]:
    return CODES.get(status, UnknownError)
