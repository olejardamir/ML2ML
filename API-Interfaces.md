# UML_OS API Interface Contract
**EQC Compliance:** Merged single-file EQC v1.1 Option A.

**Algorithm:** `UML_OS.Implementation.APIInterfaceContract_v1`  
**Purpose (1 sentence):** Define deterministic, typed, versioned callable interfaces for kernel and core operators.  
**Spec Version:** `UML_OS.Implementation.APIInterfaceContract_v1` | 2026-02-18 | Authors: Olejar Damir  
**Domain / Problem Class:** API contract specification and interoperability.

---

## 1) Header & Global Semantics

### 0.0 Identity
- **Algorithm:** `UML_OS.Implementation.APIInterfaceContract_v1`
- **Purpose (1 sentence):** Deterministic API interface contract.
- **Spec Version:** `UML_OS.Implementation.APIInterfaceContract_v1` | 2026-02-18 | Authors: Olejar Damir
- **Domain / Problem Class:** Typed API contracts.

### 0.A Objective Semantics
- Not an optimization algorithm.
- Primary comparison rule: exact schema and signature equality.
- Invalid objective policy: schema mismatch is failure.

### 0.B Reproducibility Contract
- Seed space: `seed ∈ {0..2^64-1}` where applicable.
- PRNG family: inherited from calling operator.
- Randomness locality: no sampling in interface contract checks.
- Replay guarantee: replayable given `(spec_version, interface_hash)`.
- Replay token: `api_replay_t = SHA-256(CBOR(["api_interfaces_v1", spec_version, interface_hash]))`.

### 0.C Numeric Policy
- Numeric fields specify explicit scalar kinds (`uint64`, `float64`, etc.).
- Rounding mode / fast-math: N/A for contract validation.
- NaN/Inf policy: invalid unless explicitly allowed by API field definition.
- Approx-equality: exact type match; no implicit coercion.

### 0.D Ordering and Tie-Break Policy
- Parameter order is canonical and positional.
- Tie-break: lexical ordering on field names for deterministic serialization.

### 0.E Parallel, Concurrency, and Reduction Policy
- Contract validation is deterministic and single-pass.
- No async behavior.

### 0.F Environment and Dependency Policy
- Reference runtime: language-agnostic schema validator.
- Dependencies: deterministic JSON/CBOR canonicalization.
- Determinism level: `BITWISE` for signature serialization and hashes.

### 0.G Operator Manifest
- `UML_OS.Implementation.ValidateAPISignature_v1`
- `UML_OS.Implementation.ValidateIOShape_v1`
- `UML_OS.Implementation.ComputeInterfaceHash_v1`
- `UML_OS.Error.Emit_v1`

### 0.H Namespacing and Packaging
- Fully-qualified names required.
- Sidecar mapping (`operator -> module/function`) required.

### 0.I Outputs and Metric Schema
- Declared outputs: `(validation_report, interface_hash)`.
- Metrics: `validated_operators`, `schema_mismatches`, `hash`.
- Completion status: `success | failed`.

### 0.J Spec Lifecycle Governance
- Breaking signature change requires MAJOR bump.
- Backward-compatible field additions require MINOR bump.
- Equivalence target: E0.

### 0.K Failure and Error Semantics
- Abort-only with deterministic error record.
- Codes: `API_SIGNATURE_MISMATCH`, `API_SHAPE_MISMATCH`, `API_TYPE_MISMATCH`.

### 0.L Input/Data Provenance
- Input schemas must be versioned and hash-addressable.

---

## 2) System Model

### I.A Persistent State
- `interface_registry: map<operator, signature>`.

### I.B Inputs and Hyperparameters
- `declared_interfaces`, `implemented_interfaces`.

### I.C Constraints and Feasible Set
- Unconstrained; validity determined by exact schema compatibility.

### I.D Transient Variables
- `diffs`, `validation_report`, `interface_hash`.

### I.E Invariants and Assertions
- Registry entries are unique and versioned.

### II.F Interface Registry (Concrete)
| name | version | method | request_schema_hash | response_schema_hash | idempotent | side_effects | allowed_error_codes | signature_digest |
|---|---|---|---|---|---|---|---|
| `UML_OS.Data.NextBatch_v2` | v2 | syscall | `sha256:req_nextbatch` | `sha256:resp_nextbatch` | false | `["ADVANCES_CURSOR"]` | `BATCH_SIZE_INCONSISTENT,INVALID_DATASET_KEY` | `sha256:sig_nextbatch_v2` |
| `UML_OS.Model.Forward_v2` | v2 | syscall | `sha256:req_forward` | `sha256:resp_forward` | false | `["ADVANCES_RNG"]` | `CONTRACT_VIOLATION,PRIMITIVE_UNSUPPORTED` | `sha256:sig_forward_v2` |
| `UML_OS.DifferentialPrivacy.Apply_v3` | v3 | syscall | `sha256:req_dp_apply` | `sha256:resp_dp_apply` | false | `["ADVANCES_RNG","MUTATES_ACCOUNTANT"]` | `PRIVACY_BUDGET_EXCEEDED,INVALID_DP_CONFIG` | `sha256:sig_dp_apply_v3` |
| `UML_OS.IO.SaveCheckpoint_v1` | v1 | syscall | `sha256:req_save_ckpt` | `sha256:resp_save_ckpt` | false | `["PERFORMS_IO"]` | `CONTRACT_VIOLATION` | `sha256:sig_save_ckpt_v1` |
| `UML_OS.Checkpoint.Restore_v1` | v1 | syscall | `sha256:req_restore_ckpt` | `sha256:resp_restore_ckpt` | false | `["PERFORMS_IO","MUTATES_MODEL_STATE"]` | `CONTRACT_VIOLATION` | `sha256:sig_restore_ckpt_v1` |
| `UML_OS.Trace.ComputeTraceHash_v1` | v1 | syscall | `sha256:req_trace_hash` | `sha256:resp_trace_hash` | true | `["NONE"]` | `CONTRACT_VIOLATION` | `sha256:sig_trace_hash_v1` |
| `UML_OS.Backend.LoadDriver_v1` | v1 | syscall | `sha256:req_load_driver` | `sha256:resp_load_driver` | false | `["PERFORMS_IO","NETWORK_COMM"]` | `BACKEND_CONTRACT_VIOLATION` | `sha256:sig_load_driver_v1` |
| `UML_OS.Model.ModelIR_Executor_v1` | v1 | syscall | `sha256:req_modelir_exec` | `sha256:resp_modelir_exec` | false | `["ALLOCATES_MEMORY"]` | `INVALID_IR,PRIMITIVE_UNSUPPORTED` | `sha256:sig_modelir_exec_v1` |
| `UML_OS.TMMU.PrepareMemory_v2` | v2 | syscall | `sha256:req_tmmu_prepare` | `sha256:resp_tmmu_prepare` | false | `["ALLOCATES_MEMORY"]` | `TMMU_ALLOCATION_FAILURE,ALIGNMENT_VIOLATION` | `sha256:sig_tmmu_prepare_v2` |
| `UML_OS.Tracking.RunCreate_v1` | v1 | syscall | `sha256:req_run_create` | `sha256:resp_run_create` | false | `["PERFORMS_IO"]` | `CONTRACT_VIOLATION` | `sha256:sig_run_create_v1` |
| `UML_OS.Tracking.RunStart_v1` | v1 | syscall | `sha256:req_run_start` | `sha256:resp_run_start` | false | `["PERFORMS_IO"]` | `CONTRACT_VIOLATION` | `sha256:sig_run_start_v1` |
| `UML_OS.Tracking.RunEnd_v1` | v1 | syscall | `sha256:req_run_end` | `sha256:resp_run_end` | false | `["PERFORMS_IO"]` | `CONTRACT_VIOLATION` | `sha256:sig_run_end_v1` |
| `UML_OS.Tracking.MetricLog_v1` | v1 | syscall | `sha256:req_metric_log` | `sha256:resp_metric_log` | false | `["PERFORMS_IO"]` | `CONTRACT_VIOLATION` | `sha256:sig_metric_log_v1` |
| `UML_OS.Tracking.ArtifactPut_v1` | v1 | syscall | `sha256:req_artifact_put` | `sha256:resp_artifact_put` | false | `["PERFORMS_IO"]` | `CONTRACT_VIOLATION` | `sha256:sig_artifact_put_v1` |
| `UML_OS.Tracking.ArtifactGet_v1` | v1 | syscall | `sha256:req_artifact_get` | `sha256:resp_artifact_get` | true | `["PERFORMS_IO"]` | `CONTRACT_VIOLATION` | `sha256:sig_artifact_get_v1` |
| `UML_OS.Tracking.ArtifactList_v1` | v1 | syscall | `sha256:req_artifact_list` | `sha256:resp_artifact_list` | true | `["PERFORMS_IO"]` | `CONTRACT_VIOLATION` | `sha256:sig_artifact_list_v1` |
| `UML_OS.Tracking.ArtifactTombstone_v1` | v1 | syscall | `sha256:req_artifact_tombstone` | `sha256:resp_artifact_tombstone` | false | `["PERFORMS_IO"]` | `CONTRACT_VIOLATION` | `sha256:sig_artifact_tombstone_v1` |
| `UML_OS.Registry.VersionCreate_v1` | v1 | syscall | `sha256:req_registry_version_create` | `sha256:resp_registry_version_create` | false | `["PERFORMS_IO"]` | `CONTRACT_VIOLATION` | `sha256:sig_registry_version_create_v1` |
| `UML_OS.Registry.StageTransition_v1` | v1 | syscall | `sha256:req_registry_stage_transition` | `sha256:resp_registry_stage_transition` | false | `["PERFORMS_IO"]` | `CONTRACT_VIOLATION` | `sha256:sig_registry_stage_transition_v1` |
| `UML_OS.Monitor.Register_v1` | v1 | syscall | `sha256:req_monitor_register` | `sha256:resp_monitor_register` | false | `["PERFORMS_IO"]` | `CONTRACT_VIOLATION` | `sha256:sig_monitor_register_v1` |
| `UML_OS.Monitor.Emit_v1` | v1 | syscall | `sha256:req_monitor_emit` | `sha256:resp_monitor_emit` | false | `["PERFORMS_IO"]` | `CONTRACT_VIOLATION` | `sha256:sig_monitor_emit_v1` |
| `UML_OS.Monitor.DriftCompute_v1` | v1 | syscall | `sha256:req_monitor_drift` | `sha256:resp_monitor_drift` | true | `["NONE"]` | `CONTRACT_VIOLATION` | `sha256:sig_monitor_drift_v1` |
| `UML_OS.Certificate.EvidenceValidate_v1` | v1 | syscall | `sha256:req_evidence_validate` | `sha256:resp_evidence_validate` | true | `["NONE"]` | `CONTRACT_VIOLATION` | `sha256:sig_evidence_validate_v1` |
| `UML_OS.Config.ManifestMigrate_v1` | v1 | syscall | `sha256:req_manifest_migrate` | `sha256:resp_manifest_migrate` | false | `["PERFORMS_IO"]` | `CONTRACT_VIOLATION` | `sha256:sig_manifest_migrate_v1` |
| `UML_OS.Checkpoint.CheckpointMigrate_v1` | v1 | syscall | `sha256:req_checkpoint_migrate` | `sha256:resp_checkpoint_migrate` | false | `["PERFORMS_IO"]` | `CONTRACT_VIOLATION` | `sha256:sig_checkpoint_migrate_v1` |
| `UML_OS.Trace.TraceMigrate_v1` | v1 | syscall | `sha256:req_trace_migrate` | `sha256:resp_trace_migrate` | false | `["PERFORMS_IO"]` | `CONTRACT_VIOLATION` | `sha256:sig_trace_migrate_v1` |

Signature digest rule:
- `signature_digest = SHA-256(CBOR([name, version, method, request_schema_hash, response_schema_hash, sorted(side_effects), sorted(allowed_error_codes)]))`.
- Cross-file invariant: for each operator `op`, digest in `API-Interfaces.md`, `Code-Generation-Mapping.md`, and `Backend-Adapter-Guide.md` (for backend-exposed ops) must be identical.
- `side_effects` allowed enum values:
  - `NONE`
  - `ADVANCES_CURSOR`
  - `ADVANCES_RNG`
  - `MUTATES_ACCOUNTANT`
  - `MUTATES_MODEL_STATE`
  - `PERFORMS_IO`
  - `ALLOCATES_MEMORY`
  - `NETWORK_COMM`

---

## 3) Initialization

1. Load declared interfaces.
2. Canonicalize schemas.
3. Build interface registry.

---

## 4) Operator Manifest

- `UML_OS.Implementation.ValidateAPISignature_v1`
- `UML_OS.Implementation.ValidateIOShape_v1`
- `UML_OS.Implementation.ComputeInterfaceHash_v1`
- `UML_OS.Error.Emit_v1`

---

## 5) Operator Definitions

External operator reference: `UML_OS.Error.Emit_v1` is defined normatively in `Error-Codes.md` and imported by reference.

**Operator:** `UML_OS.Implementation.ValidateAPISignature_v1`  
**Category:** IO  
**Signature:** `(declared, implemented -> report)`  
**Purity class:** PURE  
**Determinism:** deterministic  
**Definition:** exact field/type/order validation.  
**Preconditions / Postconditions:** inputs canonicalized.  
**Edge cases:** missing optional fields.  
**Numerical considerations:** N/A.  
**Ordering/tie handling:** lexical field order.  
**Complexity note:** O(total_fields).  
**Failure behavior:** emit deterministic mismatch record.  
**Dependencies:** canonical schema encoder.  
**Test vectors:** matching/mismatching signatures.

**Operator:** `UML_OS.Implementation.ValidateIOShape_v1`  
**Category:** IO  
**Signature:** `(signature, sample_payload -> ok)`  
**Purity class:** PURE  
**Determinism:** deterministic  
**Definition:** validates payload type/shape contracts.  
**Preconditions / Postconditions:** signature exists.  
**Edge cases:** optional and nullable fields.  
**Numerical considerations:** N/A.  
**Ordering/tie handling:** deterministic key traversal.  
**Complexity note:** O(payload_size).  
**Failure behavior:** `API_SHAPE_MISMATCH`.  
**Dependencies:** schema validator.  
**Test vectors:** representative payload set.

**Operator:** `UML_OS.Implementation.ComputeInterfaceHash_v1`  
**Category:** IO  
**Signature:** `(registry -> interface_hash)`  
**Purity class:** PURE  
**Determinism:** deterministic  
**Definition:** canonical hash over ordered signatures.  
**Preconditions / Postconditions:** unique registry keys.  
**Edge cases:** empty registry.  
**Numerical considerations:** N/A.  
**Ordering/tie handling:** sorted operator names.  
**Complexity note:** O(registry_size).  
**Failure behavior:** abort on hash serialization failure.  
**Dependencies:** canonical serializer + hash function.  
**Test vectors:** fixed registry hash snapshots.

---

## 6) Procedure

```text
1. ValidateAPISignature_v1(declared, implemented)
2. ValidateIOShape_v1(...) on representative payloads
3. ComputeInterfaceHash_v1(registry)
4. Return report + hash
```

---

## 7) Trace & Metrics

### Logging rule
Each validation run emits deterministic mismatch and summary records.

### Trace schema
- `run_header`: spec_version, interface_count
- `iter`: operator, check_type, result
- `run_end`: status, interface_hash

### Metric schema
- `validated_operators`, `schema_mismatches`, `hash`

### Comparability guarantee
Comparable iff identical schema keys, typing, and hash definition.

---

## 8) Validation

#### VII.A Lint rules (mandatory)
Passes symbol completeness, no hidden globals, deterministic ordering, trace compliance.

#### VII.B Operator test vectors (mandatory)
Includes exact signature and payload conformance vectors.

#### VII.C Golden traces (mandatory)
Golden hash snapshots for known interface sets.

---

## 9) Refactor & Equivalence

#### VIII.A Equivalence levels
- E0 required.

#### VIII.B Allowed refactor categories
- Validator implementation refactor preserving outputs and hashes.

#### VIII.C Equivalence test procedure (mandatory)
Compare full report and interface hash.

---

## 10) Checkpoint/Restore

### Checkpoint contents
- interface registry snapshot + hash.

### Serialization
- deterministic JSON/CBOR.

### Restore semantics
- restored registry yields identical validation outputs.
