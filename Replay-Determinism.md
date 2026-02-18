# UML_OS Replay and Determinism Contract
**EQC Compliance:** Merged single-file EQC v1.1 Option A.

**Algorithm:** `UML_OS.Implementation.ReplayDeterminismContract_v1`  
**Purpose (1 sentence):** Define and verify deterministic replay semantics, RNG ownership, token composition, and restore equivalence.  
**Spec Version:** `UML_OS.Implementation.ReplayDeterminismContract_v1` | 2026-02-18 | Authors: Olejar Damir  
**Domain / Problem Class:** Reproducibility and replay verification.

---

## 1) Header & Global Semantics

### 0.0 Identity
- **Algorithm:** `UML_OS.Implementation.ReplayDeterminismContract_v1`
- **Purpose (1 sentence):** Deterministic replay contract.
- **Spec Version:** `UML_OS.Implementation.ReplayDeterminismContract_v1` | 2026-02-18 | Authors: Olejar Damir
- **Domain / Problem Class:** Replay verification.

### 0.A Objective Semantics
- Optimization sense: `MINIMIZE` replay divergences.
- Objective type: `Scalar` (`divergence_count`).
- Invalid policy: malformed trace/token treated as failure.

### 0.B Reproducibility Contract
- Seed space: `seed ∈ {0..2^64-1}`.
- PRNG family: Philox4x32-10.
- Randomness locality: only declared stochastic operators may draw RNG.
- Replay guarantee: replayable given `(seed, policies, env_hash, operator_versions)`.
- Replay token definitions are explicit and versioned.

### 0.C Numeric Policy
- Determinism checks for critical fields are exact.
- Tolerance checks allowed only for declared non-critical metrics.
- Approx-equality uses explicit threshold definitions.

### 0.D Ordering and Tie-Break Policy
- Trace comparison order: ascending `t`, then operator sequence index.

### 0.E Parallel, Concurrency, and Reduction Policy
- Parallel traces merged deterministically by rank then `t`.

### 0.F Environment and Dependency Policy
- Reference runtime and dependency hash required for replay comparability.
- Determinism level: BITWISE/TOLERANCE/DISTRIBUTIONAL declared per field class.

### 0.G Operator Manifest
- `UML_OS.Replay.ComputeReplayToken_v1`
- `UML_OS.Replay.VerifyRNGOwnership_v1`
- `UML_OS.Replay.CompareTrace_v1`
- `UML_OS.Replay.VerifyRestore_v1`
- `UML_OS.Error.Emit_v1`

### 0.H Namespacing and Packaging
- Fully-qualified replay operator names required.

### 0.I Outputs and Metric Schema
- Outputs: `(replay_report, divergence_summary)`.
- Metrics: `divergence_count`, `first_divergence_t`, `rng_violation_count`.
- Completion status: `success | failed`.

### 0.J Spec Lifecycle Governance
- Replay token formula changes require MAJOR bump.

### 0.K Failure and Error Semantics
- Deterministic abort on malformed trace/hash state.

### 0.L Input/Data Provenance
- All compared traces/checkpoints must be hash-addressed.

---

## 2) System Model

### I.A Persistent State
- replay policy registry and token formulas.

### I.B Inputs and Hyperparameters
- trace pairs, checkpoint pairs, policy config.

### I.C Constraints and Feasible Set
- Unconstrained; validity by token/trace compatibility.

### I.D Transient Variables
- divergence records and rng counter deltas.

### I.E Invariants and Assertions
- deterministic comparator order and complete reporting.

### II.F Replay Token Formulas (Authoritative)
- `kernel_replay_token = SHA-256(CBOR(["replay_token_v1", spec_version, policy_hash, env_manifest_hash, uint64(seed)]))`.
- `data_replay_t = SHA-256(CBOR(["nextbatch_v2", kernel_replay_token, dataset_key, uint64(epoch), uint64(global_position), uint32(world_size), uint32(rank)]))`.
- `modelir_replay_t = SHA-256(CBOR(["modelir_executor_v1", kernel_replay_token, ir_hash, mode, uint64(global_position)]))`.
- `dp_replay_t = SHA-256(CBOR(["dp_apply_v3", kernel_replay_token, uint64(t), accountant_state_hash, allocation_mode, fused_kernel, safety_reserve]))`.
- Required comparator keys in traces: `t`, `operator_seq`, `rank`, `operator_id`, `status`, plus optional domain metrics.

---

## 3) Initialization

1. Load policy definitions.
2. Load traces/checkpoints.
3. Validate hash integrity.

---

## 4) Operator Manifest

- `UML_OS.Replay.ComputeReplayToken_v1`
- `UML_OS.Replay.VerifyRNGOwnership_v1`
- `UML_OS.Replay.CompareTrace_v1`
- `UML_OS.Replay.VerifyRestore_v1`
- `UML_OS.Error.Emit_v1`

---

## 5) Operator Definitions

External operator reference: `UML_OS.Error.Emit_v1` is defined normatively in `Error-Codes.md` and imported by reference.

**Operator:** `UML_OS.Replay.ComputeReplayToken_v1`  
**Category:** IO  
**Signature:** `(state -> token)`  
**Purity class:** PURE  
**Determinism:** deterministic  
**Definition:** canonical token derivation by declared formula.  
**Preconditions / Postconditions:** required fields present.  
**Edge cases:** missing optional fields disallowed if formula requires them.  
**Numerical considerations:** N/A.  
**Ordering/tie handling:** canonical field order.  
**Complexity note:** O(serialized_state_size).  
**Failure behavior:** deterministic token-computation error.  
**Dependencies:** canonical serializer/hash function.  
**Test vectors:** fixed state -> token snapshots.

**Operator:** `UML_OS.Replay.VerifyRNGOwnership_v1`  
**Category:** IO  
**Signature:** `(trace -> ownership_report)`  
**Purity class:** PURE  
**Determinism:** deterministic  
**Definition:** verifies only declared stochastic operators consume RNG offsets.  
**Preconditions / Postconditions:** trace has rng metadata.  
**Edge cases:** zero-draw runs.  
**Numerical considerations:** counter arithmetic in uint64.  
**Ordering/tie handling:** trace order.  
**Complexity note:** O(trace_events).  
**Failure behavior:** `RNG_CONSUMPTION_VIOLATION`.  
**Dependencies:** operator manifest ownership declarations.  
**Test vectors:** valid/invalid ownership traces.

**Operator:** `UML_OS.Replay.CompareTrace_v1`  
**Category:** IO  
**Signature:** `(trace_a, trace_b -> divergence_summary)`  
**Purity class:** PURE  
**Determinism:** deterministic  
**Definition:** compares trace fields under declared determinism class rules.  
**Preconditions / Postconditions:** identical schema keys/types.  
**Edge cases:** different lengths.  
**Numerical considerations:** exact for E0 fields, threshold for E1.  
**Ordering/tie handling:** ascending `t`/rank order.  
**Complexity note:** O(trace_size).  
**Failure behavior:** deterministic divergence report.  
**Dependencies:** determinism-class map.  
**Test vectors:** replay-equivalent and divergent pairs.

---

**Operator:** `UML_OS.Replay.VerifyRestore_v1`  
**Category:** Replay  
**Signature:** `(checkpoint_blob, restored_state, replay_token -> restore_report)`  
**Purity class:** PURE  
**Determinism:** deterministic  
**Definition:** Verifies that restore state and replay token exactly match checkpoint commitments and deterministic replay contracts.

## 6) Procedure

```text
1. ComputeReplayToken_v1 for both runs
2. VerifyRNGOwnership_v1 for both traces
3. CompareTrace_v1(trace_a, trace_b)
4. VerifyRestore_v1(checkpoint_a, checkpoint_b)
5. Return replay_report
```

---

## 7) Trace & Metrics

### Logging rule
Every replay check emits deterministic divergence records.

### Trace schema
- `run_header`: token formulas, policy hash
- `iter`: check_id, result, divergence_location
- `run_end`: status, divergence_summary

### Metric schema
- `divergence_count`, `first_divergence_t`, `rng_violation_count`

### Comparability guarantee
Comparable iff policy hash, token formulas, and trace schema are identical.

---

## 8) Validation

#### VII.A Lint rules (mandatory)
Passes deterministic ordering, explicit stochastic ownership, trace compliance.

#### VII.B Operator test vectors (mandatory)
Token, RNG ownership, and trace comparison vectors.

#### VII.C Golden traces (mandatory)
Golden replay-equivalent and known-divergence fixtures.

---

## 9) Refactor & Equivalence

#### VIII.A Equivalence levels
- E0 for replay report identity.

#### VIII.B Allowed refactor categories
- Comparator optimization preserving report semantics.

#### VIII.C Equivalence test procedure (mandatory)
Exact comparison of divergence summary outputs.

---

## 10) Checkpoint/Restore

### Checkpoint contents
- replay policy hash, token formulas, comparator config.

### Serialization
- deterministic CBOR/JSON.

### Restore semantics
- restored contract yields identical replay verdicts.
