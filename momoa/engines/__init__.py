"""Engine protocol and registry for Momoa model compilation."""

from collections.abc import Callable
from dataclasses import dataclass
from typing import Any, Protocol

from momoa.exceptions import SchemaError, UnknownEngineError


@dataclass
class EngineResult:
    """Result of compiling a schema spec into model classes."""

    models: tuple[type, ...]

    @property
    def model(self) -> type:
        """The primary (root) model class."""
        return self.models[-1]


class ModelEngine(Protocol):
    """Compiles a normalised schema spec into model classes."""

    @property
    def output_format(self) -> str:
        """Identifier: 'statham', 'pydantic', 'dataclass', etc."""
        ...

    def compile(self, spec: dict[str, Any], *, root_name: str | None = None) -> EngineResult:
        """Returns models built from the spec. Pure: same input -> equivalent output."""
        ...

    def context_labeller(self) -> Callable[[str], tuple[str, Any]] | None:
        """Returns a context_labeller for json_ref_dict.materialize, or None.

        Engines that need schema nodes labelled during URI materialisation (e.g.
        to derive names for anonymous nested objects) return a callable here.
        Engines that work from plain schema dicts return None.
        """
        ...


def _get_registered_engines() -> dict[str, "ModelEngine"]:
    from momoa.engines.pydantic import PydanticEngine
    from momoa.engines.statham import StathamEngine

    return {"statham": StathamEngine(), "pydantic": PydanticEngine()}


def resolve_engine(name: str) -> "ModelEngine":
    """Look up a registered engine by name, raising UnknownEngineError for unknown names."""
    engines = _get_registered_engines()
    if name not in engines:
        raise UnknownEngineError(name, ", ".join(sorted(engines)))
    return engines[name]
