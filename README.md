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

## Compatibility

For validating schemas Momoa depends on [Statham](https://statham-schema.readthedocs.io), which [supports](https://statham-schema.readthedocs.io/en/latest/compatibility.html) the [JSON Schema Draft 6 specification](https://json-schema.org/specification-links.html#draft-6).
