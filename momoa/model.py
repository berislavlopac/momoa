"""Base wrapper class for building JSONSchema based models."""
from __future__ import annotations

from typing import Any, Callable, cast, Type

from statham.schema.constants import NotPassed
from statham.schema.elements import meta, String
from statham.schema.exceptions import ValidationError
from stringcase import pascalcase

from .exceptions import DataValidationError
from .format import StringFormat

# Sentinel for unset values.
UNDEFINED = NotPassed()


class Model:
    """Base model class."""

    _schema_class: meta.ObjectMeta

    def __init__(self, **data):
        try:
            self._instance = self._schema_class(
                {key: self._format(key, value) for key, value in data.items()}
            )
        except ValidationError as ex:
            raise DataValidationError(f"{type(self).__name__} validation error: {ex}") from ex

    def _format(self, field: str, value: Any) -> str:
        """Converts Python native values to JSONSchema string equivalents on the fly."""
        element = self._get_field_element(field)
        if isinstance(element, String) and not isinstance(value, str):
            value = StringFormat(element.format).to_(value)
        return value

    def _unformat(self, field: str, value: str) -> Any:
        """Converts JSONSchema formatted string values to Python native on the fly."""
        element = self._get_field_element(field)
        if isinstance(element, String) and value:
            value = StringFormat(element.format).from_(value)
        else:
            value = element(value)
        return value

    def __getattr__(self, item: str) -> Any:
        if item in self._schema_class.properties:  # type: ignore
            return self._unformat(item, getattr(self._instance, item))
        raise AttributeError(f"'{type(self).__name__}' object has no attribute '{item}'")

    def __setattr__(self, item: str, value: Any) -> None:
        if item in self._schema_class.properties:  # type: ignore
            formatted_value = self._format(item, value)
            setattr(self._instance, item, formatted_value)
            self._instance._dict[item] = formatted_value
        else:
            super().__setattr__(item, value)

    def __iter__(self):
        return (
            (field_name, getattr(self, field_name))
            for field_name in self._schema_class.properties
        )

    def __eq__(self, other) -> bool:
        return isinstance(other, Model) and all(
            getattr(other, field) == value for field, value in self
        )

    def _get_field_element(self, field):
        try:
            return self._schema_class.properties[field].element
        except KeyError as ex:
            raise DataValidationError(f"Invalid field '{field}'") from ex

    def serialize(self):
        """Validates data and serializes it into JSON-ready format."""
        return _serialize_schema_value(self._instance)

    @staticmethod  # pragma: no mutate
    def make_model(schema_class: meta.ObjectMeta) -> Type[Model]:
        """
        Constructs a Model subclass based on the class derived from JSONSchema.

        Attributes:
            schema_class: Class derived from the JSONSchema.

        Returns:
            Subclass of the Model class.
        """
        name = pascalcase(schema_class.__name__) + "Model"
        return cast(Type[Model], type(name, (Model,), {"_schema_class": schema_class}))


ModelFactory = Callable[[meta.ObjectMeta], Type[Model]]  # pragma: no mutate


def _serialize_schema_value(value: Any) -> Any:
    """Helper function to recursively serialize schema values."""
    if isinstance(value, list):
        return [_serialize_schema_value(item) for item in value]
    if isinstance(type(value), meta.ObjectMeta):
        value = value._dict
    if isinstance(value, dict):
        return {
            field_name: _serialize_schema_value(field_value)
            for field_name, field_value in value.items()
            if not field_name.startswith("_") and field_value is not UNDEFINED
        }
    return value
