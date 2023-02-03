from datetime import datetime

from momoa import Schema
from momoa.model import UNDEFINED


def test_instantiated_object_converts_to_serialized_data_with_validation(schema_dict):
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


def test_nested_models_are_serialized(schema_dict):
    schema = Schema(schema_dict)
    data_object = schema.model(
        firstName="Boris",
        lastName="Harrison",
        age=53,
        deceased=False,
        birthday=datetime(1969, 11, 23),
        address={
            "street": "foo",
            "city": "bar",
        },
    )

    result = data_object.serialize()

    assert result == {
        "firstName": "Boris",
        "lastName": "Harrison",
        "age": 53,
        "gender": "male",
        "deceased": False,
        "birthday": "1969-11-23",
        "address": {
            "street": "foo",
            "city": "bar",
        },
    }


def test_attributes_set_after_instantiation_serialize_correctly(schema_dict):
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


def test_generic_subschemas_are_serialized_correctly(test_data_dir):
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


def test_serialization_is_inverse_of_deserialization_if_no_undefined_defaults(schema_dict):
    """Note: Works only if there are no undefined values for properties with a default."""
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
