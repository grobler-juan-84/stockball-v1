"""Data provider adapters.

Fetching stays isolated from transforms and database loading.
Concrete providers (e.g. tiingo, fred) will be added as needed.
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from pathlib import Path
from typing import Any


class BaseProvider(ABC):
    """Minimal interface for a data source adapter."""

    name: str

    @abstractmethod
    def fetch(self, **kwargs: Any) -> Path:
        """
        Fetch data from the remote source and write raw output under data/raw/.

        Returns the path to the written raw artifact.
        """
