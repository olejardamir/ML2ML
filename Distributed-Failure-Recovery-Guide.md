# UML_OS Distributed Failure Recovery Guide
**EQC Compliance:** Merged single-file EQC v1.1 Option A.

**Algorithm:** `UML_OS.Runtime.DistributedFailureRecovery_v1`  
**Purpose (1 sentence):** Define deterministic distributed failure detection, lease handling, restart sequencing, and recovery validation.  
**Spec Version:** `UML_OS.Runtime.DistributedFailureRecovery_v1` | 2026-02-19 | Authors: Olejar Damir  
**Domain / Problem Class:** Distributed runtime reliability.

---
## 1) Header & Global Semantics
### 0.0 Identity
- **Algorithm:** `UML_OS.Runtime.DistributedFailureRecovery_v1`
- **Purpose (1 sentence):** Deterministic distributed failure recovery contract.
### 0.A Objective Semantics
- minimize unrecoverable distributed run states and split-brain risk.
### 0.B Reproducibility Contract
- recovery outcomes reproducible from `(failure_event_log_hash, lease_policy_hash, checkpoint_hash)`.
### 0.C Numeric Policy
- lease counters and epochs are uint64 exact.
### 0.D Ordering and Tie-Break Policy
- recovery actions ordered by `(epoch, rank, event_seq)`.
### 0.E Parallel, Concurrency, and Reduction Policy
- rank-level checks parallelized; recovery plan aggregation deterministic.
### 0.F Environment and Dependency Policy
- distributed backend profile and timeout policy pinned.
### 0.G Operator Manifest
- `UML_OS.Runtime.DetectFailureEvent_v1`
- `UML_OS.Runtime.ResolveLeaseState_v1`
- `UML_OS.Runtime.ComputeRecoveryPlan_v1`
- `UML_OS.Runtime.ExecuteRecoveryPlan_v1`
- `UML_OS.Error.Emit_v1`
### 0.H Namespacing and Packaging
- `UML_OS.Runtime.*` namespace.
### 0.I Outputs and Metric Schema
- outputs: `(recovery_report, restart_plan_hash, final_cluster_state)`.
### 0.J Spec Lifecycle Governance
- lease/restart policy changes are MAJOR.
### 0.K Failure and Error Semantics
- unresolved lease conflicts fail closed deterministically.
### 0.L Input/Data Provenance
- all failure events and lease transitions are trace-bound.

---
## 2) System Model
### I.A Persistent State
- lease table, rank health state, recovery epoch.
### I.B Inputs and Hyperparameters
- failure events, lease TTL policy, checkpoint refs.
### I.C Constraints and Feasible Set
- exactly one active lease owner per partition.
### I.D Transient Variables
- per-rank health checks and plan candidates.
### I.E Invariants and Assertions
- no split-brain committed state transitions.

---
## 3) Initialization
1. Load cluster lease and health snapshots.
2. Validate last committed checkpoint binding.
3. Initialize recovery epoch context.

---
## 4) Operator Manifest
- `UML_OS.Runtime.DetectFailureEvent_v1`
- `UML_OS.Runtime.ResolveLeaseState_v1`
- `UML_OS.Runtime.ComputeRecoveryPlan_v1`
- `UML_OS.Runtime.ExecuteRecoveryPlan_v1`
- `UML_OS.Error.Emit_v1`

---
## 5) Operator Definitions
**Operator:** `UML_OS.Runtime.ComputeRecoveryPlan_v1`  
**Signature:** `(cluster_state, failure_events, lease_state -> recovery_plan)`  
**Purity class:** PURE  
**Determinism:** deterministic  
**Definition:** Produces deterministic restart/eviction/rejoin plan.

---
## 6) Procedure
```text
1. Detect and classify failure events
2. Resolve lease ownership deterministically
3. Compute recovery plan
4. Execute plan and validate final cluster state
```

---
## 7) Trace & Metrics
- Metrics: `failed_ranks`, `recovery_attempts`, `recovery_success`, `split_brain_prevented`.
- Trace includes epoch, lease transitions, restart actions.

---
## 8) Validation
- rank loss and network partition scenario tests.
- deterministic restart ordering and lease conflict tests.

---
## 9) Refactor & Equivalence
- E0 for recovery plan hash and final cluster-state verdict.

---
## 10) Checkpoint/Restore
- checkpoint stores recovery epoch, lease table, pending plan hash.
- restore resumes recovery workflow deterministically.
