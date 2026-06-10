# Momoa

**Momoa** generates typed, self-validating Python classes from JSON Schema at runtime - no code generation.

[![Documentation Status](https://readthedocs.org/projects/momoa/badge/?version=latest)](https://momoa.readthedocs.io/en/latest/?badge=latest)
[![CI](https://github.com/berislavlopac/momoa/actions/workflows/ci.yml/badge.svg)](https://github.com/berislavlopac/momoa/actions/workflows/ci.yml)

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

## Engine Selection

Momoa compiles schemas through a pluggable engine. The default is `StathamEngine`,
which produces `StathamModel` subclasses and supports JSON Schema Draft 6.

To use Pydantic v2 `BaseModel` subclasses (with broader draft support), pass
`engine=` to any of the constructors:

```python
from momoa import Schema
from momoa.engines.pydantic import PydanticEngine

engine = PydanticEngine()

schema = Schema.from_file("/path/to/schema.json", engine=engine)
schema = Schema.from_uri("https://path.to/schema.json", engine=engine)
schema = Schema(schema_dict, engine=engine)
```

The active engine can also be set via the `MOMOA_DEFAULT_ENGINE` environment
variable (`statham` or `pydantic`) to switch without changing code.

## Model Instance

An instantiated Schema will contain a tuple of model classes based on the schemas in the specification document. The main model will also be available separately.

Model classes are constructed dynamically when the Schema is instantiated. An instance validates values on assignment and converts them to JSON Schema compliant types internally.

### StathamEngine

```python
>>> from momoa import Schema
>>> schema = Schema.from_uri("file:///path/to/schema.json")
>>> schema.models
(<class 'momoa.engines.statham.AddressModel'>, <class 'momoa.engines.statham.PersonModel'>)
>>> schema.model
<class 'momoa.engines.statham.PersonModel'>
```

```python
from datetime import datetime
from momoa import Schema
from momoa.engines.statham import UNDEFINED

schema = Schema.from_uri("file://path/to/schema.json")
PersonModel = schema.model

person = PersonModel(firstName="Boris", lastName="Harrison")

# Unset optional fields return UNDEFINED
assert person.age is UNDEFINED

# Fields can be set after instantiation
person.age = 53
person.birthday = datetime(1969, 11, 23)

assert person.age == 53
assert person.birthday == datetime(1969, 11, 23)
```

### PydanticEngine

```python
from momoa import Schema
from momoa.engines.pydantic import PydanticEngine

schema = Schema.from_uri("file://path/to/schema.json", engine=PydanticEngine())
PersonModel = schema.model  # a pydantic.BaseModel subclass

person = PersonModel(firstName="Boris", lastName="Harrison", age=53)

# Unset optional fields return None
assert person.birthday is None

# Pydantic's native API is also available
assert person.model_dump(exclude_unset=True) == {
    "firstName": "Boris",
    "lastName": "Harrison",
    "age": 53,
}
```

### Serialization and Deserialization

All engines expose a consistent `.serialize()` method on instances that returns a JSON-compatible dict with unset fields omitted, and `schema.deserialize()` to load data into a model instance.

```python
from momoa import Schema

schema = Schema.from_uri("file://path/to/schema.json")

# Deserialize from a dict or JSON string
result = schema.deserialize({"firstName": "Boris", "lastName": "Harrison", "age": 53})

assert result.firstName == "Boris"
assert result.age == 53

# Serialize back — only fields that were provided are included
serialized = result.serialize()
assert serialized["firstName"] == "Boris"
assert "birthday" not in serialized
```

The StathamEngine additionally converts between Python-native types and JSON Schema formats (e.g. `datetime` ↔ ISO 8601 strings):

```python
from datetime import datetime
from momoa import Schema
from momoa.engines.statham import UNDEFINED

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

## Compatibility

Momoa supports two engines with different JSON Schema draft coverage:

| Engine | Backend | JSON Schema drafts |
|---|---|---|
| `StathamEngine` (default) | [Statham](https://statham-schema.readthedocs.io) | Draft 6 |
| `PydanticEngine` | [datamodel-code-generator](https://docs.koudai-liling.me/datamodel-code-generator/) + Pydantic v2 | Draft 4 – 2020-12 |
