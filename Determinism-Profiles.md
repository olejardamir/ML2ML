# UML_OS Determinism Profiles Contract
**EQC Compliance:** Merged single-file EQC v1.1 Option A.

**Algorithm:** `UML_OS.Replay.DeterminismProfiles_v1`  
**Purpose (1 sentence):** Define normative determinism profiles (`BITWISE`, `TOLERANCE`) with required runtime flags, reduction semantics, and comparability rules.  
**Spec Version:** `UML_OS.Replay.DeterminismProfiles_v1` | 2026-02-19 | Authors: Olejar Damir  
**Domain / Problem Class:** Reproducibility profile governance.

---
## 1) Header & Global Semantics
### 0.0 Identity
- **Algorithm:** `UML_OS.Replay.DeterminismProfiles_v1`
- **Purpose (1 sentence):** Determinism profile specification.
### 0.A Objective Semantics
- Optimization sense: `MINIMIZE`
- Objective type: `Scalar`
- Primary comparison rule: profile-conformant replay verdict.
- Invalid objective policy: profile violation is deterministic failure.
### 0.B Reproducibility Contract
- Replayable given `(determinism_profile_id, backend_hash, driver_runtime_fingerprint, policy_bundle_hash)`.
### 0.C Numeric Policy
- `BITWISE` requires fixed reduction order + deterministic kernels.
- `TOLERANCE` requires explicit per-field tolerance map.
### 0.D Ordering and Tie-Break Policy
- Reduction ordering must be declared by profile and captured in trace.
### 0.E Parallel, Concurrency, and Reduction Policy
- Profile defines collective algorithm, chunk ordering, and atomic allowance.
### 0.F Environment and Dependency Policy
- Determinism profile hash is required in replay token and certificate payload.
### 0.G Operator Manifest
- `UML_OS.Replay.ValidateDeterminismProfile_v1`
- `UML_OS.Replay.CompareByProfile_v1`
- `UML_OS.Error.Emit_v1`
### 0.H Namespacing and Packaging
- Profile registry path: `contracts/determinism_profiles.cbor`.
### 0.I Outputs and Metric Schema
- Outputs: `(profile_report, replay_comparison_report)`.
### 0.J Spec Lifecycle Governance
- Profile semantics changes are MAJOR.
### 0.K Failure and Error Semantics
- Emit deterministic `REPLAY_DIVERGENCE` on profile violation.
### 0.L Input/Data Provenance
- profile definitions and tolerance maps are hash-addressed.

---
## 2) System Model
### I.A Persistent State
- determinism profile registry.
### I.B Inputs and Hyperparameters
- profile id, trace pair, backend/runtime metadata.
### I.C Constraints and Feasible Set
- valid iff runtime metadata satisfies selected profile.
### I.D Transient Variables
- comparison diagnostics.
### I.E Invariants and Assertions
- one deterministic verdict per profile+trace pair.

### II.F Profile Definitions (Normative)
- `BITWISE` profile:
  - fixed collective algorithm and rank order,
  - fixed chunk order,
  - fixed accumulation dtype/order,
  - no nondeterministic atomics,
  - required runtime flags captured as exact key/value map (e.g., deterministic kernels enabled, TF32 disabled, fixed matmul precision policy),
  - backend-specific deterministic primitive allowlist hash required.
- `TOLERANCE` profile:
  - explicit per-field tolerance bands,
  - E1 comparator policy,
  - acceptable hardware/runtime equivalence set declared,
  - explicit NaN/Inf compare policy per field.

### II.H Machine-Checkable Runtime Capture (Normative)
- Required environment fingerprint fields:
  - `gpu_model`, `driver_version`, `cuda_version`, `cudnn_version`, `cublas_version`, `nccl_version`, `os_kernel_version`, `backend_build_hash`.
- Distributed profile fields:
  - `collective_algorithm_id`,
  - `collective_chunking_policy`,
  - `rank_order_policy`.
- `TOLERANCE` comparator map schema:
  - `field_name -> {abs_tol:float64, rel_tol:float64, nan_policy:enum("FORBID","EQUAL_IF_BOTH_NAN")}`.

### II.G Profile Hash (Normative)
- `determinism_profile_hash = SHA-256(CBOR_CANONICAL([profile_id, profile_rules, tolerance_map?]))`.

---
## 3) Initialization
1. Load profile registry.
2. Validate selected profile id.
3. Validate runtime metadata against profile constraints.

---
## 4) Operator Manifest
- `UML_OS.Replay.ValidateDeterminismProfile_v1`
- `UML_OS.Replay.CompareByProfile_v1`
- `UML_OS.Error.Emit_v1`

---
## 5) Operator Definitions
**Operator:** `UML_OS.Replay.ValidateDeterminismProfile_v1`  
**Category:** Replay  
**Signature:** `(profile_id, runtime_metadata -> profile_report)`  
**Purity class:** PURE  
**Determinism:** deterministic  
**Definition:** validates runtime/backend conformance to selected profile.

**Operator:** `UML_OS.Replay.CompareByProfile_v1`  
**Category:** Replay  
**Signature:** `(trace_a, trace_b, profile_id -> comparison_report)`  
**Purity class:** PURE  
**Determinism:** deterministic  
**Definition:** compares traces under profile-specific E0/E1 rules.

---
## 6) Procedure
```text
1. ValidateDeterminismProfile_v1
2. CompareByProfile_v1
3. Return profile_report + comparison_report
```

---
## 7) Trace & Metrics
### Logging rule
- profile checks and replay comparisons emit deterministic records.
### Trace schema
- `run_header`: profile_id, profile_hash
- `iter`: check_id, status
- `run_end`: comparison_status
### Metric schema
- `profile_violations`, `e0_mismatch_count`, `e1_out_of_band_count`
### Comparability guarantee
- Comparable iff profile id/hash and comparator schema are identical.

---
## 8) Validation
#### VII.A Lint rules (mandatory)
- no profile selected without declared runtime constraints.
#### VII.B Operator test vectors (mandatory)
- profile pass/fail fixtures and mixed hardware scenarios.
#### VII.C Golden traces (mandatory)
- golden profile-conformance traces.

---
## 9) Refactor & Equivalence
#### VIII.A Equivalence levels
- E0 for profile verdict and comparison report.
#### VIII.B Allowed refactor categories
- comparator implementation refactors preserving outputs.
#### VIII.C Equivalence test procedure (mandatory)
- exact compare of profile/conformance outputs.

---
## 10) Checkpoint/Restore
### Checkpoint contents
- profile id/hash and comparator cursor.
### Serialization
- deterministic canonical CBOR.
### Restore semantics
- resumed comparison yields identical verdict.
