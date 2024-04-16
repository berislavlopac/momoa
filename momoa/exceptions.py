"""Exceptions for working with JSON Schema specifications."""


class SchemaError(Exception):
    """Generic JSON Schema error."""


class SchemaParseError(SchemaError):
    """Error while parsing JSON Schema."""

    def __init__(self, schema_name: str, error: Exception):
        super().__init__(f"Error parsing schema `{schema_name}`: {error}")


class DataValidationError(SchemaError):
    """Error on validation of data."""

    def __init__(self, obj, error: Exception):
        super().__init__(f"{type(obj).__name__} validation error: {error}")


class InvalidFieldError(SchemaError):
    """Error on invalid field."""

    def __init__(self, field_name: str):
        super().__init__(f"Invalid field '{field_name}'")
