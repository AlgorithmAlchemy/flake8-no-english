# tests/conftest.py
import pytest
from flake8_only_english.checker import NonEnglishChecker

@pytest.fixture(autouse=True)
def reset_flags():
    NonEnglishChecker.nle_comments = True
    NonEnglishChecker.nle_strings = False
    NonEnglishChecker.nle001_enabled = True
    NonEnglishChecker.nle002_enabled = True