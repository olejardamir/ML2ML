# UML_OS Runtime State Machine Reference
**EQC Compliance:** Merged single-file EQC v1.1 Option A.

**Algorithm:** `UML_OS.Runtime.StateMachineReference_v1`  
**Purpose (1 sentence):** Define canonical runtime state machines and deterministic transition semantics for kernel, orchestrator, and execution subsystems.  
**Spec Version:** `UML_OS.Runtime.StateMachineReference_v1` | 2026-02-19 | Authors: Olejar Damir  
**Domain / Problem Class:** Runtime lifecycle and transition correctness.

---
## 1) Header & Global Semantics
### 0.0 Identity
- **Algorithm:** `UML_OS.Runtime.StateMachineReference_v1`
- **Purpose (1 sentence):** Canonical runtime lifecycle transition contract.
### 0.A Objective Semantics
- minimize illegal transitions and stuck states.
### 0.B Reproducibility Contract
- transition history reproducible from event log + transition rules hash.
### 0.C Numeric Policy
- binary64 for timers/metrics only.
### 0.D Ordering and Tie-Break Policy
- transition arbitration by `(event_seq, source, transition_id)`.
### 0.E Parallel, Concurrency, and Reduction Policy
- competing transitions resolved by deterministic CAS policy.
### 0.F Environment and Dependency Policy
- runtime transition engine version pinned.
### 0.G Operator Manifest
- `UML_OS.Runtime.ValidateTransition_v1`
- `UML_OS.Runtime.ApplyTransitionCAS_v1`
- `UML_OS.Runtime.EmitTransitionTrace_v1`
- `UML_OS.Error.Emit_v1`
### 0.H Namespacing and Packaging
- runtime lifecycle operators under `UML_OS.Runtime.*`.
### 0.I Outputs and Metric Schema
- outputs: `(new_state, transition_record, state_metrics)`.
### 0.J Spec Lifecycle Governance
- state additions/removals are MAJOR.
### 0.K Failure and Error Semantics
- illegal transition emits deterministic failure.
### 0.L Input/Data Provenance
- state transitions sourced from signed event records.

---
## 2) System Model
### I.A Persistent State
- runtime state, transition sequence, lease state.
### I.B Inputs and Hyperparameters
- current state, event, policy hash, expected transition seq.
### I.C Constraints and Feasible Set
- transition must exist in allowed transition table.
### I.D Transient Variables
- candidate transition and conflict diagnostics.
### I.E Invariants and Assertions
- transition sequence strictly monotonic.

---
## 3) Initialization
1. Load state machine definition.
2. Load current runtime state snapshot.
3. Initialize transition evaluator.

---
## 4) Operator Manifest
- `UML_OS.Runtime.ValidateTransition_v1`
- `UML_OS.Runtime.ApplyTransitionCAS_v1`
- `UML_OS.Runtime.EmitTransitionTrace_v1`
- `UML_OS.Error.Emit_v1`

---
## 5) Operator Definitions
**Operator:** `UML_OS.Runtime.ValidateTransition_v1`  
**Signature:** `(state, event, transition_table -> transition_ok, next_state)`  
**Purity class:** PURE  
**Definition:** Validates that requested transition is legal and deterministic.

**Operator:** `UML_OS.Runtime.ApplyTransitionCAS_v1`  
**Signature:** `(state_store, expected_seq, transition_record -> committed)`  
**Purity class:** STATEFUL  
**Definition:** Applies transition atomically using compare-and-swap semantics.

---
## 6) Procedure
```text
1. validate transition legality
2. build transition record with deterministic idempotency key
3. apply CAS transition
4. emit trace record
5. return new state
```

---
## 7) Trace & Metrics
- Metrics: `illegal_transition_count`, `conflict_retry_count`, `stuck_state_duration`.
- Trace records include `from_state`, `to_state`, `transition_seq`, `idempotency_key`.

---
## 8) Validation
- golden transition tables and event streams.
- conflict simulation tests for deterministic CAS behavior.

---
## 9) Refactor & Equivalence
- E0 for transition acceptance/rejection and resulting state.

---
## 10) Checkpoint/Restore
- runtime checkpoint stores state + transition sequence + active lease.
- restore continues from exact sequence point.
