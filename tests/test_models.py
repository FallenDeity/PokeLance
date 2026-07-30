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

import attrs
import pytest

import pokelance
from pokelance.models._base import BaseModel, _serializer

# ---------------------------------------------------------------------------
# _serializer unit tests (no network)
# ---------------------------------------------------------------------------


class _Color(enum.Enum):
    RED = "red"
    BLUE = 42


def test_serializer_unwraps_str_enum() -> None:
    result = _serializer(None, None, _Color.RED)  # type: ignore[arg-type]
    assert result == "red"


def test_serializer_unwraps_int_enum() -> None:
    result = _serializer(None, None, _Color.BLUE)  # type: ignore[arg-type]
    assert result == 42


def test_serializer_passthrough_str() -> None:
    assert _serializer(None, None, "hello") == "hello"  # type: ignore[arg-type]


def test_serializer_passthrough_int() -> None:
    assert _serializer(None, None, 99) == 99  # type: ignore[arg-type]


def test_serializer_passthrough_none() -> None:
    assert _serializer(None, None, None) is None  # type: ignore[arg-type]


def test_serializer_passthrough_list() -> None:
    lst = [1, 2, 3]
    assert _serializer(None, None, lst) is lst  # type: ignore[arg-type]


# ---------------------------------------------------------------------------
# BaseModel.from_payload()
# ---------------------------------------------------------------------------


def test_from_payload_sets_raw() -> None:
    payload = {"id": 1, "name": "bulbasaur"}
    model = BaseModel.from_payload(payload)
    assert model.raw == payload


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
    assert m1 == m2, "raw is excluded from eq; two BaseModels with no other fields are equal."


def test_base_model_hash_is_consistent() -> None:
    m = BaseModel(raw={})
    assert hash(m) == hash(m)


# ---------------------------------------------------------------------------
# Concrete model round-trip: Pokemon.to_dict() keys match known fields
# ---------------------------------------------------------------------------


@pytest.mark.asyncio
async def test_pokemon_to_dict_excludes_raw(client: pokelance.PokeLance) -> None:
    pokemon = await client.pokemon.fetch_pokemon(1)
    d = pokemon.to_dict()
    assert "raw" not in d
    assert d["name"] == "bulbasaur"
    assert d["id"] == 1


@pytest.mark.asyncio
async def test_pokemon_to_dict_has_expected_keys(client: pokelance.PokeLance) -> None:
    pokemon = await client.pokemon.fetch_pokemon(1)
    d = pokemon.to_dict()
    for key in ("name", "id", "base_experience", "height", "weight", "abilities", "types"):
        assert key in d, f"Expected key '{key}' missing from to_dict() output."
