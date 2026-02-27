"""Minimal API signature validation helpers."""
from __future__ import annotations

from typing import Any, Dict


def validate_api_signature(record: Dict[str, Any]) -> None:
    if not isinstance(record, dict):
        raise TypeError("record must be a dict")

    for key in ("operator_id", "version", "method", "surface"):
        if key not in record or not isinstance(record[key], str):
            raise ValueError(f"missing or invalid {key}")

    for key in ("request_schema_digest", "response_schema_digest"):
        if key not in record or not isinstance(record[key], str):
            raise ValueError(f"missing or invalid {key}")

    if "side_effects" in record and not isinstance(record["side_effects"], list):
        raise ValueError("side_effects must be a list")

    if "allowed_error_codes" in record and not isinstance(record["allowed_error_codes"], list):
        raise ValueError("allowed_error_codes must be a list")
