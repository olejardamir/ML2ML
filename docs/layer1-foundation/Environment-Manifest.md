# UML_OS Environment Manifest Contract
**EQC Compliance:** Merged single-file EQC v1.1 Option A.

**Algorithm:** `UML_OS.Environment.Manifest_v1`  
**Purpose (1 sentence):** Define canonical environment/runtime fingerprint schema and hashing used by replay tokens, checkpoints, and certificates.  
**Spec Version:** `UML_OS.Environment.Manifest_v1` | 2026-02-19 | Authors: Olejar Damir  
**Domain / Problem Class:** Deterministic environment identity and compatibility gating.

---
## 1) Header & Global Semantics
### 0.0 Identity
- **Algorithm:** `UML_OS.Environment.Manifest_v1`
- **Purpose (1 sentence):** Canonical environment identity contract.
### 0.A Objective Semantics
- Optimization sense: `MINIMIZE`
- Objective type: `Scalar`
- Primary comparison rule: exact hash equality.
### 0.B Reproducibility Contract
- Replayable given `(env_manifest_hash, schema_version)`.
### 0.C Numeric Policy
- Version and capability fields are exact typed scalars/strings.
### 0.D Ordering and Tie-Break Policy
- Keys serialized by canonical CBOR rules only.
### 0.E Parallel, Concurrency, and Reduction Policy
- Environment capture may be parallelized; canonical manifest bytes must be deterministic.
### 0.F Environment and Dependency Policy
- Determinism level: `BITWISE` for manifest hash.
### 0.G Operator Manifest
- `UML_OS.Environment.BuildManifest_v1`
- `UML_OS.Environment.ComputeManifestHash_v1`
- `UML_OS.Environment.ValidateCompatibility_v1`
- `UML_OS.Error.Emit_v1`
### 0.H Namespacing and Packaging
- `UML_OS.Environment.*` namespace.
### 0.I Outputs and Metric Schema
- Outputs: `(env_manifest, env_manifest_hash, compatibility_report)`.
### 0.J Spec Lifecycle Governance
- Required field changes are MAJOR.
### 0.K Failure and Error Semantics
- Abort on missing required environment fields in regulated/managed modes.
### 0.L Input/Data Provenance
- Environment capture must record source of runtime facts (driver/runtime/toolchain introspection).

---
## 2) System Model
### I.A Persistent State
- environment manifest registry keyed by hash.
### I.B Inputs and Hyperparameters
- runtime stack descriptors, driver/runtime versions, toolchain versions, determinism-impacting env vars.
### I.C Constraints and Feasible Set
- valid iff required fields exist and pass schema/type constraints.
### I.D Transient Variables
- normalization diagnostics.
### I.E Invariants and Assertions
- same runtime facts always produce the same canonical bytes/hash.

### II.F Canonical Environment Manifest Schema (Normative)
- Required fields:
  - `schema_version:string`
  - `os_name:string`, `os_version:string`, `kernel_version:string`
  - `python_version:string`
  - `backend_adapter_version:string`, `backend_binary_hash:bytes32`
  - `driver_runtime_fingerprint_hash:bytes32`
  - `determinism_profile_hash:bytes32`
  - `toolchain_hash:bytes32`
  - `env_vars_fingerprint_hash:bytes32` (determinism-impacting env vars only)

### II.G Hashing Rule (Normative)
- `env_manifest_hash = SHA-256(CBOR_CANONICAL(env_manifest_map))`.
- Naming normalization:
  - `runtime_env_hash` and `env_manifest_hash` are aliases for the same bytes32 commitment.

---
## 3) Initialization
1. Collect runtime facts.
2. Normalize to canonical manifest schema.
3. Compute `env_manifest_hash`.

---
## 4) Operator Manifest
- `UML_OS.Environment.BuildManifest_v1`
- `UML_OS.Environment.ComputeManifestHash_v1`
- `UML_OS.Environment.ValidateCompatibility_v1`
- `UML_OS.Error.Emit_v1`

---
## 5) Operator Definitions
**Operator:** `UML_OS.Environment.BuildManifest_v1`  
**Category:** Environment  
**Signature:** `(runtime_inputs -> env_manifest)`  
**Purity class:** IO  
**Determinism:** deterministic  
**Definition:** Captures required runtime facts and emits schema-valid manifest.

**Operator:** `UML_OS.Environment.ComputeManifestHash_v1`  
**Category:** Environment  
**Signature:** `(env_manifest -> env_manifest_hash)`  
**Purity class:** PURE  
**Determinism:** deterministic  
**Definition:** Computes canonical commitment hash.

---
## 6) Procedure
```text
1. BuildManifest_v1
2. ComputeManifestHash_v1
3. ValidateCompatibility_v1
4. Return manifest + hash + report
```

---
## 7) Trace & Metrics
### Logging rule
- Environment capture emits deterministic records.
### Trace schema
- `run_header`: schema_version, env_manifest_hash
- `iter`: field_group, status
- `run_end`: compatibility_status
### Metric schema
- `missing_fields`, `compatibility_failures`
### Comparability guarantee
- Comparable iff `env_manifest_hash` and schema version match.

---
## 8) Validation
#### VII.A Lint rules (mandatory)
- required fields complete and canonical serialization used.
#### VII.B Operator test vectors (mandatory)
- fixed runtime descriptors -> fixed `env_manifest_hash`.
#### VII.C Golden traces (mandatory)
- golden environment capture traces.

---
## 9) Refactor & Equivalence
#### VIII.A Equivalence levels
- E0 for `env_manifest_hash` and compatibility verdict.
#### VIII.B Allowed refactor categories
- capture implementation changes preserving manifest bytes/hash.
#### VIII.C Equivalence test procedure (mandatory)
- byte-level compare of canonical manifest and hash.

---
## 10) Checkpoint/Restore
### Checkpoint contents
- `env_manifest_hash` and schema version.
### Serialization
- deterministic canonical CBOR.
### Restore semantics
- restored run must match committed environment manifest hash or abort deterministically.
