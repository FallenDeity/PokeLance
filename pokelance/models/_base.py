import typing as t

import attrs


@attrs.define(hash=True, slots=True, kw_only=True)
class BaseModel:
    """Base model for all models"""

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
        return cls()
