# UML_OS Conformance Harness Guide
**EQC Compliance:** Merged single-file EQC v1.1 Option A.

**Algorithm:** `UML_OS.Implementation.ConformanceHarnessGuide_v1`  
**Purpose (1 sentence):** Define deterministic execution of conformance harness suites that validate contract, replay, and evidence integrity.  
**Spec Version:** `UML_OS.Implementation.ConformanceHarnessGuide_v1` | 2026-02-19 | Authors: Olejar Damir  
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
- `UML_OS.Test.RunReplayConformanceSuite_v1`
- `UML_OS.Test.RunEvidenceIntegritySuite_v1`
- `UML_OS.Test.AggregateHarnessVerdict_v1`
- `UML_OS.Error.Emit_v1`
### 0.H Namespacing and Packaging
- under `UML_OS.Test.*` and `UML_OS.Implementation.*`.
### 0.I Outputs and Metric Schema
- outputs: `(suite_reports, harness_verdict, harness_metrics)`.
### 0.J Spec Lifecycle Governance
- mandatory suite set changes are MAJOR.
### 0.K Failure and Error Semantics
- mandatory suite failure aborts release gate.
### 0.L Input/Data Provenance
- inputs from test vectors catalog and artifact fixtures.

---
## 2) System Model
### I.A Persistent State
- suite results store and history.
### I.B Inputs and Hyperparameters
- target profile, suite selection, strictness level.
### I.C Constraints and Feasible Set
- required baseline vectors must exist.
### I.D Transient Variables
- per-suite pass/fail and diagnostics.
### I.E Invariants and Assertions
- every required suite produces deterministic verdict.

---
## 3) Initialization
1. Load suite catalog.
2. Resolve target profile to required suites.
3. Initialize harness run context.

---
## 4) Operator Manifest
- `UML_OS.Test.RunSchemaConformanceSuite_v1`
- `UML_OS.Test.RunReplayConformanceSuite_v1`
- `UML_OS.Test.RunEvidenceIntegritySuite_v1`
- `UML_OS.Test.AggregateHarnessVerdict_v1`
- `UML_OS.Error.Emit_v1`

---
## 5) Operator Definitions
**Operator:** `UML_OS.Test.RunReplayConformanceSuite_v1`  
**Signature:** `(vectors, profile -> suite_report)`  
**Purity class:** IO  
**Definition:** Executes replay vectors and validates E0/E1 policies.

**Operator:** `UML_OS.Test.AggregateHarnessVerdict_v1`  
**Signature:** `(suite_reports, policy -> verdict)`  
**Purity class:** PURE  
**Definition:** Aggregates suite outcomes into deterministic final verdict.

---
## 6) Procedure
```text
1. run schema suite
2. run interface/signature suite
3. run replay suite
4. run evidence-integrity suite
5. aggregate deterministic verdict
6. abort on required-suite failure
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
- checkpoint stores completed suite ids and partial reports hash.
- restore resumes deterministically at next suite.
