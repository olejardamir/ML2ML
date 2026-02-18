# UML_OS Config Schema Contract
**EQC Compliance:** Merged single-file EQC v1.1 Option A.

**Algorithm:** `UML_OS.Config.SchemaValidator_v1`  
**Purpose (1 sentence):** Define and validate the canonical manifest/config schema used by all UML_OS components.  
**Spec Version:** `UML_OS.Config.SchemaValidator_v1` | 2026-02-18 | Authors: Olejar Damir  
**Domain / Problem Class:** Deterministic configuration validation.

---
## 1) Header & Global Semantics
### 0.0 Identity
- **Algorithm:** `UML_OS.Config.SchemaValidator_v1`
- **Purpose (1 sentence):** Canonical manifest schema enforcement.
- **Spec Version:** `UML_OS.Config.SchemaValidator_v1` | 2026-02-18 | Authors: Olejar Damir
- **Domain / Problem Class:** Config schema validation.
### 0.A Objective Semantics
- Minimize schema violations.
### 0.B Reproducibility Contract
- Replayable given `(schema_version, manifest_hash)`.
### 0.C Numeric Policy
- Type/constraint checks deterministic; float constraints in binary64.
### 0.D Ordering and Tie-Break Policy
- Field validation order is canonical by schema key path.
### 0.E Parallel, Concurrency, and Reduction Policy
- Validation is deterministic single-pass.
### 0.F Environment and Dependency Policy
- Determinism level: `BITWISE` for validation output.
### 0.G Operator Manifest
- `UML_OS.Config.ValidateRequiredFields_v1`
- `UML_OS.Config.ValidateTypes_v1`
- `UML_OS.Config.ValidateRanges_v1`
- `UML_OS.Config.NormalizeDefaults_v1`
- `UML_OS.Error.Emit_v1`
### 0.H Namespacing and Packaging
- Fully-qualified config operators required.
### 0.I Outputs and Metric Schema
- Outputs: `(normalized_manifest, validation_report)`.
- Metrics: `missing_fields`, `type_errors`, `range_errors`.
- Completion status: `success | failed`.
### 0.J Spec Lifecycle Governance
- Breaking schema changes require MAJOR bump.
### 0.K Failure and Error Semantics
- Abort-only on invalid manifest.
### 0.L Input/Data Provenance
- Input manifest hash and source path recorded.

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
- schema registry.
### I.B Inputs and Hyperparameters
- raw manifest and schema version.
### I.C Constraints and Feasible Set
- Valid if all required/type/range checks pass.
### I.D Transient Variables
- validation diagnostics.
### I.E Invariants and Assertions
- normalized manifest is canonical and deterministic.

---
## 3) Initialization
1. Load schema.
2. Parse raw manifest.
3. Initialize diagnostics.

---
## 4) Operator Manifest
- `UML_OS.Config.ValidateRequiredFields_v1`
- `UML_OS.Config.ValidateTypes_v1`
- `UML_OS.Config.ValidateRanges_v1`
- `UML_OS.Config.NormalizeDefaults_v1`
- `UML_OS.Error.Emit_v1`

---
## 5) Operator Definitions

External operator reference: `UML_OS.Error.Emit_v1` is defined normatively in `Error-Codes.md` and imported by reference.

Template conformance note (III.A): each operator definition in this section is interpreted with the full EQC operator template fields. When a field is not repeated inline, the section-level defaults are: explicit typed signatures, deterministic ordering/tie handling, declared numerical policy inheritance, deterministic failure semantics (0.K), explicit dependencies, and VII.B test-vector coverage.

**Operator:** `UML_OS.Config.ValidateRequiredFields_v1`  
**Category:** IO  
**Signature:** `(manifest, schema -> report)`  
**Purity class:** PURE  
**Determinism:** deterministic  
**Definition:** checks required keys and nested objects.

**Operator:** `UML_OS.Config.ValidateTypes_v1`  
**Category:** IO  
**Signature:** `(manifest, schema -> report)`  
**Purity class:** PURE  
**Determinism:** deterministic  
**Definition:** checks scalar/object/list types.

**Operator:** `UML_OS.Config.ValidateRanges_v1`  
**Category:** IO  
**Signature:** `(manifest, schema -> report)`  
**Purity class:** PURE  
**Determinism:** deterministic  
**Definition:** checks numeric ranges/enums.

**Operator:** `UML_OS.Config.NormalizeDefaults_v1`  
**Category:** IO  
**Signature:** `(manifest, schema -> normalized_manifest)`  
**Purity class:** PURE  
**Determinism:** deterministic  
**Definition:** fills defaults and produces canonical ordering.

---
## 6) Procedure
```text
1. ValidateRequiredFields_v1
2. ValidateTypes_v1
3. ValidateRanges_v1
4. NormalizeDefaults_v1
5. Return normalized manifest + report
```

---
## 7) Trace & Metrics
### Logging rule
Validation emits deterministic field-level diagnostics.
### Trace schema
- `run_header`: schema_version, manifest_hash
- `iter`: field_path, check, result
- `run_end`: status
### Metric schema
- `missing_fields`, `type_errors`, `range_errors`
### Comparability guarantee
Comparable iff schema version and canonicalization rules are identical.

---
## 8) Validation
#### VII.A Lint rules (mandatory)
Passes deterministic field ordering and completeness checks.
#### VII.B Operator test vectors (mandatory)
Includes valid/invalid manifest fixtures.
#### VII.C Golden traces (mandatory)
Golden normalized-manifest hashes and diagnostics.

---
## 9) Refactor & Equivalence
#### VIII.A Equivalence levels
- E0 for normalized manifest and report.
#### VIII.B Allowed refactor categories
- parser/validator optimization preserving outputs.
#### VIII.C Equivalence test procedure (mandatory)
Exact diff on normalized manifest/report.

---
## 10) Checkpoint/Restore
### Checkpoint contents
- schema and partial diagnostics.
### Serialization
- deterministic JSON/CBOR.
### Restore semantics
- resume yields identical validation output.

