import typing as t

import attrs


@attrs.define(hash=True, slots=True, kw_only=True)
class BaseModel(attrs.AttrsInstance):
    """Base model for all models"""

    raw: t.Dict[str, t.Any] = attrs.field(factory=dict, repr=False, eq=False, order=False)

    def to_dict(self) -> t.Dict[str, t.Any]:
        """Convert the model to a dict

        Returns
        -------
        typing.Dict[str, Any]
            The model as a dict.
        """
        return attrs.asdict(self)

    @classmethod
    def from_payload(cls, payload: t.Dict[str, t.Any]) -> "BaseModel":
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
