# UML_OS Trace Sidecar Schema
**EQC Compliance:** Merged single-file EQC v1.1 Option A.

**Algorithm:** `UML_OS.Trace.SidecarSchema_v1`  
**Purpose (1 sentence):** Define a canonical machine-readable trace schema shared by all UML_OS components.  
**Spec Version:** `UML_OS.Trace.SidecarSchema_v1` | 2026-02-18 | Authors: Olejar Damir  
**Domain / Problem Class:** Trace interoperability and comparability.

---
## 1) Header & Global Semantics
### 0.0 Identity
- **Algorithm:** `UML_OS.Trace.SidecarSchema_v1`
- **Purpose (1 sentence):** Canonical trace schema contract.
- **Spec Version:** `UML_OS.Trace.SidecarSchema_v1` | 2026-02-18 | Authors: Olejar Damir
- **Domain / Problem Class:** Unified trace format.
### 0.A Objective Semantics
- Optimization sense: `MINIMIZE`
- Objective type: `Scalar`
- Primary comparison rule: deterministic total preorder over declared primary metric tuple with `EPS_EQ` tie handling.
- Invalid objective policy: `NaN/Inf` ranked as worst-case and handled deterministically per 0.K.
- Minimize trace ambiguity and schema drift.
### 0.B Reproducibility Contract
- Replayable given `(schema_version, trace_root_hash, replay_token_formula)`.
### 0.C Numeric Policy
- Field types are explicit; numeric fields use declared scalar kinds.
### 0.D Ordering and Tie-Break Policy
- Record order: canonical total order `(t, rank, operator_seq)`.
### 0.E Parallel, Concurrency, and Reduction Policy
- Multi-rank traces merged in one canonical total order: `(t, rank, operator_seq)`.
### 0.F Environment and Dependency Policy
- Determinism level: `BITWISE` for schema and required key set.
### 0.G Operator Manifest
- `UML_OS.Trace.ValidateSchema_v1`
- `UML_OS.Trace.NormalizeRecord_v1`
- `UML_OS.Trace.ComputeTraceHash_v1`
### 0.H Namespacing and Packaging
- Namespaced schema keys required.
### 0.I Outputs and Metric Schema
- Outputs: `(normalized_trace, final_trace_hash)`.
- Metrics: `record_count`, `missing_required_keys`.
- Completion status: `success | failed`.
### 0.J Spec Lifecycle Governance
- Required-key changes are MAJOR.
### 0.K Failure and Error Semantics
- Abort on schema violations in strict mode.
### 0.L Input/Data Provenance
- Trace source component and replay context required.

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
- trace schema registry.
### I.B Inputs and Hyperparameters
- raw trace stream and schema version.
### I.C Constraints and Feasible Set
- valid iff required keys/types are present.
### I.D Transient Variables
- normalized records and diagnostics.
### I.E Invariants and Assertions
- key set and type contract invariant.

### II.F Canonical Trace Schema (Concrete)
- Hash algorithms:
  - `record_hash_i = SHA-256(CBOR(normalized_record_i))`
  - Whole-run hash chain:
    - `h_0 = SHA-256(CBOR(["trace_chain_v1"]))`
    - `h_i = SHA-256(CBOR(["trace_chain_v1", h_{i-1}, record_hash_i]))` for records in canonical order
    - `final_trace_hash = h_last`
- Trace endpoints:
  - `trace_head_hash = h_0`
  - `trace_tail_hash = h_last`
- Self-reference rule: when hashing the `run_end` record, `run_end.final_trace_hash` is omitted (or encoded as empty bytes) in the canonical CBOR input.
- Canonical serialization: CBOR map with sorted keys (bytewise lexicographic), UTF-8 strings, unsigned integers for counters.
- Required `run_header` fields/types: `schema_version:string`, `replay_token:bytes`, `run_id:string`, `tenant_id:string`, `task_type:string`, `world_size:uint32`, `backend_hash:bytes`, `redaction_mode:string`, `redaction_key_id?:string`, `redaction_policy_hash?:bytes32`.
- Required `iter` fields/types: `t:uint64`, `stage_id:string`, `operator_id:string`, `operator_seq:uint64`, `rank:uint32`, `status:string`, `replay_token:bytes`.
- `operator_seq` is a per-rank monotone counter.
- Optional `iter` fields/types: `loss_total:float64`, `grad_norm:float64`, `state_fp:bytes`, `functional_fp:bytes`, `rng_offset_before:uint64`, `rng_offset_after:uint64`.
- Optional `iter` fields/types: `tracking_event_type:string`, `artifact_id:string`, `metric_name:string`, `metric_value:float64`, `window_id:string`.
- Required `run_end` fields/types: `status:string`, `final_state_fp:bytes`, `final_trace_hash:bytes`.
- Migration controls:
  - `migration_supported_from: array<string>`
  - `migration_operator: string`
  - `migration_invariants: array<string>`

### II.G Privacy Classification and Redaction Contract
- Field classification labels: `PUBLIC | INTERNAL | CONFIDENTIAL`.
- Field-level baseline classes:
  - `PUBLIC`: `t`, `operator_id`, `operator_seq`, hash digests, status.
  - `INTERNAL`: driver/runtime fingerprints, backend/hash metadata.
  - `CONFIDENTIAL`: any value that can leak sample/model-sensitive properties.
- No-raw-data rule: traces must not contain raw examples, prompts, gradients, secrets, or direct identifiers.
- Confidential-mode redaction: sensitive values must be replaced by deterministic keyed hashes (`HMAC-SHA256`) with declared key identifier.
- Size and sampling controls: deterministic per-operator caps and sampling policy must be declared to bound trace overhead.
- Deterministic size/sampling controls:
  - `max_bytes_per_step:uint64`
  - `max_record_bytes:uint32`
  - `sample_policy: enum("HASH_GATED","FIXED_RATE","OFF")`
  - HASH_GATED inclusion rule: include iff `SHA-256(CBOR([replay_token, t, operator_seq])) mod M < K`.
  - Cap overflow drop policy: `DROP_LOWEST_PRIORITY_CLASS_FIRST` with declared priority ordering.
  - `mandatory_record_kinds = {run_header, policy_gate_verdict, checkpoint_commit, certificate_inputs, run_end}`.
  - Mandatory records MUST NEVER be sampled out or dropped.
  - If caps force dropping mandatory records: emit `TRACE_CAP_EXCEEDED_MANDATORY` and abort deterministically.

---
## 3) Initialization
1. Load schema version.
2. Validate required keys.
3. Initialize normalization pipeline.

---
## 4) Operator Manifest
- `UML_OS.Trace.ValidateSchema_v1`
- `UML_OS.Trace.NormalizeRecord_v1`
- `UML_OS.Trace.ComputeTraceHash_v1`

---
## 5) Operator Definitions

External operator reference: `UML_OS.Error.Emit_v1` is defined normatively in `Error-Codes.md` and imported by reference.

Template conformance note (III.A): each operator definition in this section is interpreted with the full EQC operator template fields. When a field is not repeated inline, the section-level defaults are: explicit typed signatures, deterministic ordering/tie handling, declared numerical policy inheritance, deterministic failure semantics (0.K), explicit dependencies, and VII.B test-vector coverage.

**Operator:** `UML_OS.Trace.ValidateSchema_v1`  
**Category:** IO  
**Signature:** `(trace, schema -> report)`  
**Purity class:** PURE  
**Determinism:** deterministic  
**Definition:** required key/type validation.

**Operator:** `UML_OS.Trace.NormalizeRecord_v1`  
**Category:** IO  
**Signature:** `(record -> normalized_record)`  
**Purity class:** PURE  
**Determinism:** deterministic  
**Definition:** canonical key order and value normalization.

**Operator:** `UML_OS.Trace.ComputeTraceHash_v1`  
**Category:** IO  
**Signature:** `(normalized_trace -> final_trace_hash)`  
**Purity class:** PURE  
**Determinism:** deterministic  
**Definition:** computes per-record SHA-256 hashes and folds them with the `trace_chain_v1` hash-chain rule to emit the whole-run `final_trace_hash`.

---
## 6) Procedure
```text
1. ValidateSchema_v1
2. NormalizeRecord_v1 for each record
3. ComputeTraceHash_v1
4. Return normalized_trace + hash
```

---
## 7) Trace & Metrics
### Logging rule
Trace schema validation itself emits deterministic validation records.
### Trace schema
- `run_header`: schema_version, source_component
- `iter`: t, operator, validation_status
- `run_end`: final_trace_hash, status
### Metric schema
- `record_count`, `missing_required_keys`
### Comparability guarantee
Comparable iff schema version, key set, and hash formula are identical.

---
## 8) Validation
#### VII.A Lint rules (mandatory)
Passes schema completeness, deterministic ordering, no hidden globals.
#### VII.B Operator test vectors (mandatory)
Valid/invalid trace fixtures.
#### VII.C Golden traces (mandatory)
Golden trace hashes for canonical samples.

---
## 9) Refactor & Equivalence
#### VIII.A Equivalence levels
- E0 for normalized trace and hash.
#### VIII.B Allowed refactor categories
- parser/normalizer optimization preserving outputs.
#### VIII.C Equivalence test procedure (mandatory)
Exact normalized record and hash comparison.

---
## 10) Checkpoint/Restore
### Checkpoint contents
- schema version and normalization state.
### Serialization
- deterministic JSON/CBOR.
### Restore semantics
- resumed validation yields identical outputs.
