# UML_OS API Interface Contract
**EQC Compliance:** Merged single-file EQC v1.1 Option A.

**Algorithm:** `UML_OS.Implementation.APIInterfaceContract_v1`  
**Purpose (1 sentence):** Define deterministic, typed, versioned callable interfaces for kernel and core operators.  
**Spec Version:** `UML_OS.Implementation.APIInterfaceContract_v1` | 2026-02-18 | Authors: Olejar Damir  
**Domain / Problem Class:** API contract specification and interoperability.

---

## 1) Header & Global Semantics

### 0.0 Identity
- **Algorithm:** `UML_OS.Implementation.APIInterfaceContract_v1`
- **Purpose (1 sentence):** Deterministic API interface contract.
- **Spec Version:** `UML_OS.Implementation.APIInterfaceContract_v1` | 2026-02-18 | Authors: Olejar Damir
- **Domain / Problem Class:** Typed API contracts.

### 0.A Objective Semantics
- Optimization sense: `MINIMIZE`
- Objective type: `Scalar`
- Primary comparison rule: deterministic total preorder over declared primary metric tuple with `EPS_EQ` tie handling.
- Invalid objective policy: `NaN/Inf` ranked as worst-case and handled deterministically per 0.K.
- Not an optimization algorithm.
- Primary comparison rule: exact schema and signature equality.
- Invalid objective policy: schema mismatch is failure.

### 0.B Reproducibility Contract
- Seed space: `seed ∈ {0..2^64-1}` where applicable.
- PRNG family: inherited from calling operator.
- Randomness locality: no sampling in interface contract checks.
- Replay guarantee: replayable given `(spec_version, interface_hash)`.
- Replay token: `api_replay_t = SHA-256(CBOR(["api_interfaces_v1", spec_version, interface_hash]))`.

### 0.C Numeric Policy
- Numeric fields specify explicit scalar kinds (`uint64`, `float64`, etc.).
- Rounding mode / fast-math: N/A for contract validation.
- NaN/Inf policy: invalid unless explicitly allowed by API field definition.
- Approx-equality: exact type match; no implicit coercion.

### 0.D Ordering and Tie-Break Policy
- Parameter order is canonical and positional.
- Tie-break: lexical ordering on field names for deterministic serialization.

### 0.E Parallel, Concurrency, and Reduction Policy
- Contract validation is deterministic and single-pass.
- No async behavior.

### 0.F Environment and Dependency Policy
- Reference runtime: language-agnostic schema validator.
- Dependencies: deterministic JSON/CBOR canonicalization.
- Determinism level: `BITWISE` for signature serialization and hashes.

### 0.G Operator Manifest
- `UML_OS.Implementation.ValidateAPISignature_v1`
- `UML_OS.Implementation.ValidateIOShape_v1`
- `UML_OS.Implementation.ComputeInterfaceHash_v1`
- `UML_OS.Error.Emit_v1`

### 0.H Namespacing and Packaging
- Fully-qualified names required.
- Sidecar mapping (`operator -> module/function`) required.

### 0.I Outputs and Metric Schema
- Declared outputs: `(validation_report, interface_hash)`.
- Metrics: `validated_operators`, `schema_mismatches`, `hash`.
- Completion status: `success | failed`.

### 0.J Spec Lifecycle Governance
- Breaking signature change requires MAJOR bump.
- Backward-compatible field additions require MINOR bump.
- Equivalence target: E0.

### 0.K Failure and Error Semantics
- Abort-only with deterministic error record.
- Codes: `API_SIGNATURE_MISMATCH`, `API_SHAPE_MISMATCH`, `API_TYPE_MISMATCH`.

### 0.L Input/Data Provenance
- Input schemas must be versioned and hash-addressable.

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
- `interface_registry: map<operator, signature>`.

### I.B Inputs and Hyperparameters
- `declared_interfaces`, `implemented_interfaces`.

### I.C Constraints and Feasible Set
- Unconstrained; validity determined by exact schema compatibility.

### I.D Transient Variables
- `diffs`, `validation_report`, `interface_hash`.

### I.E Invariants and Assertions
- Registry entries are unique and versioned.

### II.F Syscall Interface Registry (Concrete, Authoritative)
| surface | name | version | method | request_schema_hash | response_schema_hash | idempotent | side_effects | allowed_error_codes | signature_digest |
|---|---|---|---|---|---|---|---|---|---|
| `SYSCALL` | `UML_OS.Data.NextBatch_v2` | v2 | syscall | `sha256:b3c93fdc0519e72c27a3203174fbb5ac8b96c760f1bdc739874ea6870ae8a500` | `sha256:a74f659e6edfc9a663a78d148981b27ee46f6685bc6786ed1ca7e5e7763b4fa3` | true | `["NONE"]` | `BATCH_SIZE_INCONSISTENT,INVALID_DATASET_KEY,CARDINALITY_MISMATCH,GLOBAL_POSITION_EXCEEDS_CARDINALITY,INVALID_STAGE_TYPE` | `sha256:67069ace699a580ed23a01168b46d0242002d82f8d429266b195d3a459eb972f` |
| `SYSCALL` | `UML_OS.Model.Forward_v2` | v2 | syscall | `sha256:82a1c1413fc3fd8176c351bb828315354fb3434760cdb4a47f30408f92f26fa7` | `sha256:d69a39c6e458a4803aff256e848784fddc34f6db4c5a963b5959fbc264076c09` | false | `["ADVANCES_RNG"]` | `CONTRACT_VIOLATION,PRIMITIVE_UNSUPPORTED` | `sha256:17d85435fe2e601fe522b614938ea7853b9c36be14c8feb84f4e70e1e253bc74` |
| `SYSCALL` | `UML_OS.Model.ModelIR_Executor_v1` | v1 | syscall | `sha256:a50166213aefcd3a51e2660cd50d4dca444353e4d3642c1cacc7300c158ef362` | `sha256:a9788d4553cee1d35d7f79c65d21cdf28d143a066152462568fa5e5d3ad36024` | false | `["ALLOCATES_MEMORY"]` | `INVALID_IR,PRIMITIVE_UNSUPPORTED,CYCLE_DETECTED,SHAPE_MISMATCH,TMMU_ALLOCATION_FAILURE,CONTRACT_VIOLATION` | `sha256:ce1ec3e5cead31a92f46e79847332d3db0fdd824f2f3b6608987c77450a6de70` |
| `SYSCALL` | `UML_OS.DifferentialPrivacy.Apply_v3` | v3 | syscall | `sha256:c788135091bca6dda0dfa6be1903fe534aba3ce8aba22802338f4557c2f62b2c` | `sha256:e4511aa77256d2b3984b25381f8a14e780a0f701bfeb5db134f06143607cb7d6` | false | `["ADVANCES_RNG","MUTATES_ACCOUNTANT"]` | `PRIVACY_BUDGET_EXCEEDED,INVALID_DP_CONFIG,INVALID_GRADIENT,NAN_IN_SIGMA,ACCOUNTANT_OVERFLOW,ACCOUNTANT_DIVERGENCE,RNG_CONSUMPTION_VIOLATION` | `sha256:df574eb8b39a83a8107bce17dbcddbd3c1751aa51ccd6f9dcdd0e95ddab6b52f` |
| `SYSCALL` | `UML_OS.TMMU.PrepareMemory_v2` | v2 | syscall | `sha256:1868515eb2e8b04486ca2a2a0aec0cad27e33a85e1c66369dbdb6dd72f3aa227` | `sha256:5602da41a9eb5e0d7ab21000bb82018688523f01987e498e186ba6854991df1e` | false | `["ALLOCATES_MEMORY"]` | `INVALID_IR_SHAPES,LIVENESS_CYCLE,ADDRESS_COLLISION,ALLOCATION_OVERFLOW,ARENA_TOO_SMALL,ALIGNMENT_VIOLATION` | `sha256:87ad2acf49cc0081824d67a2b0838d03d3bd2f3f2d3ae19a9b07af50bc264b09` |
| `SYSCALL` | `UML_OS.Backend.LoadDriver_v1` | v1 | syscall | `sha256:b9d299c7e1cd2bd04e499b1458b2bb935f47de74daf18652356fc36f117f76b1` | `sha256:c2a0b76a20abbe89e02cd7626c77e300d0f0373d6b47b9e437eec408727c9768` | false | `["PERFORMS_IO","NETWORK_COMM"]` | `BACKEND_CONTRACT_VIOLATION` | `sha256:708fd111f6fc0a8f85853a4218ff9eba82ffc3da285266b15f6714a450728056` |
| `SYSCALL` | `UML_OS.IO.SaveCheckpoint_v1` | v1 | syscall | `sha256:47d294c74846623fdf009597597bfc131190727f15959b846520ccc3162494df` | `sha256:ef98d3bdf59fafb396766c343ffd67b730175f43c34d7d7b64903993132ff430` | false | `["PERFORMS_IO"]` | `CONTRACT_VIOLATION` | `sha256:7500cd45013f340439c196a8119f1da650f325f9b9fb22567574df80a78c5d77` |
| `SYSCALL` | `UML_OS.Checkpoint.Restore_v1` | v1 | syscall | `sha256:87e869485275faea2aecf8a8cf8398ecb7452cb0c6df60327b4a1671c8948caf` | `sha256:1ac5f1b5313af3eeba05b0aa2e6df19358d7ee51f957fe07dcd29f4faca2c28a` | false | `["PERFORMS_IO","MUTATES_MODEL_STATE"]` | `CONTRACT_VIOLATION` | `sha256:2ad8fce88d166dfbfd042dfd9e91e1e282e4f549cea088b141872d53a863ef89` |

### II.G Service API Registry (Concrete, Authoritative)
| surface | name | version | method | request_schema_hash | response_schema_hash | idempotent | side_effects | allowed_error_codes | signature_digest |
|---|---|---|---|---|---|---|---|---|---|
| `SERVICE` | `UML_OS.Tracking.RunCreate_v1` | v1 | service | `sha256:79f63d036b91c33bbd5a0a64468f93107f79b755e73810824d3877aeb6561fc1` | `sha256:658a3e66ec1cf259a71244bc535d7d4efa5fc648ca4aedf8686e50e2bfd29dad` | false | `["PERFORMS_IO"]` | `CONTRACT_VIOLATION` | `sha256:f9912032a083a24960b3fce71bef84b6b6669bd4f1455143b793abd46c61d979` |
| `SERVICE` | `UML_OS.Tracking.RunStart_v1` | v1 | service | `sha256:3c9f675dfcb5deb7de64eecff530e2a0d1ad327714e38b22db4b3a40834a319c` | `sha256:663474fa4ef7f6cbf299ef27426b09a36a57a05cde2af9775ccc470f91edf9c1` | false | `["PERFORMS_IO"]` | `CONTRACT_VIOLATION` | `sha256:3bbc23354e81d350087a3eb11f45db4202d35b2c3a0d789917ce250c67d604ad` |
| `SERVICE` | `UML_OS.Tracking.RunEnd_v1` | v1 | service | `sha256:2d7735c3a7d1f21b2966ef34279274fdeb2d5cdedf1295d06d69b46ffe6c44c1` | `sha256:e3fbb827b7df3c88ecbe534511e4a681c8f914b03314f45db615b0265f182767` | false | `["PERFORMS_IO"]` | `CONTRACT_VIOLATION` | `sha256:61cffc6435589391694727d1950e9b897ecb4a9a1678ad318b7cb4863762bd8a` |
| `SERVICE` | `UML_OS.Tracking.MetricLog_v1` | v1 | service | `sha256:e4dfe80e6d2e71cf3281f732fb4ce3bff8c8fb5cce4b339e0ffb0e10fbf2d705` | `sha256:dbeeadfcd9ce45b81acb44aede35acd0caebba6be61a1bf2b0775644c6812fc3` | false | `["PERFORMS_IO"]` | `CONTRACT_VIOLATION` | `sha256:2bfc26d97f932a7f4dc99529872f54dcee07c1f37fa160dc1f09d4bbc0052553` |
| `SERVICE` | `UML_OS.Tracking.ArtifactPut_v1` | v1 | service | `sha256:376c6ac9c8f23bd60de605af173aaedfb29f9a9772a16bc4319d5eaf2ca88212` | `sha256:8d5ec7401a722b52bffd442dc143be279636527005c45b7cde91ce186286f1b5` | false | `["PERFORMS_IO"]` | `CONTRACT_VIOLATION` | `sha256:4c83219b6825bbbb8b64254328e6fa7d64e4eb04065f32e214ba7576fe0c3621` |
| `SERVICE` | `UML_OS.Tracking.ArtifactGet_v1` | v1 | service | `sha256:aaa6f3df2d7f7837909b36fb6ffb8a7cb4e7137fa043c35d6d9ed441cd04400f` | `sha256:d2afbd6a00fe8ad77800be3bd21ece5e4508cccda15c614b80e648adb288d8f1` | true | `["PERFORMS_IO"]` | `CONTRACT_VIOLATION` | `sha256:89c470402948fd7717c7a89074e466ccaa731270b28bd798c8ef4b3905521d83` |
| `SERVICE` | `UML_OS.Tracking.ArtifactList_v1` | v1 | service | `sha256:390eb2cd44de8e5a8702e2e9ee5a9546fa6f3bad93ede910f191d0b5cafa9d99` | `sha256:32a01fe15e446238cd353af5b0fd517352c4584831062670e1a0d77567767a91` | true | `["PERFORMS_IO"]` | `CONTRACT_VIOLATION` | `sha256:a02167e5e2a3f785190069b65127032dd2841544af82da03dd1d237fbdc38f40` |
| `SERVICE` | `UML_OS.Tracking.ArtifactTombstone_v1` | v1 | service | `sha256:34be789a7612797a9bcac210bf5664724e7a1a10b6a1321cd2196b0378accbc5` | `sha256:269fe8e05ec1db5c082f7e3c6b1ef5a37a8e1ae65fd2cc9c9903b1dd3e8de5e1` | false | `["PERFORMS_IO"]` | `CONTRACT_VIOLATION` | `sha256:668e41817d89f2aeb2af4e9394302cb935425450e4595c5db1965ed5d3f9ea22` |
| `SERVICE` | `UML_OS.Registry.VersionCreate_v1` | v1 | service | `sha256:1535b143bf15d47cde6b95c1e8bd9d90018d9e631b8565007c3ff0f4c5eeb221` | `sha256:c422b8f784e0a458336a0d7eb7b5adb32d9608aef2d459359e99142bed3bed43` | false | `["PERFORMS_IO"]` | `CONTRACT_VIOLATION` | `sha256:5690d2ee8d34c3407e33f14f25198d35af170150c663b5290f9f6460003a8f0e` |
| `SERVICE` | `UML_OS.Registry.StageTransition_v1` | v1 | service | `sha256:e634b4adad159203c88a086e8194833a9b3a718f68bad60fdeec0c616f25e770` | `sha256:39ce69213d5b015a69485eed6bd9065065ae8981b55368c65f2148d0a8490a18` | false | `["PERFORMS_IO"]` | `CONTRACT_VIOLATION` | `sha256:df171fad79b74e99a5cf98c98c0dd0d99891c6e28d2b21de21de12e797db46af` |
| `SERVICE` | `UML_OS.Monitor.Register_v1` | v1 | service | `sha256:3812992f06cac5e8845b5707f18487a7abd1c18b797d0d17f0dbef2c5e535988` | `sha256:fc700ecfc6b59d532b0f2090fa9f3f9d5a25365503bad36df2bd7d17ace66605` | false | `["PERFORMS_IO"]` | `CONTRACT_VIOLATION` | `sha256:0a5e9373bfba01ba4bbeddba689074a704d538e7ebe4e072a139cef99bbd4440` |
| `SERVICE` | `UML_OS.Monitor.Emit_v1` | v1 | service | `sha256:063a9d6fbd2cc06ca6230a9dd42e740edec0ea0b76eae794c6695f239b9a35ff` | `sha256:6adacbfc76a20bed4a542e1df0090d662e51fb6e9b08ef1d67734dbc6de6d7f2` | false | `["PERFORMS_IO"]` | `CONTRACT_VIOLATION` | `sha256:eb4d0698028761a1d5f75b66d7a67a758045aa33846d50296990722b30156550` |
| `SERVICE` | `UML_OS.Monitor.DriftCompute_v1` | v1 | service | `sha256:84751ff5c4f6c4508d2eb3bf6b5fb382a43aeef11b15a7d5f10e392a50742d93` | `sha256:9976dd86b5801ea78df696947695ca62e1e9868f02dd36c2a8cdcbc5b793be3a` | true | `["NONE"]` | `CONTRACT_VIOLATION` | `sha256:901881d54845698125611c9d87d11e7fa5419248a4caf8dbb839465dccfe25fb` |
| `SERVICE` | `UML_OS.Certificate.EvidenceValidate_v1` | v1 | service | `sha256:1165b63ee12061a187b8bbbe0f55eb800d09f5c7ec1e7a45d02fc90ee594960a` | `sha256:b803f8990a492ff39515aa099d0d92297488a07501b37a613e43502afa17dc79` | true | `["NONE"]` | `CONTRACT_VIOLATION` | `sha256:9d55661802f55dacd9695031acfeed3745f9a501b7db5606b814ad546116d5b1` |
| `SERVICE` | `UML_OS.Config.ManifestMigrate_v1` | v1 | service | `sha256:12bfcae0d2cf5d76c722cd4f967eb4a250f2316fc5fc2173a96585f6684500e3` | `sha256:d54f71baddda92b26c3bbdad54037f9573a6d16763c437ff2d6250ddb7ac7ba7` | false | `["PERFORMS_IO"]` | `CONTRACT_VIOLATION` | `sha256:29695a8e891b995033fc2508204991bb8cb28067965ebac7bfbe26478b40cc89` |
| `SERVICE` | `UML_OS.Checkpoint.CheckpointMigrate_v1` | v1 | service | `sha256:3be7173771ea6e390239d664e137cc4a54db6fa696587a5bc3f514bdc7e35a57` | `sha256:70c2eaa4515e6662e32aee16a46c9055319fa6f61cb01ea18a7cb9d2b48dfe6f` | false | `["PERFORMS_IO"]` | `CONTRACT_VIOLATION` | `sha256:ea0f1f735948058cd9893fe6f9c661ca578097c83c93780c624c4245dc576c59` |
| `SERVICE` | `UML_OS.Trace.TraceMigrate_v1` | v1 | service | `sha256:a79b56d5d8b5629e62bfab67f08432459ffef04ae4beb121f3f098eee5a4365f` | `sha256:53a6622c6b83f35487826cf96e27b7b6cc9afc888d8afd4e76d03250de206e86` | false | `["PERFORMS_IO"]` | `CONTRACT_VIOLATION` | `sha256:fe3709bad090dcd8f5f190649a7694bd26ca059e9a47b3eaf784d0268bf442ee` |
| `SERVICE` | `UML_OS.Import.LegacyFramework_v1` | v1 | service | `sha256:64442d19eded7c78bc5b84301b0be39f5c6f3aee6dc35efe0db3cf5545a76d7c` | `sha256:8c834fc6ef6ce6a077d23903f51fc0ccab895f3b5762daf3fc03fd46fc566be5` | false | `["PERFORMS_IO"]` | `CONTRACT_VIOLATION` | `sha256:20c8da5d2c5565476edc1c59ba209b14f19e0f4f3e71be86f4854f28abea0839` |

### II.H Schema/Signature Digest Rules (Normative)
- `SchemaDigest_v1 = SHA-256(CBOR_CANONICAL(schema_ast_normalized))`.
- `SignatureDigest_v1 = SHA-256(CBOR_CANONICAL([operator_id, version, request_schema_digest, response_schema_digest, sorted(side_effects), sorted(allowed_error_codes)]))`.
- Canonical schema sources must be stored under `schemas/` and used as the single source for digest generation in build/codegen.

---

## 3) Initialization

1. Load declared interfaces.
2. Canonicalize schemas.
3. Build interface registry.

---

## 4) Operator Manifest

- `UML_OS.Implementation.ValidateAPISignature_v1`
- `UML_OS.Implementation.ValidateIOShape_v1`
- `UML_OS.Implementation.ComputeInterfaceHash_v1`
- `UML_OS.Error.Emit_v1`

---

## 5) Operator Definitions

External operator reference: `UML_OS.Error.Emit_v1` is defined normatively in `Error-Codes.md` and imported by reference.

**Operator:** `UML_OS.Implementation.ValidateAPISignature_v1`  
**Category:** IO  
**Signature:** `(declared, implemented -> report)`  
**Purity class:** PURE  
**Determinism:** deterministic  
**Definition:** exact field/type/order validation.  
**Preconditions / Postconditions:** inputs canonicalized.  
**Edge cases:** missing optional fields.  
**Numerical considerations:** N/A.  
**Ordering/tie handling:** lexical field order.  
**Complexity note:** O(total_fields).  
**Failure behavior:** emit deterministic mismatch record.  
**Dependencies:** canonical schema encoder.  
**Test vectors:** matching/mismatching signatures.

**Operator:** `UML_OS.Implementation.ValidateIOShape_v1`  
**Category:** IO  
**Signature:** `(signature, sample_payload -> ok)`  
**Purity class:** PURE  
**Determinism:** deterministic  
**Definition:** validates payload type/shape contracts.  
**Preconditions / Postconditions:** signature exists.  
**Edge cases:** optional and nullable fields.  
**Numerical considerations:** N/A.  
**Ordering/tie handling:** deterministic key traversal.  
**Complexity note:** O(payload_size).  
**Failure behavior:** `API_SHAPE_MISMATCH`.  
**Dependencies:** schema validator.  
**Test vectors:** representative payload set.

**Operator:** `UML_OS.Implementation.ComputeInterfaceHash_v1`  
**Category:** IO  
**Signature:** `(registry -> interface_hash)`  
**Purity class:** PURE  
**Determinism:** deterministic  
**Definition:** canonical hash over ordered signatures.  
**Preconditions / Postconditions:** unique registry keys.  
**Edge cases:** empty registry.  
**Numerical considerations:** N/A.  
**Ordering/tie handling:** sorted operator names.  
**Complexity note:** O(registry_size).  
**Failure behavior:** abort on hash serialization failure.  
**Dependencies:** canonical serializer + hash function.  
**Test vectors:** fixed registry hash snapshots.

---

## 6) Procedure

```text
1. ValidateAPISignature_v1(declared, implemented)
2. ValidateIOShape_v1(...) on representative payloads
3. ComputeInterfaceHash_v1(registry)
4. Return report + hash
```

---

## 7) Trace & Metrics

### Logging rule
Each validation run emits deterministic mismatch and summary records.

### Trace schema
- `run_header`: spec_version, interface_count
- `iter`: operator, check_type, result
- `run_end`: status, interface_hash

### Metric schema
- `validated_operators`, `schema_mismatches`, `hash`

### Comparability guarantee
Comparable iff identical schema keys, typing, and hash definition.

---

## 8) Validation

#### VII.A Lint rules (mandatory)
Passes symbol completeness, no hidden globals, deterministic ordering, trace compliance.

#### VII.B Operator test vectors (mandatory)
Includes exact signature and payload conformance vectors.

#### VII.C Golden traces (mandatory)
Golden hash snapshots for known interface sets.

---

## 9) Refactor & Equivalence

#### VIII.A Equivalence levels
- E0 required.

#### VIII.B Allowed refactor categories
- Validator implementation refactor preserving outputs and hashes.

#### VIII.C Equivalence test procedure (mandatory)
Compare full report and interface hash.

---

## 10) Checkpoint/Restore

### Checkpoint contents
- interface registry snapshot + hash.

### Serialization
- deterministic JSON/CBOR.

### Restore semantics
- restored registry yields identical validation outputs.
