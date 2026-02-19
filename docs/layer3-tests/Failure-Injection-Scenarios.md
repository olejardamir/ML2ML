# UML_OS Failure Injection Scenarios Contract
**EQC Compliance:** Merged single-file EQC v1.1 Option A.

**Algorithm:** `UML_OS.Test.FailureInjection_v1`  
**Purpose (1 sentence):** Define deterministic fault-injection scenarios and expected recovery outcomes across core runtime and governance paths.  
**Spec Version:** `UML_OS.Test.FailureInjection_v1` | 2026-02-19 | Authors: Olejar Damir  
**Domain / Problem Class:** Resilience and recovery verification.

---
## 1) Header & Global Semantics
### 0.0 Identity
- **Algorithm:** `UML_OS.Test.FailureInjection_v1`
- **Purpose (1 sentence):** Deterministic fault-injection contract.
### 0.A Objective Semantics
- Optimization sense: `MINIMIZE`
- Objective type: `Scalar`
- Primary objective: verify deterministic recovery under defined fault classes.
### 0.B Reproducibility Contract
- Replayable given `(scenario_id, injection_point, seed, evidence_bundle_hash)`.
### 0.C Numeric Policy
- Scenario timing and counters use exact deterministic tick values.
### 0.D Ordering and Tie-Break Policy
- Injection sequence order is fixed by scenario definition.
### 0.E Parallel, Concurrency, and Reduction Policy
- Multi-fault scenarios allowed only when deterministic ordering is declared.
### 0.F Environment and Dependency Policy
- Faults must not alter contract definitions; only runtime behavior under test.
### 0.G Operator Manifest
- `UML_OS.Test.InjectFault_v1`
- `UML_OS.Test.RunRecovery_v1`
- `UML_OS.Test.ValidateRecoveryOutcome_v1`
- `UML_OS.Error.Emit_v1`
### 0.H Namespacing and Packaging
- `tests/failure_injection/` suites.
### 0.I Outputs and Metric Schema
- Outputs: `(fault_report, recovery_verdict)`
- Metrics: `scenarios_total`, `recovery_passed`, `recovery_failed`
### 0.J Spec Lifecycle Governance
- Required scenario set changes are MAJOR.
### 0.K Failure and Error Semantics
- Unexpected recovery outcomes are deterministic failures.
### 0.L Input/Data Provenance
- Scenario definitions and expected outcomes must be hash-addressed.

---
## 2) System Model
### I.A Persistent State
- Scenario registry and expected recovery matrix.
### I.B Inputs and Hyperparameters
- scenario id, fault point, runtime profile.
### I.C Constraints and Feasible Set
- Valid iff scenario has declared expected deterministic outcome.
### I.D Transient Variables
- injection logs and recovery diagnostics.
### I.E Invariants and Assertions
- First divergence and final verdict must be deterministic.

---
## 3) Initialization
1. Load scenario definitions.
2. Validate environment and fixture preconditions.
3. Initialize deterministic injection controller.

---
## 4) Operator Manifest
- `UML_OS.Test.InjectFault_v1`
- `UML_OS.Test.RunRecovery_v1`
- `UML_OS.Test.ValidateRecoveryOutcome_v1`
- `UML_OS.Error.Emit_v1`

---
## 5) Operator Definitions
**Operator:** `UML_OS.Test.InjectFault_v1`  
**Signature:** `(scenario_id, runtime_state -> faulted_state)`  
**Purity class:** IO  
**Determinism:** deterministic.

**Operator:** `UML_OS.Test.RunRecovery_v1`  
**Signature:** `(faulted_state, recovery_policy -> recovery_state)`  
**Purity class:** IO  
**Determinism:** deterministic.

**Operator:** `UML_OS.Test.ValidateRecoveryOutcome_v1`  
**Signature:** `(recovery_state, expected_outcome -> validation_report)`  
**Purity class:** PURE  
**Determinism:** deterministic.

---
## 6) Procedure
```text
1. InjectFault_v1
2. RunRecovery_v1
3. ValidateRecoveryOutcome_v1
4. Emit fault_report
```

---
## 7) Trace & Metrics
### Logging rule
- Fault and recovery paths emit deterministic scenario records.
### Trace schema
- `run_header`: scenario_id, profile_hash
- `iter`: injection_point, status
- `run_end`: recovery_verdict, outcome_hash
### Metric schema
- `scenarios_total`, `recovery_passed`, `recovery_failed`
### Comparability guarantee
- Comparable iff same scenario and profile.

---
## 8) Validation
#### VII.A Lint rules (mandatory)
- Every required scenario has expected deterministic outcome.
#### VII.B Operator test vectors (mandatory)
- Fault/recovery vectors for WAL, checkpoint, replay, and pipeline.
#### VII.C Golden traces (mandatory)
- Golden failure-injection traces.

---
## 9) Refactor & Equivalence
#### VIII.A Equivalence levels
- E0 for scenario verdict and recovery evidence hashes.
#### VIII.B Allowed refactor categories
- Harness/runtime refactors preserving outcome semantics.
#### VIII.C Equivalence test procedure (mandatory)
- Exact compare of validation reports.

---
## 10) Checkpoint/Restore
### Checkpoint contents
- Scenario cursor and partial recovery diagnostics.
### Serialization
- Canonical CBOR.
### Restore semantics
- Resumed scenario must produce identical recovery verdict.
