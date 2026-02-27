#!/usr/bin/env python3
from __future__ import annotations

import hashlib
import json
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]


def sha256_hex(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def _enc_uint(major: int, n: int) -> bytes:
    assert n >= 0
    if n < 24:
        return bytes([(major << 5) | n])
    if n < 256:
        return bytes([(major << 5) | 24, n])
    if n < 65536:
        return bytes([(major << 5) | 25]) + n.to_bytes(2, "big")
    if n < 4294967296:
        return bytes([(major << 5) | 26]) + n.to_bytes(4, "big")
    return bytes([(major << 5) | 27]) + n.to_bytes(8, "big")


def cbor_encode(obj: Any) -> bytes:
    if obj is None:
        return b"\xf6"
    if obj is False:
        return b"\xf4"
    if obj is True:
        return b"\xf5"
    if isinstance(obj, int):
        if obj >= 0:
            return _enc_uint(0, obj)
        return _enc_uint(1, -1 - obj)
    if isinstance(obj, bytes):
        return _enc_uint(2, len(obj)) + obj
    if isinstance(obj, str):
        b = obj.encode("utf-8")
        return _enc_uint(3, len(b)) + b
    if isinstance(obj, (list, tuple)):
        out = [_enc_uint(4, len(obj))]
        for x in obj:
            out.append(cbor_encode(x))
        return b"".join(out)
    if isinstance(obj, dict):
        items = []
        for k, v in obj.items():
            kb = cbor_encode(k)
            vb = cbor_encode(v)
            items.append((kb, vb))
        items.sort(key=lambda kv: kv[0])
        out = [_enc_uint(5, len(items))]
        for kb, vb in items:
            out.append(kb)
            out.append(vb)
        return b"".join(out)
    raise TypeError(f"unsupported type: {type(obj)!r}")


def cbor_hash_preimage(domain: str, payload: Any) -> bytes:
    return cbor_encode([domain, payload])


def canonical_json_bytes(obj: Any) -> bytes:
    return json.dumps(obj, sort_keys=True, separators=(",", ":"), ensure_ascii=True).encode("utf-8")


def build_catalogs() -> dict[str, Any]:
    # Digest catalog entries use bytes32 values derived deterministically from labels.
    digest_labels = [
        "schema.request.minimal",
        "schema.response.minimal",
        "schema.trace.snippet",
        "schema.checkpoint.header",
        "schema.execution.certificate",
        "schema.vectors.catalog",
    ]
    digest_entries = []
    digest_map: dict[str, bytes] = {}
    for label in digest_labels:
        digest_value = hashlib.sha256(label.encode("utf-8")).digest()
        digest_map[label] = digest_value
        digest_entries.append(
            {
                "digest_label": label,
                "digest_value": digest_value,
                "algorithm": "sha256",
                "domain_tag": "glyphser_doc_phase",
            }
        )
    digest_entries.sort(key=lambda x: x["digest_label"])  # deterministic rule in spec
    digest_catalog = {
        "catalog_version": 1,
        "entries": digest_entries,
    }

    error_codes = {
        "catalog_version": 1,
        "entries": [
            {"code_id": "CONTRACT_VIOLATION", "severity": "ERROR"},
            {"code_id": "EVIDENCE_MISSING", "severity": "ERROR"},
            {"code_id": "SIGNATURE_MISMATCH", "severity": "ERROR"},
            {"code_id": "RELEASE_BLOCKED", "severity": "ERROR"},
            {"code_id": "CATALOG_HASH_MISMATCH", "severity": "ERROR"},
        ],
    }

    capability_catalog = {
        "catalog_version": 1,
        "capabilities": [
            "CAP_TRACE_WRITE",
            "CAP_CHECKPOINT_WRITE",
            "CAP_CERTIFICATE_WRITE",
            "CAP_REPLAY_COMPARE",
            "CAP_REGISTRY_VALIDATE",
        ],
    }

    schema_catalog = {
        "catalog_version": 1,
        "entries": [
            {
                "schema_id": "schema.request.minimal",
                "schema_digest": digest_map["schema.request.minimal"],
            },
            {
                "schema_id": "schema.response.minimal",
                "schema_digest": digest_map["schema.response.minimal"],
            },
            {
                "schema_id": "schema.trace.snippet",
                "schema_digest": digest_map["schema.trace.snippet"],
            },
            {
                "schema_id": "schema.checkpoint.header",
                "schema_digest": digest_map["schema.checkpoint.header"],
            },
            {
                "schema_id": "schema.execution.certificate",
                "schema_digest": digest_map["schema.execution.certificate"],
            },
            {
                "schema_id": "schema.vectors.catalog",
                "schema_digest": digest_map["schema.vectors.catalog"],
            },
        ],
    }

    return {
        "digest_catalog": digest_catalog,
        "error_codes": error_codes,
        "capability_catalog": capability_catalog,
        "schema_catalog": schema_catalog,
        "digest_map": digest_map,
    }


def compute_signature_digest(
    operator_id: str,
    version: str,
    method: str,
    request_digest: bytes,
    response_digest: bytes,
    side_effects: list[str],
    allowed_error_codes: list[str],
) -> bytes:
    preimage = [
        "sig",
        operator_id,
        version,
        method,
        request_digest,
        response_digest,
        sorted(side_effects),
        sorted(allowed_error_codes),
    ]
    return hashlib.sha256(cbor_encode(preimage)).digest()


def build_operator_registry(digest_map: dict[str, bytes]) -> dict[str, Any]:
    req = digest_map["schema.request.minimal"]
    resp = digest_map["schema.response.minimal"]

    records = []
    entries = [
        {
            "operator_id": "Glyphser.Data.NextBatch",
            "version": "v2",
            "method": "CALL",
            "surface": "SYSCALL",
            "request_schema_digest": "sha256:schema.request.minimal",
            "response_schema_digest": "sha256:schema.response.minimal",
            "side_effects": ["ADVANCES_CURSOR", "ADVANCES_RNG"],
            "allowed_error_codes": ["CONTRACT_VIOLATION"],
            "purity_class": "STATEFUL",
            "required_capabilities": ["CAP_TRACE_WRITE"],
            "idempotent": False,
            "rng_usage": "PHILOX4x32_10",
            "determinism_class": "DETERMINISTIC",
            "owner_team": "ml-core",
            "deprecated": False,
        },
        {
            "operator_id": "Glyphser.Registry.ValidateOperatorRegistry",
            "version": "v1",
            "method": "CALL",
            "surface": "SYSCALL",
            "request_schema_digest": "sha256:schema.request.minimal",
            "response_schema_digest": "sha256:schema.response.minimal",
            "side_effects": [],
            "allowed_error_codes": ["CATALOG_HASH_MISMATCH", "CONTRACT_VIOLATION"],
            "purity_class": "PURE",
            "required_capabilities": ["CAP_REGISTRY_VALIDATE"],
            "idempotent": True,
            "rng_usage": "NONE",
            "determinism_class": "DETERMINISTIC",
            "owner_team": "governance",
            "deprecated": False,
        },
    ]

    for e in entries:
        sig = compute_signature_digest(
            e["operator_id"],
            e["version"],
            e["method"],
            req,
            resp,
            e["side_effects"],
            e["allowed_error_codes"],
        )
        e2 = dict(e)
        e2["signature_digest"] = sig
        e2["allowed_error_codes"] = sorted(e2["allowed_error_codes"])
        e2["required_capabilities"] = sorted(e2["required_capabilities"])
        e2["side_effects"] = sorted(e2["side_effects"])
        records.append(e2)

    def version_num(v: str) -> int:
        return int(v[1:])

    records.sort(key=lambda r: (r["operator_id"], version_num(r["version"])))

    return {
        "registry_schema_version": 1,
        "operator_records": records,
    }


def build_vectors_catalog(digest_map: dict[str, bytes]) -> dict[str, Any]:
    vectors = {
        "catalog_version": "v1",
        "operators": {
            "Glyphser.Data.NextBatch": [
                {
                    "vector_id": "vector_nextbatch_001",
                    "input_digest": "sha256:schema.request.minimal",
                    "expected_output_digest": "sha256:schema.response.minimal",
                    "determinism_class": "E0",
                    "signature_digest": "sha256:schema.vectors.catalog",
                    "notes": "minimal deterministic batch sampling fixture",
                }
            ],
            "Glyphser.Registry.ValidateOperatorRegistry": [
                {
                    "vector_id": "vector_registry_validate_001",
                    "input_digest": "sha256:schema.request.minimal",
                    "expected_output_digest": "sha256:schema.response.minimal",
                    "expected_error_code": "CONTRACT_VIOLATION",
                    "determinism_class": "E0",
                    "signature_digest": "sha256:schema.vectors.catalog",
                    "notes": "negative-path schema violation fixture",
                }
            ],
        },
    }
    return vectors


def write_bytes(path: Path, data: bytes) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(data)


def write_text(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")


def materialize() -> None:
    contracts_dir = ROOT / "contracts"
    fixtures_dir = ROOT / "fixtures" / "hello-core"
    goldens_dir = ROOT / "goldens" / "hello-core"
    vectors_dir = ROOT / "vectors" / "hello-core"

    catalogs = build_catalogs()
    digest_catalog = catalogs["digest_catalog"]
    error_codes = catalogs["error_codes"]
    capability_catalog = catalogs["capability_catalog"]
    schema_catalog = catalogs["schema_catalog"]
    digest_map = catalogs["digest_map"]

    operator_registry = build_operator_registry(digest_map)
    vectors_catalog = build_vectors_catalog(digest_map)

    blobs: dict[str, bytes] = {
        "digest_catalog.cbor": cbor_encode(digest_catalog),
        "error_codes.cbor": cbor_encode(error_codes),
        "capability_catalog.cbor": cbor_encode(capability_catalog),
        "schema_catalog.cbor": cbor_encode(schema_catalog),
        "operator_registry.cbor": cbor_encode(operator_registry),
        "vectors_catalog.cbor": cbor_encode(vectors_catalog),
    }

    hash_manifest = {}
    for name, blob in blobs.items():
        write_bytes(contracts_dir / name, blob)
        hash_manifest[name] = {
            "sha256": sha256_hex(blob),
            "size_bytes": len(blob),
        }

    # Compute root hash per Operator-Registry-Schema II.G
    op_root_preimage = cbor_encode([
        "operator_registry",
        operator_registry["registry_schema_version"],
        operator_registry["operator_records"],
    ])
    operator_registry_root_hash = sha256_hex(op_root_preimage)

    digest_entries_sorted = sorted(digest_catalog["entries"], key=lambda x: x["digest_label"])
    digest_catalog_hash = sha256_hex(cbor_encode(["digest_catalog", digest_catalog["catalog_version"], digest_entries_sorted]))

    vectors_catalog_hash = sha256_hex(cbor_encode(vectors_catalog))

    catalog_manifest = {
        "manifest_version": "doc-artifacts-v1",
        "canonical_profile": "CanonicalSerialization",
        "artifacts": hash_manifest,
        "derived_identities": {
            "operator_registry_root_hash": operator_registry_root_hash,
            "digest_catalog_hash": digest_catalog_hash,
            "vectors_catalog_hash": vectors_catalog_hash,
        },
    }
    write_text(contracts_dir / "catalog-manifest.json", json.dumps(catalog_manifest, indent=2, sort_keys=True) + "\n")

    # Fixture materialization
    src_manifest = ROOT / "docs" / "examples" / "hello-core" / "manifest.core.yaml"
    manifest_text = src_manifest.read_text(encoding="utf-8")
    write_text(fixtures_dir / "manifest.core.yaml", manifest_text)

    dataset_rows = [
        {"x": [0.0, 1.0, 0.0, 1.0], "y": 1.0},
        {"x": [1.0, 0.0, 1.0, 0.0], "y": 1.0},
        {"x": [1.0, 1.0, 0.0, 0.0], "y": 2.0},
    ]
    dataset_jsonl = "\n".join(json.dumps(row, sort_keys=True, separators=(",", ":")) for row in dataset_rows) + "\n"
    write_text(fixtures_dir / "tiny_synth_dataset.jsonl", dataset_jsonl)

    model_ir = {
        "ir_version": "v1",
        "graph": [
            {"node_id": "n1", "op": "MatMul", "inputs": ["x", "w"], "outputs": ["z1"]},
            {"node_id": "n2", "op": "Add", "inputs": ["z1", "b"], "outputs": ["y_hat"]},
            {"node_id": "n3", "op": "MSE", "inputs": ["y_hat", "y"], "outputs": ["loss"]},
        ],
    }
    write_text(fixtures_dir / "model_ir.json", json.dumps(model_ir, indent=2, sort_keys=True) + "\n")

    fixture_files = [
        fixtures_dir / "manifest.core.yaml",
        fixtures_dir / "tiny_synth_dataset.jsonl",
        fixtures_dir / "model_ir.json",
    ]
    fixture_manifest = {
        "fixture_set_id": "hello-core-fixtures-v1",
        "files": [
            {
                "path": str(p.relative_to(ROOT)).replace("\\", "/"),
                "sha256": sha256_hex(p.read_bytes()),
                "size_bytes": p.stat().st_size,
            }
            for p in fixture_files
        ],
    }
    write_text(fixtures_dir / "fixture-manifest.json", json.dumps(fixture_manifest, indent=2, sort_keys=True) + "\n")

    # Golden artifacts (doc-phase pinned values)
    trace_snippet = {
        "run_id": "hello-core-run-v1",
        "records": [
            {"step": 1, "operator_id": "Glyphser.Data.NextBatch", "event_hash": "9f4af21c3f1f6f0f6b95c6154312ecfda4f0a77e8626ced6f1938ad4b3f6f2a0"},
            {"step": 1, "operator_id": "Glyphser.Model.ModelIR_Executor", "event_hash": "b61d2e4de12799d86659895b3ee2ef9b4f14f183de6a2728e6017b1979b7e6c5"},
        ],
    }
    checkpoint_header = {
        "checkpoint_id": "hello-core-ckpt-v1",
        "global_step": 1,
        "manifest_hash": sha256_hex((fixtures_dir / "manifest.core.yaml").read_bytes()),
        "operator_registry_root_hash": operator_registry_root_hash,
    }
    execution_certificate = {
        "certificate_id": "hello-core-cert-v1",
        "run_id": "hello-core-run-v1",
        "trace_final_hash": "2f2f3b84dd88b5a5924abfe6051b7f2e0d669bcdb42bb4ff6d9f38eb43f57d9a",
        "checkpoint_hash": sha256_hex(canonical_json_bytes(checkpoint_header)),
        "operator_contracts_root_hash": operator_registry_root_hash,
        "policy_gate_hash": "5a5e629c6f1bece7ef8d0b20f8ee99153f7eda4e2ec03eaa7b65db06d20fca67",
    }

    write_text(goldens_dir / "trace_snippet.json", json.dumps(trace_snippet, indent=2, sort_keys=True) + "\n")
    write_text(goldens_dir / "checkpoint_header.json", json.dumps(checkpoint_header, indent=2, sort_keys=True) + "\n")
    write_text(goldens_dir / "execution_certificate.json", json.dumps(execution_certificate, indent=2, sort_keys=True) + "\n")

    # keep synchronized with docs/examples golden identities
    hello_golden = json.loads((ROOT / "docs" / "examples" / "hello-core" / "hello-core-golden.json").read_text(encoding="utf-8"))
    write_text(goldens_dir / "golden-identities.json", json.dumps(hello_golden, indent=2, sort_keys=True) + "\n")

    golden_files = [
        goldens_dir / "trace_snippet.json",
        goldens_dir / "checkpoint_header.json",
        goldens_dir / "execution_certificate.json",
        goldens_dir / "golden-identities.json",
    ]
    golden_manifest = {
        "golden_set_id": "hello-core-goldens-v1",
        "files": [
            {
                "path": str(p.relative_to(ROOT)).replace("\\", "/"),
                "sha256": sha256_hex(p.read_bytes()),
                "size_bytes": p.stat().st_size,
            }
            for p in golden_files
        ],
    }
    write_text(goldens_dir / "golden-manifest.json", json.dumps(golden_manifest, indent=2, sort_keys=True) + "\n")

    # Vector fixtures
    vector_rows = {
        "vector_set_id": "hello-core-vectors-v1",
        "vectors": [
            {
                "vector_id": "vector_nextbatch_001",
                "operator_id": "Glyphser.Data.NextBatch",
                "input_ref": "fixtures/hello-core/tiny_synth_dataset.jsonl",
                "expected_ref": "goldens/hello-core/trace_snippet.json",
            },
            {
                "vector_id": "vector_registry_validate_001",
                "operator_id": "Glyphser.Registry.ValidateOperatorRegistry",
                "input_ref": "contracts/operator_registry.cbor",
                "expected_error_code": "CONTRACT_VIOLATION",
            },
        ],
    }
    write_text(vectors_dir / "vectors.json", json.dumps(vector_rows, indent=2, sort_keys=True) + "\n")
    vectors_manifest = {
        "vectors_set_id": "hello-core-vectors-v1",
        "vectors_file": "vectors/hello-core/vectors.json",
        "vectors_file_sha256": sha256_hex((vectors_dir / "vectors.json").read_bytes()),
        "vectors_catalog_hash": vectors_catalog_hash,
    }
    write_text(vectors_dir / "vectors-manifest.json", json.dumps(vectors_manifest, indent=2, sort_keys=True) + "\n")

    print("Materialized deterministic doc-phase artifacts:")
    print(f"  - contracts: {contracts_dir}")
    print(f"  - fixtures:  {fixtures_dir}")
    print(f"  - goldens:   {goldens_dir}")
    print(f"  - vectors:   {vectors_dir}")
    print("Derived identities:")
    print(f"  operator_registry_root_hash={operator_registry_root_hash}")
    print(f"  digest_catalog_hash={digest_catalog_hash}")
    print(f"  vectors_catalog_hash={vectors_catalog_hash}")


if __name__ == "__main__":
    materialize()
