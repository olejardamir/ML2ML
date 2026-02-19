# UML_OS Digest Catalog Contract
**EQC Compliance:** Merged single-file EQC v1.1 Option A.

**Algorithm:** `UML_OS.Registry.DigestCatalog_v1`  
**Purpose (1 sentence):** Define an authoritative catalog mapping digest labels to full bytes32 values and deterministic resolution rules.  
**Spec Version:** `UML_OS.Registry.DigestCatalog_v1` | 2026-02-19 | Authors: Olejar Damir  
**Domain / Problem Class:** Digest governance and consistency control.

---
## 1) Header & Global Semantics
### 0.0 Identity
- **Algorithm:** `UML_OS.Registry.DigestCatalog_v1`
- **Purpose (1 sentence):** Canonical digest label-to-bytes32 mapping.
### 0.A Objective Semantics
- Optimization sense: `MINIMIZE`
- Objective type: `Scalar`
- Primary comparison rule: exact digest lookup and equality.
- Invalid objective policy: unresolved label is fatal.
### 0.B Reproducibility Contract
- Replayable given `(catalog_version, catalog_hash)`.
### 0.C Numeric Policy
- Digests are fixed-length `bytes32`.
### 0.D Ordering and Tie-Break Policy
- Records sorted lexicographically by `digest_label`.
### 0.E Parallel, Concurrency, and Reduction Policy
- Lookup is pure read-only.
### 0.F Environment and Dependency Policy
- Determinism level: `BITWISE`.
### 0.G Operator Manifest
- `UML_OS.Registry.ResolveDigestRef_v1`
- `UML_OS.Registry.ValidateDigestCatalog_v1`
- `UML_OS.Error.Emit_v1`
### 0.H Namespacing and Packaging
- Canonical location: `contracts/digest_catalog.cbor`.
### 0.I Outputs and Metric Schema
- Outputs: `(resolved_digest, catalog_report)`.
### 0.J Spec Lifecycle Governance
- Label removal is MAJOR.
### 0.K Failure and Error Semantics
- Abort on unresolved or duplicate labels.
### 0.L Input/Data Provenance
- Catalog is content-addressed and immutable.

---
## 2) System Model
### I.A Persistent State
- `digest_catalog`.
### I.B Inputs and Hyperparameters
- `digest_ref` and catalog blob.
### I.C Constraints and Feasible Set
- Valid iff labels unique and digests are bytes32.
### I.D Transient Variables
- resolution diagnostics.
### I.E Invariants and Assertions
- no duplicate labels.

### II.F Digest Catalog Schema (Normative)
- Required record fields:
  - `digest_label:string`
  - `digest_value:bytes32`
  - `algorithm:string` (must be `sha256`)
  - `domain_tag:string`

### II.H Catalog Commitment (Normative)
- `entries_sorted` are sorted by `digest_label` ascending (bytewise UTF-8).
- `catalog_hash = SHA-256(CBOR_CANONICAL(["digest_catalog_v1", catalog_version, entries_sorted]))`.
- Any document using `sha256:<label>` references is valid only against the committed `catalog_hash`.

### II.G Resolution Rule (Normative)
- `digest_ref` supports two forms:
  - inline: `sha256:<hex64>` where `<hex64>` is exactly 64 lowercase hex chars and resolves directly to bytes32,
  - catalog label: `sha256:<label>` where `<label>` must exist in catalog and resolve to bytes32.
- Disambiguation rule:
  - if tail matches `^[0-9a-f]{64}$`, treat as inline bytes32 digest,
  - otherwise treat as catalog label and perform lookup.
- Signature/hash computations must use resolved bytes32 digest bytes, never label string bytes.

---
## 3) Initialization
1. Load digest catalog.
2. Validate schema and uniqueness.
3. Build lookup index.

---
## 4) Operator Manifest
- `UML_OS.Registry.ResolveDigestRef_v1`
- `UML_OS.Registry.ValidateDigestCatalog_v1`
- `UML_OS.Error.Emit_v1`

---
## 5) Operator Definitions
**Operator:** `UML_OS.Registry.ResolveDigestRef_v1`  
**Category:** Governance  
**Signature:** `(digest_ref, digest_catalog -> digest_value)`  
**Purity class:** PURE  
**Determinism:** deterministic  
**Definition:** resolves digest labels to bytes32 values.

---
## 6) Procedure
```text
1. ValidateDigestCatalog_v1
2. ResolveDigestRef_v1
3. Return digest_value
```

---
## 7) Trace & Metrics
### Logging rule
- digest reference resolutions emit deterministic events.
### Trace schema
- `run_header`: catalog_hash
- `iter`: digest_ref, status
- `run_end`: resolved_digest
### Metric schema
- `resolved_count`, `missing_count`
### Comparability guarantee
- Comparable iff catalog hash is identical.

---
## 8) Validation
#### VII.A Lint rules (mandatory)
- no unresolved digest labels.
#### VII.B Operator test vectors (mandatory)
- valid/missing/duplicate label cases.
#### VII.C Golden traces (mandatory)
- golden resolution traces.

---
## 9) Refactor & Equivalence
#### VIII.A Equivalence levels
- E0 for digest resolution outputs.
#### VIII.B Allowed refactor categories
- indexing optimizations preserving output.
#### VIII.C Equivalence test procedure (mandatory)
- exact compare of resolved bytes32.

---
## 10) Checkpoint/Restore
### Checkpoint contents
- catalog hash and resolution cursor.
### Serialization
- deterministic canonical CBOR.
### Restore semantics
- identical resolution on resume.
