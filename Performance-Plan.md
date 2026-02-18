# UML_OS Performance Governance
**EQC Compliance:** Merged single-file EQC v1.1 Option A.

**Algorithm:** `UML_OS.Implementation.PerformanceGovernance_v1`  
**Purpose (1 sentence):** Define deterministic performance measurement, thresholds, and regression-gating for core UML_OS operators.  
**Spec Version:** `UML_OS.Implementation.PerformanceGovernance_v1` | 2026-02-18 | Authors: Olejar Damir  
**Domain / Problem Class:** Reproducible performance benchmarking and policy enforcement.

---

## 1) Header & Global Semantics

### 0.0 Identity
- **Algorithm:** `UML_OS.Implementation.PerformanceGovernance_v1`
- **Purpose (1 sentence):** Deterministic benchmark governance.
- **Spec Version:** `UML_OS.Implementation.PerformanceGovernance_v1` | 2026-02-18 | Authors: Olejar Damir
- **Domain / Problem Class:** Performance policy contract.

### 0.A Objective Semantics
- Optimization sense: `MINIMIZE` p95 latency and memory peak regressions.
- Objective type: `Vector` with deterministic lexicographic order: `(regression_failures, p95_latency_delta, memory_delta)`.

### 0.B Reproducibility Contract
- Seed space: `seed ∈ {0..2^64-1}` for stochastic workloads.
- PRNG family: inherited from tested operators.
- Randomness locality: benchmark harness does not sample except workload generation operators.
- Replay guarantee: benchmark replayable given `(workload_manifest, env_hash, seeds, commit_hash)`.
- Determinism scope: metric sampling is physical-world variable; aggregation and verdict are deterministic given a frozen metric snapshot hash.

### 0.C Numeric Policy
- Timing and memory metrics stored in binary64/integer nanoseconds and bytes.
- Quantile method: nearest-rank (`k = ceil(p*n)` on sorted ascending samples, 1-indexed); ties resolved by stable input order.
- NaN/Inf metrics are invalid and fail the run.
- Approx-equality: threshold-based comparisons.

### 0.D Ordering and Tie-Break Policy
- Benchmarks run in deterministic workload order.
- Tie-break by workload id.

### 0.E Parallel, Concurrency, and Reduction Policy
- Parallel benchmark execution allowed with deterministic metric merge order.

### 0.F Environment and Dependency Policy
- Pinned benchmark runtime image and dependency lockfile required.
- Determinism level: deterministic analysis/verdict over frozen samples (E0 on analysis), tolerance-based policy on raw metrics.

### 0.G Operator Manifest
- `UML_OS.Perf.RunBenchmark_v1`
- `UML_OS.Perf.AggregateMetrics_v1`
- `UML_OS.Perf.EvaluateRegressionPolicy_v1`
- `UML_OS.Error.Emit_v1`

### 0.H Namespacing and Packaging
- Fully-qualified performance operators required.

### 0.I Outputs and Metric Schema
- Outputs: `(perf_report, gate_verdict)`.
- Metrics: `p50`, `p95`, `p99`, `peak_memory`, `throughput`, `regression_count`, `peak_memory_bytes`, `tmmu_fragmentation_ratio`.
- Completion status: `success | failed`.

### 0.J Spec Lifecycle Governance
- Threshold or metric definition changes require version bump and migration notes.

### 0.K Failure and Error Semantics
- Deterministic abort on invalid benchmark artifacts.

### 0.L Input/Data Provenance
- Workloads and baselines must be hash-addressed with provenance metadata.

---

## 2) System Model

### I.A Persistent State
- benchmark baseline registry and threshold policy.

### I.B Inputs and Hyperparameters
- workload set, hardware profile, seeds, thresholds.

### I.C Constraints and Feasible Set
- Unconstrained; gate verdict determined by policy thresholds.

### I.D Transient Variables
- per-workload metric samples and aggregate stats.

### I.E Invariants and Assertions
- deterministic run order and complete metric emission.

### II.F Regression Guards (Normative)
- `peak_memory_bytes` ceiling is mandatory per workload/profile; exceeding ceiling is a hard failure.
- `tmmu_fragmentation_ratio` is computed deterministically as `1 - (largest_free_block_bytes / total_free_bytes)` at measurement point.
- Division-by-zero rule: if `total_free_bytes == 0`, set `tmmu_fragmentation_ratio = 0`.
- Fragmentation regression beyond declared threshold is a hard failure.
- Gate verdict is computed on frozen snapshot samples only.

---

## 3) Initialization

1. Load baseline metrics and thresholds.
2. Validate workload manifests.
3. Initialize deterministic execution order.

---

## 4) Operator Manifest

- `UML_OS.Perf.RunBenchmark_v1`
- `UML_OS.Perf.AggregateMetrics_v1`
- `UML_OS.Perf.EvaluateRegressionPolicy_v1`
- `UML_OS.Error.Emit_v1`

---

## 5) Operator Definitions

External operator reference: `UML_OS.Error.Emit_v1` is defined normatively in `Error-Codes.md` and imported by reference.

**Operator:** `UML_OS.Perf.RunBenchmark_v1`  
**Category:** IO  
**Signature:** `(workload, env -> metric_samples)`  
**Purity class:** STATEFUL  
**Determinism:** deterministic under fixed env/workload seeds  
**Definition:** executes one workload and records latency/memory/throughput samples.  
**Preconditions / Postconditions:** workload/env validated.  
**Edge cases:** warmup-only short runs.  
**Numerical considerations:** metrics in ns/bytes with stable aggregators.  
**Ordering/tie handling:** deterministic sample ordering.  
**Complexity note:** workload-dependent.  
**Failure behavior:** deterministic benchmark failure record.  
**Dependencies:** benchmark harness.  
**Test vectors:** synthetic workload performance fixtures.

**Operator:** `UML_OS.Perf.AggregateMetrics_v1`  
**Category:** IO  
**Signature:** `(metric_samples -> aggregate_metrics)`  
**Purity class:** PURE  
**Determinism:** deterministic  
**Definition:** computes p50/p95/p99/peaks/throughput in deterministic order using nearest-rank quantiles on stably sorted samples.  
**Preconditions / Postconditions:** sufficient samples.  
**Edge cases:** low-sample run.  
**Numerical considerations:** stable percentile computation policy.  
**Ordering/tie handling:** sorted sample values, stable tie handling.  
**Complexity note:** O(n log n).  
**Failure behavior:** abort on invalid sample values.  
**Dependencies:** percentile calculator.  
**Test vectors:** fixed sample -> fixed aggregates.

**Operator:** `UML_OS.Perf.EvaluateRegressionPolicy_v1`  
**Category:** IO  
**Signature:** `(aggregate_metrics, baselines, thresholds -> gate_verdict)`  
**Purity class:** PURE  
**Determinism:** deterministic  
**Definition:** applies regression policy and emits pass/fail verdict.  
**Preconditions / Postconditions:** baselines exist for workload profile.  
**Edge cases:** missing baseline path.  
**Numerical considerations:** tolerance thresholds applied in binary64.  
**Ordering/tie handling:** deterministic workload merge and policy order.  
**Complexity note:** O(workloads).  
**Failure behavior:** deterministic policy failure report.  
**Dependencies:** policy config and baseline registry.  
**Test vectors:** pass/fail threshold boundary cases.

---

## 6) Procedure

```text
1. RunBenchmark_v1 for each workload
2. AggregateMetrics_v1
3. EvaluateRegressionPolicy_v1
4. Return perf_report + gate_verdict
```

---

## 7) Trace & Metrics

### Logging rule
Each workload emits deterministic benchmark records.

### Trace schema
- `run_header`: env_hash, baseline_hash
- `iter`: workload_id, sample_stats
- `run_end`: aggregate_metrics, gate_verdict

### Metric schema
- `p50`, `p95`, `p99`, `peak_memory`, `throughput`, `regression_count`

### Comparability guarantee
Comparable iff workloads, env, baselines, and threshold policies are identical.

---

## 8) Validation

#### VII.A Lint rules (mandatory)
Passes deterministic ordering, explicit thresholds, trace compliance.

#### VII.B Operator test vectors (mandatory)
Benchmark, aggregation, and policy-evaluation vectors.

#### VII.C Golden traces (mandatory)
Golden aggregate metrics for canonical workloads.

---

## 9) Refactor & Equivalence

#### VIII.A Equivalence levels
- E0 for gate verdict and aggregate metrics under same samples.

#### VIII.B Allowed refactor categories
- harness optimization preserving metrics/verdict semantics.

#### VIII.C Equivalence test procedure (mandatory)
Compare aggregate metrics and verdicts exactly/tolerance as declared.

---

## 10) Checkpoint/Restore

### Checkpoint contents
- partial benchmark samples and deterministic run cursor.

### Serialization
- deterministic JSON/CBOR.

### Restore semantics
- resumed run yields identical aggregate metrics and verdict.
