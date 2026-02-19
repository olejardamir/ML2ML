# UML_OS Determinism Debug Checklist
**EQC Compliance:** Merged single-file EQC v1.1 Option A.

**Algorithm:** `UML_OS.Implementation.DeterminismDebugChecklist_v1`  
**Purpose (1 sentence):** Define deterministic debugging workflow to localize and resolve replay divergence sources across data, model, DP, backend, and runtime layers.  
**Spec Version:** `UML_OS.Implementation.DeterminismDebugChecklist_v1` | 2026-02-19 | Authors: Olejar Damir  
**Domain / Problem Class:** Replay debugging and incident triage.

---
## 1) Header & Global Semantics
### 0.0 Identity
- **Algorithm:** `UML_OS.Implementation.DeterminismDebugChecklist_v1`
- **Purpose (1 sentence):** Deterministic divergence triage.
### 0.A Objective Semantics
- minimize time-to-root-cause for determinism failures.
### 0.B Reproducibility Contract
- checklist verdict reproducible from artifacts and profile hash.
### 0.C Numeric Policy
- comparator math in binary64.
### 0.D Ordering and Tie-Break Policy
- triage sequence fixed: config -> data -> RNG -> backend -> DP -> model.
### 0.E Parallel, Concurrency, and Reduction Policy
- checks may run parallel, findings merged in fixed order.
### 0.F Environment and Dependency Policy
- must compare lockfile + env manifest before other checks.
### 0.G Operator Manifest
- `UML_OS.Replay.CheckArtifactLinkage_v1`
- `UML_OS.Replay.CheckRNGProgression_v1`
- `UML_OS.Replay.CheckBackendProfile_v1`
- `UML_OS.Replay.LocalizeFirstDivergence_v1`
- `UML_OS.Error.Emit_v1`
### 0.H Namespacing and Packaging
- replay/debug operators under `UML_OS.Replay.*`.
### 0.I Outputs and Metric Schema
- `(debug_report, root_cause, remediation_actions)`.
### 0.J Spec Lifecycle Governance
- checklist ordering changes are MINOR; acceptance criteria changes MAJOR.
### 0.K Failure and Error Semantics
- inability to localize emits deterministic fallback code.
### 0.L Input/Data Provenance
- uses run artifacts and trace chain.

---
## 2) System Model
### I.A Persistent State
- debug session state and finding registry.
### I.B Inputs and Hyperparameters
- baseline run refs, candidate run refs, replay mode.
### I.C Constraints and Feasible Set
- both runs must be artifact-complete.
### I.D Transient Variables
- per-stage check results.
### I.E Invariants and Assertions
- first divergence index monotonic once found.

---
## 3) Initialization
1. Load evidence bundles.
2. Verify shared schema versions.
3. Initialize check pipeline.

---
## 4) Operator Manifest
- `UML_OS.Replay.CheckArtifactLinkage_v1`
- `UML_OS.Replay.CheckRNGProgression_v1`
- `UML_OS.Replay.CheckBackendProfile_v1`
- `UML_OS.Replay.LocalizeFirstDivergence_v1`
- `UML_OS.Error.Emit_v1`

---
## 5) Operator Definitions
**Operator:** `UML_OS.Replay.CheckArtifactLinkage_v1`  
**Signature:** `(baseline_refs, candidate_refs -> linkage_report)`  
**Purity class:** PURE  
**Definition:** Verifies hash-chain and artifact binding coherence.

**Operator:** `UML_OS.Replay.LocalizeFirstDivergence_v1`  
**Signature:** `(trace_a, trace_b -> divergence_location)`  
**Purity class:** PURE  
**Definition:** Finds first mismatched record by comparator profile.

---
## 6) Procedure
```text
1. linkage <- CheckArtifactLinkage_v1(...)
2. rng_check <- CheckRNGProgression_v1(...)
3. backend_check <- CheckBackendProfile_v1(...)
4. loc <- LocalizeFirstDivergence_v1(...)
5. return debug_report with deterministic remediation ordering
```

---
## 7) Trace & Metrics
- Metrics: `first_divergence_t`, `first_divergence_operator`, `failed_checks_count`.
- Trace logs each checklist stage result.

---
## 8) Validation
- golden divergence cases for data/RNG/backend/DP.
- deterministic root-cause ranking test.

---
## 9) Refactor & Equivalence
- E0 for root-cause category and first divergence location.

---
## 10) Checkpoint/Restore
- debug checkpoint includes completed stage ids and localized divergence cursor.
