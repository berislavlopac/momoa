"""Tests for the engine registry: resolve_engine and UnknownEngineError."""

import pytest

from momoa.engines import resolve_engine
from momoa.engines.pydantic import PydanticEngine
from momoa.engines.statham import StathamEngine
from momoa.exceptions import UnknownEngineError


def test_resolve_engine_statham():
    engine = resolve_engine("statham")
    assert isinstance(engine, StathamEngine)


def test_resolve_engine_pydantic():
    engine = resolve_engine("pydantic")
    assert isinstance(engine, PydanticEngine)


def test_resolve_engine_unknown_raises():
    with pytest.raises(UnknownEngineError):
        resolve_engine("nonexistent")
