# UML_OS Data Lineage Contract
**EQC Compliance:** Merged single-file EQC v1.1 Option A.

**Algorithm:** `UML_OS.Data.Lineage_v1`  
**Purpose (1 sentence):** Define deterministic dataset snapshot lineage and transform-chain provenance for replayable training/evaluation runs.  
**Spec Version:** `UML_OS.Data.Lineage_v1` | 2026-02-18 | Authors: Olejar Damir  
**Domain / Problem Class:** Data provenance and versioning.

---
## 1) Header & Global Semantics
### 0.0 Identity
- **Algorithm:** `UML_OS.Data.Lineage_v1`
- **Purpose (1 sentence):** Deterministic dataset snapshot provenance.
### 0.A Objective Semantics
- Minimize unverifiable data lineage.
### 0.B Reproducibility Contract
- Replayable given `(dataset_snapshot_id, transform_chain_hash, sampler_config_hash)`.
### 0.C Numeric Policy
- Hashes/IDs exact.
### 0.D Ordering and Tie-Break Policy
- Transform chain ordering fixed by declared transform_seq.
### 0.E Parallel, Concurrency, and Reduction Policy
- Multi-source merges resolved deterministically by sorted source ID.
### 0.F Environment and Dependency Policy
- Data import and transforms must be content-addressed and immutable.
### 0.G Operator Manifest
- `UML_OS.Data.BuildSnapshot_v1`
- `UML_OS.Data.ComputeLineageHash_v1`
- `UML_OS.Data.ValidateSnapshot_v1`
- `UML_OS.Error.Emit_v1`
### 0.H Namespacing and Packaging
- `UML_OS.Data.*` namespace.
### 0.I Outputs and Metric Schema
- Outputs: `(dataset_snapshot_id, lineage_report)`
- Metrics: `source_count`, `transform_count`, `snapshot_size_bytes`
### 0.J Spec Lifecycle Governance
- snapshot ID and lineage hash semantics changes are MAJOR.
### 0.K Failure and Error Semantics
- abort on snapshot hash mismatch or missing lineage refs.
### 0.L Input/Data Provenance
- lineage includes source hashes and transform chain hash.

---
## 2) System Model
### I.A Persistent State
- snapshot catalog and lineage graph.
### I.B Inputs and Hyperparameters
- source refs, split configs, transform specs.
### I.C Constraints and Feasible Set
- snapshot immutable after publish.
### I.D Transient Variables
- hashing buffers and lineage diagnostics.
### I.E Invariants and Assertions
- every snapshot ID is content-addressed and deterministic.

### II.F Snapshot Identifier (Normative)
- `dataset_snapshot_id = SHA-256(CBOR([dataset_root_hash, split_hashes, transform_chain_hash]))`

---
## 3) Initialization
1. Load source references.
2. Validate transform chain.
3. Initialize snapshot build context.

---
## 4) Operator Manifest
- `UML_OS.Data.BuildSnapshot_v1`
- `UML_OS.Data.ComputeLineageHash_v1`
- `UML_OS.Data.ValidateSnapshot_v1`
- `UML_OS.Error.Emit_v1`

---
## 5) Operator Definitions
**Operator:** `UML_OS.Data.BuildSnapshot_v1`  
**Category:** Data  
**Signature:** `(source_refs, transform_chain, split_defs -> dataset_snapshot_id)`  
**Purity class:** IO  
**Determinism:** deterministic  
**Definition:** materializes immutable snapshot and canonical lineage metadata.

---
## 6) Procedure
```text
1. ValidateSnapshot_v1(inputs)
2. ComputeLineageHash_v1
3. BuildSnapshot_v1
4. Return dataset_snapshot_id + lineage_report
```

---
## 7) Trace & Metrics
### Logging rule
- snapshot creation emits deterministic lineage records.
### Trace schema
- `run_header`: source_hashes, transform_chain_hash
- `iter`: step, hash, status
- `run_end`: dataset_snapshot_id
### Metric schema
- `source_count`, `transform_count`
### Comparability guarantee
- comparable iff source hashes, transforms, and split configs are identical.

---
## 8) Validation
#### VII.A Lint rules (mandatory)
- immutable snapshots, deterministic hash serialization.
#### VII.B Operator test vectors (mandatory)
- source/transform permutations, split hash validations.
#### VII.C Golden traces (mandatory)
- golden snapshot IDs for canonical datasets.

---
## 9) Refactor & Equivalence
#### VIII.A Equivalence levels
- E0 for snapshot ID and lineage hashes.
#### VIII.B Allowed refactor categories
- storage layout changes preserving snapshot ID semantics.
#### VIII.C Equivalence test procedure (mandatory)
- exact snapshot ID compare.

---
## 10) Checkpoint/Restore
### Checkpoint contents
- active snapshot build cursor and lineage partial hashes.
### Serialization
- deterministic CBOR.
### Restore semantics
- resumed snapshot build yields identical snapshot ID.
