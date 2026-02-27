#!/usr/bin/env python3
from __future__ import annotations

import json
import sys
from pathlib import Path

from src.glyphser.certificate.build import write_execution_certificate
from src.glyphser.checkpoint.write import save_checkpoint
from src.glyphser.data.next_batch import next_batch
from src.glyphser.model.model_ir_executor import execute
from src.glyphser.trace.trace_sidecar import compute_trace_hash, write_trace

ROOT = Path(__file__).resolve().parents[1]
FIXTURES = ROOT / "fixtures" / "hello-core"
GOLDEN = ROOT / "docs" / "examples" / "hello-core" / "hello-core-golden.json"


def _load_dataset(path: Path) -> list[dict]:
    rows = []
    for line in path.read_text(encoding="utf-8").splitlines():
        if not line.strip():
            continue
        rows.append(json.loads(line))
    return rows


def main() -> int:
    if not GOLDEN.exists():
        print(f"missing golden file: {GOLDEN}")
        return 1

    dataset_path = FIXTURES / "tiny_synth_dataset.jsonl"
    model_ir_path = FIXTURES / "model_ir.json"
    if not dataset_path.exists() or not model_ir_path.exists():
        print("missing fixture inputs in fixtures/hello-core")
        return 1

    dataset = _load_dataset(dataset_path)
    model_ir = json.loads(model_ir_path.read_text(encoding="utf-8"))

    cursor = 0
    batch, cursor = next_batch(dataset, cursor, batch_size=1)
    if not batch:
        print("empty batch")
        return 1

    inputs = batch[0]["x"]
    outputs = execute(model_ir, inputs)

    trace_records = [
        {
            "t": 0,
            "operator_id": "Glyphser.Model.Forward",
            "inputs": inputs,
            "outputs": outputs,
        }
    ]

    trace_path = FIXTURES / "trace.json"
    trace_hash = write_trace(trace_records, trace_path)

    checkpoint_state = {"theta": outputs, "step": 0}
    checkpoint_path = FIXTURES / "checkpoint.json"
    checkpoint_hash = save_checkpoint(checkpoint_state, checkpoint_path)

    evidence = {
        "trace_final_hash": trace_hash,
        "checkpoint_hash": checkpoint_hash,
    }
    certificate_path = FIXTURES / "execution_certificate.json"
    certificate_hash = write_execution_certificate(evidence, certificate_path)

    interface_hash = json.loads(
        (ROOT / "contracts" / "interface_hash.json").read_text(encoding="utf-8")
    )["interface_hash"]

    golden = json.loads(GOLDEN.read_text(encoding="utf-8"))
    expected = golden["expected_identities"]

    results = {
        "trace_final_hash": trace_hash,
        "certificate_hash": certificate_hash,
        "interface_hash": interface_hash,
    }

    print("Glyphser hello-core: RUN")
    print(json.dumps(results, indent=2, sort_keys=True))

    ok = True
    for key, expected_value in expected.items():
        actual_value = results.get(key)
        if actual_value != expected_value:
            print(f"MISMATCH {key}: expected={expected_value} got={actual_value}")
            ok = False

    return 0 if ok else 2


if __name__ == "__main__":
    raise SystemExit(main())
