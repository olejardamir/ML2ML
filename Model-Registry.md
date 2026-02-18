# UML_OS Model Registry Contract
**EQC Compliance:** Merged single-file EQC v1.1 Option A.

**Algorithm:** `UML_OS.Registry.ModelRegistry_v1`  
**Purpose (1 sentence):** Define deterministic model/version registry and approval gates bound to execution evidence.  
**Spec Version:** `UML_OS.Registry.ModelRegistry_v1` | 2026-02-18 | Authors: Olejar Damir  
**Domain / Problem Class:** Model governance and promotion workflows.

---
## 1) Header & Global Semantics
### 0.0 Identity
- **Algorithm:** `UML_OS.Registry.ModelRegistry_v1`
- **Purpose (1 sentence):** Evidence-gated model lifecycle governance.
### 0.A Objective Semantics
- Minimize ungoverned model promotions.
### 0.B Reproducibility Contract
- Replayable given `(model_id, model_version_id, execution_certificate_hash)`.
### 0.C Numeric Policy
- Version counters exact.
### 0.D Ordering and Tie-Break Policy
- Stage transitions follow deterministic policy graph.
### 0.E Parallel, Concurrency, and Reduction Policy
- Concurrent approvals reduced by deterministic policy precedence.
### 0.F Environment and Dependency Policy
- Registry write requires valid `ExecutionCertificate`.
### 0.G Operator Manifest
- `UML_OS.Registry.ModelCreate_v1`
- `UML_OS.Registry.VersionCreate_v1`
- `UML_OS.Registry.StageTransition_v1`
- `UML_OS.Registry.PolicyGateEvaluate_v1`
- `UML_OS.Registry.ApprovalRecord_v1`
- `UML_OS.Error.Emit_v1`
### 0.H Namespacing and Packaging
- `UML_OS.Registry.*` namespace.
### 0.I Outputs and Metric Schema
- Outputs: `(registry_event, gate_report)`
- Metrics: `versions_created`, `stage_transitions`, `gate_failures`
### 0.J Spec Lifecycle Governance
- Governance semantics changes are MAJOR.
### 0.K Failure and Error Semantics
- Abort on missing/invalid evidence bundle.
### 0.L Input/Data Provenance
- Every version must bind evidence refs: replay token, trace root, checkpoint Merkle root.

---
## 2) System Model
### I.A Persistent State
- model/version registry, approvals, policy gates.
### I.B Inputs and Hyperparameters
- `Model`, `ModelVersion`, `Stage`, `Approval`, `PolicyGate`, `SBOMRef`, `EvidenceBundleRef`.
### I.C Constraints and Feasible Set
- Stage transition invalid without policy gate pass.
### I.D Transient Variables
- gate diagnostics and approval context.
### I.E Invariants and Assertions
- immutable model version payload; append-only approvals.

---
## 3) Initialization
1. Load registry schema.
2. Validate RBAC role bindings.
3. Load policy-gate definitions.

---
## 4) Operator Manifest
- `UML_OS.Registry.ModelCreate_v1`
- `UML_OS.Registry.VersionCreate_v1`
- `UML_OS.Registry.StageTransition_v1`
- `UML_OS.Registry.PolicyGateEvaluate_v1`
- `UML_OS.Registry.ApprovalRecord_v1`
- `UML_OS.Error.Emit_v1`

---
## 5) Operator Definitions
External operator reference: `UML_OS.Error.Emit_v1` in `Error-Codes.md`.

**Operator:** `UML_OS.Registry.VersionCreate_v1`  
**Category:** Governance  
**Signature:** `(model_id, artifact_ref, evidence_bundle_ref -> model_version_id)`  
**Purity class:** IO  
**Determinism:** deterministic  
**Definition:** creates immutable model version only if evidence bundle is valid.

**Operator:** `UML_OS.Registry.PolicyGateEvaluate_v1`  
**Category:** Governance  
**Signature:** `(model_version_id, policy_set -> gate_report)`  
**Purity class:** PURE  
**Determinism:** deterministic  
**Definition:** evaluates policy gates including certificate/evidence coherence.

---
## 6) Procedure
```text
1. ModelCreate_v1
2. VersionCreate_v1
3. PolicyGateEvaluate_v1
4. ApprovalRecord_v1
5. StageTransition_v1
```

---
## 7) Trace & Metrics
### Logging rule
- Every registry mutation emits deterministic governance events.
### Trace schema
- `run_header`: tenant_id, registry_version
- `iter`: model_version_id, action, status
- `run_end`: final_stage
### Metric schema
- `stage_transitions`, `gate_failures`
### Comparability guarantee
- Comparable iff policy set + evidence validation rules are identical.

---
## 8) Validation
#### VII.A Lint rules (mandatory)
- no stage transition without valid evidence + gate pass.
#### VII.B Operator test vectors (mandatory)
- valid/invalid certificate; approval role violations; gate failures.
#### VII.C Golden traces (mandatory)
- golden model promotion traces.

---
## 9) Refactor & Equivalence
#### VIII.A Equivalence levels
- E0 for governance decisions and stage transitions.
#### VIII.B Allowed refactor categories
- registry storage changes preserving policy outcomes.
#### VIII.C Equivalence test procedure (mandatory)
- exact compare of gate reports + transition logs.

---
## 10) Checkpoint/Restore
### Checkpoint contents
- registry index and policy gate state.
### Serialization
- deterministic CBOR.
### Restore semantics
- restored registry yields identical gate decisions for same inputs.
