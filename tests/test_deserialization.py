import json
from datetime import datetime

import pytest
from statham.schema.constants import NotPassed

from momoa import Schema
from momoa.exceptions import DataValidationError
from momoa.model import UNDEFINED


def test_serialized_data_is_validated_and_converted_to_python_from_dict(schema_dict):
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


def test_serialized_data_is_validated_and_converted_to_python_from_string(schema_dict):
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


def test_invalid_data_raises_exception(schema_dict):
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


def test_serialized_data_containing_datetime_is_validated_and_converted(schema_dict):
    test_data = {"firstName": "Boris", "lastName": "Harrison", "birthday": "1969-11-23"}

    schema = Schema(schema_dict)
    result = schema.deserialize(test_data)

    assert type(result).__name__ == "PersonModel"
    assert isinstance(result, schema.model)
    assert result.birthday == datetime(1969, 11, 23)


def test_deserialization_is_inverse_of_serialization(schema_dict):
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


def test_deserialization_creates_default_values(schema_dict):
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
