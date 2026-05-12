# Momoa

A library for definition, validation and serialisation of models based on JSON Schema specifications.

[![Documentation Status](https://readthedocs.org/projects/momoa/badge/?version=latest)](https://momoa.readthedocs.io/en/latest/?badge=latest)
[![Build Status](https://b11c.semaphoreci.com/badges/momoa/branches/main.svg?style=shields&key=3e80692d-ad00-401e-b445-75303b8f35d0)](https://b11c.semaphoreci.com/projects/momoa)

## Basic Usage

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

## Engine Selection

Momoa compiles schemas through a pluggable engine. The default is `StathamEngine`.
To use Pydantic v2 `BaseModel` subclasses instead, pass `engine=` explicitly:

```python
from momoa import Schema
from momoa.engines.pydantic import PydanticEngine

schema = Schema.from_file("path/to/schema.json", engine=PydanticEngine())
person = schema.deserialize({"firstName": "Alice", "lastName": "Smith"})
print(person.model_dump())  # standard Pydantic API also available
```

The active engine can also be set via the `MOMOA_DEFAULT_ENGINE` environment variable
(`statham` or `pydantic`), which is useful for switching without changing code.

## Compatibility

Momoa supports two engines with different JSON Schema draft coverage:

| Engine | Backend | JSON Schema drafts |
|---|---|---|
| `StathamEngine` (default) | [Statham](https://statham-schema.readthedocs.io) | Draft 6 |
| `PydanticEngine` | [datamodel-code-generator](https://docs.koudai-liling.me/datamodel-code-generator/) + Pydantic v2 | Draft 4 – 2020-12 |
