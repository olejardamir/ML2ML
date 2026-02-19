# UML_OS Local Replay Runbook
**EQC Compliance:** Merged single-file EQC v1.1 Option A.

**Algorithm:** `UML_OS.Implementation.LocalReplayRunbook_v1`  
**Purpose (1 sentence):** Define deterministic local replay execution steps for developers to reproduce and diagnose run divergence.  
**Spec Version:** `UML_OS.Implementation.LocalReplayRunbook_v1` | 2026-02-19 | Authors: Olejar Damir  
**Domain / Problem Class:** Developer replay operations.

---
## 1) Header & Global Semantics
### 0.0 Identity
- **Algorithm:** `UML_OS.Implementation.LocalReplayRunbook_v1`
- **Purpose (1 sentence):** Deterministic local replay workflow.
### 0.A Objective Semantics
- Optimization sense: `MINIMIZE`
- Objective type: `Scalar`
- Primary comparison rule: minimize replay divergence count.
### 0.B Reproducibility Contract
- replay requires identical `manifest_hash`, `replay_token`, `determinism_profile_hash`.
### 0.C Numeric Policy
- binary64 for replay checks and comparator metrics.
### 0.D Ordering and Tie-Break Policy
- process trace records in canonical `(t, rank, operator_seq)` order.
### 0.E Parallel, Concurrency, and Reduction Policy
- local replay runs single-process unless distributed replay profile is explicitly enabled.
### 0.F Environment and Dependency Policy
- lockfile-pinned local runtime required.
### 0.G Operator Manifest
- `UML_OS.Replay.LoadArtifacts_v1`
- `UML_OS.Replay.RunDeterministicReplay_v1`
- `UML_OS.Replay.CompareOutputs_v1`
- `UML_OS.Error.Emit_v1`
### 0.H Namespacing and Packaging
- all operators under `UML_OS.Replay.*`.
### 0.I Outputs and Metric Schema
- outputs: `(replay_report, divergence_report)`.
### 0.J Spec Lifecycle Governance
- comparator key changes are MAJOR.
### 0.K Failure and Error Semantics
- failures emit deterministic replay error record.
### 0.L Input/Data Provenance
- replay inputs are content-addressed artifacts from checkpoint/trace/certificate.

---
## 2) System Model
### I.A Persistent State
- replay cursor, divergence accumulator, diagnostics context.
### I.B Inputs and Hyperparameters
- run id, artifact paths, replay mode (`STRICT_E0` / `TOLERANT_E1`).
### I.C Constraints and Feasible Set
- artifacts must share same `replay_token`.
### I.D Transient Variables
- per-step comparison deltas.
### I.E Invariants and Assertions
- monotonic replay step progression.

---
## 3) Initialization
1. Load manifest/checkpoint/trace/certificate references.
2. Validate hash/link consistency.
3. Initialize replay comparator state.

---
## 4) Operator Manifest
- `UML_OS.Replay.LoadArtifacts_v1`
- `UML_OS.Replay.RunDeterministicReplay_v1`
- `UML_OS.Replay.CompareOutputs_v1`
- `UML_OS.Error.Emit_v1`

---
## 5) Operator Definitions
**Operator:** `UML_OS.Replay.LoadArtifacts_v1`  
**Signature:** `(artifact_refs -> replay_inputs)`  
**Purity class:** IO  
**Definition:** Loads and validates artifact hash links required for replay.

**Operator:** `UML_OS.Replay.CompareOutputs_v1`  
**Signature:** `(expected, observed, replay_mode -> diff)`  
**Purity class:** PURE  
**Definition:** Applies E0/E1 comparator rules and emits deterministic diff.

---
## 6) Procedure
```text
1. replay_inputs <- LoadArtifacts_v1(...)
2. observed <- RunDeterministicReplay_v1(replay_inputs)
3. diff <- CompareOutputs_v1(expected, observed, replay_mode)
4. if diff.has_divergence: Error.Emit_v1(REPLAY_DIVERGENCE)
5. return replay_report
```

---
## 7) Trace & Metrics
- Metrics: `divergence_count`, `first_divergence_t`, `max_abs_error`, `max_rel_error`.
- Trace includes replay mode and comparator profile hash.

---
## 8) Validation
- Golden replays for one E0 and one E1 profile.
- Fault-injected replay for deterministic divergence detection.

---
## 9) Refactor & Equivalence
- E0 for replay verdict and first divergence location.
- E1 allowed only for declared tolerant metrics.

---
## 10) Checkpoint/Restore
- Replay session checkpoint stores replay cursor and diff accumulator.
- Restore must resume with identical comparator output.
