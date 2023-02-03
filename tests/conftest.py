import json
from pathlib import Path

import pytest


@pytest.fixture
def test_data_dir():
    return Path(__file__).parent / "test_data"


@pytest.fixture
def schema_file_path(test_data_dir):
    return test_data_dir / "schema.json"


@pytest.fixture
def schema_dict(schema_file_path):
    return json.loads(schema_file_path.read_text())
