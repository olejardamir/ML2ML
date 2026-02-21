# UML_OS Conformance Harness Guide
**EQC Compliance:** Merged single-file EQC v1.1 Option A.

**Algorithm:** `UML_OS.Implementation.ConformanceHarnessGuide_v1`  
**Purpose (1 sentence):** Define deterministic execution of conformance harness suites that validate contract, replay, and evidence integrity.  
**Spec Version:** `UML_OS.Implementation.ConformanceHarnessGuide_v1` | 2026-02-19 | Authors: Olejar Damir  
**Normativity Legend:** `docs/layer1-foundation/Normativity-Legend.md`

**Domain / Problem Class:** Test harness execution and conformance gating.

---
## 1) Header & Global Semantics
### 0.0 Identity
- **Algorithm:** `UML_OS.Implementation.ConformanceHarnessGuide_v1`
- **Purpose (1 sentence):** Canonical conformance harness execution contract.
### 0.A Objective Semantics
- minimize conformance failures and unresolved contract drift.
### 0.B Reproducibility Contract
- same suite set + same inputs produce same verdict.
- hash policy: all hashes are `SHA-256(CBOR_CANONICAL(...))` unless explicitly overridden.
### 0.C Numeric Policy
- binary64 for score aggregation and thresholds.
### 0.D Ordering and Tie-Break Policy
- suite order fixed: schema -> interfaces -> replay -> checkpoint -> security.
### 0.E Parallel, Concurrency, and Reduction Policy
- within-suite tests parallelized; suite verdict reduction deterministic.
### 0.F Environment and Dependency Policy
- harness executes in locked environment.
### 0.G Operator Manifest
- `UML_OS.Test.RunSchemaConformanceSuite_v1`
- `UML_OS.Test.RunInterfaceSuite_v1`
- `UML_OS.Test.RunReplayConformanceSuite_v1`
- `UML_OS.Test.RunCheckpointConformanceSuite_v1`
- `UML_OS.Test.RunSecurityConformanceSuite_v1`
- `UML_OS.Test.RunEvidenceIntegritySuite_v1`
- `UML_OS.Test.AggregateHarnessVerdict_v1`
- `UML_OS.Error.Emit_v1`
### 0.H Namespacing and Packaging
- under `UML_OS.Test.*` and `UML_OS.Implementation.*`.
### 0.I Outputs and Metric Schema
- outputs: `(suite_reports, harness_verdict, harness_metrics, certification_evidence_bundle_hash)`.
### 0.J Spec Lifecycle Governance
- mandatory suite set changes are MAJOR.
### 0.K Failure and Error Semantics
- mandatory suite failure aborts release gate.
### 0.L Input/Data Provenance
- inputs from test vectors catalog and artifact fixtures.
### 0.Z EQC Mandatory Declarations Addendum
- seed space: `uint64` (suite-level stochastic tests must consume deterministic seeds).
- PRNG family: `Philox4x32-10` for stochastic harness suites.
- replay guarantee: identical `(target_profile, suite_selection, strictness_level)` and identical fixture hashes produce identical `harness_verdict`.
- floating-point format: IEEE-754 binary64; rounding mode `roundTiesToEven`.
- NaN/Inf policy: invalid for verdict-bearing aggregates; emit deterministic failure.
- default tolerances: `abs_tol=EPS_EQ`, `rel_tol=0` unless suite profile specifies stricter/looser bounds.
- determinism target: E0 for `harness_verdict` and failing vector ids.

---
## 2) System Model
### I.A Persistent State
- suite results store and history.
### I.B Inputs and Hyperparameters
- target profile id (`profile_hash`), suite selection, strictness level.
### I.C Constraints and Feasible Set
- required baseline vectors must exist.
### I.D Transient Variables
- per-suite pass/fail and diagnostics.
### I.E Invariants and Assertions
- every required suite produces deterministic verdict.
- certification evidence bundle is reproducible and hash-stable for identical suite inputs.

### II.F Certification Evidence Bundle (Normative)
- Harness MUST produce a canonical certification evidence bundle for adapter/store/vendor publication.
- Bundle minimum contents:
  - suite selection and profile hash,
  - per-suite report hashes,
  - failing vector ids (if any),
  - final `harness_verdict`,
  - fixture catalog hash,
  - harness runtime/environment hash.
- Identity rule:
  - `certification_evidence_bundle_hash = SHA-256(CBOR_CANONICAL(certification_evidence_bundle))`.

### II.G Portable Vendor Package Format (Normative)
- Harness MUST support packaging certification outputs as portable artifact:
  - `conformance_package.cbor`,
  - `fixtures_manifest.json`,
  - `verdicts.json`,
  - `hash_manifest.json`.
- Package identity:
  - `conformance_package_hash = SHA-256(CBOR_CANONICAL(conformance_package))`.
- Third parties MUST be able to verify package integrity with published contract hashes and trust roots only.
- Certification workflow reference:
  - `docs/layer4-implementation/Third-Party-Operator-Certification-Program.md`.

---
## 3) Initialization
1. Load suite catalog.
2. Resolve target profile to required suites.
3. Initialize harness run context.

---
## 4) Operator Manifest
- `UML_OS.Test.RunSchemaConformanceSuite_v1`
- `UML_OS.Test.RunInterfaceSuite_v1`
- `UML_OS.Test.RunReplayConformanceSuite_v1`
- `UML_OS.Test.RunCheckpointConformanceSuite_v1`
- `UML_OS.Test.RunSecurityConformanceSuite_v1`
- `UML_OS.Test.RunEvidenceIntegritySuite_v1`
- `UML_OS.Test.AggregateHarnessVerdict_v1`
- `UML_OS.Error.Emit_v1`

---
## 5) Operator Definitions
**Operator:** `UML_OS.Test.RunSchemaConformanceSuite_v1`
**Signature:** `(schema_vectors, profile -> suite_report)`
**Purity class:** IO
**Definition:** Executes schema conformance vectors in deterministic order.
**allowed_error_codes:** `CONTRACT_VIOLATION`, `VECTOR_LOAD_FAILURE`, `SCHEMA_MISMATCH`.

**Operator:** `UML_OS.Test.RunInterfaceSuite_v1`
**Signature:** `(interface_vectors, profile -> suite_report)`
**Purity class:** IO
**Definition:** Verifies API/signature and interface digest conformance.
**allowed_error_codes:** `CONTRACT_VIOLATION`, `SIGNATURE_MISMATCH`, `INTERFACE_MISMATCH`.

**Operator:** `UML_OS.Test.RunReplayConformanceSuite_v1`  
**Signature:** `(vectors, profile -> suite_report)`  
**Purity class:** IO  
**Definition:** Executes replay vectors and validates E0/E1 policies.
**allowed_error_codes:** `CONTRACT_VIOLATION`, `REPLAY_DIVERGENCE`.

**Operator:** `UML_OS.Test.RunCheckpointConformanceSuite_v1`
**Signature:** `(checkpoint_vectors, profile -> suite_report)`
**Purity class:** IO
**Definition:** Validates checkpoint/restore invariants and replay continuity.
**allowed_error_codes:** `CONTRACT_VIOLATION`, `CHECKPOINT_INTEGRITY_FAILURE`, `RESTORE_IDENTITY_MISMATCH`.

**Operator:** `UML_OS.Test.RunSecurityConformanceSuite_v1`
**Signature:** `(security_vectors, profile -> suite_report)`
**Purity class:** IO
**Definition:** Validates certificate/authz/policy-evidence integrity paths.
**allowed_error_codes:** `CONTRACT_VIOLATION`, `CERTIFICATE_INVALID`, `AUTHZ_CONTEXT_MISSING`.

**Operator:** `UML_OS.Test.RunEvidenceIntegritySuite_v1`
**Signature:** `(evidence_vectors, profile -> suite_report)`
**Purity class:** IO
**Definition:** Validates cross-artifact hash-link and evidence-bundle integrity.
**allowed_error_codes:** `CONTRACT_VIOLATION`, `EVIDENCE_HASH_MISMATCH`.

**Operator:** `UML_OS.Test.AggregateHarnessVerdict_v1`  
**Signature:** `(suite_reports, policy -> verdict)`  
**Purity class:** PURE  
**Definition:** Aggregates suite outcomes into deterministic final verdict.
**allowed_error_codes:** `CONTRACT_VIOLATION`.

---
## 6) Procedure
```text
1. run schema suite
2. run interface/signature suite
3. run replay suite
4. run checkpoint suite
5. run security suite
6. run evidence-integrity suite
7. aggregate deterministic verdict
8. abort on required-suite failure
9. emit certification_evidence_bundle_hash
```

---
## 7) Trace & Metrics
- Metrics: `required_suites_total`, `required_suites_passed`, `optional_suites_passed`, `failure_count`.
- Trace includes suite ids and vector ids.

---
## 8) Validation
- golden harness runs with fixed vectors and expected verdict.
- failure-injection conformance path.

---
## 9) Refactor & Equivalence
- E0 for final harness verdict and failing vector ids.

---
## 10) Checkpoint/Restore
- checkpoint stores: `completed_suite_ids[]`, `pending_suite_queue`, `partial_suite_reports_hash`, `harness_context_hash`.
- restore resumes deterministically at next suite.
