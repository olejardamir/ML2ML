# UML_OS Canonical CBOR Profile Contract
**EQC Compliance:** Merged single-file EQC v1.1 Option A.

**Algorithm:** `UML_OS.Serialization.CanonicalCBORProfile_v1`  
**Purpose (1 sentence):** Define the single canonical CBOR encoding profile used for all commitment hashes and signatures.  
**Spec Version:** `UML_OS.Serialization.CanonicalCBORProfile_v1` | 2026-02-19 | Authors: Olejar Damir  
**Domain / Problem Class:** Deterministic serialization and cryptographic commitment consistency.

---
## 1) Header & Global Semantics
### 0.0 Identity
- **Algorithm:** `UML_OS.Serialization.CanonicalCBORProfile_v1`
- **Purpose (1 sentence):** Single-source canonical CBOR profile.
### 0.A Objective Semantics
- Optimization sense: `MINIMIZE`
- Objective type: `Scalar`
- Primary comparison rule: byte-identical canonical encoding.
- Invalid objective policy: non-canonical payload is invalid.
### 0.B Reproducibility Contract
- Replayable given `(profile_version, input_object)`.
### 0.C Numeric Policy
- All floating-point values MUST encode as IEEE-754 binary64.
### 0.D Ordering and Tie-Break Policy
- Map keys MUST be sorted in ascending lexicographic order of their canonical encoded key bytes (RFC 8949 canonical ordering).
### 0.E Parallel, Concurrency, and Reduction Policy
- Encoding output must be deterministic independent of thread scheduling.
### 0.F Environment and Dependency Policy
- Determinism level: `BITWISE`.
### 0.G Operator Manifest
- `UML_OS.Serialization.EncodeCanonicalCBOR_v1`
- `UML_OS.Serialization.ValidateCanonicalCBOR_v1`
- `UML_OS.Error.Emit_v1`
### 0.H Namespacing and Packaging
- Canonical profile identifier: `CanonicalSerialization_v1`.
### 0.I Outputs and Metric Schema
- Outputs: `(canonical_bytes, validation_report)`.
### 0.J Spec Lifecycle Governance
- Any rule change is MAJOR.
### 0.K Failure and Error Semantics
- Abort on non-canonical encoding input/output mismatch.
### 0.L Input/Data Provenance
- Input schema and profile id must be declared with hash.

---
## 2) System Model
### I.A Persistent State
- `profile_rules`.
### I.B Inputs and Hyperparameters
- structured object and profile id.
### I.C Constraints and Feasible Set
- valid iff object can be encoded under all canonical constraints.
### I.D Transient Variables
- serializer buffers and diagnostics.
### I.E Invariants and Assertions
- stable bytes for identical object semantics.

### II.F Canonical Rules (Normative)
- RFC 8949 canonical CBOR baseline with profile overrides below.
- Additional restrictions:
  - map keys must be UTF-8 strings,
  - map-key ordering MUST follow canonical encoded-key byte ordering (RFC 8949 canonical ordering),
  - integers MUST be encoded in the shortest possible canonical form,
  - disallow duplicate keys,
  - forbid indefinite-length encodings for strings/arrays/maps,
  - forbid CBOR tags unless explicitly enumerated by consuming schema,
  - NaN and Inf are disallowed for all payloads under this profile,
  - every float is encoded as binary64 regardless of usage context,
  - fixed-length digest fields (`bytes32`, `bytes64`) must match required lengths,
  - optional fields absent are encoded by key omission (never null unless schema explicitly requires null).
  - nonconformant CBOR in any commitment/signature path is a deterministic `CONTRACT_VIOLATION`.

### II.G Commitment Rule (Normative)
- All signatures and commitment hashes MUST use:
  - `SHA-256(CBOR_CANONICAL([...]))`
- Domain-separation tag must be the first element in hashed arrays.

### II.H Conformance Vectors (Normative)
- Implementations MUST pass canonicalization vectors for key ordering, integer shortest-form encoding, and float consistency.
- Minimum required vectors:
  - mixed key lengths and UTF-8 multibyte keys,
  - nested maps with independently canonicalized key ordering,
  - integer shortest-form cases (e.g., `0`, `23`, `24`, `255`, `256`),
  - float binary64 encoding stability,
  - NaN/Inf rejection cases.

---
## 3) Initialization
1. Load profile rules.
2. Validate encoder/decoder implementation.
3. Initialize deterministic buffer policy.

---
## 4) Operator Manifest
- `UML_OS.Serialization.EncodeCanonicalCBOR_v1`
- `UML_OS.Serialization.ValidateCanonicalCBOR_v1`
- `UML_OS.Error.Emit_v1`

---
## 5) Operator Definitions
**Operator:** `UML_OS.Serialization.EncodeCanonicalCBOR_v1`  
**Category:** Serialization  
**Signature:** `(typed_object -> canonical_bytes)`  
**Purity class:** PURE  
**Determinism:** deterministic  
**Definition:** produces canonical CBOR bytes under profile rules.

**Operator:** `UML_OS.Serialization.ValidateCanonicalCBOR_v1`  
**Category:** Serialization  
**Signature:** `(typed_object, canonical_bytes -> validation_report)`  
**Purity class:** PURE  
**Determinism:** deterministic  
**Definition:** validates encoding equivalence and canonical constraints.

---
## 6) Procedure
```text
1. EncodeCanonicalCBOR_v1
2. ValidateCanonicalCBOR_v1
3. Return canonical_bytes + validation_report
```

---
## 7) Trace & Metrics
### Logging rule
- Serialization emits deterministic validation diagnostics.
### Trace schema
- `run_header`: profile_version
- `iter`: object_id, status
- `run_end`: canonical_hash
### Metric schema
- `encoded_objects`, `canonical_failures`
### Comparability guarantee
- Comparable iff profile version is identical.

---
## 8) Validation
#### VII.A Lint rules (mandatory)
- canonical constraints enforced without exceptions.
#### VII.B Operator test vectors (mandatory)
- map ordering, float encoding, optional-absence vectors.
#### VII.C Golden traces (mandatory)
- golden canonical byte snapshots.

---
## 9) Refactor & Equivalence
#### VIII.A Equivalence levels
- E0 for canonical bytes and hash outputs.
#### VIII.B Allowed refactor categories
- implementation refactors preserving byte output.
#### VIII.C Equivalence test procedure (mandatory)
- byte-for-byte compare against golden vectors.

---
## 10) Checkpoint/Restore
### Checkpoint contents
- profile id and serializer implementation hash.
### Serialization
- deterministic canonical CBOR.
### Restore semantics
- identical canonical bytes after restore.
