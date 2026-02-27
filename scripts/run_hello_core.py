#!/usr/bin/env python3
from __future__ import annotations

import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

FIXTURE_MANIFEST = ROOT / "docs" / "examples" / "hello-core" / "manifest.core.yaml"
GOLDEN = ROOT / "docs" / "examples" / "hello-core" / "hello-core-golden.json"


def main() -> int:
    # NOTE: This is a stub aligned with docs/START-HERE.md.
    if not FIXTURE_MANIFEST.exists():
        print(f"missing fixture manifest: {FIXTURE_MANIFEST}")
        return 1
    if not GOLDEN.exists():
        print(f"missing golden file: {GOLDEN}")
        return 1

    golden = json.loads(GOLDEN.read_text(encoding="utf-8"))
    expected = {
        "trace_final_hash": golden.get("trace_final_hash"),
        "certificate_hash": golden.get("certificate_hash"),
        "interface_hash": golden.get("interface_hash"),
    }

    print("Glyphser hello-core: STUB")
    print(f"fixture_manifest: {FIXTURE_MANIFEST}")
    print("expected_identities:")
    for k, v in expected.items():
        print(f"  {k}: {v}")

    print("\nTODO:")
    print("- Execute minimal reference stack (WAL -> trace -> checkpoint -> certificate -> replay check)")
    print("- Compute deterministic identities and compare against expected")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
