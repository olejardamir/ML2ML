# UML_OS Reference Implementations Contract
**EQC Compliance:** Merged single-file EQC v1.1 Option A.

**Algorithm:** `UML_OS.Implementation.ReferenceImplementations_v1`  
**Purpose (1 sentence):** Define canonical coding-level signatures and pseudocode for critical operators to eliminate implementation ambiguity.  
**Spec Version:** `UML_OS.Implementation.ReferenceImplementations_v1` | 2026-02-18 | Authors: Olejar Damir  
**Domain / Problem Class:** Developer implementation guidance.

---
## 1) Header & Global Semantics
### 0.0 Identity
- **Algorithm:** `UML_OS.Implementation.ReferenceImplementations_v1`
- **Purpose (1 sentence):** Normative coding reference for critical operators.
### 0.A Objective Semantics
- Optimization sense: `MINIMIZE`
- Objective type: `Scalar`
- Primary comparison rule: deterministic total preorder over declared primary metric tuple with `EPS_EQ` tie handling.
- Invalid objective policy: `NaN/Inf` ranked as worst-case and handled deterministically per 0.K.
- Minimize implementation drift across languages/backends.
### 0.B Reproducibility Contract
- Reference behavior must be replayable under identical inputs and policy hashes.
### 0.C Numeric Policy
- Critical arithmetic paths use binary64 and deterministic ordering.
### 0.D Ordering and Tie-Break Policy
- Stable deterministic index/rank ordering in all reference loops.
### 0.E Parallel, Concurrency, and Reduction Policy
- Reference code is sequential semantics; parallel implementations must be equivalent.
### 0.F Environment and Dependency Policy
- Reference implementations are language-agnostic and side-effect explicit.
### 0.G Operator Manifest
- `UML_OS.Data.NextBatch_v2`
- `UML_OS.DifferentialPrivacy.Apply_v3`
- `UML_OS.TMMU.PrepareMemory_v2`
- `UML_OS.Replay.CompareTrace_v1`
- `UML_OS.Certificate.EvidenceValidate_v1`
### 0.H Namespacing and Packaging
- One reference module per operator family.
### 0.I Outputs and Metric Schema
- Outputs are canonical return structs per operator signature.
### 0.J Spec Lifecycle Governance
- Signature/algorithm-semantic changes are MAJOR.
### 0.K Failure and Error Semantics
- Error handling must map to `Error-Codes.md` IDs only.
### 0.L Input/Data Provenance
- Inputs reference manifest/checkpoint/trace/schema hashes.

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
- none; references are pure semantic templates.
### I.B Inputs and Hyperparameters
- operator-specific typed inputs.
### I.C Constraints and Feasible Set
- valid only for schema-valid inputs.
### I.D Transient Variables
- local deterministic work buffers.
### I.E Invariants and Assertions
- signatures and side-effects must match `API-Interfaces.md`.

### II.F Canonical Function Signatures (Normative)
- `next_batch_v2(dataset_key, world_size, rank, stage_type, cursor_in) -> (indices, cursor_next, metrics)`
- `dp_apply_v3(gradients, dp_config, t, state) -> (noisy_gradients, state_next, metrics)`
- `prepare_memory_v2(ir_dag, execution_order, mode, arena_config) -> (tensor_map, metrics)`
- `replay_compare_trace_v1(trace_a, trace_b, replay_mode) -> divergence_report`
- `evidence_validate_v1(certificate, manifest, trace, checkpoint, replay_ctx) -> validation_report`
- All signatures must be derived from `contracts/operator_registry.cbor`; manual signature drift is forbidden.

### II.G Normative Reference Pseudocode (Required)
- `CBOR_CANONICAL(value)`:
  - encode using `Canonical-CBOR-Profile.md` (definite lengths, no duplicate keys, key order by `(len(encoded_key), encoded_key)`).
  - reject non-UTF8 text keys and forbidden float values in signed payloads.
- `ResolveDigestRef_v1(digest_ref, digest_catalog)`:
  - if tail matches `^[0-9a-f]{64}$`, return inline bytes32 digest.
  - else resolve label in `digest_catalog`; abort with `CONTRACT_VIOLATION` if missing.
- `TraceRecordHashChain_v1(normalized_records)`:
  - `h = SHA-256(CBOR_CANONICAL(["trace_chain_v1"]))`
  - for each record in canonical order:
    - `r = SHA-256(CBOR_CANONICAL(record))`
    - `h = SHA-256(CBOR_CANONICAL(["trace_chain_v1", h, r]))`
  - return `h` as `trace_final_hash` in linear-chain mode.
- `WalChainAndFinalize_v1(records)`:
  - compute each `record_hash_i = SHA-256(CBOR_CANONICAL(["wal_record_v1", tenant_id, run_id, wal_seq_i, record_type_i, prev_record_hash_i, payload_i]))`.
  - terminal `FINALIZE` record hash is `commit_record_hash`.
  - `wal_terminal_hash = commit_record_hash`.
- `PublishCommitPointer_v1(pointer_payload)`:
  - payload must include `{trace_final_hash, checkpoint_hash, lineage_root_hash, execution_certificate_hash, wal_terminal_hash}`.
  - publish `runs/<tenant_id>/<run_id>/COMMITTED` via conditional create-if-absent.
  - if object exists, compare payload hash; mismatch is deterministic failure.

---
## 3) Initialization
1. Load typed schemas.
2. Validate operator signatures.
3. Bind deterministic helper primitives.

---
## 4) Operator Manifest
- `UML_OS.Implementation.Ref.NextBatch_v2`
- `UML_OS.Implementation.Ref.ApplyDP_v3`
- `UML_OS.Implementation.Ref.PrepareMemory_v2`
- `UML_OS.Implementation.Ref.ReplayCompare_v1`
- `UML_OS.Implementation.Ref.EvidenceValidate_v1`

---
## 5) Operator Definitions
**Operator:** `UML_OS.Implementation.Ref.NextBatch_v2`  
**Category:** Implementation  
**Signature:** `(dataset_key, world_size, rank, stage_type, cursor_in -> indices, cursor_next, metrics)`  
**Purity class:** PURE  
**Determinism:** deterministic  
**Definition:** canonical sampling pseudocode consistent with `Data-NextBatch.md`.

**Operator:** `UML_OS.Implementation.Ref.ApplyDP_v3`  
**Category:** Implementation  
**Signature:** `(gradients, dp_config, t, state -> noisy_gradients, state_next, metrics)`  
**Purity class:** STATEFUL  
**Determinism:** deterministic control / stochastic noise per RNG contract  
**Definition:** canonical DP pseudocode consistent with `DifferentialPrivacy-Apply.md`.

**Operator:** `UML_OS.Implementation.Ref.PrepareMemory_v2`  
**Category:** Implementation  
**Signature:** `(ir_dag, execution_order, mode, arena_config -> tensor_map, metrics)`  
**Purity class:** STATEFUL  
**Determinism:** deterministic  
**Definition:** canonical injective arena-offset planner pseudocode.

---
## 6) Procedure
```text
1. Validate schemas and signatures.
2. Execute operator-specific reference procedure.
3. Emit canonical outputs and metrics.
4. Verify expected side-effects set.
```

---
## 7) Trace & Metrics
### Logging rule
- reference runs emit deterministic debug traces for compare-only use.
### Trace schema
- `run_header`: operator, signature_digest
- `iter`: step, local_state_hash
- `run_end`: output_hash
### Metric schema
- `steps`, `deterministic_checks_passed`
### Comparability guarantee
- comparable iff signatures, inputs, and policies are identical.

---
## 8) Validation
#### VII.A Lint rules (mandatory)
- no hidden globals, total state updates, deterministic ordering.
#### VII.B Operator test vectors (mandatory)
- each reference function must pass catalog vectors from `Test-Vectors-Catalog.md`.
#### VII.C Golden traces (mandatory)
- golden output hashes per reference operator.

---
## 9) Refactor & Equivalence
#### VIII.A Equivalence levels
- E0 for outputs and side-effects on deterministic paths.
#### VIII.B Allowed refactor categories
- language/runtime rewrites preserving signature and semantics.
#### VIII.C Equivalence test procedure (mandatory)
- exact compare against golden vectors and output hashes.

---
## 10) Checkpoint/Restore
### Checkpoint contents
- optional local reference-state snapshots for debug replay.
### Serialization
- deterministic CBOR.
### Restore semantics
- restored reference state yields identical outputs.
