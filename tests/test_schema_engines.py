"""Schema public API tests parametrized over all available engines.

Simulates how a client codebase uses Schema with different engine backends.
"""

import inspect

from pydantic import BaseModel
import pytest

from momoa import Schema
from momoa.engines import Serializable
from momoa.engines.pydantic import PydanticEngine
from momoa.engines.statham import StathamEngine, StathamModel

ENGINES = pytest.mark.parametrize(
    "engine,model_base",
    [
        (StathamEngine(), StathamModel),
        (PydanticEngine(), BaseModel),
    ],
    ids=["statham", "pydantic"],
)


@ENGINES
def test_schema_loads_from_dict(schema_dict, engine, model_base):
    schema = Schema(schema_dict, engine=engine)
    assert inspect.isclass(schema.model)
    assert issubclass(schema.model, model_base)
    assert len(schema.models) > 0


@ENGINES
def test_schema_loads_from_file(schema_file_path, engine, model_base):
    schema = Schema.from_file(schema_file_path, engine=engine)
    assert inspect.isclass(schema.model)
    assert issubclass(schema.model, model_base)


@ENGINES
def test_schema_model_is_last_of_models(schema_dict, engine, model_base):
    schema = Schema(schema_dict, engine=engine)
    assert schema.model is schema.models[-1]


@ENGINES
def test_deserialize_returns_instance(schema_dict, engine, model_base):
    schema = Schema(schema_dict, engine=engine)
    instance = schema.deserialize({"firstName": "Alice", "lastName": "Smith"})
    assert instance is not None
    assert isinstance(instance, Serializable)


@ENGINES
def test_deserialize_from_json_string(schema_dict, engine, model_base):
    schema = Schema(schema_dict, engine=engine)
    instance = schema.deserialize('{"firstName": "Alice", "lastName": "Smith"}')
    assert instance is not None
    assert isinstance(instance, Serializable)


@ENGINES
def test_serialize_returns_dict(schema_dict, engine, model_base):
    schema = Schema(schema_dict, engine=engine)
    instance = schema.deserialize({"firstName": "Alice", "lastName": "Smith"})
    result = instance.serialize()
    assert isinstance(result, dict)
    assert result["firstName"] == "Alice"
    assert result["lastName"] == "Smith"


@ENGINES
def test_optional_fields_absent_from_serialize(schema_dict, engine, model_base):
    schema = Schema(schema_dict, engine=engine)
    instance = schema.deserialize({"firstName": "Alice", "lastName": "Smith"})
    result = instance.serialize()
    assert "age" not in result
    assert "deceased" not in result


@ENGINES
def test_roundtrip(schema_dict, engine, model_base):
    schema = Schema(schema_dict, engine=engine)
    data = {"firstName": "Alice", "lastName": "Smith", "age": 30}
    instance = schema.deserialize(data)
    serialized = instance.serialize()
    instance2 = schema.deserialize(serialized)
    assert instance2.serialize() == serialized
