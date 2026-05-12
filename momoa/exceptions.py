"""Exceptions for working with JSON Schema specifications."""


class SchemaError(Exception):
    """Generic JSON Schema error."""


class SchemaParseError(SchemaError):
    """Error while parsing JSON Schema."""

    def __init__(self, schema_name: str, error: Exception):
        super().__init__(f"Error parsing schema `{schema_name}`: {error}")


class SchemaCompileError(SchemaError):
    """Error while compiling a JSON Schema into model classes."""

    def __init__(self, schema_name: str, reason: str):
        super().__init__(f"Failed to compile schema `{schema_name}`: {reason}")


class UnknownEngineError(SchemaError):
    """Error when an unknown engine name is requested."""

    def __init__(self, name: str, valid: str):
        super().__init__(f"Unknown engine {name!r}. Valid engines: {valid}")


class DataValidationError(SchemaError):
    """Error on validation of data."""

    def __init__(self, obj, error: Exception):
        super().__init__(f"{type(obj).__name__} validation error: {error}")


class InvalidFieldError(SchemaError):
    """Error on invalid field."""

    def __init__(self, field_name: str):
        super().__init__(f"Invalid field '{field_name}'")
