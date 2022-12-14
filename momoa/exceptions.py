"""Exceptions for working with JSON Schema specifications."""


class SchemaError(Exception):
    """Generic JSON Schema error."""


class SchemaParseError(SchemaError):
    """Error while parsing JSON Schema."""


class DataValidationError(SchemaError):
    """Error on validation of data."""
