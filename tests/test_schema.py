import logging

import pytest

from momoa import Schema
from momoa.exceptions import SchemaError
from momoa.model import Model


def test_valid_schema_loads_from_dict(schema_dict, caplog):
    caplog.set_level(logging.DEBUG)

    loaded_schema = Schema(schema_dict)

    assert loaded_schema.schema_dict == schema_dict
    assert loaded_schema.title == "Person"

    model_names = ("AddressModel", "ShoePreferencesModel", "PersonModel")
    assert loaded_schema.model == loaded_schema.models[-1]
    assert loaded_schema.model.__name__ == model_names[-1]

    for index, model in enumerate(loaded_schema.models):
        assert issubclass(model, Model)
        assert model.__name__ == model_names[index]


def test_invalid_schema_fails_loading(schema_dict):
    schema_dict["properties"]["lastName"]["type"] = "blabla"

    with pytest.raises(SchemaError):
        Schema(schema_dict)


def test_valid_schema_loads_from_uri(schema_file_path):
    loaded_schema = Schema.from_uri(f"file://{schema_file_path}")

    for model in loaded_schema.models:
        assert issubclass(model, Model)


def test_valid_schema_loads_from_file_path(schema_file_path):
    loaded_schema = Schema.from_file(schema_file_path)

    for model in loaded_schema.models:
        assert issubclass(model, Model)


def test_custom_model_factory_creates_model(schema_dict):
    def custom_model_factory(schema_class):
        name = schema_class.__name__.lower() + "blabla"
        return type(name, (Model,), {"_schema_class": schema_class})

    loaded_schema = Schema(schema_dict, model_factory=custom_model_factory)
    assert loaded_schema.model.__name__ == "personblabla"
