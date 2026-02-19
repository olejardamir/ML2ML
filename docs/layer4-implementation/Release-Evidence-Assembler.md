# UML_OS Release Evidence Assembler Contract
**EQC Compliance:** Merged single-file EQC v1.1 Option A.

**Algorithm:** `UML_OS.Release.EvidenceAssembler_v1`  
**Purpose (1 sentence):** Define deterministic assembly of release evidence bundles consumed by certificate signing and deployment gates.  
**Spec Version:** `UML_OS.Release.EvidenceAssembler_v1` | 2026-02-19 | Authors: Olejar Damir  
**Domain / Problem Class:** Release governance and evidence binding.

---
## 1) Header & Global Semantics
### 0.0 Identity
- **Algorithm:** `UML_OS.Release.EvidenceAssembler_v1`
- **Purpose (1 sentence):** Deterministic release evidence assembly contract.
### 0.A Objective Semantics
- minimize missing or inconsistent release evidence.
### 0.B Reproducibility Contract
- evidence bundle reproducible from `(release_manifest_hash, artifact_hash_set, assembly_policy_hash)`.
### 0.C Numeric Policy
- hash-based commitments only.
### 0.D Ordering and Tie-Break Policy
- evidence entries sorted by `(evidence_type, evidence_id)`.
### 0.E Parallel, Concurrency, and Reduction Policy
- evidence fetches parallel; final assembly deterministic.
### 0.F Environment and Dependency Policy
- assembler runtime and policy pinned.
### 0.G Operator Manifest
- `UML_OS.Release.CollectEvidenceRefs_v1`
- `UML_OS.Release.BuildEvidenceBundle_v1`
- `UML_OS.Release.ValidateEvidenceBundle_v1`
- `UML_OS.Error.Emit_v1`
### 0.H Namespacing and Packaging
- `UML_OS.Release.*` namespace.
### 0.I Outputs and Metric Schema
- outputs: `(evidence_bundle_ref, evidence_bundle_hash, validation_report)`.
### 0.J Spec Lifecycle Governance
- required evidence field changes are MAJOR.
### 0.K Failure and Error Semantics
- missing mandatory evidence fails assembly.
### 0.L Input/Data Provenance
- all evidence refs must be content-addressed.

---
## 2) System Model
### I.A Persistent State
- evidence policy catalog and assembler version.
### I.B Inputs and Hyperparameters
- release manifest, trace/checkpoint/certificate refs, registry refs.
### I.C Constraints and Feasible Set
- mandatory evidence set must be complete.
### I.D Transient Variables
- resolved evidence rows and validation diagnostics.
### I.E Invariants and Assertions
- bundle hash uniquely identifies assembled evidence set.

---
## 3) Initialization
1. Load evidence policy.
2. Resolve required evidence set.
3. Initialize assembly context.

---
## 4) Operator Manifest
- `UML_OS.Release.CollectEvidenceRefs_v1`
- `UML_OS.Release.BuildEvidenceBundle_v1`
- `UML_OS.Release.ValidateEvidenceBundle_v1`
- `UML_OS.Error.Emit_v1`

---
## 5) Operator Definitions
**Operator:** `UML_OS.Release.BuildEvidenceBundle_v1`  
**Signature:** `(evidence_refs, policy -> evidence_bundle)`  
**Purity class:** IO  
**Determinism:** deterministic  
**Definition:** Builds canonical evidence bundle and computes commitment hash.

---
## 6) Procedure
```text
1. Collect required evidence refs
2. Build canonical evidence bundle
3. Validate completeness and hash links
4. Emit bundle ref and bundle hash
```

---
## 7) Trace & Metrics
- Metrics: `required_evidence_total`, `missing_evidence_count`, `bundle_size_bytes`.
- Trace includes bundle hash and validation status.

---
## 8) Validation
- golden evidence bundles for release profiles.
- deterministic ordering and hash stability tests.

---
## 9) Refactor & Equivalence
- E0 for bundle hash and validation verdict.

---
## 10) Checkpoint/Restore
- checkpoint stores evidence-resolution cursor and partial bundle hash.
- restore continues assembly deterministically.

---
## 11) Related Contracts
- `docs/layer4-implementation/Contracts-Artifact-Lifecycle.md`
- `docs/layer2-specs/Execution-Certificate.md`
- `docs/layer2-specs/Run-Commit-WAL.md`
