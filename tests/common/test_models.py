"""
Tests for pokelance.models._base BaseModel, to_dict(), from_payload(),
and the _serializer used during attrs.asdict().

Coverage
--------
- _serializer: enum values are unwrapped to their .value
- _serializer: non-enum values pass through unchanged
- BaseModel.to_dict() excludes the `raw` field
- BaseModel.to_dict() unwraps enum fields via _serializer
- BaseModel.from_payload() sets raw correctly
- BaseModel equality (__eq__ from attrs, excludes raw)
- BaseModel hash (__hash__ from attrs)
- Concrete model to_dict() round-trip (Pokemon)
"""

import enum
import typing as t

import attrs
import pytest

import pokelance
from pokelance.constants import validate_url
from pokelance.models._base import (
    BaseModel,
    _serializer,  # pyright: ignore[reportUnknownVariableType, reportPrivateUsage]
)


@pytest.mark.parametrize(
    "path", ["pokemon/25/encounters/extra", "pokemon/25/ability", "berry/1/berry-firmness", "berry/1/encounters"]
)
def test_validate_url_rejects_invalid_subresources(path: str) -> None:
    assert validate_url(f"https://pokeapi.co/api/v2/{path}") is None


# ---------------------------------------------------------------------------
# _serializer unit tests (no network)
# ---------------------------------------------------------------------------


class _Color(enum.Enum):
    RED = "red"
    BLUE = 42


@pytest.mark.parametrize(("value", "expected"), [(_Color.RED, "red"), (_Color.BLUE, 42)])
def test_serializer_unwraps_enum(value: _Color, expected: str | int) -> None:
    assert _serializer(None, t.cast("t.Any", None), value) == expected


@pytest.mark.parametrize("value", ["hello", 99, None, [1, 2, 3]])
def test_serializer_preserves_non_enum(value: object) -> None:
    assert _serializer(None, t.cast("t.Any", None), value) is value


# ---------------------------------------------------------------------------
# BaseModel.from_payload() raw inclusion
# ---------------------------------------------------------------------------


def test_from_payload_raw_is_same_object() -> None:
    payload = {"id": 1}
    model = BaseModel.from_payload(payload)
    assert model.raw is payload


# ---------------------------------------------------------------------------
# BaseModel.to_dict() raw excluded, enum unwrapped
# ---------------------------------------------------------------------------


def test_to_dict_excludes_raw() -> None:
    model = BaseModel(raw={"hidden": True})
    d = model.to_dict()
    assert "raw" not in d


@attrs.define(hash=True, slots=True, kw_only=True, eq=True)
class _ModelWithEnum(BaseModel):
    color: _Color = attrs.field(default=_Color.RED)
    count: int = attrs.field(default=0)


def test_to_dict_unwraps_enum_field() -> None:
    m = _ModelWithEnum(raw={}, color=_Color.BLUE, count=5)
    d = m.to_dict()
    assert d["color"] == 42  # .value of _Color.BLUE
    assert d["count"] == 5
    assert "raw" not in d


# ---------------------------------------------------------------------------
# BaseModel equality and hash (attrs-generated, raw excluded from eq)
# ---------------------------------------------------------------------------


def test_base_model_equality_ignores_raw() -> None:
    m1 = BaseModel(raw={"a": 1})
    m2 = BaseModel(raw={"b": 2})
    assert m1 == m2
    assert hash(m1) == hash(m2)


# ---------------------------------------------------------------------------
# Concrete model round-trip: Pokemon.to_dict() keys match known fields
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_pokemon_to_dict_excludes_raw(client: pokelance.PokeLanceAsyncClient) -> None:
    pokemon = await client.pokemon.fetch_pokemon(1)
    d = pokemon.to_dict()
    assert "raw" not in d
    assert d["name"] == "bulbasaur"
    assert d["id"] == 1
    assert {"name", "id", "base_experience", "height", "weight", "abilities", "types"} <= d.keys()


# ---------------------------------------------------------------------------
# parse_rpn_expression unit tests
# ---------------------------------------------------------------------------


def test_parse_rpn_expression_operators() -> None:
    from pokelance.utils import parse_rpn_expression

    assert parse_rpn_expression("") == ""
    assert parse_rpn_expression("EC 100 % 0 ==") == "(EC % 100) == 0"
    assert parse_rpn_expression("PID 16 >> 10 % 4 <=") == "((PID >> 16) % 10) <= 4"
    assert parse_rpn_expression("SPIN_DIR 1 == SPIN_SEC 5 < &&") == "(SPIN_DIR == 1) && (SPIN_SEC < 5)"
    assert parse_rpn_expression("SPIN_DIR 1 == SPIN_SEC 5 < and") == "(SPIN_DIR == 1) and (SPIN_SEC < 5)"
    assert parse_rpn_expression("IS_NIGHT not") == "not IS_NIGHT"
    assert parse_rpn_expression("SPIN_DIR 1 == !") == "!(SPIN_DIR == 1)"
    assert parse_rpn_expression("EC 100 % 0 == PID 10 % 5 >= ||") == "((EC % 100) == 0) || ((PID % 10) >= 5)"


@pytest.mark.parametrize(
    ("expression", "expected"),
    [
        ("A 1 == B 2 == || C 3 == D 4 == || &&", "((A == 1) || (B == 2)) && ((C == 3) || (D == 4))"),
        ("0 not 2 ==", "(not 0) == 2"),
        ("A B == C ==", "(A == B) == C"),
        ("A B && C ==", "(A && B) == C"),
        ("A B or C D or and", "(A or B) and (C or D)"),
    ],
)
def test_parse_rpn_expression_preserves_grouping(expression: str, expected: str) -> None:
    from pokelance.utils import parse_rpn_expression

    assert parse_rpn_expression(expression) == expected
