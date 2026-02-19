# UML_OS Artifact Store Adapter Guide
**EQC Compliance:** Merged single-file EQC v1.1 Option A.

**Algorithm:** `UML_OS.Storage.ArtifactStoreAdapterGuide_v1`  
**Purpose (1 sentence):** Define deterministic adapter behavior for local/object-store artifact persistence, commit pointers, and recovery-safe semantics.  
**Spec Version:** `UML_OS.Storage.ArtifactStoreAdapterGuide_v1` | 2026-02-19 | Authors: Olejar Damir  
**Domain / Problem Class:** Storage adapter implementation.

---
## 1) Header & Global Semantics
### 0.0 Identity
- **Algorithm:** `UML_OS.Storage.ArtifactStoreAdapterGuide_v1`
- **Purpose (1 sentence):** Deterministic storage adapter contract.
### 0.A Objective Semantics
- minimize commit inconsistency and recovery ambiguity.
### 0.B Reproducibility Contract
- storage outcomes reproducible from `(object_keys, object_hashes, commit_policy_hash)`.
### 0.C Numeric Policy
- byte counts and sequence ids are uint64 exact.
### 0.D Ordering and Tie-Break Policy
- object writes ordered by deterministic key order.
### 0.E Parallel, Concurrency, and Reduction Policy
- data objects can upload in parallel; commit-pointer publish is single-writer.
### 0.F Environment and Dependency Policy
- adapter must declare backend type and consistency model.
### 0.G Operator Manifest
- `UML_OS.Storage.PutImmutableObject_v1`
- `UML_OS.Storage.PublishCommitPointer_v1`
- `UML_OS.Storage.ValidateCommittedRun_v1`
- `UML_OS.Error.Emit_v1`
### 0.H Namespacing and Packaging
- `UML_OS.Storage.*` namespace.
### 0.I Outputs and Metric Schema
- outputs: `(storage_report, commit_status, recovery_report)`.
### 0.J Spec Lifecycle Governance
- commit-pointer semantics changes are MAJOR.
### 0.K Failure and Error Semantics
- partial commit states must fail closed deterministically.
### 0.L Input/Data Provenance
- all objects referenced by content hash.

---
## 2) System Model
### I.A Persistent State
- object index and commit-pointer map.
### I.B Inputs and Hyperparameters
- object set, run id, tenant id, backend mode.
### I.C Constraints and Feasible Set
- COMMITTED pointer publish must be conditional create-if-absent.
### I.D Transient Variables
- upload status and pointer payload.
### I.E Invariants and Assertions
- immutable objects never overwritten.

---
## 3) Initialization
1. Resolve backend adapter policy.
2. Initialize object index.
3. Validate write preconditions.

---
## 4) Operator Manifest
- `UML_OS.Storage.PutImmutableObject_v1`
- `UML_OS.Storage.PublishCommitPointer_v1`
- `UML_OS.Storage.ValidateCommittedRun_v1`
- `UML_OS.Error.Emit_v1`

---
## 5) Operator Definitions
**Operator:** `UML_OS.Storage.PublishCommitPointer_v1`  
**Signature:** `(tenant_id, run_id, pointer_payload -> publish_status)`  
**Purity class:** IO  
**Determinism:** deterministic  
**Definition:** Publishes COMMITTED pointer atomically using conditional semantics.

---
## 6) Procedure
```text
1. Write immutable content-addressed objects
2. Validate object hashes
3. Publish COMMITTED pointer via conditional create
4. Validate committed run linkage
```

---
## 7) Trace & Metrics
- Metrics: `objects_written`, `bytes_written`, `pointer_publish_attempts`, `recovery_events`.
- Trace includes pointer payload hash and commit status.

---
## 8) Validation
- backend matrix tests (local fs, s3-compatible, gcs-compatible).
- crash-recovery tests for partial upload states.

---
## 9) Refactor & Equivalence
- E0 for commit-pointer payload and committed artifact linkage.

---
## 10) Checkpoint/Restore
- checkpoint stores upload cursor and pending pointer payload hash.
- restore resumes upload/commit deterministically.
