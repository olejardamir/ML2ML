# UML_OS Operator Registry Schema Contract
**EQC Compliance:** Merged single-file EQC v1.1 Option A.

**Algorithm:** `UML_OS.Registry.OperatorRegistrySchema_v1`  
**Purpose (1 sentence):** Define the authoritative machine-readable schema for `contracts/operator_registry.cbor` and its deterministic validation rules.  
**Spec Version:** `UML_OS.Registry.OperatorRegistrySchema_v1` | 2026-02-19 | Authors: Olejar Damir  
**Domain / Problem Class:** Interface governance and contract integrity.

---
## 1) Header & Global Semantics
### 0.0 Identity
- **Algorithm:** `UML_OS.Registry.OperatorRegistrySchema_v1`
- **Purpose (1 sentence):** Canonical operator registry schema and validation.
### 0.A Objective Semantics
- Optimization sense: `MINIMIZE`
- Objective type: `Scalar`
- Primary comparison rule: deterministic schema validity and digest equality.
- Invalid objective policy: schema violations are deterministic failures.
### 0.B Reproducibility Contract
- Replayable given `(registry_schema_version, canonical_cbor_bytes)`.
- Hash/token paths use `SHA-256(CBOR_CANONICAL(...))`.
### 0.C Numeric Policy
- Integer fields are unsigned fixed ranges; digest fields are `bytes32`.
### 0.D Ordering and Tie-Break Policy
- Registry records sorted by `(operator_id, version)`.
### 0.E Parallel, Concurrency, and Reduction Policy
- Validation can be parallelized but merged in deterministic key order.
### 0.F Environment and Dependency Policy
- Determinism level: `BITWISE` for validation reports and computed hashes.
### 0.G Operator Manifest
- `UML_OS.Registry.ValidateOperatorRegistry_v1`
- `UML_OS.Registry.ComputeRegistryHash_v1`
- `UML_OS.Error.Emit_v1`
### 0.H Namespacing and Packaging
- Registry file path: `contracts/operator_registry.cbor`.
### 0.I Outputs and Metric Schema
- Outputs: `(validation_report, registry_hash)`.
- Metrics: `operators_count`, `schema_errors`.
### 0.J Spec Lifecycle Governance
- Required field changes are MAJOR.
### 0.K Failure and Error Semantics
- Abort-only with deterministic failure record.
### 0.L Input/Data Provenance
- Input registry blob must be content-addressed and immutable.

---
## 2) System Model
### I.A Persistent State
- `registry_schema`.
### I.B Inputs and Hyperparameters
- `operator_registry_blob`.
### I.C Constraints and Feasible Set
- Valid iff all required keys/types/enum values pass.
### I.D Transient Variables
- decoded records and diagnostics.
### I.E Invariants and Assertions
- unique `(operator_id, version)` keys.

### II.F Canonical Operator Record Schema (Normative)
- Required fields per operator record:
  - `operator_id:string`
  - `version:string`
  - `surface:enum("SYSCALL","SERVICE")`
  - `request_schema_digest:digest_ref`
  - `response_schema_digest:digest_ref`
  - `signature_digest:digest_ref`
  - `side_effects:array<side_effect_enum>` (sorted, unique; enum from `Data-Structures.md`)
  - `allowed_error_codes:array<error_code_id>` (sorted, unique; ids from `Error-Codes.md`)
  - `purity_class:enum("PURE","STATEFUL","IO")`
  - `required_capabilities:array<string>` (sorted, unique)
  - `idempotent:bool`
  - `rng_usage:enum("NONE","PHILOX4x32_10")`
  - `determinism_class:enum("DETERMINISTIC","STOCHASTIC","MIXED")`
- Optional fields:
  - `owner_team:string`
  - `deprecated:bool`
  - `replacement_operator_id:string`

### II.G Registry Hash (Normative)
- `registry_hash = SHA-256(CBOR_CANONICAL(["operator_registry_v1", sorted_operator_records]))`.

### II.H SignatureDigest Rule (Normative, Global)
- Signature digest computation is defined only here and consumed by all interface/mapping/backend docs.
- Preimage:
  - `signature_digest = SHA-256(CBOR_CANONICAL(["sig_v1", operator_id, version, method, request_schema_digest_resolved, response_schema_digest_resolved, sorted(side_effects), sorted(allowed_error_codes)]))`.
- `request_schema_digest_resolved` and `response_schema_digest_resolved` are resolved bytes32 values after `digest_ref` resolution.
- Any mismatch with this rule in rendered documentation is a deterministic `CONTRACT_VIOLATION`.

### II.I Operator Registry Root Commitment (Normative)
- `operator_registry_root_hash = SHA-256(CBOR_CANONICAL(operator_registry_object))`.
- `operator_registry_root_hash` is the required value bound as `operator_contracts_root_hash` in execution certificates and checkpoint headers.

---
## 3) Initialization
1. Load `contracts/operator_registry.cbor`.
2. Decode canonical CBOR.
3. Initialize validation diagnostics.

---
## 4) Operator Manifest
- `UML_OS.Registry.ValidateOperatorRegistry_v1`
- `UML_OS.Registry.ComputeRegistryHash_v1`
- `UML_OS.Error.Emit_v1`

---
## 5) Operator Definitions
**Operator:** `UML_OS.Registry.ValidateOperatorRegistry_v1`  
**Category:** Governance  
**Signature:** `(registry_blob -> validation_report)`  
**Purity class:** PURE  
**Determinism:** deterministic  
**Definition:** validates required fields, enum values, key uniqueness, and sorted list invariants.

**Operator:** `UML_OS.Registry.ComputeRegistryHash_v1`  
**Category:** Governance  
**Signature:** `(validated_registry -> registry_hash)`  
**Purity class:** PURE  
**Determinism:** deterministic  
**Definition:** computes canonical registry hash from sorted operator records.

---
## 6) Procedure
```text
1. ValidateOperatorRegistry_v1
2. ComputeRegistryHash_v1
3. Return report + registry_hash
```

---
## 7) Trace & Metrics
### Logging rule
- Validation emits deterministic registry diagnostics.
### Trace schema
- `run_header`: schema_version
- `iter`: operator_id, status
- `run_end`: registry_hash
### Metric schema
- `operators_count`, `schema_errors`
### Comparability guarantee
- Comparable iff schema version and canonical hash rule are identical.

---
## 8) Validation
#### VII.A Lint rules (mandatory)
- all required fields present and typed.
#### VII.B Operator test vectors (mandatory)
- valid/invalid registry fixtures.
#### VII.C Golden traces (mandatory)
- golden registry hash snapshots.

---
## 9) Refactor & Equivalence
#### VIII.A Equivalence levels
- E0 for validation report and registry hash.
#### VIII.B Allowed refactor categories
- parser/runtime implementation changes preserving outputs.
#### VIII.C Equivalence test procedure (mandatory)
- exact compare of report and registry hash.

---
## 10) Checkpoint/Restore
### Checkpoint contents
- last validated registry hash and diagnostics cursor.
### Serialization
- deterministic canonical CBOR.
### Restore semantics
- resumed validation yields identical output.
