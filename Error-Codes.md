# UML_OS Error Code Contract
**EQC Compliance:** Merged single-file EQC v1.1 Option A.

**Algorithm:** `UML_OS.Error.CodeRegistry_v1`  
**Purpose (1 sentence):** Define a deterministic unified error taxonomy and emission contract across all UML_OS operators.  
**Spec Version:** `UML_OS.Error.CodeRegistry_v1` | 2026-02-18 | Authors: Olejar Damir  
**Domain / Problem Class:** Error semantics and interoperability.

---
## 1) Header & Global Semantics
### 0.0 Identity
- **Algorithm:** `UML_OS.Error.CodeRegistry_v1`
- **Purpose (1 sentence):** Unified deterministic error registry.
- **Spec Version:** `UML_OS.Error.CodeRegistry_v1` | 2026-02-18 | Authors: Olejar Damir
- **Domain / Problem Class:** Error taxonomy governance.
### 0.A Objective Semantics
- Minimize ambiguous or unclassified failures.
### 0.B Reproducibility Contract
- Replayable given `(error_registry_version, failure_context_hash)`.
### 0.C Numeric Policy
- Error fields are typed; numeric values deterministic and explicit.
### 0.D Ordering and Tie-Break Policy
- Error code ordering by lexical code id.
### 0.E Parallel, Concurrency, and Reduction Policy
- Concurrent failures reduced deterministically by first `(t, operator, code)`.
### 0.F Environment and Dependency Policy
- Determinism level: `BITWISE` for emitted error records.
### 0.G Operator Manifest
- `UML_OS.Error.Emit_v1`
- `UML_OS.Error.ValidateRecord_v1`
- `UML_OS.Error.SerializeRecord_v1`
### 0.H Namespacing and Packaging
- Error codes are global and unique.
### 0.I Outputs and Metric Schema
- Outputs: `(error_record, serialized_error)`.
- Metrics: `error_code_frequency`, `first_failure_t`.
- Completion status: `failed` (or `success` for validation-only runs).
### 0.J Spec Lifecycle Governance
- New code additions are MINOR; semantic changes/removals are MAJOR.
### 0.K Failure and Error Semantics
- Abort-only or structured depending on caller policy; record always deterministic.
### 0.L Input/Data Provenance
- Error records include replay token and operator provenance.

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
- error code registry.
### I.B Inputs and Hyperparameters
- failure context and policy.
### I.C Constraints and Feasible Set
- registry uniqueness and schema validity constraints.
### I.D Transient Variables
- formatted error record.
### I.E Invariants and Assertions
- every emitted code exists in registry.

### II.F Error Registry (Authoritative)
| code_id | numeric_code | category | severity | retryable | deterministic_fields_required | message_template | remediation | version_introduced |
|---|---:|---|---|---|---|---|---|---|
| `CONTRACT_VIOLATION` | 1001 | kernel | critical | false | `t,failure_operator,replay_token` | `Contract violation in {failure_operator}` | Validate manifest/operator contracts | v1 |
| `BATCH_SIZE_INCONSISTENT` | 2001 | data | error | false | `t,dataset_key,replay_token` | `global_batch_size % world_size != 0` | Fix manifest batch/world_size | v1 |
| `PRIVACY_BUDGET_EXCEEDED` | 3001 | dp | critical | false | `t,failure_operator,cumulative_epsilon,target_epsilon` | `DP budget exceeded` | Increase noise/reduce steps | v1 |
| `ALIGNMENT_VIOLATION` | 4001 | tmmu | critical | false | `t,arena,logical_slot` | `Memory alignment violation` | Increase alignment or remap slot | v1 |
| `BACKEND_CONTRACT_VIOLATION` | 5001 | backend | critical | false | `t,driver_hash,operator_id` | `Backend failed determinism contract` | Use certified driver build | v1 |

Numeric range reservation:
- 1000-1999 kernel/contract
- 2000-2999 data/config
- 3000-3999 differential privacy
- 4000-4999 tmmu/memory/checkpoint
- 5000-5999 backend/model execution
- 6000-6999 security/compliance

Additional referenced codes:
- `INVALID_IR` (5002), `CYCLE_DETECTED` (5003), `SHAPE_MISMATCH` (5004), `PRIMITIVE_UNSUPPORTED` (5005), `TMMU_ALLOCATION_FAILURE` (4002), `API_SIGNATURE_MISMATCH` (2002), `INVALID_DP_CONFIG` (3002), `ACCOUNTANT_OVERFLOW` (3003), `DISTRIBUTED_COMMUNICATION_FAILURE` (5006), `ATTESTATION_FAILURE` (6001), `ALIGNMENT_VIOLATION` (4001).

Lint invariant:
- Build/test must fail if any referenced `code_id` in any spec is absent from this registry.

---
## 3) Initialization
1. Load registry.
2. Validate uniqueness and payload schemas.
3. Initialize counters.

---
## 4) Operator Manifest
- `UML_OS.Error.Emit_v1`
- `UML_OS.Error.ValidateRecord_v1`
- `UML_OS.Error.SerializeRecord_v1`

---
## 5) Operator Definitions

Template conformance note (III.A): each operator definition in this section is interpreted with the full EQC operator template fields. When a field is not repeated inline, the section-level defaults are: explicit typed signatures, deterministic ordering/tie handling, declared numerical policy inheritance, deterministic failure semantics (0.K), explicit dependencies, and VII.B test-vector coverage.

**Operator:** `UML_OS.Error.Emit_v1`  
**Category:** Error  
**Signature:** `(code, context -> error_record)`  
**Purity class:** IO  
**Determinism:** deterministic  
**Definition:** emits standardized failure record.

**Operator:** `UML_OS.Error.ValidateRecord_v1`  
**Category:** Error  
**Signature:** `(error_record -> ok)`  
**Purity class:** PURE  
**Determinism:** deterministic  
**Definition:** checks required fields and payload schema.

**Operator:** `UML_OS.Error.SerializeRecord_v1`  
**Category:** Error  
**Signature:** `(error_record -> bytes)`  
**Purity class:** PURE  
**Determinism:** deterministic  
**Definition:** canonical encoding for trace/certificate inclusion.

---
## 6) Procedure
```text
1. Emit_v1(code, context)
2. ValidateRecord_v1
3. SerializeRecord_v1
4. Return record + bytes
```

---
## 7) Trace & Metrics
### Logging rule
All failures must log one canonical record.
### Trace schema
- `run_header`: registry_version
- `iter`: error_code, operator, t, replay_token
- `run_end`: failure summary
### Metric schema
- `error_code_frequency`, `first_failure_t`
### Comparability guarantee
Comparable iff registry and serialization rules are identical.

---
## 8) Validation
#### VII.A Lint rules (mandatory)
Ensures code uniqueness, schema completeness, deterministic serialization.
#### VII.B Operator test vectors (mandatory)
Known contexts map to exact error records.
#### VII.C Golden traces (mandatory)
Golden serialized error bytes for canonical contexts.

---
## 9) Refactor & Equivalence
#### VIII.A Equivalence levels
- E0 for emitted record and serialization.
#### VIII.B Allowed refactor categories
- internal formatting optimizations preserving outputs.
#### VIII.C Equivalence test procedure (mandatory)
Exact record and byte-level comparison.

---
## 10) Checkpoint/Restore
### Checkpoint contents
- registry snapshot and counters.
### Serialization
- deterministic JSON/CBOR.
### Restore semantics
- identical future error records for same contexts.
