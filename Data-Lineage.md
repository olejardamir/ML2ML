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
- Optimization sense: `MINIMIZE`
- Objective type: `Scalar`
- Primary comparison rule: deterministic total preorder over declared primary metric tuple with `EPS_EQ` tie handling.
- Invalid objective policy: `NaN/Inf` ranked as worst-case and handled deterministically per 0.K.
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
- snapshot catalog and lineage graph.
### I.B Inputs and Hyperparameters
- `tenant_id`, `run_id`, source refs, split configs, transform specs, `sampler_config_hash`.
### I.C Constraints and Feasible Set
- snapshot immutable after publish.
### I.D Transient Variables
- hashing buffers and lineage diagnostics.
### I.E Invariants and Assertions
- every snapshot ID is content-addressed and deterministic.

### II.F Snapshot Identifier (Normative)
- `dataset_snapshot_id = SHA-256(CBOR([tenant_id, run_id, dataset_root_hash, split_hashes, transform_chain_hash, sampler_config_hash]))`
- Cross-tenant rule: all lineage objects are namespaced by `(tenant_id, object_id)`; cross-tenant references must hard-fail deterministically.
- CAS retention metadata is mandatory:
  - `retention_class ∈ {golden, certified_release, experimental, ephemeral}`,
  - `pin_root_refs` (certificate/model-release roots),
  - `gc_eligible_after_utc`.
- GC invariant: lineage objects reachable from active certificate/release roots are not collectible.
- Commit binding: finalized lineage objects must participate in the atomic run commit protocol and be referenced by `lineage_root_hash` in the execution certificate.

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
