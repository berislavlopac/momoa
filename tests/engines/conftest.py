import json
from pathlib import Path

import pytest

from momoa.engines import resolve_engine
from momoa.engines.pydantic import PydanticEngine
from momoa.engines.statham import StathamEngine


@pytest.fixture
def fixtures_dir() -> Path:
    return Path(__file__).parent.parent / "fixtures" / "schemas"


@pytest.fixture
def person_schema(fixtures_dir: Path) -> dict:
    return json.loads((fixtures_dir / "person.json").read_text())


@pytest.fixture(params=["statham", "pydantic"])
def any_engine(request):
    return resolve_engine(request.param)


@pytest.fixture
def statham_engine() -> StathamEngine:
    return StathamEngine()


@pytest.fixture
def pydantic_engine() -> PydanticEngine:
    return PydanticEngine()
