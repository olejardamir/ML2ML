# UML_OS Dependency Lock Policy
**EQC Compliance:** Merged single-file EQC v1.1 Option A.

**Algorithm:** `UML_OS.Implementation.DependencyLockPolicy_v1`  
**Purpose (1 sentence):** Define deterministic dependency pinning, verification, and upgrade governance for reproducible builds and runs.  
**Spec Version:** `UML_OS.Implementation.DependencyLockPolicy_v1` | 2026-02-18 | Authors: Olejar Damir  
**Domain / Problem Class:** Build/runtime dependency control.

---
## 1) Header & Global Semantics
### 0.0 Identity
- **Algorithm:** `UML_OS.Implementation.DependencyLockPolicy_v1`
- **Purpose (1 sentence):** Deterministic dependency governance.
- **Spec Version:** `UML_OS.Implementation.DependencyLockPolicy_v1` | 2026-02-18 | Authors: Olejar Damir
- **Domain / Problem Class:** Reproducible dependency management.
### 0.A Objective Semantics
- Minimize dependency drift and supply-chain risk.
### 0.B Reproducibility Contract
- Replayable given `(lockfile_hash, toolchain_hash, environment_hash)`.
### 0.C Numeric Policy
- Version comparison uses deterministic semantic-version parsing.
### 0.D Ordering and Tie-Break Policy
- Dependency entries sorted by package name and source.
### 0.E Parallel, Concurrency, and Reduction Policy
- Lock verification can be parallelized; verdict merged deterministically.
### 0.F Environment and Dependency Policy
- Determinism level: `BITWISE` for lockfile verification verdict.
### 0.G Operator Manifest
- `UML_OS.DepLock.ValidateLockfile_v1`
- `UML_OS.DepLock.VerifyArtifactHashes_v1`
- `UML_OS.DepLock.EvaluateUpgradeRequest_v1`
- `UML_OS.Error.Emit_v1`
### 0.H Namespacing and Packaging
- Lock policy operators are fully-qualified and versioned.
### 0.I Outputs and Metric Schema
- Outputs: `(lock_verdict, upgrade_report)`.
- Metrics: `packages_total`, `hash_mismatches`, `policy_violations`.
- Completion status: `success | failed`.
### 0.J Spec Lifecycle Governance
- Policy-rule changes require version bump and migration notes.
### 0.K Failure and Error Semantics
- Abort on hash mismatch or forbidden dependency source.
### 0.L Input/Data Provenance
- Lockfile source and artifact provenance are required.

---
### 0.Z EQC Mandatory Declarations Addendum
- Seed space: `seed ∈ {0..2^64-1}` when stochastic sub-operators are used.
- PRNG family: `Philox4x32-10` for declared stochastic operators.
- Randomness locality: all sampling occurs only inside declared stochastic operators in section 5.
- Replay guarantee: replayable given (seed, PRNG family, numeric policy, ordering policy, parallel policy, environment policy).
- Replay token: deterministic per-run token contribution is defined and included in trace records.
- Floating-point format: IEEE-754 binary64 unless explicitly declared otherwise.
- Rounding mode: round-to-nearest ties-to-even unless explicitly overridden.
- Fast-math policy: forbidden for critical checks and verdict paths.
- Named tolerances: `EPS_EQ=1e-10`, `EPS_DENOM=1e-12`, and domain-specific thresholds as declared.
- NaN/Inf policy: invalid values trigger deterministic failure handling per 0.K.
- Normalized exponentials: stable log-sum-exp required when exponential paths are used (otherwise N/A).
- Overflow/underflow: explicit abort or clamp behavior must be declared (this contract uses deterministic abort on critical paths).
- Approx-equality: `a ≈ b` iff `|a-b| <= EPS_EQ` when tolerance checks apply.
- Transcendental functions policy: deterministic implementation requirements are inherited from consuming operators.
- Reference runtime class: CPU-only/GPU-enabled/distributed as required by the consuming workflow.
- Compiler/flags: deterministic compilation; fast-math disabled for critical paths.
- Dependency manifest: pinned runtime dependencies and versions are required.
- Determinism level: `BITWISE` for contract-critical outputs unless a stricter local declaration exists.
- Error trace rule: final failure record includes `t`, `failure_code`, `failure_operator`, replay token, and minimal diagnostics.
- Recovery policy: none unless explicitly declared; default is deterministic abort-only.


## 2) System Model
### I.A Persistent State
- lock policy registry and approved source list.
### I.B Inputs and Hyperparameters
- lockfile, artifact index, upgrade request.
### I.C Constraints and Feasible Set
- Valid if all entries satisfy policy and hashes match.
### I.D Transient Variables
- mismatch report and upgrade diff.
### I.E Invariants and Assertions
- no unlocked transitive dependency allowed in strict mode.

### II.F Operative Lock Policy Rules
- Accepted lockfile formats: `poetry.lock`, `requirements.txt` with hashes, `uv.lock`.
- Artifact verification: each package entry must include SHA-256; downloaded artifact hash must match exactly.
- Registry allowlist: explicit host allowlist only; direct URL dependencies forbidden unless signed and pinned.
- SBOM requirement: CycloneDX JSON emitted per build and hashed into trace.
- Toolchain hash: `toolchain_hash = SHA-256(CBOR(["toolchain_v1", python_version, pip_version, installer_version]))`.

---
## 3) Initialization
1. Load lock policy.
2. Parse lockfile.
3. Initialize verification context.

---
## 4) Operator Manifest
- `UML_OS.DepLock.ValidateLockfile_v1`
- `UML_OS.DepLock.VerifyArtifactHashes_v1`
- `UML_OS.DepLock.EvaluateUpgradeRequest_v1`
- `UML_OS.Error.Emit_v1`

---
## 5) Operator Definitions

External operator reference: `UML_OS.Error.Emit_v1` is defined normatively in `Error-Codes.md` and imported by reference.

Template conformance note (III.A): each operator definition in this section is interpreted with the full EQC operator template fields. When a field is not repeated inline, the section-level defaults are: explicit typed signatures, deterministic ordering/tie handling, declared numerical policy inheritance, deterministic failure semantics (0.K), explicit dependencies, and VII.B test-vector coverage.

**Operator:** `UML_OS.DepLock.ValidateLockfile_v1`  
**Category:** IO  
**Signature:** `(lockfile, policy -> report)`  
**Purity class:** PURE  
**Determinism:** deterministic  
**Definition:** validates pinned versions and allowed sources.

**Operator:** `UML_OS.DepLock.VerifyArtifactHashes_v1`  
**Category:** IO  
**Signature:** `(lockfile, artifact_index -> report)`  
**Purity class:** PURE  
**Determinism:** deterministic  
**Definition:** validates hash integrity for all locked artifacts.

**Operator:** `UML_OS.DepLock.EvaluateUpgradeRequest_v1`  
**Category:** IO  
**Signature:** `(current_lock, proposal, policy -> upgrade_report)`  
**Purity class:** PURE  
**Determinism:** deterministic  
**Definition:** computes allowed/disallowed changes and risk classification.

---
## 6) Procedure
```text
1. ValidateLockfile_v1
2. VerifyArtifactHashes_v1
3. EvaluateUpgradeRequest_v1 (if requested)
4. Emit lock_verdict + upgrade_report
```

---
## 7) Trace & Metrics
### Logging rule
Every dependency verification step emits deterministic records.
### Trace schema
- `run_header`: lockfile_hash, policy_hash
- `iter`: package, check, result
- `run_end`: status, mismatch_summary
### Metric schema
- `packages_total`, `hash_mismatches`, `policy_violations`
### Comparability guarantee
Comparable iff lock policy and artifact index definition are identical.

---
## 8) Validation
#### VII.A Lint rules (mandatory)
Passes determinism, completeness, and policy traceability checks.
#### VII.B Operator test vectors (mandatory)
Valid/invalid lockfiles and upgrade proposals.
#### VII.C Golden traces (mandatory)
Golden lock-verification reports for baseline lockfiles.

---
## 9) Refactor & Equivalence
#### VIII.A Equivalence levels
- E0 for lock verdict and mismatch reports.
#### VIII.B Allowed refactor categories
- verifier optimization preserving report semantics.
#### VIII.C Equivalence test procedure (mandatory)
Exact report comparison on baseline lockfiles.

---
## 10) Checkpoint/Restore
### Checkpoint contents
- verification cursor and partial mismatch report.
### Serialization
- deterministic JSON/CBOR.
### Restore semantics
- resumed verification yields identical final verdict.
