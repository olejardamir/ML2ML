# UML_OS Pipeline Orchestrator Contract
**EQC Compliance:** Merged single-file EQC v1.1 Option A.

**Algorithm:** `UML_OS.Pipeline.Orchestrator_v1`  
**Purpose (1 sentence):** Define deterministic job lifecycle orchestration and signed transition recording for multi-stage ML pipelines.  
**Spec Version:** `UML_OS.Pipeline.Orchestrator_v1` | 2026-02-18 | Authors: Olejar Damir  
**Domain / Problem Class:** Job scheduling and pipeline state governance.

---
## 1) Header & Global Semantics
### 0.0 Identity
- **Algorithm:** `UML_OS.Pipeline.Orchestrator_v1`
- **Purpose (1 sentence):** Deterministic pipeline/job state orchestration.
### 0.A Objective Semantics
- Minimize ambiguous job lifecycle transitions.
### 0.B Reproducibility Contract
- Replayable given `(job_manifest_hash, transition_log_hash)`.
### 0.C Numeric Policy
- timestamps and counters deterministic integer types.
### 0.D Ordering and Tie-Break Policy
- transitions ordered by `(job_id, transition_seq)`.
### 0.E Parallel, Concurrency, and Reduction Policy
- queue arbitration deterministic by priority then FIFO.
### 0.F Environment and Dependency Policy
- job manifests must be signed and schema-valid.
### 0.G Operator Manifest
- `UML_OS.Pipeline.JobSubmit_v1`
- `UML_OS.Pipeline.JobTransition_v1`
- `UML_OS.Pipeline.JobCancel_v1`
- `UML_OS.Pipeline.JobQuery_v1`
- `UML_OS.Error.Emit_v1`
### 0.H Namespacing and Packaging
- `UML_OS.Pipeline.*` namespace.
### 0.I Outputs and Metric Schema
- Outputs: `(job_state, transition_record)`
- Metrics: `queue_depth`, `job_success_rate`
### 0.J Spec Lifecycle Governance
- state machine changes are MAJOR.
### 0.K Failure and Error Semantics
- invalid transitions abort deterministically.
### 0.L Input/Data Provenance
- all transitions reference signed job manifest hash.

---
## 2) System Model
### I.A Persistent State
- job table and transition log.
### I.B Inputs and Hyperparameters
- job manifest, priority, policy constraints.
### I.C Constraints and Feasible Set
- allowed transitions:
  - `QUEUED -> RUNNING`
  - `RUNNING -> SUCCEEDED|FAILED|CANCELED`
### I.D Transient Variables
- scheduling diagnostics.
### I.E Invariants and Assertions
- no skipped lifecycle states; transition records are append-only.

---
## 3) Initialization
1. Initialize queue and policy checks.
2. Load signing/trust config for manifests.
3. Initialize transition log.

---
## 4) Operator Manifest
- `UML_OS.Pipeline.JobSubmit_v1`
- `UML_OS.Pipeline.JobTransition_v1`
- `UML_OS.Pipeline.JobCancel_v1`
- `UML_OS.Pipeline.JobQuery_v1`
- `UML_OS.Error.Emit_v1`

---
## 5) Operator Definitions
**Operator:** `UML_OS.Pipeline.JobTransition_v1`  
**Category:** Orchestration  
**Signature:** `(job_id, from_state, to_state, evidence_ref -> transition_record)`  
**Purity class:** IO  
**Determinism:** deterministic  
**Definition:** validates transition against state machine and writes signed transition record.

---
## 6) Procedure
```text
1. JobSubmit_v1
2. JobTransition_v1(QUEUED->RUNNING)
3. JobTransition_v1(RUNNING->terminal)
4. Return final job state
```

---
## 7) Trace & Metrics
### Logging rule
- every transition emits a deterministic trace event.
### Trace schema
- `run_header`: orchestrator_version, queue_policy_hash
- `iter`: job_id, from_state, to_state, status
- `run_end`: transition_log_hash
### Metric schema
- queue and lifecycle metrics.
### Comparability guarantee
- comparable iff same policy, queue order, and manifest signatures.

---
## 8) Validation
#### VII.A Lint rules (mandatory)
- state machine completeness and illegal transition rejection.
#### VII.B Operator test vectors (mandatory)
- legal/illegal transitions, retries, cancellation cases.
#### VII.C Golden traces (mandatory)
- golden job lifecycle traces.

---
## 9) Refactor & Equivalence
#### VIII.A Equivalence levels
- E0 for transition decisions and transition log.
#### VIII.B Allowed refactor categories
- queue backend changes preserving transition order semantics.
#### VIII.C Equivalence test procedure (mandatory)
- exact transition log compare.

---
## 10) Checkpoint/Restore
### Checkpoint contents
- queue state + transition cursor.
### Serialization
- deterministic CBOR.
### Restore semantics
- resumed orchestrator yields identical transition sequence.
