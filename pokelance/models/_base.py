import enum
import typing as t

import attrs

_T = t.TypeVar("_T", bound="BaseModel")


def _serializer(_instance: t.Any, _field: attrs.Attribute, value: t.Any) -> t.Any:  # type: ignore
    if isinstance(value, enum.Enum):
        return value.value
    return value


@attrs.define(hash=True, slots=True, kw_only=True, eq=True)
class BaseModel:
    """Base model for all models"""

    raw: t.Dict[str, t.Any] = attrs.field(factory=dict, repr=False, eq=False, order=False)

    def to_dict(self) -> t.Dict[str, t.Any]:
        """Convert the model to a dict

        Returns
        -------
        typing.Dict[str, Any]
            The model as a dict.
        """
        return attrs.asdict(
            self, filter=attrs.filters.exclude(attrs.fields(BaseModel).raw), value_serializer=_serializer
        )

    @classmethod
    def optional_from_payload(cls: t.Type[_T], data: t.Optional[t.Dict[str, t.Any]]) -> t.Optional[_T]:
        return cls.from_payload(data) if data else None

    @classmethod
    def from_payload(cls: t.Type[_T], payload: t.Dict[str, t.Any]) -> _T:
        """Create a model from a payload

        Parameters
        ----------
        payload: typing.Dict[str, Any]
            The payload to create the model from.

        Returns
        -------
        BaseModel
            The model created from the payload.
        """
        return cls(raw=payload)
