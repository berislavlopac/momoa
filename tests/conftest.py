import json
from pathlib import Path

import pytest


@pytest.fixture
def test_data_dir():
    return Path(__file__).parent / "test_data"


@pytest.fixture
def schema_text(test_data_dir):
    schema_path = test_data_dir / "schema.json"
    return schema_path.read_text()


@pytest.fixture
def schema_dict(schema_text):
    return json.loads(schema_text)
