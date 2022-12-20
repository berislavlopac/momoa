import logging
from inspect import isclass

import pytest

from momoa import Schema
from momoa.exceptions import SchemaError
from momoa.model import Model


def test_valid_schema_loads_from_dict(schema_dict, caplog):
    caplog.set_level(logging.DEBUG)

    loaded_schema = Schema(schema_dict)

    assert loaded_schema.schema_dict == schema_dict

    for model in loaded_schema.models:
        assert model.__name__ in ("AddressModel", "ShoePreferencesModel", "PersonModel")
        assert isclass(model)
        assert issubclass(model, Model)
        assert loaded_schema.title == "Person"


def test_invalid_schema_fails_loading(schema_dict):
    schema_dict["properties"]["lastName"]["type"] = "blabla"

    with pytest.raises(SchemaError):
        Schema(schema_dict)


def test_valid_schema_loads_from_uri(test_data_dir):
    schema_file_path = test_data_dir / "schema.json"
    loaded_schema = Schema.from_uri(f"file://{schema_file_path}")

    for model in loaded_schema.models:
        assert isclass(model)
        assert issubclass(model, Model)


def test_valid_schema_loads_from_file_path(test_data_dir):
    schema_file_path = test_data_dir / "schema.json"
    loaded_schema = Schema.from_file(schema_file_path)

    for model in loaded_schema.models:
        assert isclass(model)
        assert issubclass(model, Model)
