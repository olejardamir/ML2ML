# UML_OS Checkpoint Schema Contract
**EQC Compliance:** Merged single-file EQC v1.1 Option A.

**Algorithm:** `UML_OS.Checkpoint.SchemaContract_v1`  
**Purpose (1 sentence):** Define deterministic checkpoint structure, compatibility rules, and restore guarantees across UML_OS subsystems.  
**Spec Version:** `UML_OS.Checkpoint.SchemaContract_v1` | 2026-02-18 | Authors: Olejar Damir  
**Domain / Problem Class:** State persistence and restore compatibility.

---
## 1) Header & Global Semantics
### 0.0 Identity
- **Algorithm:** `UML_OS.Checkpoint.SchemaContract_v1`
- **Purpose (1 sentence):** Canonical checkpoint contract.
- **Spec Version:** `UML_OS.Checkpoint.SchemaContract_v1` | 2026-02-18 | Authors: Olejar Damir
- **Domain / Problem Class:** Deterministic persistence.
### 0.A Objective Semantics
- Optimization sense: `MINIMIZE`
- Objective type: `Scalar`
- Primary comparison rule: deterministic total preorder over declared primary metric tuple with `EPS_EQ` tie handling.
- Invalid objective policy: `NaN/Inf` ranked as worst-case and handled deterministically per 0.K.
- Minimize restore divergence and compatibility errors.
### 0.B Reproducibility Contract
- Replayable given `(checkpoint_hash, schema_version, replay_token)`.
### 0.C Numeric Policy
- Binary blobs and scalar metadata are typed and deterministic.
### 0.D Ordering and Tie-Break Policy
- Canonical field order for serialization.
### 0.E Parallel, Concurrency, and Reduction Policy
- Checkpoint writes are atomic and serialized deterministically.
### 0.F Environment and Dependency Policy
- Determinism level: `BITWISE` for checkpoint metadata and hashes.
### 0.G Operator Manifest
- `UML_OS.Checkpoint.ValidateSchema_v1`
- `UML_OS.Checkpoint.Serialize_v1`
- `UML_OS.Checkpoint.Restore_v1`
- `UML_OS.Error.Emit_v1`
### 0.H Namespacing and Packaging
- Fully-qualified checkpoint fields by subsystem.
### 0.I Outputs and Metric Schema
- Outputs: `(checkpoint_blob, restore_report)`.
- Metrics: `checkpoint_size_bytes`, `restore_time_ms`, `compatibility_level`.
- Completion status: `success | failed`.
### 0.J Spec Lifecycle Governance
- Breaking field changes require MAJOR bump.
### 0.K Failure and Error Semantics
- Abort on incompatible schema or hash mismatch.
### 0.L Input/Data Provenance
- Checkpoint records source run hash and manifest hash.

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
- checkpoint schema registry.
### I.B Inputs and Hyperparameters
- subsystem states and schema version.
### I.C Constraints and Feasible Set
- Valid if required fields and hashes match.
### I.D Transient Variables
- serialization buffers and restore diagnostics.
### I.E Invariants and Assertions
- round-trip serialize/restore invariance.

### II.F Checkpoint Record Layout (Concrete)
- Required fields:
  - `tenant_id:string`
  - `run_id:string`
  - `spec_version:string`
  - `checkpoint_schema_version:string`
  - `replay_token:bytes(32)`
  - `t:uint64`
  - `manifest_hash:bytes32`
  - `trace_root_hash:bytes32`
  - `sampler_config_hash:bytes32`
  - `tmmu_plan_hash:bytes32`
  - `backend_binary_hash:bytes32`
  - `checkpoint_merkle_root:bytes32`
  - `policy_hash:bytes32`
  - `determinism_profile_hash:bytes32`
  - `dependencies_lock_hash:bytes32`
  - `operator_contracts_root_hash:bytes32`
  - `runtime_env_hash:bytes32`
  - `code_commit_hash:bytes32`
  - `lineage_root_hash:bytes32`
  - `tensors_root_hash:bytes32`
  - `optimizer_state_root_hash:bytes32`
  - `dp_accountant_state_root_hash?:bytes32`
  - `trace_tail_hash_at_checkpoint:bytes32`
  - `checkpoint_hash_prev?:bytes32`
- Serialization: canonical CBOR (sorted keys), then `checkpoint_hash = SHA-256(checkpoint_header_cbor)`.
- Evolution rule: additive optional fields allowed in MINOR; required-field changes require MAJOR.
- Migration controls:
  - `migration_supported_from: array<string>`
  - `migration_operator: string`
  - `migration_invariants: array<string>`

### II.G Sharded/Streaming Container Format
- Container layout:
  - `checkpoint_manifest.cbor` (authoritative metadata + shard index)
  - `tensors/rank=<r>/shard=<k>.bin`
  - `optimizer/rank=<r>/state.bin` (optional)
  - `dp/accountant_state.cbor`
  - `data/cursors.cbor`
  - `tmmu/plan.cbor`
  - `trace/link.cbor`
  - `artifacts/artifact_index.cbor`
- Integrity:
  - `checkpoint_manifest.cbor` includes per-shard hash list and Merkle root.
  - Full checkpoint hash derives from canonical manifest + shard hash list.
  - Binding rule:
    - `weights_manifest_hash` must hash to a manifest whose content-addressed entries jointly hash to `tensors_root_hash`.
    - `optimizer_manifest_hash` must hash to a manifest whose entries jointly hash to `optimizer_state_root_hash`.
    - `dp_accountant_manifest_hash` must hash to canonical accountant blobs that hash to `dp_accountant_state_root_hash` (when DP enabled).
- Atomicity protocol:
  - write to temp path, `fsync(file)`, `rename(temp, final)`, `fsync(directory)`.
  - crash-consistency guarantee: either previous checkpoint remains valid or new checkpoint is fully valid; partial writes are invalid.
- Restore semantics:
  - supports full restore and deterministic partial restore by shard subset when declared by policy.

### II.H Partial Restore Matrix (Normative)
- Training restore requires: model params, optimizer state, RNG states, DP accountant state, data cursors, TMMU plan.
- Eval/infer partial restore may use: model params + minimal runtime config.
- Any partial restore must emit `restore_profile_id` and trace record.

### II.I Trace-Link Integrity (Normative)
- Checkpoint header must store:
  - `trace_tail_hash_at_checkpoint`
  - `checkpoint_hash_prev` (if checkpoint chaining enabled)
- `trace/link.cbor` binds checkpoint to trace hash chain for tamper-evident replay.
- checkpoint manifest must include `dataset_snapshot_id` and `artifact_index_hash`.
- Canonical contract rule: the checkpoint header in this file is the authoritative shape and must match `Data-Structures.md` `CheckpointHeader`.
- Restore identity rule: restore must abort deterministically on any mismatch in `{tenant_id, run_id, replay_token, trace_root_hash, checkpoint_merkle_root, manifest_hash, sampler_config_hash, tmmu_plan_hash, backend_binary_hash, determinism_profile_hash}`.

### II.J Run Commit Protocol (Normative)
- Commit is atomic across trace/checkpoint/lineage/certificate using temp objects:
  1. write `trace.tmp`, `checkpoint.tmp`, `lineage.tmp`,
  2. compute `trace_tail_hash`, `checkpoint_merkle_root`, `lineage_root_hash`,
  3. build/sign certificate bound to those hashes,
  4. atomically rename all temp objects to final names and emit `run_commit_record`.
- Recovery rule after crash:
  - if complete signed certificate and all bound final objects exist, finalize commit,
  - otherwise roll back temp objects deterministically and emit failure record.

### II.K Migration Certificate (Normative)
- Every schema migration must emit a signed migration certificate:
  - `from_schema_version`, `to_schema_version`,
  - `source_hash`, `target_hash`,
  - `migration_operator`, `migration_policy_hash`.
- Migration output must hash identically across conforming implementations.

---
## 3) Initialization
1. Load checkpoint schema.
2. Validate subsystem state snapshots.
3. Initialize canonical serializer.

---
## 4) Operator Manifest
- `UML_OS.Checkpoint.ValidateSchema_v1`
- `UML_OS.Checkpoint.Serialize_v1`
- `UML_OS.Checkpoint.Restore_v1`
- `UML_OS.Error.Emit_v1`

---
## 5) Operator Definitions

External operator reference: `UML_OS.Error.Emit_v1` is defined normatively in `Error-Codes.md` and imported by reference.

Template conformance note (III.A): each operator definition in this section is interpreted with the full EQC operator template fields. When a field is not repeated inline, the section-level defaults are: explicit typed signatures, deterministic ordering/tie handling, declared numerical policy inheritance, deterministic failure semantics (0.K), explicit dependencies, and VII.B test-vector coverage.

**Operator:** `UML_OS.Checkpoint.ValidateSchema_v1`  
**Category:** IO  
**Signature:** `(state, schema -> report)`  
**Purity class:** PURE  
**Determinism:** deterministic  
**Definition:** validates checkpoint field presence/types.

**Operator:** `UML_OS.Checkpoint.Serialize_v1`  
**Category:** IO  
**Signature:** `(validated_state -> checkpoint_blob)`  
**Purity class:** IO  
**Determinism:** deterministic  
**Definition:** canonical deterministic serialization with hash attachment.

**Operator:** `UML_OS.Checkpoint.Restore_v1`  
**Category:** IO  
**Signature:** `(checkpoint_blob -> restored_state, report)`  
**Purity class:** IO  
**Determinism:** deterministic  
**Definition:** validates hash/schema and reconstructs subsystem state.

---
## 6) Procedure
```text
1. ValidateSchema_v1
2. Serialize_v1
3. Restore_v1 (verification mode)
4. Return checkpoint_blob + restore_report
```

---
## 7) Trace & Metrics
### Logging rule
Checkpoint writes/restores emit deterministic records.
### Trace schema
- `run_header`: schema_version, source_hash
- `iter`: step, status
- `run_end`: checkpoint_hash, restore_status
### Metric schema
- `checkpoint_size_bytes`, `restore_time_ms`, `compatibility_level`
### Comparability guarantee
Comparable iff schema version and hash rules are identical.

---
## 8) Validation
#### VII.A Lint rules (mandatory)
Passes deterministic ordering, schema completeness, round-trip invariance.
#### VII.B Operator test vectors (mandatory)
Checkpoint fixtures for valid/incompatible/corrupt cases.
#### VII.C Golden traces (mandatory)
Golden checkpoint hashes for baseline states.

---
## 9) Refactor & Equivalence
#### VIII.A Equivalence levels
- E0 for blob/hash and restored state.
#### VIII.B Allowed refactor categories
- serializer optimization preserving canonical bytes.
#### VIII.C Equivalence test procedure (mandatory)
Exact blob/hash compare + state equivalence.

---
## 10) Checkpoint/Restore
### Checkpoint contents
- kernel, data, model, tmmu, dp states + metadata hashes.
### Serialization
- deterministic CBOR/protobuf.
### Restore semantics
- restored run must produce identical subsequent deterministic traces.
