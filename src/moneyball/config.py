"""Centralized environment configuration for MoneyBall DB."""

from __future__ import annotations

import os
from dataclasses import dataclass
from functools import lru_cache
from pathlib import Path

from dotenv import load_dotenv

# Repository root: src/moneyball/config.py → parents[2]
REPO_ROOT = Path(__file__).resolve().parents[2]


class ConfigurationError(RuntimeError):
    """Raised when required configuration is missing or invalid."""


@dataclass(frozen=True)
class Settings:
    """Application settings loaded from the environment."""

    database_url: str
    data_raw_dir: Path
    data_processed_dir: Path


def _load_dotenv() -> None:
    """Load `.env` then `.env.local` from the repository root if present."""
    load_dotenv(dotenv_path=REPO_ROOT / ".env", override=False)
    load_dotenv(dotenv_path=REPO_ROOT / ".env.local", override=True)


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    """
    Return cached settings.

    Raises ConfigurationError if DATABASE_URL is missing.
    """
    _load_dotenv()

    database_url = os.getenv("DATABASE_URL", "").strip()
    if not database_url:
        raise ConfigurationError(
            "DATABASE_URL is not set. "
            "Copy .env.example to .env and configure your PostgreSQL connection."
        )

    return Settings(
        database_url=database_url,
        data_raw_dir=REPO_ROOT / "data" / "raw",
        data_processed_dir=REPO_ROOT / "data" / "processed",
    )


def clear_settings_cache() -> None:
    """Clear cached settings (useful in tests)."""
    get_settings.cache_clear()
