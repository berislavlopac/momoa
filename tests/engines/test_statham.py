"""Tests for StathamEngine: contract compliance and statham-specific behaviour."""

import pytest

from momoa.engines.statham import StathamEngine
from momoa.model import Model
from tests.engines.contract import run_contract_tests


class TestStathamEngineContract:
    def test_contract(self, statham_engine, person_schema):
        run_contract_tests(statham_engine, person_schema)


class TestStathamEngineSpecific:
    def test_output_format(self, statham_engine):
        assert statham_engine.output_format == "statham"

    def test_models_are_model_subclasses(self, statham_engine, person_schema):
        result = statham_engine.compile(person_schema)
        for cls in result.models:
            assert issubclass(cls, Model)

    def test_custom_model_factory(self, person_schema):
        def factory(schema_class):
            return type(
                schema_class.__name__ + "Custom", (Model,), {"_schema_class": schema_class}
            )

        engine = StathamEngine(model_factory=factory)
        result = engine.compile(person_schema)
        assert result.model.__name__.endswith("Custom")

    def test_invalid_schema_raises_schema_error(self, statham_engine):
        from momoa.exceptions import SchemaError

        bad_schema = {
            "title": "Bad",
            "type": "object",
            "properties": {"x": {"type": "blabla"}},
        }
        with pytest.raises(SchemaError):
            statham_engine.compile(bad_schema)
