# UML_OS Run Commit WAL Contract
**EQC Compliance:** Merged single-file EQC v1.1 Option A.

**Algorithm:** `UML_OS.Commit.RunCommitWAL_v1`  
**Purpose (1 sentence):** Define deterministic write-ahead logging and recovery rules for atomic run commit of trace/checkpoint/lineage/certificate artifacts.  
**Spec Version:** `UML_OS.Commit.RunCommitWAL_v1` | 2026-02-19 | Authors: Olejar Damir  
**Domain / Problem Class:** Crash-consistent artifact finalization.

---
## 1) Header & Global Semantics
### 0.0 Identity
- **Algorithm:** `UML_OS.Commit.RunCommitWAL_v1`
- **Purpose (1 sentence):** Atomic, replayable run finalization.
### 0.A Objective Semantics
- Optimization sense: `MINIMIZE`
- Objective type: `Scalar`
- Primary comparison rule: exact WAL replay and final artifact set equality.
- Invalid objective policy: partial-commit states are failures.
### 0.B Reproducibility Contract
- Replayable given `(wal_records, run_id, tenant_id)`.
### 0.C Numeric Policy
- Counters and sequence IDs use uint64.
### 0.D Ordering and Tie-Break Policy
- WAL records are strictly ordered by `wal_seq`.
### 0.E Parallel, Concurrency, and Reduction Policy
- Exactly one active commit writer per `(tenant_id, run_id)`.
### 0.F Environment and Dependency Policy
- Determinism level: `BITWISE`.
### 0.G Operator Manifest
- `UML_OS.Commit.WALAppend_v1`
- `UML_OS.Commit.WALRecover_v1`
- `UML_OS.Commit.FinalizeRunCommit_v1`
- `UML_OS.Error.Emit_v1`
### 0.H Namespacing and Packaging
- WAL paths:
  - `wal/run_commit/<tenant_id>/<run_id>/records/<wal_seq>.cbor`
  - `wal/run_commit/<tenant_id>/<run_id>/commit.cbor` (single terminal commit object)
### 0.I Outputs and Metric Schema
- Outputs: `(commit_status, commit_record_hash)`.
### 0.J Spec Lifecycle Governance
- WAL record shape changes are MAJOR.
### 0.K Failure and Error Semantics
- Abort on sequence gaps, duplicate terminal records, or hash mismatch.
### 0.L Input/Data Provenance
- All artifact IDs/hashes in WAL must be content-addressed.

---
## 2) System Model
### I.A Persistent State
- WAL append log and commit index.
### I.B Inputs and Hyperparameters
- temp artifact refs and final artifact refs.
### I.C Constraints and Feasible Set
- valid iff WAL sequence monotone and commit protocol complete.
### I.D Transient Variables
- recovery plan and validation diagnostics.
### I.E Invariants and Assertions
- exactly one committed terminal record per run.

### II.F WAL Record Schema (Normative)
- Required fields:
  - `tenant_id:string`
  - `run_id:string`
  - `wal_seq:uint64`
  - `record_type:enum("PREPARE","CERT_SIGNED","FINALIZE","ROLLBACK")`
  - `trace_tmp_hash?:bytes32`
  - `checkpoint_tmp_hash?:bytes32`
  - `lineage_tmp_hash?:bytes32`
  - `certificate_tmp_hash?:bytes32`
  - `trace_final_hash?:bytes32`
  - `checkpoint_final_hash?:bytes32`
  - `lineage_final_hash?:bytes32`
  - `certificate_final_hash?:bytes32`
  - `policy_hash?:bytes32`
  - `operator_registry_hash?:bytes32`
  - `determinism_profile_hash?:bytes32`
  - `trace_tail_hash?:bytes32`
  - `checkpoint_merkle_root?:bytes32`
  - `lineage_root_hash?:bytes32`
  - `certificate_hash?:bytes32`
  - `prev_record_hash:bytes32`
  - `record_hash:bytes32`

WAL hash-chain rule:
- `record_hash_i = SHA-256(CBOR_CANONICAL(["wal_rec_v1", wal_seq_i, prev_record_hash_i, record_type_i, payload_i]))`

Terminal commit record rule:
- `record_type="FINALIZE"` MUST include:
  - `trace_tail_hash`, `checkpoint_merkle_root`, `lineage_root_hash`, `certificate_hash`,
  - `manifest_hash`, `policy_hash`, `operator_registry_hash`, `determinism_profile_hash`.

### II.G Recovery Rule (Normative)
- On startup:
  - if terminal `FINALIZE` exists and all final artifacts verify, commit is complete.
  - if only non-terminal records exist, rollback temp objects and emit deterministic failure record.
  - if terminal `ROLLBACK` exists, no final artifacts may be visible.

Backend-specific atomic publish:
- Local FS:
  - write temp files, `fsync(file)`, atomic rename, `fsync(directory)`.
- Object stores (S3/GCS compatible):
  - write immutable content objects first,
  - publish `commit.cbor` via conditional write (create-if-absent generation precondition),
  - commit object is immutable and singular for `(tenant_id, run_id)`.

---
## 3) Initialization
1. Open/create WAL stream.
2. Validate existing sequence continuity.
3. Initialize commit state machine.

---
## 4) Operator Manifest
- `UML_OS.Commit.WALAppend_v1`
- `UML_OS.Commit.WALRecover_v1`
- `UML_OS.Commit.FinalizeRunCommit_v1`
- `UML_OS.Error.Emit_v1`

---
## 5) Operator Definitions
**Operator:** `UML_OS.Commit.WALAppend_v1`  
**Category:** IO  
**Signature:** `(wal_record -> wal_state')`  
**Purity class:** IO  
**Determinism:** deterministic  
**Definition:** appends canonical record with monotone `wal_seq`.

**Operator:** `UML_OS.Commit.WALRecover_v1`  
**Category:** IO  
**Signature:** `(wal_stream, artifact_store -> recovery_report)`  
**Purity class:** IO  
**Determinism:** deterministic  
**Definition:** executes finalize-or-rollback deterministic recovery.

---
## 6) Procedure
```text
1. WALAppend_v1(PREPARE)
2. WALAppend_v1(CERT_SIGNED)
3. FinalizeRunCommit_v1
4. WALAppend_v1(FINALIZE)
```

---
## 7) Trace & Metrics
### Logging rule
- Every WAL transition emits deterministic trace records.
### Trace schema
- `run_header`: tenant_id, run_id
- `iter`: wal_seq, record_type, status
- `run_end`: commit_status, commit_record_hash
### Metric schema
- `wal_records`, `recovery_attempts`, `rollback_count`
### Comparability guarantee
- Comparable iff WAL schema and recovery rules are identical.

---
## 8) Validation
#### VII.A Lint rules (mandatory)
- monotone sequence, single terminal state.
#### VII.B Operator test vectors (mandatory)
- crash-before-finalize, crash-after-cert, duplicate-finalize cases.
#### VII.C Golden traces (mandatory)
- golden commit and recovery traces.

---
## 9) Refactor & Equivalence
#### VIII.A Equivalence levels
- E0 for final commit status and committed artifact hashes.
#### VIII.B Allowed refactor categories
- storage backend changes preserving WAL semantics.
#### VIII.C Equivalence test procedure (mandatory)
- exact compare of terminal WAL state and final artifacts.

---
## 10) Checkpoint/Restore
### Checkpoint contents
- WAL cursor and last validated terminal record hash.
### Serialization
- deterministic canonical CBOR.
### Restore semantics
- resumed commit/recovery produces identical terminal outcome.
