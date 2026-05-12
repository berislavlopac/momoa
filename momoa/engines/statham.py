"""Statham-based engine: wraps the existing JSON Schema Draft 6 implementation."""

from collections.abc import Callable
from copy import deepcopy
from typing import Any

from statham.schema.parser import parse
from statham.serializers.orderer import orderer
from statham.titles import title_labeller

from momoa.engines import EngineResult
from momoa.exceptions import SchemaParseError
from momoa.model import Model, ModelFactory


class StathamEngine:
    """Compiles JSON Schema (Draft 6) into Momoa Model subclasses via statham."""

    def __init__(self, model_factory: ModelFactory = Model.make_model) -> None:
        self._model_factory = model_factory

    @property
    def output_format(self) -> str:
        """Engine identifier."""
        return "statham"

    def context_labeller(self) -> Callable[[str], tuple[str, Any]]:
        """Returns statham's title_labeller for naming anonymous nested schemas."""
        return title_labeller()

    def compile(self, spec: dict[str, Any], *, root_name: str | None = None) -> EngineResult:
        """Compile a JSON Schema spec into Model subclasses."""
        title = spec.get("title", "<schema>")
        try:
            parsed = parse(deepcopy(spec))
        except KeyError as ex:
            raise SchemaParseError(title, ex) from ex
        models = tuple(map(self._model_factory, orderer(*parsed)))
        return EngineResult(models=models)
