# UML_OS Validation and Test Plan
**EQC Compliance:** Merged single-file EQC v1.1 Option A.

**Algorithm:** `UML_OS.Implementation.TestPlanOrchestrator_v1`  
**Purpose (1 sentence):** Execute deterministic validation suites that certify EQC invariants, operator behavior, and replay correctness.  
**Spec Version:** `UML_OS.Implementation.TestPlanOrchestrator_v1` | 2026-02-18 | Authors: Olejar Damir  
**Domain / Problem Class:** Deterministic verification and regression control.

---

## 1) Header & Global Semantics

### 0.0 Identity
- **Algorithm:** `UML_OS.Implementation.TestPlanOrchestrator_v1`
- **Purpose (1 sentence):** Deterministic test orchestration.
- **Spec Version:** `UML_OS.Implementation.TestPlanOrchestrator_v1` | 2026-02-18 | Authors: Olejar Damir
- **Domain / Problem Class:** Reproducible validation execution.

### 0.A Objective Semantics
- Optimization sense: `MINIMIZE` failures.
- Objective type: `Scalar` (`failed_tests`).
- Comparison: fewer failures is better; ties by lower p95 regression.

### 0.B Reproducibility Contract
- Seed space: `seed ∈ {0..2^64-1}` for stochastic tests.
- PRNG family: Philox4x32-10.
- Randomness locality: only stochastic test operators.
- Replay guarantee: replayable given `(test_manifest_hash, seed_set, environment_hash)`.

### 0.C Numeric Policy
- Critical verdicts are boolean/integer exact.
- Performance thresholds use binary64 comparisons.
- Approx-equality: threshold-defined tolerance for performance metrics.

### 0.D Ordering and Tie-Break Policy
- Test order is deterministic by suite then test_id.
- Tie-break for flaky-equivalent outcomes: lowest test_id.

### 0.E Parallel, Concurrency, and Reduction Policy
- Parallel test execution allowed only with deterministic merge of reports.
- Aggregate counts reduced in deterministic order.

### 0.F Environment and Dependency Policy
- Reference runtime: pinned CI image.
- Determinism level: `BITWISE` for pass/fail reports; `TOLERANCE` for perf metrics.

### 0.G Operator Manifest
- `UML_OS.Test.RunUnitSuite_v1`
- `UML_OS.Test.RunIntegrationSuite_v1`
- `UML_OS.Test.RunGoldenTraceSuite_v1`
- `UML_OS.Test.RunReplaySuite_v1`
- `UML_OS.Test.AggregateResults_v1`
- `UML_OS.Error.Emit_v1`

### 0.H Namespacing and Packaging
- Fully-qualified test operators required.

### 0.I Outputs and Metric Schema
- Outputs: `(test_report, verdict)`.
- Metrics: `passed`, `failed`, `skipped`, `p95_regression`, `determinism_failures`.
- Completion status: `success | failed`.

### 0.J Spec Lifecycle Governance
- Threshold/policy changes require version bump and migration note.

### 0.K Failure and Error Semantics
- Abort-only on infrastructure failures; per-test failures recorded deterministically.

### 0.L Input/Data Provenance
- Test fixtures and golden traces must be hash-addressed.

---

## 2) System Model

### I.A Persistent State
- `test_registry`, `golden_registry`.

### I.B Inputs and Hyperparameters
- suites, thresholds, seed sets, environment metadata.

### I.C Constraints and Feasible Set
- Unconstrained; validity determined by threshold policies.

### I.D Transient Variables
- per-suite reports, aggregate counters.

### I.E Invariants and Assertions
- deterministic ordering and complete report emission.

### II.F Test Manifest and Golden Inventory (Concrete)
- Test manifest required fields:
  - `manifest_version:string`
  - `suites:array<string>`
  - `seed_set:array<uint64>`
  - `thresholds:object`
  - `golden_ids:array<string>`
- Golden inventory (minimum):
  - `golden_kernel_train_v1` -> `sha256:aa01...`
  - `golden_data_nextbatch_v2` -> `sha256:bb02...`
  - `golden_modelir_exec_v1` -> `sha256:cc03...`
  - `golden_dp_apply_v3` -> `sha256:dd04...`
- Deterministic pass/fail rule: pass iff all required suites pass and no E0 field mismatch against referenced golden IDs.
- Required hardening suites:
  - property/fuzz tests for IR validation, schema parsing, checkpoint decode, and TMMU planner invariants,
  - distributed chaos tests (rank loss, network partition, delayed collective),
  - replay divergence minimization tests at scale (multi-rank long-horizon).

---

## 3) Initialization

1. Load test manifest.
2. Validate fixture hashes.
3. Initialize deterministic run order.

---

## 4) Operator Manifest

- `UML_OS.Test.RunUnitSuite_v1`
- `UML_OS.Test.RunIntegrationSuite_v1`
- `UML_OS.Test.RunGoldenTraceSuite_v1`
- `UML_OS.Test.RunReplaySuite_v1`
- `UML_OS.Test.AggregateResults_v1`
- `UML_OS.Error.Emit_v1`

---

## 5) Operator Definitions

External operator reference: `UML_OS.Error.Emit_v1` is defined normatively in `Error-Codes.md` and imported by reference.

**Operator:** `UML_OS.Test.RunUnitSuite_v1`  
**Category:** IO  
**Signature:** `(suite_config -> suite_report)`  
**Purity class:** STATEFUL  
**Determinism:** deterministic  
**Definition:** executes ordered unit tests and records outcomes.  
**Preconditions / Postconditions:** fixtures available.  
**Edge cases:** skipped tests.  
**Numerical considerations:** threshold comparisons in binary64 where needed.  
**Ordering/tie handling:** test_id ascending.  
**Complexity note:** O(number_of_tests).  
**Failure behavior:** deterministic failure logs.  
**Dependencies:** test runner backend.  
**Test vectors:** synthetic pass/fail suites.

**Operator:** `UML_OS.Test.RunGoldenTraceSuite_v1`  
**Category:** IO  
**Signature:** `(golden_config -> golden_report)`  
**Purity class:** STATEFUL  
**Determinism:** deterministic  
**Definition:** compares produced traces against golden references.  
**Preconditions / Postconditions:** golden artifacts present.  
**Edge cases:** missing optional trace fields.  
**Numerical considerations:** exact for E0 fields; tolerance for E1 fields.  
**Ordering/tie handling:** trace step order strict.  
**Complexity note:** O(trace_size).  
**Failure behavior:** deterministic mismatch reports.  
**Dependencies:** trace comparator.  
**Test vectors:** known golden mismatch/pass cases.

**Operator:** `UML_OS.Test.AggregateResults_v1`  
**Category:** IO  
**Signature:** `(suite_reports -> test_report, verdict)`  
**Purity class:** PURE  
**Determinism:** deterministic  
**Definition:** deterministic aggregation and verdict computation.  
**Preconditions / Postconditions:** all suite reports available.  
**Edge cases:** empty suite set.  
**Numerical considerations:** deterministic reduction order.  
**Ordering/tie handling:** suite-name lexical merge.  
**Complexity note:** O(total_cases).  
**Failure behavior:** abort on malformed report.  
**Dependencies:** suite schemas.  
**Test vectors:** aggregate snapshots.

---

**Operator:** `UML_OS.Test.RunIntegrationSuite_v1`  
**Category:** Test  
**Signature:** `(integration_manifest -> integration_report)`  
**Purity class:** IO  
**Determinism:** deterministic  
**Definition:** Executes deterministic integration scenarios across kernel, data, model, memory, and DP boundaries.
**Preconditions / Postconditions:** integration fixtures and dependency contracts are available; output report includes per-scenario status and hashes.  
**Edge cases:** optional components disabled by profile.  
**Numerical considerations:** E0 fields exact; E1 metrics use declared tolerances only.  
**Ordering/tie handling:** scenario_id ascending deterministic execution.  
**Complexity note:** O(number_of_integration_scenarios).  
**Failure behavior:** abort on malformed integration manifest; otherwise deterministic failure records in report.  
**Dependencies:** kernel/component contracts and trace schema.  
**Test vectors:** mixed pass/fail integration matrices.

**Operator:** `UML_OS.Test.RunReplaySuite_v1`  
**Category:** Test  
**Signature:** `(replay_manifest -> replay_report)`  
**Purity class:** IO  
**Determinism:** deterministic  
**Definition:** Validates replay-token determinism, RNG locality, and checkpoint-restore replay guarantees.
**Preconditions / Postconditions:** replay traces/checkpoints and token definitions are available; output report includes replay equivalence verdicts.  
**Edge cases:** missing intermediate checkpoint segments.  
**Numerical considerations:** replay-critical comparisons are bitwise for E0 fields.  
**Ordering/tie handling:** replay-case order is deterministic by replay_case_id ascending.  
**Complexity note:** O(total_replayed_steps).  
**Failure behavior:** abort on invalid replay manifest; deterministic mismatch reports otherwise.  
**Dependencies:** Replay-Determinism and Checkpoint-Schema contracts.  
**Test vectors:** fixed-token replay pass/mismatch scenarios.

## 6) Procedure

```text
1. RunUnitSuite_v1
2. RunIntegrationSuite_v1
3. RunGoldenTraceSuite_v1
4. RunReplaySuite_v1
5. AggregateResults_v1
6. Return report + verdict
```

---

## 7) Trace & Metrics

### Logging rule
Every executed test emits deterministic result records.

### Trace schema
- `run_header`: manifest_hash, environment_hash
- `iter`: suite, test_id, result
- `run_end`: verdict, aggregate counts

### Metric schema
- `passed`, `failed`, `skipped`, `p95_regression`, `determinism_failures`

### Comparability guarantee
Comparable iff same suites, fixtures, thresholds, and merge policy.

---

## 8) Validation

#### VII.A Lint rules (mandatory)
Covers symbol completeness, no hidden globals, deterministic order, trace compliance.

#### VII.B Operator test vectors (mandatory)
Includes suite-runner and aggregator vectors.

#### VII.C Golden traces (mandatory)
Golden report snapshots for canonical test manifests.

---

## 9) Refactor & Equivalence

#### VIII.A Equivalence levels
- E0 for verdict and aggregate counters.

#### VIII.B Allowed refactor categories
- Runner implementation changes preserving outputs.

#### VIII.C Equivalence test procedure (mandatory)
Exact report diff against golden baseline.

---

## 10) Checkpoint/Restore

### Checkpoint contents
- partial suite reports and deterministic run cursor.

### Serialization
- deterministic JSON/CBOR.

### Restore semantics
- resume yields identical final report and verdict.
