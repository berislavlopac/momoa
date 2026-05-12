"""Statham-based engine: wraps the existing JSON Schema Draft 6 implementation."""

from collections.abc import Callable
from copy import deepcopy
from typing import Any, cast

from humps import pascalize
from statham.schema.constants import NotPassed
from statham.schema.elements import String, meta
from statham.schema.exceptions import ValidationError
from statham.schema.parser import parse
from statham.serializers.orderer import orderer
from statham.titles import title_labeller

from momoa.engines import EngineResult
from momoa.exceptions import DataValidationError, InvalidFieldError, SchemaParseError
from momoa.format import StringFormat

UNDEFINED = NotPassed()


class StathamModel:
    """Base model class for StathamEngine output."""

    _schema_class: meta.ObjectMeta
    _formatter: type[StringFormat]

    def __init__(self, **data):
        try:
            self._instance = self._schema_class(
                {key: self._format(key, value) for key, value in data.items()}
            )
        except ValidationError as ex:
            raise DataValidationError(self, ex) from ex

    def _format(self, field: str, value: Any) -> str:
        """Converts Python native values to JSONSchema string equivalents on the fly."""
        element = self._get_field_element(field)
        if isinstance(element, String) and not isinstance(value, str):
            value = self._formatter(element.format).to_(value)
        return value

    def _unformat(self, field: str, value: str) -> Any:
        """Converts JSONSchema formatted string values to Python native on the fly."""
        element = self._get_field_element(field)
        if isinstance(element, String) and value:
            value = self._formatter(element.format).from_(value)
        else:
            value = element(value)
        return value

    def __getattr__(self, item: str) -> Any:
        if item in self._schema_class.properties:  # type: ignore
            return self._unformat(item, getattr(self._instance, item))
        message = f"'{type(self).__name__}' object has no attribute '{item}'"
        raise AttributeError(message)

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
        return isinstance(other, StathamModel) and all(
            getattr(other, field) == value for field, value in self
        )

    def _get_field_element(self, field):
        try:
            return self._schema_class.properties[field].element
        except KeyError as ex:
            raise InvalidFieldError(field) from ex

    def serialize(self) -> dict[str, Any]:
        """Validates data and serializes it into JSON-ready format."""
        return _serialize_schema_value(self._instance)

    @staticmethod  # pragma: no mutate
    def make_model(
        schema_class: meta.ObjectMeta, string_formatter=StringFormat
    ) -> "type[StathamModel]":
        """Constructs a StathamModel subclass based on the class derived from JSONSchema."""
        name = pascalize(schema_class.__name__) + "Model"
        return cast(
            type[StathamModel],
            type(
                name,
                (StathamModel,),
                {"_schema_class": schema_class, "_formatter": string_formatter},
            ),
        )


ModelFactory = Callable[[meta.ObjectMeta], type[StathamModel]]  # pragma: no mutate


def _serialize_schema_value(value: Any) -> Any:
    """Recursively serialize schema values to JSON-compatible types."""
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


class StathamEngine:
    """Compiles JSON Schema (Draft 6) into StathamModel subclasses via statham."""

    def __init__(self, model_factory: ModelFactory = StathamModel.make_model) -> None:
        self._model_factory = model_factory

    @property
    def output_format(self) -> str:
        """Engine identifier."""
        return "statham"

    def context_labeller(self) -> Callable[[str], tuple[str, Any]]:
        """Returns statham's title_labeller for naming anonymous nested schemas."""
        return title_labeller()

    def compile(self, spec: dict[str, Any], *, root_name: str | None = None) -> EngineResult:
        """Compile a JSON Schema spec into StathamModel subclasses."""
        title = spec.get("title", "<schema>")
        try:
            parsed = parse(deepcopy(spec))
        except KeyError as ex:
            raise SchemaParseError(title, ex) from ex
        models = tuple(map(self._model_factory, orderer(*parsed)))
        return EngineResult(models=models)
