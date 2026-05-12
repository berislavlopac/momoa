"""Tests for StathamEngine: contract compliance, engine-level, model, and Schema behaviour."""

from datetime import datetime
import inspect
import json
import logging

import pytest
from statham.schema.constants import NotPassed
from statham.schema.parser import parse

from momoa import Schema
from momoa.engines.statham import UNDEFINED, StathamEngine, StathamModel
from momoa.exceptions import DataValidationError, InvalidFieldError, SchemaError
from tests.engines.contract import run_contract_tests


@pytest.fixture
def person_model(schema_dict):
    schema_class = parse(schema_dict).pop()
    return StathamModel.make_model(schema_class)


class TestStathamEngineContract:
    def test_contract(self, statham_engine, person_schema):
        run_contract_tests(statham_engine, person_schema)


class TestStathamEngineSpecific:
    def test_output_format(self, statham_engine):
        assert statham_engine.output_format == "statham"

    def test_models_are_model_subclasses(self, statham_engine, person_schema):
        result = statham_engine.compile(person_schema)
        for cls in result.models:
            assert issubclass(cls, StathamModel)

    def test_custom_model_factory(self, person_schema):
        def factory(schema_class):
            return type(
                schema_class.__name__ + "Custom",
                (StathamModel,),
                {"_schema_class": schema_class},
            )

        engine = StathamEngine(model_factory=factory)
        result = engine.compile(person_schema)
        assert result.model.__name__.endswith("Custom")

    def test_invalid_schema_raises_schema_error(self, statham_engine):
        bad_schema = {
            "title": "Bad",
            "type": "object",
            "properties": {"x": {"type": "blabla"}},
        }
        with pytest.raises(SchemaError):
            statham_engine.compile(bad_schema)


class TestStathamModel:
    def test_make_model_creates_model_class(self, schema_dict):
        schema_class = parse(schema_dict).pop()
        model = StathamModel.make_model(schema_class)

        assert inspect.isclass(model)
        assert issubclass(model, StathamModel)
        assert model.__name__ == "PersonModel"
        assert model._schema_class is schema_class

    def test_instantiation_without_required_fields_raises_validation_error(self, person_model):
        with pytest.raises(DataValidationError):
            person_model()

    def test_instantiation_with_required_values_also_sets_default_values(self, person_model):
        data_object = person_model(firstName="Boris", lastName="Harrison")
        assert data_object.firstName == "Boris"
        assert data_object.lastName == "Harrison"
        assert data_object.gender == "male"
        assert data_object.deceased is UNDEFINED

    def test_instantiation_with_incorrect_values_raises_validation_error(self, person_model):
        with pytest.raises(DataValidationError):
            person_model(firstName="Boris", lastName="Harrison", age="53")

    def test_instantiation_with_incorrect_fields_raises_validation_error(self, person_model):
        with pytest.raises(InvalidFieldError):
            person_model(firstName="Boris", lastName="Harrison", foo="bar")

    def test_instantiation_with_native_datetime(self, person_model):
        birthday = datetime(1969, 11, 23)
        person = person_model(firstName="Boris", lastName="Harrison", birthday=birthday)
        assert person.birthday == birthday

    def test_instantiation_with_iso_datetime(self, person_model):
        person = person_model(firstName="Boris", lastName="Harrison", birthday="1969-11-23")
        assert person.birthday == datetime(1969, 11, 23)

    def test_invalid_attribute_raises_exception(self, person_model):
        person = person_model(firstName="Boris", lastName="Harrison")
        with pytest.raises(AttributeError):
            person.foobar  # noqa: B018

    def test_unset_attribute_returns_sentinel_value(self, person_model):
        person = person_model(firstName="Boris", lastName="Harrison")
        assert person.age is UNDEFINED

    def test_setting_attributes_after_instantiation(self, person_model):
        birthday = datetime(1969, 11, 23)
        person = person_model(firstName="Boris", lastName="Harrison")

        assert person.age is UNDEFINED
        assert person.birthday is UNDEFINED

        person.age = 53
        person.birthday = birthday

        assert person.age == 53
        assert person.birthday == birthday

    def test_model_is_iterable(self, person_model):
        person = person_model(firstName="Boris", lastName="Harrison")
        for field, value in person:
            assert value == getattr(person, field)

    def test_models_with_same_data_are_equal_but_not_identical(self, person_model):
        person_1 = person_model(
            firstName="Boris", lastName="Harrison", dogs=["Fluffy", "Cerberus"]
        )
        person_2 = person_model(
            firstName="Boris", lastName="Harrison", dogs=["Fluffy", "Cerberus"]
        )
        assert person_1 == person_2
        assert person_1 is not person_2

    def test_models_with_different_data_are_not_equal(self, person_model):
        person_1 = person_model(
            firstName="Boris", lastName="Harrison", dogs=["Fluffy", "Cerberus"]
        )
        person_2 = person_model(firstName="Boris", lastName="Harrison", dogs=["Fluffy"])
        assert person_1 != person_2


class TestStathamSchema:
    def test_valid_schema_loads_from_dict(self, schema_dict, caplog):
        caplog.set_level(logging.DEBUG)
        loaded_schema = Schema(schema_dict)

        assert loaded_schema.schema_dict == schema_dict
        assert loaded_schema.title == "Person"

        model_names = ("AddressModel", "ShoePreferencesModel", "PersonModel")
        assert loaded_schema.model == loaded_schema.models[-1]
        assert loaded_schema.model.__name__ == model_names[-1]

        for index, model in enumerate(loaded_schema.models):
            assert issubclass(model, StathamModel)
            assert model.__name__ == model_names[index]

    def test_invalid_schema_fails_loading(self, schema_dict):
        schema_dict["properties"]["lastName"]["type"] = "blabla"
        with pytest.raises(SchemaError):
            Schema(schema_dict)

    def test_valid_schema_loads_from_uri(self, schema_file_path):
        loaded_schema = Schema.from_uri(f"file://{schema_file_path}")
        for model in loaded_schema.models:
            assert issubclass(model, StathamModel)

    def test_valid_schema_loads_from_file_path(self, schema_file_path):
        loaded_schema = Schema.from_file(schema_file_path)
        for model in loaded_schema.models:
            assert issubclass(model, StathamModel)

    def test_custom_model_factory_creates_model(self, schema_dict):
        def custom_model_factory(schema_class):
            name = schema_class.__name__.lower() + "blabla"
            return type(name, (StathamModel,), {"_schema_class": schema_class})

        loaded_schema = Schema(
            schema_dict, engine=StathamEngine(model_factory=custom_model_factory)
        )
        assert loaded_schema.model.__name__ == "personblabla"


class TestStathamDeserialization:
    def test_deserializes_from_dict(self, schema_dict):
        test_data = {
            "firstName": "Boris",
            "lastName": "Harrison",
            "age": 53,
            "dogs": ["Fluffy", "Crumpet"],
            "gender": "male",
            "deceased": False,
            "address": {
                "street": "adipisicing do proident laborum",
                "city": "veniam nulla ipsum adipisicing eu",
                "state": "Excepteur esse elit",
            },
        }
        schema = Schema(schema_dict)
        result = schema.deserialize(test_data)

        assert type(result).__name__ == "PersonModel"
        assert isinstance(result, schema.model)
        assert result.firstName == "Boris"
        assert result.lastName == "Harrison"
        assert result.gender == "male"
        assert not result.deceased
        assert result.birthday is UNDEFINED

    def test_deserializes_from_json_string(self, schema_dict):
        test_data = json.dumps(
            {
                "firstName": "Boris",
                "lastName": "Harrison",
                "age": 53,
                "dogs": ["Fluffy", "Crumpet"],
                "gender": "male",
                "deceased": False,
                "address": {
                    "street": "adipisicing do proident laborum",
                    "city": "veniam nulla ipsum adipisicing eu",
                    "state": "Excepteur esse elit",
                },
            }
        )
        schema = Schema(schema_dict)
        result = schema.deserialize(test_data)

        assert type(result).__name__ == "PersonModel"
        assert isinstance(result, schema.model)
        assert result.firstName == "Boris"
        assert result.lastName == "Harrison"
        assert result.birthday is NotPassed()
        assert not result.deceased

    def test_invalid_data_raises_exception(self, schema_dict):
        test_data = json.dumps(
            {
                "firstName": "Boris",
                "lastName": "Harrison",
                "age": "53",
                "dogs": ["Fluffy", "Crumpet"],
                "gender": "male",
                "deceased": False,
                "address": {
                    "street": "adipisicing do proident laborum",
                    "city": "veniam nulla ipsum adipisicing eu",
                    "state": "Excepteur esse elit",
                },
            }
        )
        schema = Schema(schema_dict)
        with pytest.raises(DataValidationError):
            schema.deserialize(test_data)

    def test_deserializes_datetime_field(self, schema_dict):
        schema = Schema(schema_dict)
        result = schema.deserialize(
            {"firstName": "Boris", "lastName": "Harrison", "birthday": "1969-11-23"}
        )

        assert type(result).__name__ == "PersonModel"
        assert isinstance(result, schema.model)
        assert result.birthday == datetime(1969, 11, 23)

    def test_deserialization_is_inverse_of_serialization(self, schema_dict):
        schema = Schema(schema_dict)
        test_data = {
            "firstName": "Boris",
            "lastName": "Harrison",
            "age": 53,
            "dogs": ["Fluffy", "Crumpet"],
            "gender": "male",
            "deceased": False,
            "address": {
                "street": "adipisicing do proident laborum",
                "city": "veniam nulla ipsum adipisicing eu",
                "state": "Excepteur esse elit",
            },
        }
        instance = schema.model(**test_data)
        serialized = instance.serialize()
        deserialized = schema.deserialize(serialized)
        assert deserialized == instance

    def test_deserialization_creates_default_values(self, schema_dict):
        schema = Schema(schema_dict)
        test_data = {
            "firstName": "Boris",
            "lastName": "Harrison",
            "age": 53,
            "dogs": ["Fluffy", "Crumpet"],
            "deceased": False,
            "address": {
                "street": "adipisicing do proident laborum",
                "city": "veniam nulla ipsum adipisicing eu",
                "state": "Excepteur esse elit",
            },
        }
        deserialized = schema.deserialize(test_data)
        assert deserialized.gender == "male"


class TestStathamSerialization:
    def test_serializes_to_dict(self, schema_dict):
        schema = Schema(schema_dict)
        data_object = schema.model(
            firstName="Boris",
            lastName="Harrison",
            age=53,
            deceased=False,
            birthday=datetime(1969, 11, 23),
        )
        result = data_object.serialize()
        assert result == {
            "firstName": "Boris",
            "lastName": "Harrison",
            "age": 53,
            "gender": "male",
            "deceased": False,
            "birthday": "1969-11-23",
        }

    def test_nested_models_are_serialized(self, schema_dict):
        schema = Schema(schema_dict)
        data_object = schema.model(
            firstName="Boris",
            lastName="Harrison",
            age=53,
            deceased=False,
            birthday=datetime(1969, 11, 23),
            address={"street": "foo", "city": "bar"},
        )
        result = data_object.serialize()
        assert result == {
            "firstName": "Boris",
            "lastName": "Harrison",
            "age": 53,
            "gender": "male",
            "deceased": False,
            "birthday": "1969-11-23",
            "address": {"street": "foo", "city": "bar"},
        }

    def test_attributes_set_after_instantiation_serialize_correctly(self, schema_dict):
        schema = Schema(schema_dict)
        person = schema.model(firstName="Boris", lastName="Harrison")

        assert person.age is UNDEFINED
        assert person.birthday is UNDEFINED

        serialized = person.serialize()
        assert "age" not in serialized
        assert "birthday" not in serialized

        person.age = 53
        person.birthday = datetime(1969, 11, 23)

        serialized = person.serialize()
        assert serialized["age"] == 53
        assert serialized["birthday"] == "1969-11-23"

    def test_generic_subschemas_are_serialized_correctly(self, test_data_dir):
        description_schema = Schema.from_file(test_data_dir / "action_description.json")
        input_schema = Schema.from_file(test_data_dir / "action_input_schema.json")
        output_schema = Schema.from_file(test_data_dir / "action_output_schema.json")
        description = {
            "action": "test_action",
            "input_schema": input_schema.schema_dict,
            "output_schema": output_schema.schema_dict,
        }
        description_model = description_schema.model(**description)
        serialized = description_model.serialize()
        assert serialized == {
            "action": "test_action",
            "input_schema": {
                "type": "object",
                "title": "Get Example Input Schema",
                "properties": {"something": {"type": "string"}},
                "required": ["something"],
            },
            "output_schema": {
                "type": "object",
                "title": "Get Example Output Schema",
                "properties": {"something_else": {"type": "string"}},
                "required": ["something_else"],
            },
        }

    def test_serialization_is_inverse_of_deserialization(self, schema_dict):
        """Works only when all properties with defaults are explicitly provided."""
        schema = Schema(schema_dict)
        test_data = {
            "firstName": "Boris",
            "lastName": "Harrison",
            "age": 53,
            "dogs": ["Fluffy", "Crumpet"],
            "gender": "other",
            "deceased": False,
            "address": {
                "street": "adipisicing do proident laborum",
                "city": "veniam nulla ipsum adipisicing eu",
                "state": "Excepteur esse elit",
            },
        }
        deserialized = schema.deserialize(test_data)
        serialized = deserialized.serialize()
        assert serialized == test_data
