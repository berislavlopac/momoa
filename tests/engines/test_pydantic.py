"""Tests for PydanticEngine: contract compliance and pydantic-specific behaviour."""

import pickle

from pydantic import BaseModel
import pytest

from momoa.exceptions import SchemaError
from tests.engines.contract import run_contract_tests


class TestPydanticEngineContract:
    def test_contract(self, pydantic_engine, person_schema):
        run_contract_tests(pydantic_engine, person_schema)


class TestPydanticEngineSpecific:
    def test_output_format(self, pydantic_engine):
        assert pydantic_engine.output_format == "pydantic"

    def test_models_are_basemodel_subclasses(self, pydantic_engine, person_schema):
        result = pydantic_engine.compile(person_schema)
        for cls in result.models:
            assert issubclass(cls, BaseModel)

    def test_model_has_serialize_method(self, pydantic_engine, person_schema):
        result = pydantic_engine.compile(person_schema)
        instance = result.model(firstName="Alice", lastName="Smith")
        assert callable(instance.serialize)

    def test_pydantic_features_accessible(self, pydantic_engine, person_schema):
        result = pydantic_engine.compile(person_schema)
        person_cls = result.model
        instance = person_cls(firstName="Alice", lastName="Smith")
        dumped = instance.model_dump(exclude_unset=True)
        assert dumped == {"firstName": "Alice", "lastName": "Smith"}

    def test_pydantic_validation_raises_on_invalid_data(self, pydantic_engine, person_schema):
        from pydantic import ValidationError

        result = pydantic_engine.compile(person_schema)
        person_cls = result.model
        with pytest.raises(ValidationError):
            person_cls()  # missing required fields

    def test_root_name_selects_named_model(self, pydantic_engine, person_schema):
        result = pydantic_engine.compile(person_schema, root_name="Person")
        assert result.model.__name__ == "Person"

    def test_root_name_unknown_raises(self, pydantic_engine, person_schema):
        with pytest.raises(SchemaError):
            pydantic_engine.compile(person_schema, root_name="NoSuchModel")

    def test_dynamically_generated_models_not_picklable(self, pydantic_engine, person_schema):
        result = pydantic_engine.compile(person_schema)
        instance = result.model(firstName="Alice", lastName="Smith")
        with pytest.raises((TypeError, AttributeError, pickle.PicklingError)):
            pickle.dumps(instance)
