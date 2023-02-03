"""Basic class to parse a schema and prepare the model class."""
from __future__ import annotations

import json
from copy import deepcopy
from functools import cached_property
from pathlib import Path
from typing import Any, Dict, Mapping, Sequence, Type, Union

from json_ref_dict import materialize, RefDict
from statham.schema.parser import parse
from statham.serializers.orderer import orderer
from statham.titles import title_labeller

from .exceptions import SchemaParseError
from .model import Model, ModelFactory


class Schema:
    """Basic class to parse the schema and prepare the model class."""

    def __init__(self, schema: Dict[str, Any], model_factory: ModelFactory = Model.make_model):
        """
        Constructs the Schema class instance.

        Arguments:
            schema: A Python dict representation of the JSONSchema specification.
            model_factory: A callable that creates a model subclass from a JSON Schema.
                           Can be used to customize Model creation.
        """
        self.schema_dict = schema
        self.title: str = self.schema_dict["title"]
        try:
            parsed = parse(deepcopy(self.schema_dict))
        except KeyError as ex:
            raise SchemaParseError(f"Error parsing schema `{self.title}`: {ex}") from ex
        else:
            self.models: Sequence[Type[Model]] = tuple(map(model_factory, orderer(*parsed)))

    @classmethod
    def from_uri(cls, input_uri: str) -> Schema:
        """
        Instantiates the Schema from a URI to the schema document.

        For local files use the `file://` scheme. This method also dereferences
        the internal `$ref` links.

        Arguments:
            input_uri: String representation of the URI to the schema.

        Returns:
            Schema instance.
        """
        return cls(materialize(RefDict.from_uri(input_uri), context_labeller=title_labeller()))

    @classmethod
    def from_file(cls, file_path: Union[Path, str]) -> Schema:
        """
        Helper to instantiate the Schema from a local file path.

        Note: This method will _not_ dereference any internal `$ref` links.

        Arguments:
            file_path: Either a simple string path or a `pathlib.Path` object.

        Returns:
            Schema instance.
        """
        return cls.from_uri(Path(file_path).absolute().as_uri())

    @cached_property
    def model(self) -> Type[Model]:
        """
        Retrieves the top model class of the schema.

        Returns:
            Model subclass.
        """
        return self.models[-1]

    def deserialize(self, raw_data: Union[Mapping[str, Any], str]) -> Model:
        """
        Converts raw data to the Model instance, validating it in the process.

        Arguments:
            raw_data: The raw data to deserialize. Can be either a JSON string
                or a preloaded Python mapping object.

        Returns:
            An instance of the Model class.
        """
        if isinstance(raw_data, str):
            raw_data = json.loads(raw_data)
        return self.model(**raw_data)  # type: ignore
