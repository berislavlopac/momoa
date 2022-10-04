"""Exceptions for working with JSONSchema specifications."""


class SchemaError(Exception):
    """Generic JSONSchema error."""


class SchemaParseError(SchemaError):
    """Error while parsing JSONSchema."""


class DataValidationError(SchemaError):
    """Error on validation of data."""
