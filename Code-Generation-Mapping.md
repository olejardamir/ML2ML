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
- Optimization sense: `MINIMIZE`
- Objective type: `Scalar`
- Primary comparison rule: deterministic total preorder over declared primary metric tuple with `EPS_EQ` tie handling.
- Invalid objective policy: `NaN/Inf` ranked as worst-case and handled deterministically per 0.K.
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

### II.F Mapping Table (Concrete)
| operator | module_path | symbol_name | stub_template | ownership | side_effects | signature_digest |
|---|---|---|---|---|---|---|
| `UML_OS.Data.NextBatch_v2` | `src/data/next_batch.py` | `next_batch_v2` | `py_operator_stub_v1` | data team | `["NONE"]` | `sha256:67069ace699a580ed23a01168b46d0242002d82f8d429266b195d3a459eb972f` |
| `UML_OS.Model.ModelIR_Executor_v1` | `src/model/modelir_executor.py` | `modelir_executor_v1` | `py_operator_stub_v1` | model team | `["ALLOCATES_MEMORY"]` | `sha256:ce1ec3e5cead31a92f46e79847332d3db0fdd824f2f3b6608987c77450a6de70` |
| `UML_OS.DifferentialPrivacy.Apply_v3` | `src/dp/apply.py` | `dp_apply_v3` | `py_operator_stub_v1` | privacy team | `["ADVANCES_RNG","MUTATES_ACCOUNTANT"]` | `sha256:df574eb8b39a83a8107bce17dbcddbd3c1751aa51ccd6f9dcdd0e95ddab6b52f` |
| `UML_OS.TMMU.PrepareMemory_v2` | `src/tmmu/prepare_memory.py` | `prepare_memory_v2` | `py_operator_stub_v1` | runtime team | `["ALLOCATES_MEMORY"]` | `sha256:87ad2acf49cc0081824d67a2b0838d03d3bd2f3f2d3ae19a9b07af50bc264b09` |
| `UML_OS.Trace.ComputeTraceHash_v1` | `src/trace/compute_trace_hash.py` | `compute_trace_hash_v1` | `py_operator_stub_v1` | trace team | `["NONE"]` | `sha256:688952452590da608369e8ce224f014a053ccf9ec0b0f1d58766a6433d62c6bb` |
| `UML_OS.IO.SaveCheckpoint_v1` | `src/io/save_checkpoint.py` | `save_checkpoint_v1` | `py_operator_stub_v1` | runtime team | `["PERFORMS_IO"]` | `sha256:7500cd45013f340439c196a8119f1da650f325f9b9fb22567574df80a78c5d77` |
| `UML_OS.Certificate.EvidenceValidate_v1` | `src/cert/evidence_validate.py` | `evidence_validate_v1` | `py_operator_stub_v1` | security team | `["NONE"]` | `sha256:9d55661802f55dacd9695031acfeed3745f9a501b7db5606b814ad546116d5b1` |
| `UML_OS.Tracking.MetricLog_v1` | `src/tracking/metric_log.py` | `metric_log_v1` | `py_operator_stub_v1` | platform team | `["PERFORMS_IO"]` | `sha256:2bfc26d97f932a7f4dc99529872f54dcee07c1f37fa160dc1f09d4bbc0052553` |
| `UML_OS.Backend.LoadDriver_v1` | `src/backend/load_driver.py` | `load_driver_v1` | `py_operator_stub_v1` | backend team | `["PERFORMS_IO","NETWORK_COMM"]` | `sha256:708fd111f6fc0a8f85853a4218ff9eba82ffc3da285266b15f6714a450728056` |
| `UML_OS.Checkpoint.CheckpointMigrate_v1` | `src/checkpoint/migrate_checkpoint.py` | `checkpoint_migrate_v1` | `py_operator_stub_v1` | runtime team | `["PERFORMS_IO"]` | `sha256:ea0f1f735948058cd9893fe6f9c661ca578097c83c93780c624c4245dc576c59` |
| `UML_OS.Checkpoint.Restore_v1` | `src/checkpoint/restore.py` | `checkpoint_restore_v1` | `py_operator_stub_v1` | runtime team | `["PERFORMS_IO","MUTATES_MODEL_STATE"]` | `sha256:2ad8fce88d166dfbfd042dfd9e91e1e282e4f549cea088b141872d53a863ef89` |
| `UML_OS.Config.ManifestMigrate_v1` | `src/config/migrate_manifest.py` | `manifest_migrate_v1` | `py_operator_stub_v1` | platform team | `["PERFORMS_IO"]` | `sha256:29695a8e891b995033fc2508204991bb8cb28067965ebac7bfbe26478b40cc89` |
| `UML_OS.Model.Forward_v2` | `src/model/forward.py` | `forward_v2` | `py_operator_stub_v1` | model team | `["ADVANCES_RNG"]` | `sha256:17d85435fe2e601fe522b614938ea7853b9c36be14c8feb84f4e70e1e253bc74` |
| `UML_OS.Monitor.DriftCompute_v1` | `src/monitor/drift_compute.py` | `drift_compute_v1` | `py_operator_stub_v1` | platform team | `["NONE"]` | `sha256:901881d54845698125611c9d87d11e7fa5419248a4caf8dbb839465dccfe25fb` |
| `UML_OS.Monitor.Emit_v1` | `src/monitor/emit.py` | `monitor_emit_v1` | `py_operator_stub_v1` | platform team | `["PERFORMS_IO"]` | `sha256:eb4d0698028761a1d5f75b66d7a67a758045aa33846d50296990722b30156550` |
| `UML_OS.Monitor.Register_v1` | `src/monitor/register.py` | `monitor_register_v1` | `py_operator_stub_v1` | platform team | `["PERFORMS_IO"]` | `sha256:0a5e9373bfba01ba4bbeddba689074a704d538e7ebe4e072a139cef99bbd4440` |
| `UML_OS.Registry.StageTransition_v1` | `src/registry/stage_transition.py` | `registry_stage_transition_v1` | `py_operator_stub_v1` | governance team | `["PERFORMS_IO"]` | `sha256:df171fad79b74e99a5cf98c98c0dd0d99891c6e28d2b21de21de12e797db46af` |
| `UML_OS.Registry.VersionCreate_v1` | `src/registry/version_create.py` | `registry_version_create_v1` | `py_operator_stub_v1` | governance team | `["PERFORMS_IO"]` | `sha256:5690d2ee8d34c3407e33f14f25198d35af170150c663b5290f9f6460003a8f0e` |
| `UML_OS.Trace.TraceMigrate_v1` | `src/trace/migrate_trace.py` | `trace_migrate_v1` | `py_operator_stub_v1` | trace team | `["PERFORMS_IO"]` | `sha256:fe3709bad090dcd8f5f190649a7694bd26ca059e9a47b3eaf784d0268bf442ee` |
| `UML_OS.Import.LegacyFramework_v1` | `src/import/legacy_framework.py` | `legacy_framework_import_v1` | `py_operator_stub_v1` | platform team | `["PERFORMS_IO"]` | `sha256:20c8da5d2c5565476edc1c59ba209b14f19e0f4f3e71be86f4854f28abea0839` |
| `UML_OS.Tracking.ArtifactTombstone_v1` | `src/tracking/artifact_tombstone.py` | `artifact_tombstone_v1` | `py_operator_stub_v1` | platform team | `["PERFORMS_IO"]` | `sha256:668e41817d89f2aeb2af4e9394302cb935425450e4595c5db1965ed5d3f9ea22` |
| `UML_OS.Tracking.ArtifactGet_v1` | `src/tracking/artifact_get.py` | `artifact_get_v1` | `py_operator_stub_v1` | platform team | `["PERFORMS_IO"]` | `sha256:89c470402948fd7717c7a89074e466ccaa731270b28bd798c8ef4b3905521d83` |
| `UML_OS.Tracking.ArtifactList_v1` | `src/tracking/artifact_list.py` | `artifact_list_v1` | `py_operator_stub_v1` | platform team | `["PERFORMS_IO"]` | `sha256:a02167e5e2a3f785190069b65127032dd2841544af82da03dd1d237fbdc38f40` |
| `UML_OS.Tracking.ArtifactPut_v1` | `src/tracking/artifact_put.py` | `artifact_put_v1` | `py_operator_stub_v1` | platform team | `["PERFORMS_IO"]` | `sha256:4c83219b6825bbbb8b64254328e6fa7d64e4eb04065f32e214ba7576fe0c3621` |
| `UML_OS.Tracking.RunCreate_v1` | `src/tracking/run_create.py` | `run_create_v1` | `py_operator_stub_v1` | platform team | `["PERFORMS_IO"]` | `sha256:f9912032a083a24960b3fce71bef84b6b6669bd4f1455143b793abd46c61d979` |
| `UML_OS.Tracking.RunEnd_v1` | `src/tracking/run_end.py` | `run_end_v1` | `py_operator_stub_v1` | platform team | `["PERFORMS_IO"]` | `sha256:61cffc6435589391694727d1950e9b897ecb4a9a1678ad318b7cb4863762bd8a` |
| `UML_OS.Tracking.RunStart_v1` | `src/tracking/run_start.py` | `run_start_v1` | `py_operator_stub_v1` | platform team | `["PERFORMS_IO"]` | `sha256:3bbc23354e81d350087a3eb11f45db4202d35b2c3a0d789917ce250c67d604ad` |

Signature lock invariant:
- For each operator `op`, `signature_digest` must match `API-Interfaces.md` and (for backend-exposed ops/primitives) `Backend-Adapter-Guide.md`.
- Client surface split (normative):
  - `syscalls/*` generated for `surface=SYSCALL` interfaces (no network transport).
  - `services/*` generated for `surface=SERVICE` interfaces (network/auth/retry/idempotency policy applied).
- Digest generation invariant:
  - request/response schema digests and signature digests are derived from canonical schema AST files (`schemas/*`) using `SchemaDigest_v1` and `SignatureDigest_v1` from `API-Interfaces.md`; placeholders are forbidden in generated artifacts.

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

External operator reference: `UML_OS.Error.Emit_v1` is defined normatively in `Error-Codes.md` and imported by reference.

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
**Purity class:** IO  
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
