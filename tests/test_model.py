import inspect
from datetime import datetime

import pytest
from statham.schema.parser import parse

from momoa.exceptions import DataValidationError
from momoa.model import Model, UNDEFINED


@pytest.fixture
def PersonModel(schema_dict):
    schema_class = parse(schema_dict).pop()
    return Model.make_model(schema_class)


def test_make_model_creates_model_class(schema_dict):
    schema_class = parse(schema_dict).pop()
    model = Model.make_model(schema_class)

    assert inspect.isclass(model)
    assert issubclass(model, Model)
    assert model.__name__ == "PersonModel"
    assert model._schema_class is schema_class


def test_instantiation_without_required_fields_raises_validation_error(PersonModel):
    with pytest.raises(DataValidationError):
        PersonModel()


def test_instantiation_with_required_values_also_sets_default_values(PersonModel):
    data_object = PersonModel(firstName="Boris", lastName="Harrison")
    assert data_object.firstName == "Boris"
    assert data_object.lastName == "Harrison"
    assert data_object.gender == "male"
    assert data_object.deceased is UNDEFINED


def test_instantiation_with_incorrect_values_raises_validation_error(PersonModel):
    with pytest.raises(DataValidationError):
        PersonModel(firstName="Boris", lastName="Harrison", age="53")


def test_instantiation_with_incorrect_fields_raises_validation_error(PersonModel):
    with pytest.raises(DataValidationError):
        PersonModel(firstName="Boris", lastName="Harrison", foo="bar")


def test_instantiation_with_native_datetime(PersonModel):
    birthday = datetime(1969, 11, 23)
    person = PersonModel(firstName="Boris", lastName="Harrison", birthday=birthday)

    assert person.birthday == birthday


def test_instantiation_with_iso_datetime(PersonModel):
    birthday = "1969-11-23"
    person = PersonModel(firstName="Boris", lastName="Harrison", birthday=birthday)

    assert person.birthday == datetime(1969, 11, 23)


def test_invalid_attribute_raises_exception(PersonModel):
    person = PersonModel(firstName="Boris", lastName="Harrison")
    with pytest.raises(AttributeError):
        person.foobar


def test_unset_attribute_returns_sentinel_value(PersonModel):
    person = PersonModel(firstName="Boris", lastName="Harrison")
    assert person.age is UNDEFINED


def test_setting_attributes_after_instantiation(PersonModel):
    birthday = datetime(1969, 11, 23)
    person = PersonModel(firstName="Boris", lastName="Harrison")

    assert person.age is UNDEFINED
    assert person.birthday is UNDEFINED

    person.age = 53
    person.birthday = birthday

    assert person.age == 53
    assert person.birthday == birthday


def test_model_is_iterable(PersonModel):
    person = PersonModel(firstName="Boris", lastName="Harrison")

    for field, value in person:
        assert value == getattr(person, field)


def test_models_with_same_data_are_equal_but_not_identical(PersonModel):
    person_1 = PersonModel(firstName="Boris", lastName="Harrison", dogs=["Fluffy", "Cerberus"])
    person_2 = PersonModel(firstName="Boris", lastName="Harrison", dogs=["Fluffy", "Cerberus"])

    assert person_1 == person_2
    assert person_1 is not person_2


def test_models_with_different_data_are_not_equal(PersonModel):
    person_1 = PersonModel(firstName="Boris", lastName="Harrison", dogs=["Fluffy", "Cerberus"])
    person_2 = PersonModel(firstName="Boris", lastName="Harrison", dogs=["Fluffy"])

    assert person_1 != person_2
