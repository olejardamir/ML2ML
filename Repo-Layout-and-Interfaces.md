# UML_OS Repo Layout and Interfaces Contract
**EQC Compliance:** Merged single-file EQC v1.1 Option A.

**Algorithm:** `UML_OS.Implementation.RepoLayoutInterfaces_v1`  
**Purpose (1 sentence):** Define canonical repository structure, module boundaries, and ownership aligned to operator interface contracts.  
**Spec Version:** `UML_OS.Implementation.RepoLayoutInterfaces_v1` | 2026-02-18 | Authors: Olejar Damir  
**Domain / Problem Class:** Implementation architecture and module governance.

---
## 1) Header & Global Semantics
### 0.0 Identity
- **Algorithm:** `UML_OS.Implementation.RepoLayoutInterfaces_v1`
- **Purpose (1 sentence):** Canonical codebase layout and boundary contract.
### 0.A Objective Semantics
- Minimize code ownership ambiguity and cross-module contract drift.
### 0.B Reproducibility Contract
- layout and interface manifests are hash-addressed and versioned.
### 0.C Numeric Policy
- N/A except hash and version identifiers.
### 0.D Ordering and Tie-Break Policy
- module resolution order is deterministic lexical path order.
### 0.E Parallel, Concurrency, and Reduction Policy
- build graph resolution deterministic by declared dependencies.
### 0.F Environment and Dependency Policy
- dependency boundaries enforced by static import rules.
### 0.G Operator Manifest
- `UML_OS.Implementation.ValidateRepoLayout_v1`
- `UML_OS.Implementation.ValidateModuleBoundaries_v1`
- `UML_OS.Implementation.ValidateOwnershipMap_v1`
- `UML_OS.Error.Emit_v1`
### 0.H Namespacing and Packaging
- namespace roots: `src/`, `tests/`, `vectors/`, `schemas/`, `ops/`.
### 0.I Outputs and Metric Schema
- outputs: `(layout_report, boundary_report, ownership_report)`.
### 0.J Spec Lifecycle Governance
- boundary/ownership semantics changes are MAJOR.
### 0.K Failure and Error Semantics
- boundary violations emit deterministic errors.
### 0.L Input/Data Provenance
- repo state bound to commit hash and manifest hash.

---
## 2) System Model
### I.A Persistent State
- module registry and ownership map.
### I.B Inputs and Hyperparameters
- repo tree, module manifest, ownership manifest.
### I.C Constraints and Feasible Set
- every mapped operator must have exactly one module target.
### I.D Transient Variables
- validation diagnostics.
### I.E Invariants and Assertions
- ownership coverage complete for mapped operators.

### II.F Canonical Layout (Normative)
- `src/data`, `src/model`, `src/dp`, `src/tmmu`, `src/replay`, `src/trace`, `src/checkpoint`, `src/backend`, `src/security`, `src/registry`, `src/tracking`, `src/monitor`, `src/cert`.
- `tests/unit`, `tests/integration`, `tests/replay`, `tests/perf`.
- `vectors/<operator_id>/`.
- `schemas/` for config/trace/checkpoint/api schemas.

### II.G Ownership Map (Normative)
- `data team`: `src/data/*`
- `model team`: `src/model/*`
- `privacy team`: `src/dp/*`
- `runtime team`: `src/tmmu/*`, `src/checkpoint/*`
- `platform team`: `src/tracking/*`, `src/monitor/*`, `src/config/*`
- `security team`: `src/security/*`, `src/cert/*`
- `governance team`: `src/registry/*`

---
## 3) Initialization
1. Load repo layout manifest.
2. Load ownership manifest.
3. Load operator mapping manifest.

---
## 4) Operator Manifest
- `UML_OS.Implementation.ValidateRepoLayout_v1`
- `UML_OS.Implementation.ValidateModuleBoundaries_v1`
- `UML_OS.Implementation.ValidateOwnershipMap_v1`
- `UML_OS.Error.Emit_v1`

---
## 5) Operator Definitions
**Operator:** `UML_OS.Implementation.ValidateRepoLayout_v1`  
**Category:** Implementation  
**Signature:** `(repo_tree, layout_contract -> report)`  
**Purity class:** PURE  
**Determinism:** deterministic  
**Definition:** checks required directories/files and canonical placement rules.

**Operator:** `UML_OS.Implementation.ValidateModuleBoundaries_v1`  
**Category:** Implementation  
**Signature:** `(import_graph, boundary_rules -> report)`  
**Purity class:** PURE  
**Determinism:** deterministic  
**Definition:** enforces allowed dependencies and forbids boundary leaks.

---
## 6) Procedure
```text
1. ValidateRepoLayout_v1
2. ValidateModuleBoundaries_v1
3. ValidateOwnershipMap_v1
4. Emit reports and fail on violations
```

---
## 7) Trace & Metrics
### Logging rule
- repository validation emits deterministic structural diagnostics.
### Trace schema
- `run_header`: commit_hash, mapping_hash
- `iter`: module_id, check_id, status
- `run_end`: violation_count
### Metric schema
- `missing_paths`, `boundary_violations`, `ownership_gaps`
### Comparability guarantee
- comparable iff repo snapshot and contracts are identical.

---
## 8) Validation
#### VII.A Lint rules (mandatory)
- every mapped API operator has exactly one repo module target.
#### VII.B Operator test vectors (mandatory)
- valid/invalid layout trees and boundary graphs.
#### VII.C Golden traces (mandatory)
- golden layout validation traces.

---
## 9) Refactor & Equivalence
#### VIII.A Equivalence levels
- E0 for reports and violation counts.
#### VIII.B Allowed refactor categories
- tooling implementation changes preserving validation semantics.
#### VIII.C Equivalence test procedure (mandatory)
- exact compare of reports for golden repo snapshots.

---
## 10) Checkpoint/Restore
### Checkpoint contents
- validator cursor and partial diagnostics.
### Serialization
- deterministic CBOR.
### Restore semantics
- resumed validation yields identical final report.
