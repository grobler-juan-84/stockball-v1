"""Infrastructure tests for MoneyBall DB configuration and package layout."""

from __future__ import annotations

import pytest

from moneyball import __version__
from moneyball.config import ConfigurationError, clear_settings_cache, get_settings


def test_package_imports() -> None:
    assert __version__ == "0.1.0"


def test_missing_database_url_fails_clearly(monkeypatch: pytest.MonkeyPatch) -> None:
    clear_settings_cache()
    monkeypatch.delenv("DATABASE_URL", raising=False)
    # Prevent a local .env from supplying DATABASE_URL during this test.
    monkeypatch.setattr(
        "moneyball.config._load_dotenv",
        lambda: None,
    )

    with pytest.raises(ConfigurationError, match="DATABASE_URL is not set"):
        get_settings()


def test_settings_load_from_environment(monkeypatch: pytest.MonkeyPatch) -> None:
    clear_settings_cache()
    monkeypatch.setattr("moneyball.config._load_dotenv", lambda: None)
    monkeypatch.setenv(
        "DATABASE_URL",
        "postgresql+psycopg://postgres:password@localhost:5432/moneyball",
    )

    settings = get_settings()
    assert settings.database_url.endswith("/moneyball")
    assert settings.data_raw_dir.name == "raw"
    assert settings.data_processed_dir.name == "processed"

    clear_settings_cache()
