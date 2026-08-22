"""Pipeline orchestration: fetch → clean → derive → validate → load."""

from __future__ import annotations

from abc import ABC, abstractmethod


class Pipeline(ABC):
    """
    Conceptual stages for a MoneyBall data pipeline.

    BUILD: full rebuild from source data.
    UPDATE: incremental fetch/load of missing or new data.
    """

    @abstractmethod
    def build(self) -> None:
        """Run a full build. Not implemented until schema and providers exist."""

    @abstractmethod
    def update(self) -> None:
        """Run an incremental update. Not implemented until providers exist."""
