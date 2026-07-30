"""
Tests for pokelance.exceptions all exception classes, __str__ methods,
create(), and get_exception().

These tests are pure unit tests: no network, no client, no fixtures needed.
We construct a minimal Route stand-in because Route is only imported under
TYPE_CHECKING in exceptions.py at runtime the parameter is duck-typed.

Coverage
--------
- PokeLanceException: __init__, __str__, attributes
- HTTPException: __init__, __str__, create() dispatches to correct subclass
- BadRequest / Unauthorized / Forbidden / NotFound / MethodNotAllowed: instantiation
- ResourceNotFound: __str__ with and without suggestions
- ImageNotFound: __init__, __str__
- AudioNotFound: __init__, __str__
- UnknownError: returned for unmapped status codes
- get_exception(): all mapped codes and fallback
- CODES dict: correct mapping
"""
import typing as t

import pytest

from pokelance.exceptions import (
    AudioNotFound,
    BadRequest,
    Forbidden,
    HTTPException,
    ImageNotFound,
    MethodNotAllowed,
    NotFound,
    PokeLanceException,
    ResourceNotFound,
    Unauthorized,
    UnknownError,
    get_exception,
)

# ---------------------------------------------------------------------------
# Minimal Route stand-in (avoids importing the real Route which needs aiohttp)
# ---------------------------------------------------------------------------


class _FakeRoute:
    def __str__(self) -> str:
        return "/fake/route"


ROUTE: t.Any = _FakeRoute()


# ---------------------------------------------------------------------------
# PokeLanceException
# ---------------------------------------------------------------------------


def test_pokelance_exception_message() -> None:
    exc = PokeLanceException("something went wrong", ROUTE)
    assert exc.message == "something went wrong"


def test_pokelance_exception_route() -> None:
    exc = PokeLanceException("msg", ROUTE)
    assert exc.route is ROUTE


def test_pokelance_exception_str() -> None:
    exc = PokeLanceException("oops", ROUTE)
    assert str(exc) == "oops | /fake/route"


def test_pokelance_exception_is_exception() -> None:
    exc = PokeLanceException("msg", ROUTE)
    assert isinstance(exc, Exception)


# ---------------------------------------------------------------------------
# HTTPException
# ---------------------------------------------------------------------------


def test_http_exception_status() -> None:
    exc = HTTPException("bad", ROUTE, 400)
    assert exc.status == 400


def test_http_exception_str() -> None:
    exc = HTTPException("bad", ROUTE, 400)
    assert str(exc) == "bad | /fake/route | 400"


def test_http_exception_create_returns_correct_subclass() -> None:
    exc = HTTPException("not found", ROUTE, 404)
    created = exc.create()
    assert isinstance(created, ResourceNotFound)


def test_http_exception_create_unknown_status() -> None:
    exc = HTTPException("server error", ROUTE, 500)
    created = exc.create()
    assert isinstance(created, UnknownError)


# ---------------------------------------------------------------------------
# Concrete HTTP subclasses basic instantiation
# ---------------------------------------------------------------------------


@pytest.mark.parametrize(
    "cls,status",
    [
        (BadRequest, 400),
        (Unauthorized, 401),
        (Forbidden, 403),
        (NotFound, 404),
        (MethodNotAllowed, 405),
        (UnknownError, 999),
    ],
)
def test_http_subclass_instantiation(cls: type, status: int) -> None:
    exc = cls("msg", ROUTE, status)
    assert exc.status == status
    assert exc.message == "msg"
    assert exc.route is ROUTE


# ---------------------------------------------------------------------------
# ResourceNotFound
# ---------------------------------------------------------------------------


def test_resource_not_found_str_no_suggestions() -> None:
    exc = ResourceNotFound("not found", ROUTE, 404)
    s = str(exc)
    assert "not found" in s
    assert "/fake/route" in s
    assert "404" in s
    assert "Suggestions" not in s


def test_resource_not_found_str_with_suggestions() -> None:
    exc = ResourceNotFound("not found", ROUTE, 404, suggestions=["bulbasaur", "ivysaur"])
    s = str(exc)
    assert "Suggestions" in s
    assert "bulbasaur" in s
    assert "ivysaur" in s


def test_resource_not_found_suggestions_none_by_default() -> None:
    exc = ResourceNotFound("not found", ROUTE, 404)
    assert exc.suggestions is None


def test_resource_not_found_suggestions_stored() -> None:
    exc = ResourceNotFound("not found", ROUTE, 404, suggestions=["charmander"])
    assert exc.suggestions == ["charmander"]


def test_resource_not_found_is_not_found() -> None:
    exc = ResourceNotFound("not found", ROUTE, 404)
    assert isinstance(exc, NotFound)


# ---------------------------------------------------------------------------
# ImageNotFound
# ---------------------------------------------------------------------------


def test_image_not_found_str() -> None:
    exc = ImageNotFound("image missing", ROUTE, 404)
    s = str(exc)
    assert "image missing" in s
    assert "/fake/route" in s
    assert "404" in s


def test_image_not_found_is_not_found() -> None:
    exc = ImageNotFound("image missing", ROUTE, 404)
    assert isinstance(exc, NotFound)


# ---------------------------------------------------------------------------
# AudioNotFound
# ---------------------------------------------------------------------------


def test_audio_not_found_str() -> None:
    exc = AudioNotFound("audio missing", ROUTE, 404)
    s = str(exc)
    assert "audio missing" in s
    assert "/fake/route" in s
    assert "404" in s


def test_audio_not_found_is_not_found() -> None:
    exc = AudioNotFound("audio missing", ROUTE, 404)
    assert isinstance(exc, NotFound)


# ---------------------------------------------------------------------------
# get_exception()
# ---------------------------------------------------------------------------


@pytest.mark.parametrize(
    "status,expected_cls",
    [
        (400, BadRequest),
        (401, Unauthorized),
        (403, Forbidden),
        (404, ResourceNotFound),
        (405, MethodNotAllowed),
        (500, UnknownError),
        (418, UnknownError),
        (0, UnknownError),
    ],
)
def test_get_exception_mapping(status: int, expected_cls: type) -> None:
    cls = get_exception(status)
    assert cls is expected_cls


def test_get_exception_returns_callable() -> None:
    cls = get_exception(404)
    exc = cls("msg", ROUTE, 404)
    assert isinstance(exc, NotFound)
