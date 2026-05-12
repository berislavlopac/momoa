"""Engine contract tests: every registered engine must pass these."""

from momoa.engines import EngineResult, ModelEngine


def run_contract_tests(engine: ModelEngine, person_schema: dict):
    """Run all contract tests for a given engine against the person schema."""
    _test_compile_returns_engine_result(engine, person_schema)
    _test_models_are_nonempty(engine, person_schema)
    _test_model_is_last(engine, person_schema)
    _test_model_instantiation(engine, person_schema)
    _test_serialize_returns_dict(engine, person_schema)
    _test_undefined_fields_absent_in_serialize(engine, person_schema)
    _test_roundtrip(engine, person_schema)


def _test_compile_returns_engine_result(engine: ModelEngine, schema: dict):
    result = engine.compile(schema)
    assert isinstance(result, EngineResult)


def _test_models_are_nonempty(engine: ModelEngine, schema: dict):
    result = engine.compile(schema)
    assert len(result.models) > 0


def _test_model_is_last(engine: ModelEngine, schema: dict):
    result = engine.compile(schema)
    assert result.model is result.models[-1]


def _test_model_instantiation(engine: ModelEngine, schema: dict):
    result = engine.compile(schema)
    model_cls = result.model
    instance = model_cls(firstName="Alice", lastName="Smith")
    assert instance is not None


def _test_serialize_returns_dict(engine: ModelEngine, schema: dict):
    result = engine.compile(schema)
    model_cls = result.model
    instance = model_cls(firstName="Alice", lastName="Smith")
    serialized = instance.serialize()
    assert isinstance(serialized, dict)


def _test_undefined_fields_absent_in_serialize(engine: ModelEngine, schema: dict):
    """Optional fields not provided must not appear in serialize() output."""
    result = engine.compile(schema)
    model_cls = result.model
    instance = model_cls(firstName="Alice", lastName="Smith")
    serialized = instance.serialize()
    assert "firstName" in serialized
    assert "lastName" in serialized
    assert "age" not in serialized
    assert "deceased" not in serialized


def _test_roundtrip(engine: ModelEngine, schema: dict):
    """deserialize → serialize → deserialize must preserve structural equality."""
    result = engine.compile(schema)
    model_cls = result.model

    data = {"firstName": "Alice", "lastName": "Smith", "age": 30}
    instance1 = model_cls(**data)
    serialized = instance1.serialize()
    instance2 = model_cls(**serialized)
    serialized2 = instance2.serialize()

    assert serialized == serialized2
    assert serialized["firstName"] == "Alice"
    assert serialized["lastName"] == "Smith"
    assert serialized["age"] == 30
