# UML_OS Storage Recovery Test Matrix
**EQC Compliance:** Merged single-file EQC v1.1 Option A.

**Algorithm:** `UML_OS.Test.StorageRecoveryMatrix_v1`  
**Purpose (1 sentence):** Define deterministic storage crash-recovery tests for WAL segments, commit pointers, and artifact integrity.  
**Spec Version:** `UML_OS.Test.StorageRecoveryMatrix_v1` | 2026-02-19 | Authors: Olejar Damir  
**Domain / Problem Class:** Storage reliability testing.

---
## 1) Header & Global Semantics
### 0.0 Identity
- **Algorithm:** `UML_OS.Test.StorageRecoveryMatrix_v1`
- **Purpose (1 sentence):** Deterministic storage recovery test contract.
### 0.A Objective Semantics
- minimize unrecoverable commit states.
### 0.B Reproducibility Contract
- scenario verdict reproducible from `(scenario_id, backend_profile_hash, fixtures_hash)`.
### 0.C Numeric Policy
- sequence ids and counters as uint64.
### 0.D Ordering and Tie-Break Policy
- scenarios ordered by `(backend, scenario_id)`.
### 0.E Parallel, Concurrency, and Reduction Policy
- scenarios parallelizable with deterministic report merge.
### 0.F Environment and Dependency Policy
- backend adapter versions pinned.
### 0.G Operator Manifest
- `UML_OS.Test.InjectStorageFault_v1`
- `UML_OS.Test.RunRecoveryProcedure_v1`
- `UML_OS.Test.VerifyRecoveryInvariants_v1`
- `UML_OS.Error.Emit_v1`
### 0.H Namespacing and Packaging
- `UML_OS.Test.*` and `UML_OS.Storage.*`.
### 0.I Outputs and Metric Schema
- outputs: `(scenario_reports, matrix_verdict)`.
### 0.J Spec Lifecycle Governance
- scenario semantics changes are MAJOR.
### 0.K Failure and Error Semantics
- unrecoverable states are deterministic failures.
### 0.L Input/Data Provenance
- fixtures and expected results are hash-addressed.

---
## 2) System Model
### I.A Persistent State
- scenario catalog and backend capability matrix.
### I.B Inputs and Hyperparameters
- backend id, scenario set, strictness profile.
### I.C Constraints and Feasible Set
- commit pointer logic required for all backends.
### I.D Transient Variables
- injected fault records and recovery outputs.
### I.E Invariants and Assertions
- committed runs must remain verifiable after recovery.

---
## 3) Initialization
1. Load scenario matrix and backend profile.
2. Initialize isolated test storage namespace.
3. Seed deterministic fault injector.

---
## 4) Operator Manifest
- `UML_OS.Test.InjectStorageFault_v1`
- `UML_OS.Test.RunRecoveryProcedure_v1`
- `UML_OS.Test.VerifyRecoveryInvariants_v1`
- `UML_OS.Error.Emit_v1`

---
## 5) Operator Definitions
**Operator:** `UML_OS.Test.VerifyRecoveryInvariants_v1`  
**Signature:** `(recovery_result, expected_invariants -> verdict)`  
**Purity class:** PURE  
**Determinism:** deterministic  
**Definition:** Verifies WAL chain integrity, pointer correctness, and artifact hash coherence.

---
## 6) Procedure
```text
1. Inject deterministic storage fault
2. Execute recovery flow
3. Verify invariants
4. Record scenario verdict
```

---
## 7) Trace & Metrics
- Metrics: `scenarios_total`, `scenarios_failed`, `recovery_time_ms`.
- Trace includes scenario id, backend id, invariant failures.

---
## 8) Validation
- baseline scenarios for local fs, s3-compatible, gcs-compatible adapters.
- deterministic fault replay tests.

---
## 9) Refactor & Equivalence
- E0 for per-scenario verdicts and invariant failure identities.

---
## 10) Checkpoint/Restore
- checkpoint stores scenario cursor and partial matrix report hash.
- restore resumes matrix deterministically.
