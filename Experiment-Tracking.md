# UML_OS Experiment Tracking Contract
**EQC Compliance:** Merged single-file EQC v1.1 Option A.

**Algorithm:** `UML_OS.Tracking.ExperimentTracking_v1`  
**Purpose (1 sentence):** Define deterministic run/metric/artifact tracking APIs and storage contracts for lifecycle observability.  
**Spec Version:** `UML_OS.Tracking.ExperimentTracking_v1` | 2026-02-18 | Authors: Olejar Damir  
**Domain / Problem Class:** Experiment tracking and artifact lifecycle.

---
## 1) Header & Global Semantics
### 0.0 Identity
- **Algorithm:** `UML_OS.Tracking.ExperimentTracking_v1`
- **Purpose (1 sentence):** Deterministic experiment/run tracking.
- **Spec Version:** `UML_OS.Tracking.ExperimentTracking_v1` | 2026-02-18 | Authors: Olejar Damir
- **Domain / Problem Class:** Tracking and artifacts.
### 0.A Objective Semantics
- Optimization sense: `MINIMIZE`
- Objective type: `Scalar`
- Primary comparison rule: deterministic total preorder over declared primary metric tuple with `EPS_EQ` tie handling.
- Invalid objective policy: `NaN/Inf` ranked as worst-case and handled deterministically per 0.K.
- Minimize tracking ambiguity and non-replayable run metadata.
### 0.B Reproducibility Contract
- Replayable given `(run_id, tracking_store_hash, artifact_index_hash)`.
### 0.C Numeric Policy
- Metric values in binary64; identifiers exact.
### 0.D Ordering and Tie-Break Policy
- Events ordered by `(t, operator_seq, rank)`.
### 0.E Parallel, Concurrency, and Reduction Policy
- Concurrent metric writes merged deterministically.
### 0.F Environment and Dependency Policy
- Tracking backend must expose content-addressable artifact APIs.
### 0.G Operator Manifest
- `UML_OS.Tracking.RunCreate_v1`
- `UML_OS.Tracking.RunStart_v1`
- `UML_OS.Tracking.RunEnd_v1`
- `UML_OS.Tracking.MetricLog_v1`
- `UML_OS.Tracking.ArtifactPut_v1`
- `UML_OS.Tracking.ArtifactGet_v1`
- `UML_OS.Tracking.ArtifactList_v1`
- `UML_OS.Tracking.ArtifactTombstone_v1`
- `UML_OS.Error.Emit_v1`
### 0.H Namespacing and Packaging
- `UML_OS.Tracking.*` operators.
### 0.I Outputs and Metric Schema
- Outputs: `(tracking_report, artifact_index_hash)`
- Metrics: `run_count`, `metric_events`, `artifact_count`
- Completion status: `success | failed`
### 0.J Spec Lifecycle Governance
- API/signature changes require MAJOR.
### 0.K Failure and Error Semantics
- Deterministic failures on invalid run/artifact operations.
### 0.L Input/Data Provenance
- Every artifact must include content hash and tenant scope.

---
### 0.Z EQC Mandatory Declarations Addendum
- Seed space: `seed ∈ {0..2^64-1}` when stochastic sub-operators are used.
- PRNG family: `Philox4x32-10` for declared stochastic operators.
- Randomness locality: all sampling occurs only inside declared stochastic operators in section 5.
- Replay guarantee: replayable given (seed, PRNG family, numeric policy, ordering policy, parallel policy, environment policy).
- Replay token: deterministic per-run token contribution is defined and included in trace records.
- Floating-point format: IEEE-754 binary64 unless explicitly declared otherwise.
- Rounding mode: round-to-nearest ties-to-even unless explicitly overridden.
- Fast-math policy: forbidden for critical checks and verdict paths.
- Named tolerances: `EPS_EQ=1e-10`, `EPS_DENOM=1e-12`, and domain-specific thresholds as declared.
- NaN/Inf policy: invalid values trigger deterministic failure handling per 0.K.
- Normalized exponentials: stable log-sum-exp required when exponential paths are used (otherwise N/A).
- Overflow/underflow: explicit abort or clamp behavior must be declared (this contract uses deterministic abort on critical paths).
- Approx-equality: `a ≈ b` iff `|a-b| <= EPS_EQ` when tolerance checks apply.
- Transcendental functions policy: deterministic implementation requirements are inherited from consuming operators.
- Reference runtime class: CPU-only/GPU-enabled/distributed as required by the consuming workflow.
- Compiler/flags: deterministic compilation; fast-math disabled for critical paths.
- Dependency manifest: pinned runtime dependencies and versions are required.
- Determinism level: `BITWISE` for contract-critical outputs unless a stricter local declaration exists.
- Error trace rule: final failure record includes `t`, `failure_code`, `failure_operator`, replay token, and minimal diagnostics.
- Recovery policy: none unless explicitly declared; default is deterministic abort-only.

## 2) System Model
### I.A Persistent State
- run registry and artifact index.
### I.B Inputs and Hyperparameters
- `tenant_id`, `run_id`, metric payloads, artifact metadata.
### I.C Constraints and Feasible Set
- run_id unique per tenant/project.
### I.D Transient Variables
- write buffers and upload diagnostics.
### I.E Invariants and Assertions
- immutable run lineage; append-only metrics/events.

### II.F CAS Retention and GC Policy (Normative)
- Artifacts and event objects are content-addressed and immutable.
- Retention classes: `golden`, `certified_release`, `experimental`, `ephemeral`.
- Physical deletion is prohibited while object is reachable from active execution certificates or pinned model releases.
- GC must be deterministic mark/sweep over declared roots and emit hash-chained GC audit records.

### II.G Canonical Tracking Record Schemas (Normative)
- `RunRecord` (CBOR map):
  - `tenant_id:string`, `run_id:string`, `replay_token:bytes32`, `manifest_hash:bytes32`, `trace_root_hash:bytes32`, `checkpoint_hash:bytes32`, `execution_certificate_hash:bytes32`, `status:string`, `created_at:string`, `ended_at?:string`.
- `MetricRecord` (CBOR map):
  - `tenant_id:string`, `run_id:string`, `metric_name:string`, `metric_value:float64`, `metric_step:uint64`, `aggregation:enum(raw|sum|mean|min|max|quantile)`, `quantile_p?:float64`, `window_id?:string`, `recorded_at:string`.
- `ArtifactRecord` (CBOR map):
  - `tenant_id:string`, `run_id:string`, `artifact_id:string`, `artifact_digest:digest_ref`, `artifact_size_bytes:uint64`, `storage_locator:string`, `artifact_class:string`, `created_at:string`, `tombstoned_at?:string`.
- Record hash rule:
  - `record_hash = SHA-256(CBOR_CANONICAL(record_map))`.

### II.H Tracking Gate Binding (Normative)
- Any tracking record used by policy gates must be hash-addressed.
- If a gate decision depends on tracking evidence, the decision transcript must include the relevant `record_hash` values and bind them through `policy_gate_hash`.
- For regulated/confidential modes, retention rules must preserve all gate-referenced records until retention expiry.

---
## 3) Initialization
1. Initialize tracking store bindings.
2. Validate tenant/project namespace.
3. Initialize run/event streams.

---
## 4) Operator Manifest
- `UML_OS.Tracking.RunCreate_v1`
- `UML_OS.Tracking.RunStart_v1`
- `UML_OS.Tracking.RunEnd_v1`
- `UML_OS.Tracking.MetricLog_v1`
- `UML_OS.Tracking.ArtifactPut_v1`
- `UML_OS.Tracking.ArtifactGet_v1`
- `UML_OS.Tracking.ArtifactList_v1`
- `UML_OS.Tracking.ArtifactTombstone_v1`
- `UML_OS.Error.Emit_v1`

---
## 5) Operator Definitions
External operator reference: `UML_OS.Error.Emit_v1` is defined in `Error-Codes.md`.

**Operator:** `UML_OS.Tracking.RunCreate_v1`  
**Category:** IO  
**Signature:** `(tenant_id, run_manifest -> run_id)`  
**Purity class:** IO  
**Determinism:** deterministic  
**Definition:** creates immutable run metadata anchor.

**Operator:** `UML_OS.Tracking.MetricLog_v1`  
**Category:** IO  
**Signature:** `(run_id, metric_event -> ok)`  
**Purity class:** IO  
**Determinism:** deterministic  
**Definition:** appends typed metric event.

**Operator:** `UML_OS.Tracking.ArtifactPut_v1`  
**Category:** IO  
**Signature:** `(run_id, artifact_bytes, metadata -> artifact_id)`  
**Purity class:** IO  
**Determinism:** deterministic  
**Definition:** stores content-addressed artifact and updates index.

**Operator:** `UML_OS.Tracking.ArtifactTombstone_v1`
**Category:** IO
**Signature:** `(run_id, artifact_id, reason -> tombstone_id)`
**Purity class:** IO
**Determinism:** deterministic
**Definition:** appends immutable tombstone metadata; physical deletion is deferred to retention policy.

---
## 6) Procedure
```text
1. RunCreate_v1
2. RunStart_v1
3. MetricLog_v1 / ArtifactPut_v1 repeated
4. ArtifactTombstone_v1 optional
5. RunEnd_v1
6. Return tracking_report
```

---
## 7) Trace & Metrics
### Logging rule
- Tracking operations emit deterministic run/metric/artifact events.
### Trace schema
- `run_header`: tenant_id, run_id
- `iter`: event_type, key, status
- `run_end`: artifact_index_hash
### Metric schema
- `metric_events`, `artifact_count`
### Comparability guarantee
- Comparable iff schemas, run IDs, and content hashes are identical.

---
## 8) Validation
#### VII.A Lint rules (mandatory)
- signature-locked APIs, typed events, hash-addressed artifacts.
#### VII.B Operator test vectors (mandatory)
- create/start/end flow, invalid state transitions, artifact hash mismatch.
#### VII.C Golden traces (mandatory)
- golden run-tracking traces.

---
## 9) Refactor & Equivalence
#### VIII.A Equivalence levels
- E0 for run/artifact identifiers and trace outputs.
#### VIII.B Allowed refactor categories
- storage backend optimization preserving IDs and hashes.
#### VIII.C Equivalence test procedure (mandatory)
- exact compare of run metadata + artifact index hash.

---
## 10) Checkpoint/Restore
### Checkpoint contents
- run cursor and artifact index watermark.
### Serialization
- deterministic CBOR.
### Restore semantics
- resumed tracking yields identical IDs/order under same inputs.
