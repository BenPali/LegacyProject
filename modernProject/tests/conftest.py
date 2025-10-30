import sys
import tempfile
import shutil
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).parent.parent))

@pytest.fixture
def temp_dir():
    tmpdir = tempfile.mkdtemp()
    yield tmpdir
    shutil.rmtree(tmpdir, ignore_errors=True)

@pytest.fixture
def sample_base_path(temp_dir):
    base_path = Path(temp_dir) / "test_base"
    base_path.mkdir()
    return str(base_path)

@pytest.fixture
def mock_config():
    from lib.config import Config
    return Config(
        command="test",
        env={},
        base_env={},
        allowed_titles=[],
        friend=False,
        wizard=False,
        is_printed_by_template=False,
        cancel_links=False,
    )
