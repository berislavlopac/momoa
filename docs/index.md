# Momoa

**Momoa** is a library for definition, validation and serialization of Python data objects based on JSON Schema specifications.

[![Documentation Status](https://readthedocs.org/projects/momoa/badge/?version=latest)](https://momoa.readthedocs.io/en/latest/?badge=latest)
[![Build Status](https://b11c.semaphoreci.com/badges/momoa/branches/main.svg?style=shields&key=3e80692d-ad00-401e-b445-75303b8f35d0)](https://b11c.semaphoreci.com/projects/momoa)

## Schema Object

The recommended way to instantiate a JSON Schema spec - especially if the schema contains internal `$ref` references - is directly from the URI to the specification file.

```python
from momoa import Schema

schema_1 = Schema.from_uri("file://path/to/schema-1.json")
schema_2 = Schema.from_uri("https://path.to/schema-2.json")
```

If the specification is available as a local file, a helper method `from_file` can be used instead of constructing the URI manually. The method accepts the file path both as a string and as a `pathlib.Path` instance:

```python
from momoa import Schema
from pathlib import Path

schema_1 = Schema.from_file(Path("/path/to/schema-1.json"))
schema_2 = Schema.from_file("/path/to/schema-2.json")
```

Alternatively, spec can be instantiated from a pre-loaded Python dict, which assumes that any links have been dereferenced. For example, if the schema spec file is YAML instead of JSON:

```python
from momoa import Schema
from pathlib import Path
import yaml

schema_file = Path("path/to/schema.yaml")
schema_dict = yaml.safe_load(schema_file.read_text())

schema = Schema(schema_dict)
```

## Model Instance

An instantiated Schema will contain a tuple of model classes based on the schemas in the specification document. The main model will also be available separately.

```python
>>> from momoa import Schema
>>> schema = Schema.from_uri("file:///path/to/schema.json")
>>> schema.models
(<class 'momoa.model.AddressModel'>, <class 'momoa.model.PersonModel'>)
>>> schema.model
<class 'momoa.model.PersonModel'>
>>>
```

The model classes are constructed dynamically when the Schema is instantiated. An instance of a model subclass is a Python object which automatically validates values and converts them to JSON Schema compliant types internally.

```python
from datetime import datetime
from momoa import Schema
from momoa.model import UNDEFINED

schema = Schema.from_uri("file://path/to/schema.json")
PersonModel = schema.model

birthday = datetime(1969, 11, 23)
person = PersonModel(firstName="Boris", lastName="Harrison", birthday=birthday)

assert person.age is UNDEFINED
assert person.birthday is UNDEFINED

person.age = 53
person.birthday = datetime(1969, 11, 23)

assert person.age == 53
assert person.birthday == datetime(1969, 11, 23)
```

### Serialization and Deserialization

A model instance can be serialised into a JSON-compatible Python dict:

```python
from datetime import datetime
from momoa import Schema

schema = Schema.from_uri("file://path/to/schema.json")

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
```

Conversely, data can be deserialized from a JSON-formatted string or a Python dict directly into a Model instance:

```python
from momoa import Schema
from momoa.model import UNDEFINED

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

schema = Schema.from_uri("file://path/to/schema.json")
result = schema.deserialize(test_data)

assert type(result).__name__ == "PersonModel"
assert isinstance(result, schema.model)
assert result.firstName == "Boris"
assert result.lastName == "Harrison"
assert result.gender == "male"
assert not result.deceased
assert result.birthday is UNDEFINED
```
