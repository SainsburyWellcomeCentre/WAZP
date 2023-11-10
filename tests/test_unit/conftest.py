from pathlib import Path

import pytest

from wazp.datasets import get_sample_project


@pytest.fixture()
def sample_project() -> Path:
    """Get the sample project for testing."""
    return get_sample_project("jewel-wasp", "short-clips_compressed", progressbar=True)
