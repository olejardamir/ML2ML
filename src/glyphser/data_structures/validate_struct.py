"""Minimal struct validation scaffolding (stub)."""
from __future__ import annotations

from typing import Any


def validate_trace_iter_record(record: dict[str, Any]) -> None:
    # Placeholder: validate required keys and types in future.
    if not isinstance(record, dict):
        raise TypeError("record must be a dict")


def validate_checkpoint_header(header: dict[str, Any]) -> None:
    # Placeholder: validate required keys and types in future.
    if not isinstance(header, dict):
        raise TypeError("header must be a dict")
