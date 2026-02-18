# UML_OS Test Vectors Catalog Contract
**EQC Compliance:** Merged single-file EQC v1.1 Option A.

**Algorithm:** `UML_OS.Test.VectorsCatalog_v1`  
**Purpose (1 sentence):** Define authoritative operator-level input/output vectors and expected hashes/errors for deterministic conformance testing.  
**Spec Version:** `UML_OS.Test.VectorsCatalog_v1` | 2026-02-18 | Authors: Olejar Damir  
**Domain / Problem Class:** Golden-vector governance.

---
## 1) Header & Global Semantics
### 0.0 Identity
- **Algorithm:** `UML_OS.Test.VectorsCatalog_v1`
- **Purpose (1 sentence):** Canonical test vector registry.
### 0.A Objective Semantics
- Minimize ambiguous test expectations across implementations.
### 0.B Reproducibility Contract
- vectors and expected outputs are content-addressed and immutable.
### 0.C Numeric Policy
- expected numeric outputs include explicit dtype and tolerance class.
### 0.D Ordering and Tie-Break Policy
- vectors are ordered by `(operator_id, vector_id)`.
### 0.E Parallel, Concurrency, and Reduction Policy
- suite merge order is deterministic lexical order.
### 0.F Environment and Dependency Policy
- vector files use canonical serialization and hashes.
### 0.G Operator Manifest
- `UML_OS.Test.VectorLoad_v1`
- `UML_OS.Test.VectorExecute_v1`
- `UML_OS.Test.VectorVerify_v1`
- `UML_OS.Error.Emit_v1`
### 0.H Namespacing and Packaging
- `vectors/<operator>/<vector_id>.cbor`.
### 0.I Outputs and Metric Schema
- outputs: `(verification_report)` and mismatch diagnostics.
### 0.J Spec Lifecycle Governance
- vector content changes are MAJOR unless additive new vector IDs.
### 0.K Failure and Error Semantics
- mismatch emits deterministic error records.
### 0.L Input/Data Provenance
- each vector stores source-spec hash and operator signature digest.

---
## 2) System Model
### I.A Persistent State
- vector registry and golden hash index.
### I.B Inputs and Hyperparameters
- operator_id, vector_id, implementation target.
### I.C Constraints and Feasible Set
- vector must match declared operator signature digest.
### I.D Transient Variables
- run outputs, diff report.
### I.E Invariants and Assertions
- exact expected outputs for E0 fields.

### II.F Vector Record Schema (Normative)
- `operator_id:string`
- `vector_id:string`
- `input_payload_hash:bytes32`
- `expected_output_hash:bytes32`
- `expected_error_code?:string`
- `determinism_class: "E0" | "E1"`
- `signature_digest:bytes32`

---
## 3) Initialization
1. Load vector registry.
2. Validate hash/index integrity.
3. Bind operator executor.

---
## 4) Operator Manifest
- `UML_OS.Test.VectorLoad_v1`
- `UML_OS.Test.VectorExecute_v1`
- `UML_OS.Test.VectorVerify_v1`
- `UML_OS.Error.Emit_v1`

---
## 5) Operator Definitions
**Operator:** `UML_OS.Test.VectorVerify_v1`  
**Category:** Test  
**Signature:** `(actual_output, expected_vector -> verify_report)`  
**Purity class:** PURE  
**Determinism:** deterministic  
**Definition:** verifies outputs/errors against canonical vector expectations.

---
## 6) Procedure
```text
1. VectorLoad_v1(operator_id, vector_id)
2. VectorExecute_v1(implementation, input_payload)
3. VectorVerify_v1(actual, expected)
4. Emit verify_report
```

---
## 7) Trace & Metrics
### Logging rule
- every vector execution emits deterministic verification records.
### Trace schema
- `run_header`: operator_id, vector_id
- `iter`: step, status
- `run_end`: verify_status, mismatch_hash?
### Metric schema
- `passed`, `failed`, `mismatch_count`
### Comparability guarantee
- comparable iff vector payloads and signature digests match.

---
## 8) Validation
#### VII.A Lint rules (mandatory)
- no duplicate vector IDs per operator; required fields complete.
#### VII.B Operator test vectors (mandatory)
- self-test vectors for loader/executor/verifier.
#### VII.C Golden traces (mandatory)
- golden verify traces for representative vectors.

---
## 9) Refactor & Equivalence
#### VIII.A Equivalence levels
- E0 for verifier verdict and mismatch report.
#### VIII.B Allowed refactor categories
- storage/indexing changes preserving vector contents and IDs.
#### VIII.C Equivalence test procedure (mandatory)
- exact compare of verify_report on golden vectors.

---
## 10) Checkpoint/Restore
### Checkpoint contents
- vector-run cursor and partial batch verification state.
### Serialization
- deterministic CBOR.
### Restore semantics
- resumed vector run yields identical final verify report.
