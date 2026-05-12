"""Basic class to parse a schema and prepare the model class."""

from collections.abc import Mapping, Sequence
from functools import cached_property
import json
import os
from pathlib import Path
from typing import Any

from json_ref_dict import RefDict, materialize

from momoa.engines import EngineResult, ModelEngine, resolve_engine
from momoa.exceptions import SchemaError, UnknownEngineError

_VALID_ENGINES = {"statham", "pydantic"}
_env_engine = os.environ.get("MOMOA_DEFAULT_ENGINE")
if _env_engine and _env_engine not in _VALID_ENGINES:
    raise UnknownEngineError(_env_engine, ", ".join(sorted(_VALID_ENGINES)))


class Schema:
    """Basic class to parse the schema and prepare the model class."""

    def __init__(
        self,
        schema: dict[str, Any],
        *,
        engine: ModelEngine | None = None,
    ):
        """
        Constructs the Schema class instance.

        Arguments:
            schema: A Python dict representation of the JSONSchema specification.
            engine: A ModelEngine instance to compile the schema. If None, uses the
                    engine specified by MOMOA_DEFAULT_ENGINE env var, or StathamEngine.
        """
        self.schema_dict = schema
        self.title: str = self.schema_dict.get("title", "")

        resolved_engine = self._resolve_engine(engine)
        result: EngineResult = resolved_engine.compile(schema)
        self.models: Sequence[type] = result.models

    @staticmethod
    def _resolve_engine(engine: ModelEngine | None) -> ModelEngine:
        if engine is not None:
            return engine
        if _env_engine:
            return resolve_engine(_env_engine)
        from momoa.engines.statham import StathamEngine

        return StathamEngine()

    @classmethod
    def from_uri(cls, input_uri: str, engine: ModelEngine | None = None) -> "Schema":
        """
        Instantiates the Schema from a URI to the schema document.

        For local files use the `file://` scheme. This method also dereferences
        the internal `$ref` links.

        Arguments:
            input_uri: String representation of the URI to the schema.
            engine: Optional ModelEngine to use for compilation.

        Returns:
            Schema instance.
        """
        resolved = cls._resolve_engine(engine)
        labeller = resolved.context_labeller()
        return cls(
            materialize(RefDict.from_uri(input_uri), context_labeller=labeller),
            engine=engine,
        )

    @classmethod
    def from_file(cls, file_path: Path | str, engine: ModelEngine | None = None) -> "Schema":
        """
        Helper to instantiate the Schema from a local file path.

        Note: This method will _not_ dereference any internal `$ref` links.

        Arguments:
            file_path: Either a simple string path or a `pathlib.Path` object.
            engine: Optional ModelEngine to use for compilation.

        Returns:
            Schema instance.
        """
        return cls.from_uri(Path(file_path).absolute().as_uri(), engine=engine)

    @cached_property
    def model(self) -> type:
        """
        Retrieves the top model class of the schema.

        Returns
            Model subclass.
        """
        return self.models[-1]

    def deserialize(self, raw_data: Mapping[str, Any] | str) -> Any:
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
