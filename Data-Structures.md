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
- `TraceIterRecord` (CBOR map): `{t:uint64, stage_id:string, operator_id:string, operator_seq:uint64, rank:uint32, status:string, replay_token:bytes32, rng_offset_before?:uint64, rng_offset_after?:uint64, dp_accountant_state_hash?:bytes32, sampler_config_hash?:bytes32, tmmu_plan_hash?:bytes32, determinism_profile_hash?:bytes32, privacy_class:enum(PUBLIC|INTERNAL|CONFIDENTIAL), loss_total?:float64, grad_norm?:float64}`.
- `CheckpointHeader`: `{spec_version:string, replay_token:bytes32, t:uint64, checkpoint_merkle_root:bytes32}`.
- `ErrorRecord`: `{code_id:string, numeric_code:uint32, severity:enum(FATAL|ERROR|WARN), subsystem:string, t:uint64, rank:uint32, failure_operator:string, replay_token:bytes32, message:string, retryable:bool, diagnostics?:map<string,scalar|string|bytes>, privacy_class:enum(PUBLIC|INTERNAL|CONFIDENTIAL)}`.
- `MonitorEvent`: `{tenant_id:string, run_id:string, model_version_id:string, window_id:string, metric_name:string, metric_value:float64, privacy_class:enum(PUBLIC|INTERNAL|CONFIDENTIAL)}`.
- `MetricSchema`: `{metric_name:string, scalar_type:enum(float64|int64|bool|string), aggregation:enum(sum|mean|min|max|quantile), window_policy:string, privacy_class:enum(PUBLIC|INTERNAL|CONFIDENTIAL)}`.
- Alignment policy for binary layouts: fields aligned to natural size; packed representation forbidden for cross-language canonical payloads.

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
