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
- Replay token: `api_replay_t = SHA-256(spec_version || interface_hash)`.

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
