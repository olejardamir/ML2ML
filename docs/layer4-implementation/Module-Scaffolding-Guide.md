# UML_OS Module Scaffolding Guide Contract
**EQC Compliance:** Merged single-file EQC v1.1 Option A.

**Algorithm:** `UML_OS.Implementation.ModuleScaffold_v1`  
**Purpose (1 sentence):** Define deterministic module scaffolding templates and required wiring for new operator implementations.  
**Spec Version:** `UML_OS.Implementation.ModuleScaffold_v1` | 2026-02-19 | Authors: Olejar Damir  
**Normativity Legend:** `docs/layer1-foundation/Normativity-Legend.md`

**Domain / Problem Class:** Code generation and module bootstrap governance.

---
## 1) Header & Global Semantics
### 0.0 Identity
- **Algorithm:** `UML_OS.Implementation.ModuleScaffold_v1`
- **Purpose (1 sentence):** Deterministic module skeleton contract.
### 0.A Objective Semantics
- Optimization sense: `MINIMIZE`
- Objective type: `Scalar`
- Primary objective: eliminate ad-hoc operator module structure.
### 0.B Reproducibility Contract
- Replayable given `(operator_id, scaffold_template_hash, signature_digest)`.
### 0.C Numeric Policy
- N/A except deterministic versioning and hash comparisons.
### 0.D Ordering and Tie-Break Policy
- Generated files and sections follow fixed ordering.
### 0.E Parallel, Concurrency, and Reduction Policy
- Multi-module generation allowed with deterministic merge order.
### 0.F Environment and Dependency Policy
- Scaffold must be generated from operator registry metadata only.
### 0.G Operator Manifest
- `UML_OS.Scaffold.GenerateModule_v1`
- `UML_OS.Scaffold.ValidateScaffold_v1`
- `UML_OS.Scaffold.BindTests_v1`
- `UML_OS.Error.Emit_v1`
### 0.H Namespacing and Packaging
- `src/<subsystem>/<operator>.py` + tests + vectors.
### 0.I Outputs and Metric Schema
- Outputs: `(scaffold_report, generated_paths)`
- Metrics: `files_generated`, `validation_failures`
### 0.J Spec Lifecycle Governance
- Template contract changes are MAJOR.
### 0.K Failure and Error Semantics
- Missing required scaffold files is fatal.
### 0.L Input/Data Provenance
- All generated artifacts must cite operator id/version/digest.

---
## 2) System Model
### I.A Persistent State
- Scaffold template registry.
### I.B Inputs and Hyperparameters
- operator metadata, template version, module root.
### I.C Constraints and Feasible Set
- Valid iff scaffold matches required structure and signature bindings.
### I.D Transient Variables
- generated file map and validation diagnostics.
### I.E Invariants and Assertions
- Scaffold placeholders must be deterministic and complete.

---
## 3) Initialization
1. Load operator registry row.
2. Resolve template.
3. Prepare deterministic output paths.

---
## 4) Operator Manifest
- `UML_OS.Scaffold.GenerateModule_v1`
- `UML_OS.Scaffold.ValidateScaffold_v1`
- `UML_OS.Scaffold.BindTests_v1`
- `UML_OS.Error.Emit_v1`

---
## 5) Operator Definitions
**Operator:** `UML_OS.Scaffold.GenerateModule_v1`  
**Signature:** `(operator_record, template -> generated_module)`  
**Purity class:** IO  
**Determinism:** deterministic.

**Operator:** `UML_OS.Scaffold.ValidateScaffold_v1`  
**Signature:** `(generated_module, scaffold_rules -> validation_report)`  
**Purity class:** PURE  
**Determinism:** deterministic.

**Operator:** `UML_OS.Scaffold.BindTests_v1`  
**Signature:** `(generated_module, vector_catalog -> test_bundle)`  
**Purity class:** IO  
**Determinism:** deterministic.

---
## 6) Procedure
```text
1. GenerateModule_v1
2. ValidateScaffold_v1
3. BindTests_v1
4. Emit scaffold_report
```

---
## 7) Trace & Metrics
### Logging rule
- Scaffold generation emits deterministic file and validation records.
### Trace schema
- `run_header`: operator_id, template_hash
- `iter`: file_path, status
- `run_end`: scaffold_status
### Metric schema
- `files_generated`, `validation_failures`
### Comparability guarantee
- Comparable iff same operator record + template hash.

---
## 8) Validation
#### VII.A Lint rules (mandatory)
- Required files/sections present.
#### VII.B Operator test vectors (mandatory)
- Scaffold generation fixtures.
#### VII.C Golden traces (mandatory)
- Golden generated-path traces.

---
## 9) Refactor & Equivalence
#### VIII.A Equivalence levels
- E0 for generated file set and normalized content hash.
#### VIII.B Allowed refactor categories
- Template engine internals preserving output artifacts.
#### VIII.C Equivalence test procedure (mandatory)
- Exact compare of generated module hashes.

---
## 10) Checkpoint/Restore
### Checkpoint contents
- Generation cursor and partial output index.
### Serialization
- Canonical CBOR.
### Restore semantics
- Resumed generation must produce identical outputs.
