# UML_OS Code Generation Mapping
**EQC Compliance:** Merged single-file EQC v1.1 Option A.

**Algorithm:** `UML_OS.Implementation.CodeGenerationMapping_v1`  
**Purpose (1 sentence):** Define deterministic mappings from EQC operators to concrete code modules, files, and generated stubs.  
**Spec Version:** `UML_OS.Implementation.CodeGenerationMapping_v1` | 2026-02-18 | Authors: Olejar Damir  
**Domain / Problem Class:** Build-time operator-to-code realization.

---
## 1) Header & Global Semantics
### 0.0 Identity
- **Algorithm:** `UML_OS.Implementation.CodeGenerationMapping_v1`
- **Purpose (1 sentence):** Deterministic code generation mapping.
- **Spec Version:** `UML_OS.Implementation.CodeGenerationMapping_v1` | 2026-02-18 | Authors: Olejar Damir
- **Domain / Problem Class:** Source layout and stub generation.
### 0.A Objective Semantics
- Minimize unmapped operators and ambiguous ownership.
### 0.B Reproducibility Contract
- Replayable given `(mapping_version, operator_manifest_hash, template_hash)`.
### 0.C Numeric Policy
- N/A except deterministic indexing/counting of mappings.
### 0.D Ordering and Tie-Break Policy
- Mapping order by namespace then operator name then version.
### 0.E Parallel, Concurrency, and Reduction Policy
- Parallel codegen allowed with deterministic output merge order.
### 0.F Environment and Dependency Policy
- Determinism level: `BITWISE` for generated file set and stub signatures.
### 0.G Operator Manifest
- `UML_OS.Implementation.ResolveOperatorTargets_v1`
- `UML_OS.Implementation.GenerateStub_v1`
- `UML_OS.Implementation.ValidateGeneratedLayout_v1`
- `UML_OS.Error.Emit_v1`
### 0.H Namespacing and Packaging
- Generated modules preserve EQC namespace segments.
### 0.I Outputs and Metric Schema
- Outputs: `(mapping_table, generated_artifacts)`.
- Metrics: `operators_mapped`, `stubs_generated`, `conflicts`.
- Completion status: `success | failed`.
### 0.J Spec Lifecycle Governance
- Breaking folder/module layout change requires MAJOR bump.
### 0.K Failure and Error Semantics
- Abort on unresolved operator mapping or path conflict.
### 0.L Input/Data Provenance
- Source manifests/templates are hash-addressed.

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
- mapping registry (`operator -> file/module/symbol`).
### I.B Inputs and Hyperparameters
- operator manifests, language target, template set.
### I.C Constraints and Feasible Set
- Valid if every operator resolves to exactly one concrete target.
### I.D Transient Variables
- pending stub list and conflict diagnostics.
### I.E Invariants and Assertions
- unique symbol per mapped operator.

---
## 3) Initialization
1. Load operator manifests.
2. Load template library.
3. Initialize deterministic target registry.

---
## 4) Operator Manifest
- `UML_OS.Implementation.ResolveOperatorTargets_v1`
- `UML_OS.Implementation.GenerateStub_v1`
- `UML_OS.Implementation.ValidateGeneratedLayout_v1`
- `UML_OS.Error.Emit_v1`

---
## 5) Operator Definitions

Template conformance note (III.A): each operator definition in this section is interpreted with the full EQC operator template fields. When a field is not repeated inline, the section-level defaults are: explicit typed signatures, deterministic ordering/tie handling, declared numerical policy inheritance, deterministic failure semantics (0.K), explicit dependencies, and VII.B test-vector coverage.

**Operator:** `UML_OS.Implementation.ResolveOperatorTargets_v1`  
**Category:** IO  
**Signature:** `(operator_manifest, conventions -> mapping_table)`  
**Purity class:** PURE  
**Determinism:** deterministic  
**Definition:** resolves canonical code targets for each operator.

**Operator:** `UML_OS.Implementation.GenerateStub_v1`  
**Category:** IO  
**Signature:** `(mapping_entry, template -> source_file)`  
**Purity class:** IO  
**Determinism:** deterministic  
**Definition:** generates typed stub with signature and TODO markers.

**Operator:** `UML_OS.Implementation.ValidateGeneratedLayout_v1`  
**Category:** IO  
**Signature:** `(generated_artifacts, mapping_table -> report)`  
**Purity class:** PURE  
**Determinism:** deterministic  
**Definition:** validates that all required files/symbols exist and match signatures.

---
## 6) Procedure
```text
1. ResolveOperatorTargets_v1
2. GenerateStub_v1 for each mapping entry
3. ValidateGeneratedLayout_v1
4. Emit mapping table + generation report
```

---
## 7) Trace & Metrics
### Logging rule
Each generated artifact emits deterministic mapping and validation records.
### Trace schema
- `run_header`: mapping_version, template_hash
- `iter`: operator, target_path, status
- `run_end`: generated_count, conflict_count
### Metric schema
- `operators_mapped`, `stubs_generated`, `conflicts`
### Comparability guarantee
Comparable iff manifest, templates, and mapping conventions are identical.

---
## 8) Validation
#### VII.A Lint rules (mandatory)
Passes symbol completeness, deterministic ordering, manifest completeness.
#### VII.B Operator test vectors (mandatory)
Includes manifest->mapping and mapping->stub vectors.
#### VII.C Golden traces (mandatory)
Golden generated-file inventories and signatures.

---
## 9) Refactor & Equivalence
#### VIII.A Equivalence levels
- E0 for mapping table and generated signatures.
#### VIII.B Allowed refactor categories
- template engine implementation changes preserving generated outputs.
#### VIII.C Equivalence test procedure (mandatory)
Exact compare of mapping and generated signatures.

---
## 10) Checkpoint/Restore
### Checkpoint contents
- mapping registry and generation cursor.
### Serialization
- deterministic JSON/CBOR.
### Restore semantics
- resumed generation yields identical artifact set.

