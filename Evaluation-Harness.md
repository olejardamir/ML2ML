# UML_OS Evaluation Harness Contract
**EQC Compliance:** Merged single-file EQC v1.1 Option A.

**Algorithm:** `UML_OS.Eval.Harness_v1`  
**Purpose (1 sentence):** Define deterministic safety/bias/robustness evaluation runs and evidence bundles linked to registry/deployment policy gates.  
**Spec Version:** `UML_OS.Eval.Harness_v1` | 2026-02-18 | Authors: Olejar Damir  
**Domain / Problem Class:** Evaluation governance and evidence generation.

---
## 1) Header & Global Semantics
### 0.0 Identity
- **Algorithm:** `UML_OS.Eval.Harness_v1`
- **Purpose (1 sentence):** Replayable evaluation evidence contract.
### 0.A Objective Semantics
- Minimize unsafe/unvetted deployments.
### 0.B Reproducibility Contract
- Replayable given `(eval_manifest_hash, dataset_snapshot_hash, determinism_tier)`.
### 0.C Numeric Policy
- Metrics in binary64 with explicit thresholds.
### 0.D Ordering and Tie-Break Policy
- Test case ordering deterministic by case_id.
### 0.E Parallel, Concurrency, and Reduction Policy
- Multi-rank evaluation aggregation deterministic.
### 0.F Environment and Dependency Policy
- Evaluation must declare determinism tier (`E0` or `E1`) and tolerance map.
### 0.G Operator Manifest
- `UML_OS.Eval.RunSuite_v1`
- `UML_OS.Eval.AggregateMetrics_v1`
- `UML_OS.Eval.BuildEvidenceBundle_v1`
- `UML_OS.Error.Emit_v1`
### 0.H Namespacing and Packaging
- `UML_OS.Eval.*`
### 0.I Outputs and Metric Schema
- Outputs: `(eval_report, evidence_bundle_ref)`
- Metrics: `safety_score`, `bias_score`, `robustness_score`
### 0.J Spec Lifecycle Governance
- evaluation metric semantics changes are MAJOR.
### 0.K Failure and Error Semantics
- abort on schema mismatch or missing evidence references.
### 0.L Input/Data Provenance
- evaluation must bind `dataset_snapshot_hash` and model version hash.

---
## 2) System Model
### I.A Persistent State
- eval suite definitions and threshold policies.
### I.B Inputs and Hyperparameters
- eval manifest, dataset snapshot, model artifact ref.
### I.C Constraints and Feasible Set
- evidence bundle required for policy-gated promotion.
### I.D Transient Variables
- per-case metrics and aggregated scores.
### I.E Invariants and Assertions
- evidence includes trace root and metrics digest.

### II.F Evidence Bundle (Normative)
- `eval_manifest_hash`
- `dataset_snapshot_hash`
- `metrics_digest`
- `trace_root_hash`
- `determinism_tier`
- `replay_token`

---
## 3) Initialization
1. Validate eval manifest and dataset snapshot.
2. Load model artifact and determinism profile.
3. Initialize evaluation run context.

---
## 4) Operator Manifest
- `UML_OS.Eval.RunSuite_v1`
- `UML_OS.Eval.AggregateMetrics_v1`
- `UML_OS.Eval.BuildEvidenceBundle_v1`
- `UML_OS.Error.Emit_v1`

---
## 5) Operator Definitions
**Operator:** `UML_OS.Eval.BuildEvidenceBundle_v1`  
**Category:** Governance  
**Signature:** `(eval_report, trace_ref, dataset_snapshot_ref -> evidence_bundle_ref)`  
**Purity class:** IO  
**Determinism:** deterministic  
**Definition:** builds content-addressed evidence bundle for downstream policy gates.

---
## 6) Procedure
```text
1. RunSuite_v1
2. AggregateMetrics_v1
3. BuildEvidenceBundle_v1
4. Return eval_report + evidence_bundle_ref
```

---
## 7) Trace & Metrics
### Logging rule
- evaluation events emit deterministic suite/case metrics.
### Trace schema
- `run_header`: eval_manifest_hash, dataset_snapshot_hash
- `iter`: case_id, metrics, status
- `run_end`: metrics_digest, evidence_bundle_ref
### Metric schema
- safety/bias/robustness metrics + threshold verdicts.
### Comparability guarantee
- comparable iff same manifest, snapshot, determinism tier, and thresholds.

---
## 8) Validation
#### VII.A Lint rules (mandatory)
- evidence completeness and replay linkage.
#### VII.B Operator test vectors (mandatory)
- deterministic evaluation on fixed datasets and tolerance-tier tests.
#### VII.C Golden traces (mandatory)
- golden evidence bundle digests.

---
## 9) Refactor & Equivalence
#### VIII.A Equivalence levels
- E0 for evidence bundle and pass/fail verdict on frozen inputs.
#### VIII.B Allowed refactor categories
- suite execution optimization preserving metrics/verdicts.
#### VIII.C Equivalence test procedure (mandatory)
- exact compare of metrics digest + verdict.

---
## 10) Checkpoint/Restore
### Checkpoint contents
- evaluation cursor and partial metrics state.
### Serialization
- deterministic CBOR.
### Restore semantics
- resumed evaluation yields identical evidence bundle for same inputs.
