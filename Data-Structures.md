# UML_OS Data Structure Contract
**EQC Compliance:** Merged single-file EQC v1.1 Option A.

**Algorithm:** `UML_OS.Implementation.DataStructureContract_v1`  
**Purpose (1 sentence):** Define deterministic canonical runtime data structures for kernel, model IR, TMMU, data, and DP modules.  
**Spec Version:** `UML_OS.Implementation.DataStructureContract_v1` | 2026-02-18 | Authors: Olejar Damir  
**Domain / Problem Class:** Type/layout specification for interoperable deterministic execution.

---

## 1) Header & Global Semantics

### 0.0 Identity
- **Algorithm:** `UML_OS.Implementation.DataStructureContract_v1`
- **Purpose (1 sentence):** Canonical data-structure definitions.
- **Spec Version:** `UML_OS.Implementation.DataStructureContract_v1` | 2026-02-18 | Authors: Olejar Damir
- **Domain / Problem Class:** Runtime type contracts.

### 0.A Objective Semantics
- Optimization sense: `MINIMIZE`
- Objective type: `Scalar`
- Primary comparison rule: deterministic total preorder over declared primary metric tuple with `EPS_EQ` tie handling.
- Invalid objective policy: `NaN/Inf` ranked as worst-case and handled deterministically per 0.K.
- Not an optimization algorithm.
- Primary guarantee: exact type/field consistency across modules.

### 0.B Reproducibility Contract
- Seed space/PRNG inherited by consuming operators.
- Randomness locality: none in structure contract.
- Replay guarantee: structure version + canonical schema hash sufficient for replay compatibility.

### 0.C Numeric Policy
- Numeric scalar kinds are explicit (`uint64`, `float64`, etc.).
- NaN/Inf allowances must be declared by consuming operator.
- Approx-equality: N/A (schema exactness).

### 0.D Ordering and Tie-Break Policy
- Field ordering is canonical and deterministic.
- Map-like structures require sorted key serialization.

### 0.E Parallel, Concurrency, and Reduction Policy
- Structure validation is deterministic and side-effect free.

### 0.F Environment and Dependency Policy
- Reference runtime: any deterministic schema validator.
- Determinism level: `BITWISE` for serialized schema hash.

### 0.G Operator Manifest
- `UML_OS.Implementation.ValidateStruct_v1`
- `UML_OS.Implementation.SerializeCanonical_v1`
- `UML_OS.Implementation.ComputeStructHash_v1`
- `UML_OS.Error.Emit_v1`

### 0.H Namespacing and Packaging
- Structure names are namespaced by subsystem.

### 0.I Outputs and Metric Schema
- Outputs: `(validated_structs, struct_hash)`.
- Metrics: `struct_count`, `field_count`, `violations`.
- Completion status: `success | failed`.

### 0.J Spec Lifecycle Governance
- Breaking field deletion/rename/type change => MAJOR.
- Additive backward-compatible field => MINOR.

### 0.K Failure and Error Semantics
- Abort-only; deterministic failure records.

### 0.L Input/Data Provenance
- Schema source must be version-tagged and hashable.

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
- `struct_registry: map<name, schema>`.

### I.B Inputs and Hyperparameters
- canonical structure declarations.

### I.C Constraints and Feasible Set
- Unconstrained, validity defined by exact schema rules.

### I.D Transient Variables
- validation diagnostics.

### I.E Invariants and Assertions
- unique structure names and stable field ordering.

### II.F Concrete Structure Layouts
- Authoritative enums:
  - `purity_class = PURE | STATEFUL | IO`
  - `side_effect = NONE | ADVANCES_RNG | ADVANCES_CURSOR | MUTATES_ACCOUNTANT | MUTATES_MODEL_STATE | PERFORMS_IO | NETWORK_COMM | ALLOCATES_MEMORY`
- `TraceIterRecord` (CBOR map): `{t:uint64, stage_id:string, operator_id:string, operator_seq:uint64, rank:uint32, status:string, replay_token:bytes32, rng_offset_before?:uint64, rng_offset_after?:uint64, dp_accountant_state_hash?:bytes32, sampler_config_hash?:bytes32, tmmu_plan_hash?:bytes32, determinism_profile_hash?:bytes32, state_fp?:bytes32, functional_fp?:bytes32, quota_decision?:string, quota_policy_hash?:bytes32, tracking_event_type?:string, artifact_id?:string, metric_name?:string, metric_value?:float64, window_id?:string, privacy_class:enum(PUBLIC|INTERNAL|CONFIDENTIAL), loss_total?:float64, grad_norm?:float64}`.
- `TraceRunHeader`: `{schema_version:string, tenant_id:string, run_id:string, replay_token:bytes32, task_type:string, world_size:uint32, backend_hash:bytes32, policy_bundle_hash:bytes32, monitor_policy_hash:bytes32, policy_gate_hash?:bytes32, authz_decision_hash?:bytes32, redaction_mode:enum(NONE|HMAC_SHA256_V1), redaction_key_id?:string, redaction_policy_hash?:bytes32, hash_gate_M:uint64, hash_gate_K:uint64}`.
- `CheckpointHeader`: `{tenant_id:string, run_id:string, spec_version:string, replay_token:bytes32, t:uint64, manifest_hash:bytes32, trace_root_hash:bytes32, sampler_config_hash:bytes32, data_access_plan_hash?:bytes32, tmmu_plan_hash:bytes32, backend_binary_hash:bytes32, checkpoint_merkle_root:bytes32, checkpoint_header_hash:bytes32, checkpoint_manifest_hash:bytes32, checkpoint_hash:bytes32, policy_bundle_hash:bytes32, determinism_profile_hash:bytes32, dependencies_lock_hash:bytes32, operator_contracts_root_hash:bytes32, runtime_env_hash:bytes32, code_commit_hash:bytes32, lineage_root_hash:bytes32, tensors_root_hash:bytes32, optimizer_state_root_hash:bytes32, dp_accountant_state_root_hash?:bytes32}`.
- `ErrorRecord`: `{code_id:string, numeric_code:uint32, severity:enum(FATAL|ERROR|WARN), subsystem:string, t:uint64, rank:uint32, failure_operator:string, replay_token:bytes32, message:string, retryable:bool, diagnostics?:map<string,scalar|string|bytes>, privacy_class:enum(PUBLIC|INTERNAL|CONFIDENTIAL)}`.
- `MonitorEvent`: `{tenant_id:string, run_id:string, model_version_id:string, window_id:string, metric_name:string, metric_value:float64, privacy_class:enum(PUBLIC|INTERNAL|CONFIDENTIAL)}`.
- `MetricSchema`: `{metric_name:string, scalar_type:enum(float64|int64|bool|string), aggregation:enum(sum|mean|min|max|quantile), window_policy:string, privacy_class:enum(PUBLIC|INTERNAL|CONFIDENTIAL)}`.
- `PipelineTransitionRecord`: `{tenant_id:string, job_id:string, attempt_id:uint32, transition_seq:uint64, idempotency_key:bytes32, from_state:string, to_state:string, status:string, diagnostics?:map<string,string>}`.
- `ResourceLedgerRecord`: `{tenant_id:string, run_id:string, t:uint64, bytes_allocated:uint64, peak_bytes:uint64, io_bytes_read:uint64, io_bytes_written:uint64, gpu_time_ms:uint64, cpu_time_ms:uint64, quota_decision:string, quota_policy_hash:bytes32}`.
- Alignment policy for binary layouts: fields aligned to natural size; packed representation forbidden for cross-language canonical payloads.

### II.G Canonical Serialization v1 (Normative)
- All contract-critical hashes/signatures must be computed over canonical CBOR bytes only.
- Canonicalization rules:
  - map keys ordered by `(len(CBOR_ENCODE(key)), CBOR_ENCODE(key))` as defined in `Canonical-CBOR-Profile.md`,
  - integers encoded in shortest canonical form,
  - signed fields must encode floats as IEEE-754 binary64 only,
  - `NaN` and `Inf` are forbidden in signed/hash-critical payloads unless explicitly normalized by operator contract,
  - strings must be valid UTF-8; non-normalized forms are invalid for signed payloads,
  - fixed-length digests (`bytes32`) must be exactly 32 bytes.
- Domain separation labels (for chained hashes/signatures) must be explicit CBOR string tags in the hashed tuple.

---

## 3) Initialization

1. Load structure declarations.
2. Canonicalize field order.
3. Build registry.

---

## 4) Operator Manifest

- `UML_OS.Implementation.ValidateStruct_v1`
- `UML_OS.Implementation.SerializeCanonical_v1`
- `UML_OS.Implementation.ComputeStructHash_v1`
- `UML_OS.Error.Emit_v1`

---

## 5) Operator Definitions

External operator reference: `UML_OS.Error.Emit_v1` is defined normatively in `Error-Codes.md` and imported by reference.

**Operator:** `UML_OS.Implementation.ValidateStruct_v1`  
**Category:** IO  
**Signature:** `(registry -> report)`  
**Purity class:** PURE  
**Determinism:** deterministic  
**Definition:** validates required fields, types, and ordering rules.  
**Preconditions / Postconditions:** registry loaded.  
**Edge cases:** optional fields and nested maps.  
**Numerical considerations:** N/A.  
**Ordering/tie handling:** lexical key order.  
**Complexity note:** O(total_fields).  
**Failure behavior:** deterministic schema failures.  
**Dependencies:** canonical schema parser.  
**Test vectors:** valid/invalid schema fixtures.

**Operator:** `UML_OS.Implementation.SerializeCanonical_v1`  
**Category:** IO  
**Signature:** `(registry -> bytes)`  
**Purity class:** PURE  
**Determinism:** deterministic  
**Definition:** deterministic canonical encoding for hashing and checkpointing.  
**Preconditions / Postconditions:** validated registry.  
**Edge cases:** empty registry.  
**Numerical considerations:** N/A.  
**Ordering/tie handling:** sorted names then fields.  
**Complexity note:** O(registry_size).  
**Failure behavior:** abort on serialization mismatch.  
**Dependencies:** serializer backend.  
**Test vectors:** golden serialized bytes.

**Operator:** `UML_OS.Implementation.ComputeStructHash_v1`  
**Category:** IO  
**Signature:** `(canonical_bytes -> hash)`  
**Purity class:** PURE  
**Determinism:** deterministic  
**Definition:** computes deterministic structure hash.  
**Preconditions / Postconditions:** canonical bytes only.  
**Edge cases:** zero-length bytes.  
**Numerical considerations:** N/A.  
**Ordering/tie handling:** N/A.  
**Complexity note:** O(bytes).  
**Failure behavior:** abort on hash failure.  
**Dependencies:** hash function.  
**Test vectors:** fixed byte->hash vectors.

---

## 6) Procedure

```text
1. ValidateStruct_v1(registry)
2. SerializeCanonical_v1(registry)
3. ComputeStructHash_v1(bytes)
4. Return report + hash
```

---

## 7) Trace & Metrics

### Logging rule
Emit deterministic structure validation and hash records.

### Trace schema
- `run_header`: struct_count
- `iter`: struct_name, result
- `run_end`: status, struct_hash

### Metric schema
- `struct_count`, `field_count`, `violations`

### Comparability guarantee
Comparable iff schema definitions and canonical serializer are identical.

---

## 8) Validation

#### VII.A Lint rules (mandatory)
Passes determinism, completeness, ordering, no hidden globals.

#### VII.B Operator test vectors (mandatory)
Schema fixtures and canonical serialization vectors.

#### VII.C Golden traces (mandatory)
Golden hashes for canonical registries.

---

## 9) Refactor & Equivalence

#### VIII.A Equivalence levels
- E0 required.

#### VIII.B Allowed refactor categories
- Parser/serializer refactor with identical bytes/hash output.

#### VIII.C Equivalence test procedure (mandatory)
Compare report and final hash exactly.

---

## 10) Checkpoint/Restore

### Checkpoint contents
- canonical schema bytes + hash.

### Serialization
- deterministic CBOR/JSON.

### Restore semantics
- identical restored registry and hash.
