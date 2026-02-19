# UML_OS Authorization Capability Matrix Contract
**EQC Compliance:** Merged single-file EQC v1.1 Option A.

**Algorithm:** `UML_OS.Security.AuthZCapabilityMatrix_v1`  
**Purpose (1 sentence):** Define deterministic operator-to-capability authorization requirements and policy evaluation outputs.  
**Spec Version:** `UML_OS.Security.AuthZCapabilityMatrix_v1` | 2026-02-19 | Authors: Olejar Damir  
**Domain / Problem Class:** RBAC/capability enforcement and auditability.

---
## 1) Header & Global Semantics
### 0.0 Identity
- **Algorithm:** `UML_OS.Security.AuthZCapabilityMatrix_v1`
- **Purpose (1 sentence):** Deterministic operator capability gating.
### 0.A Objective Semantics
- Optimization sense: `MINIMIZE`
- Objective type: `Scalar`
- Primary comparison rule: deterministic authorization verdict correctness.
- Invalid objective policy: missing capability mapping is fatal.
### 0.B Reproducibility Contract
- Replayable given `(tenant_id, principal_id, operator_id, policy_hash, capability_matrix_hash)`.
### 0.C Numeric Policy
- N/A except deterministic hashing and enum handling.
### 0.D Ordering and Tie-Break Policy
- Capabilities sorted lexicographically before verdict hash.
### 0.E Parallel, Concurrency, and Reduction Policy
- Parallel checks allowed; final verdict is deterministic.
### 0.F Environment and Dependency Policy
- Determinism level: `BITWISE`.
### 0.G Operator Manifest
- `UML_OS.Security.ResolveRequiredCapabilities_v1`
- `UML_OS.Security.EvaluateAuthorization_v1`
- `UML_OS.Error.Emit_v1`
### 0.H Namespacing and Packaging
- Canonical matrix source: `contracts/operator_registry.cbor`.
### 0.I Outputs and Metric Schema
- Outputs: `(authz_verdict, authz_hash, authz_report)`.
### 0.J Spec Lifecycle Governance
- Capability changes for existing operator versions are MAJOR.
### 0.K Failure and Error Semantics
- Denied authorization emits deterministic failure with `authz_hash`.
### 0.L Input/Data Provenance
- Operator capability mapping must be hash-bound to registry hash.

---
## 2) System Model
### I.A Persistent State
- capability matrix and role-policy bindings.
### I.B Inputs and Hyperparameters
- `tenant_id`, `principal_id`, `operator_id`, `policy_hash`.
### I.C Constraints and Feasible Set
- valid iff operator is mapped and policy binding exists.
### I.D Transient Variables
- resolved capability set and diagnostics.
### I.E Invariants and Assertions
- one deterministic verdict per authorization query.

### II.F Capability Resolution Rule (Normative)
- `required_capabilities` is read from canonical operator registry for `operator_id`.
- Missing `operator_id` mapping is deterministic failure.

### II.G Deterministic Verdict Hash (Normative)
- `authz_hash = SHA-256(CBOR_CANONICAL([tenant_id, principal_id, operator_id, sorted(required_capabilities), policy_hash]))`.

---
## 3) Initialization
1. Load capability matrix from registry.
2. Load tenant/principal policy bindings.
3. Validate matrix hash consistency.

---
## 4) Operator Manifest
- `UML_OS.Security.ResolveRequiredCapabilities_v1`
- `UML_OS.Security.EvaluateAuthorization_v1`
- `UML_OS.Error.Emit_v1`

---
## 5) Operator Definitions
**Operator:** `UML_OS.Security.ResolveRequiredCapabilities_v1`  
**Category:** Security  
**Signature:** `(operator_id, registry -> required_capabilities)`  
**Purity class:** PURE  
**Determinism:** deterministic  
**Definition:** resolves sorted unique required capabilities for operator.

**Operator:** `UML_OS.Security.EvaluateAuthorization_v1`  
**Category:** Security  
**Signature:** `(tenant_id, principal_id, operator_id, policy -> authz_verdict, authz_hash, report)`  
**Purity class:** PURE  
**Determinism:** deterministic  
**Definition:** evaluates capability grants and emits deterministic authorization hash.

---
## 6) Procedure
```text
1. ResolveRequiredCapabilities_v1
2. EvaluateAuthorization_v1
3. Return verdict + authz_hash + report
```

---
## 7) Trace & Metrics
### Logging rule
- every authorization decision emits deterministic trace event.
### Trace schema
- `run_header`: tenant_id, policy_hash
- `iter`: principal_id, operator_id, verdict, authz_hash
- `run_end`: denied_count
### Metric schema
- `allowed_count`, `denied_count`
### Comparability guarantee
- Comparable iff policy hash and capability matrix hash match.

---
## 8) Validation
#### VII.A Lint rules (mandatory)
- all callable operators have required_capabilities.
#### VII.B Operator test vectors (mandatory)
- allowed/denied capability fixtures per tenant.
#### VII.C Golden traces (mandatory)
- golden authorization decision traces.

---
## 9) Refactor & Equivalence
#### VIII.A Equivalence levels
- E0 for verdict, authz_hash, and report.
#### VIII.B Allowed refactor categories
- policy engine refactors preserving outputs.
#### VIII.C Equivalence test procedure (mandatory)
- exact compare of verdict/authz hash.

---
## 10) Checkpoint/Restore
### Checkpoint contents
- policy snapshot hash and decision cursor.
### Serialization
- deterministic canonical CBOR.
### Restore semantics
- resumed authorization yields identical outcomes.

