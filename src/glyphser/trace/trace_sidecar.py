"""Deterministic trace writer and hash helper (minimal)."""
from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any, Dict, Iterable

from src.glyphser.serialization.canonical_cbor import encode_canonical


def compute_trace_hash(records: Iterable[Dict[str, Any]]) -> str:
    data = [r for r in records]
    preimage = ["trace_records", data]
    return hashlib.sha256(encode_canonical(preimage)).hexdigest()


def write_trace(records: Iterable[Dict[str, Any]], path: Path) -> str:
    data = [r for r in records]
    path.parent.mkdir(parents=True, exist_ok=True)
    text = json.dumps(data, sort_keys=True, separators=(",", ":"), ensure_ascii=True)
    path.write_text(text + "\n", encoding="utf-8")
    return compute_trace_hash(data)
