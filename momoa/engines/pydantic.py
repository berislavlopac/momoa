"""Pydantic v2 engine: compiles JSON Schema into pydantic.BaseModel subclasses.

Uses datamodel-code-generator to handle the full JSON Schema → Pydantic mapping,
including $ref, $defs, nested objects, arrays, enums, and composition keywords.

Known limitation: dynamically generated models are not pickle-able. Use
model_dump() / model_validate() for cross-process serialisation instead of pickle.
"""

from typing import Any

from datamodel_code_generator import GenerateConfig
from datamodel_code_generator.dynamic import generate_dynamic_models
from pydantic import BaseModel

from momoa.engines import EngineResult
from momoa.exceptions import SchemaCompileError

_CONFIG = GenerateConfig(formatters=[])


class PydanticEngine:
    """Compiles JSON Schema into pydantic.BaseModel subclasses."""

    @property
    def output_format(self) -> str:
        """Engine identifier."""
        return "pydantic"

    def context_labeller(self) -> None:
        """No URI labelling needed; datamodel-code-generator handles naming itself."""
        return None

    def compile(self, spec: dict[str, Any], *, root_name: str | None = None) -> EngineResult:
        """Compile a JSON Schema spec into BaseModel subclasses with .serialize()."""
        title = spec.get("title", "<schema>")
        try:
            raw = generate_dynamic_models(spec, config=_CONFIG, cache_size=1024)
        except Exception as ex:
            raise SchemaCompileError(title, str(ex)) from ex

        base_models = [cls for cls in raw.values() if issubclass(cls, BaseModel)]
        if not base_models:
            raise SchemaCompileError(title, "produced no model classes")

        models = tuple(_with_serialize(cls) for cls in base_models)

        if root_name is not None:
            root_candidates = [m for m in models if m.__name__ == root_name]
            if not root_candidates:
                available = ", ".join(m.__name__ for m in models)
                raise SchemaCompileError(
                    title, f"no model named {root_name!r}; available: {available}"
                )
            # Put the named root model last so EngineResult.model returns it
            models = (*[m for m in models if m.__name__ != root_name], root_candidates[0])

        return EngineResult(models=models)


def _with_serialize(cls: type[BaseModel]) -> type[BaseModel]:
    """Return a subclass of cls that adds a .serialize() method."""

    def serialize(self) -> dict[str, Any]:
        return self.model_dump(mode="json", exclude_unset=True)

    return type(cls.__name__, (cls,), {"serialize": serialize})
