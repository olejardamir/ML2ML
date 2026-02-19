# UML_OS Redaction Policy Contract
**EQC Compliance:** Merged single-file EQC v1.1 Option A.

**Algorithm:** `UML_OS.Security.RedactionPolicy_v1`  
**Purpose (1 sentence):** Define deterministic field-level trace/evidence redaction rules that preserve verifiability while preventing sensitive leakage.  
**Spec Version:** `UML_OS.Security.RedactionPolicy_v1` | 2026-02-18 | Authors: Olejar Damir  
**Domain / Problem Class:** Deterministic privacy-preserving telemetry transformation.

---
## 1) Header & Global Semantics
### 0.0 Identity
- **Algorithm:** `UML_OS.Security.RedactionPolicy_v1`
- **Purpose (1 sentence):** Deterministic redaction contract for trace and governance records.
### 0.A Objective Semantics
- Optimization sense: `MINIMIZE`
- Objective type: `Scalar`
- Primary objective: eliminate raw sensitive payload exposure while preserving replay/audit comparability.
### 0.B Reproducibility Contract
- Replayable given `(redaction_mode, redaction_policy_hash, redaction_key_id, canonicalization_policy)`.
### 0.C Numeric Policy
- Redacted numeric values must be either deterministic bucket values or HMAC digests over canonical preimages.
### 0.D Ordering and Tie-Break Policy
- Field traversal order is canonical schema order.
### 0.E Parallel, Concurrency, and Reduction Policy
- Parallel redaction is allowed only if output ordering remains canonical and deterministic.
### 0.F Environment and Dependency Policy
- HMAC implementation/version must be pinned and included in `redaction_policy_hash`.
### 0.G Operator Manifest
- `UML_OS.Security.RedactRecord_v1`
- `UML_OS.Security.ComputeRedactionPolicyHash_v1`
- `UML_OS.Security.ValidateRedactionCoverage_v1`
- `UML_OS.Error.Emit_v1`
### 0.H Namespacing and Packaging
- `UML_OS.Security.*` namespace.
### 0.I Outputs and Metric Schema
- Outputs: `(redacted_record, redaction_audit)`
- Metrics: `redacted_field_count`, `forbidden_raw_field_count`
### 0.J Spec Lifecycle Governance
- Any field-classification or preimage-format change is MAJOR.
### 0.K Failure and Error Semantics
- Deterministic abort on missing required key material or policy mismatch.
### 0.L Input/Data Provenance
- Source schema hash and record schema version are required redaction inputs.

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
- Named tolerances: `EPS_EQ=1e-10`, `EPS_DENOM=1e-12`.
- NaN/Inf policy: invalid values trigger deterministic failure handling per 0.K.
- Determinism level: `BITWISE` for contract-critical outputs unless stricter local declaration exists.

## 2) System Model
### I.A Persistent State
- `redaction_policy_registry`
- key reference metadata (`redaction_key_id`, validity window)
### I.B Inputs and Hyperparameters
- `record`, `schema_version`, `redaction_mode`, `redaction_key_id`, `redaction_policy_hash`
### I.C Constraints and Feasible Set
- Only declared fields may be redacted.
- Mandatory verification fields must remain unredacted.
### I.D Transient Variables
- canonical field preimages, hmac outputs, coverage diagnostics.
### I.E Invariants and Assertions
- No raw samples, no raw gradients, no raw parameter values in redacted outputs.

### II.F Field Classification (Normative)
- `PUBLIC`: metadata safe for disclosure.
- `INTERNAL`: infra/config fields; may be redacted by policy.
- `CONFIDENTIAL`: always redacted or bucketed per mode.

### II.G Canonical Redaction Rules (Normative)
- Redaction modes:
  - `NONE`
  - `HMAC_SHA256_V1`
- Preimage format for HMAC:
  - `CBOR_CANONICAL(["redaction_v1", schema_version, field_path, field_value_canonical])`
- Output encoding:
  - `redacted_value = HMAC_SHA256(key(redaction_key_id), preimage)` as `bytes32`.
- Bucketed numeric fallback (if policy declares):
  - deterministic bucket boundaries fixed in policy and included in `redaction_policy_hash`.

### II.H Mandatory Unredacted Verification Fields
- Fields required for replay/certificate validation must remain present and verifiable:
  - `replay_token`, `record_hash`, `trace_final_hash`, `policy_bundle_hash`, `authz_decision_hash`, `policy_gate_hash`, `checkpoint_hash`, `execution_certificate_hash`.

### II.I Policy Hash Definition
- `redaction_policy_hash = SHA-256(CBOR_CANONICAL(["redaction_policy_v1", policy_rules, field_classification_map, preimage_format_id, key_policy]))`.

---
## 3) Initialization
1. Load redaction policy by `redaction_policy_hash`.
2. Validate key metadata for `redaction_key_id`.
3. Validate schema-version compatibility.

---
## 4) Operator Manifest
- `UML_OS.Security.RedactRecord_v1`
- `UML_OS.Security.ComputeRedactionPolicyHash_v1`
- `UML_OS.Security.ValidateRedactionCoverage_v1`
- `UML_OS.Error.Emit_v1`

---
## 5) Operator Definitions
External operator reference: `UML_OS.Error.Emit_v1` is defined in `docs/layer1-foundation/Error-Codes.md`.

**Operator:** `UML_OS.Security.RedactRecord_v1`  
**Category:** Security  
**Signature:** `(record, redaction_mode, redaction_key_id, redaction_policy -> redacted_record, redaction_audit)`  
**Purity class:** IO  
**Determinism:** deterministic  
**Definition:** Applies field-level deterministic redaction according to II.G while preserving II.H fields.

**Operator:** `UML_OS.Security.ValidateRedactionCoverage_v1`  
**Category:** Security  
**Signature:** `(record_schema, redaction_policy -> coverage_report)`  
**Purity class:** PURE  
**Determinism:** deterministic  
**Definition:** Ensures all `CONFIDENTIAL` fields are transformed and mandatory verification fields remain available.

---
## 6) Procedure
```text
1. ValidateRedactionCoverage_v1(schema, policy)
2. For each field in canonical order:
   - if field is CONFIDENTIAL: apply mode-specific transform
   - else preserve field value
3. Emit redaction_audit with transformed field paths and counts
4. Return redacted_record
```

---
## 7) Trace & Metrics
### Logging rule
- Redaction decisions emit deterministic audit records without raw sensitive payloads.
### Trace schema
- `run_header`: redaction_mode, redaction_key_id, redaction_policy_hash
- `iter`: record_id, redacted_field_count, status
- `run_end`: coverage_status
### Metric schema
- `redacted_field_count`, `forbidden_raw_field_count`
### Comparability guarantee
- Comparable iff `redaction_policy_hash`, `redaction_mode`, and canonical preimage rules are identical.

---
## 8) Validation
#### VII.A Lint rules (mandatory)
- No undeclared redaction transforms; no raw confidential fields in outputs.
#### VII.B Operator test vectors (mandatory)
- HMAC preimage vectors, bucketization vectors, missing-key failures.
#### VII.C Golden traces (mandatory)
- Golden redaction traces with deterministic hashes.

---
## 9) Refactor & Equivalence
#### VIII.A Equivalence levels
- E0 for transformed output fields and audit hashes.
#### VIII.B Allowed refactor categories
- Implementation/runtime optimizations preserving bytes-level outputs.
#### VIII.C Equivalence test procedure (mandatory)
- Exact compare of redacted records and redaction_audit hashes.

---
## 10) Checkpoint/Restore
### Checkpoint contents
- active `redaction_policy_hash`, `redaction_key_id`, and coverage audit cursor.
### Serialization
- deterministic canonical CBOR.
### Restore semantics
- Restored redaction context must produce identical redacted outputs for identical inputs.
