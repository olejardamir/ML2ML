# Universal Machine Learning Operating System (UML_OS) v3.20-OS
**EQC Compliance:** This specification follows the merged single-file format of EquationCode (EQC) v1.1 (Option A) with the required 10 top-level sections and all mandatory invariants (global semantics first, control-flow-only procedure, versioned operators, purity/RNG contracts, total state updates, trace schema, equivalence levels, lint rules, checkpoint replay guarantees).

**Algorithm:** Deterministic training OS kernel with operator contracts, namespace isolation, and hardware attestation.  
**Purpose (1 sentence):** Execute declarative machine learning training, evaluation, inference, and confidential operations under contract-enforced determinism, namespace isolation, hardware-rooted attestation, and verifiable provenance.  
**Spec Version:** UML_OS-v3.20-OS | 2026-02-17 | Authors: Olejar Damir  
**Domain / Problem Class:** Reproducible neural-network training, evaluation, inference, and confidential lifecycle management.

---

## 1) Header & Global Semantics

#### 0.0 Identity
- **Algorithm:** Deterministic training OS kernel with operator contracts, namespace isolation, and hardware attestation
- **Purpose (1 sentence):** Execute declarative machine learning training, evaluation, inference, and confidential operations under contract-enforced determinism, namespace isolation, hardware-rooted attestation, and verifiable provenance.
- **Spec Version:** UML_OS-v3.20-OS | 2026-02-17 | Authors: Olejar Damir
- **Domain / Problem Class:** Reproducible neural-network training, evaluation, inference, and confidential lifecycle management.

### 0.A Objective Semantics
- Optimization sense: `MINIMIZE`
- Objective type: `Scalar`
- Primary comparison rule: `a ≼ b ⇔ a ≤ b + EPS_EQ`
- `EPS_EQ = 1e-10` (float64)
- Invalid objective policy: NaN/±Inf ranked as `+Inf`; mark `INVALID_OBJECTIVE`; do not apply update; emit deterministic failure record; abort (0.K).

### 0.B Reproducibility Contract
- Default reproducibility class: `R1 (statistical)`
- `R0` only for reference single-process CPU golden traces
- PRNG family: Philox4x32-10
- Single master stream with fixed sub-stream offsets: `init`, `cluster`, `misc`
- Replay token: `replay_token = SHA-256(spec_version || policy_hash || env_manifest_hash || seed)`

### 0.C Numeric Policy
- Core arithmetic for loss/metric/termination/fingerprint: IEEE-754 binary64
- Parameters/intermediates/optimizer state: manifest `compute_dtype` (`float32` default)
- Critical reductions and fingerprints: binary64, deterministic ascending-index order
- Rounding mode: round-to-nearest ties-to-even
- Fast-math: forbidden
- Constants: `EPS_EQ = 1e-10`, `EPS_DENOM = 1e-12`, `EPS_PROB = 1e-15`
- Clamps: `exp` argument `[-80, 80]`; denominator `max(den, EPS_DENOM)`; probabilities `[EPS_PROB, 1]` then renormalize

### 0.D Ordering and Tie-Break Policy
- Index base: `0-based`
- Stable sort required
- Ties: lowest index wins
- Fixed action order: `["optimize", "eval", "infer", "switch"]`

### 0.E Parallel, Concurrency, and Reduction Policy
- Parallel reductions: fixed 256-element chunks in ascending global index
- Rank aggregation: ascending rank order
- `world_size > 1` requires deterministic collectives and fixed ordering

### 0.F Environment and Dependency Policy
- Pinned core runtime: Python 3.12, NumPy 2.1. Compute backend selected by manifest `backend`; each backend driver (loaded via `UML_OS.Backend.LoadDriver_v1`) must implement: deterministic forward/backward, collectives (all-reduce, broadcast), RNG forwarding, and exact operator contracts. Driver verification mandatory in `Contract.Validate_v1`.

### 0.G Operator Manifest
Active operators (exact list):
- `UML_OS.OS.Bootstrap_v1`
- `UML_OS.OS.ResolvePath_v1`
- `UML_OS.OS.NamespaceEnter_v1`
- `UML_OS.Data.Manifest_v1`
- `UML_OS.Data.ValidateManifest_v1`
- `UML_OS.Data.NextBatch_v1`
- `UML_OS.Data.RegisterDataset_v1`
- `UML_OS.Data.ImportAndRegister_v1`
- `UML_OS.Model.Forward_v2`
- `UML_OS.Model.ExpandPreset_v1`
- `UML_OS.Model.ApplyFineTune_v1`
- `UML_OS.Objective.TotalLoss_v1`
- `UML_OS.Update_v1`
- `UML_OS.Module.RegisterCustom_v1`
- `UML_OS.Policy.Evaluate_v1`
- `UML_OS.Transition.SwitchState_v1`
- `UML_OS.Contract.Validate_v1`
- `UML_OS.IO.WriteTape_v1`
- `UML_OS.IO.SaveCheckpoint_v1`
- `UML_OS.IO.WriteTrainingCertificate_v1`
- `UML_OS.Logging.LogIteration_v1`
- `UML_OS.Termination.Check_v1`
- `UML_OS.StateFingerprint_v1`
- `UML_OS.Fingerprint.Functional_v1`
- `UML_OS.Error.Emit_v1`
- `UML_OS.Distributed.Setup_v1`
- `UML_OS.Evaluation.Run_v1`
- `UML_OS.Security.AttestTEE_v1`
- `UML_OS.Verifiable.CommitFunctional_v1`
- `UML_OS.DifferentialPrivacy.Apply_v1`
- `UML_OS.Backend.LoadDriver_v1`
- `UML_OS.Pipeline.Dispatch_v1`
- `UML_OS.Inference.RunBatch_v1`

### 0.H Namespacing and Packaging
- Fully-qualified names: `UML_OS.<Category>.<Name>_v#`
- Sidecar mapping required: operator -> module/function

### 0.I Outputs and Metric Schema
- Declared outputs: `theta_final`, `trace`, `checkpoint`, `tape_digest`, `training_certificate`
- Minimum metric schema: `loss_total`, `grad_norm`, `functional_fp`

#### 0.J Spec Lifecycle Governance (mandatory)
Reproducibility-breaking changes require MAJOR bump (vX.Y.Z → v(X+1).0.0).  
Deprecations replace via manifest wiring only.  
Equivalence target for any change: E1 (metric-equivalent) minimum, E0 (trace-equivalent) for kernel or attestation changes.  
Migration: update manifest operator versions and replay_token.

### 0.K Failure and Error Semantics
- Global error model: abort-only
- Final failure record includes: `t`, `failure_code`, `failure_operator`, `replay_token`, `rng_fingerprint_t`, `state_fp_t`

### 0.L Input/Data Provenance
- Dataset id/version/hash mandatory
- Strict parsing and immutable dataset registration mandatory

### 0.M Declarative Configuration
- YAML config mandatory input path
- Canonical JSON serialization before hashing

### 0.N Layered Operating-System Architecture
- Layer ordering:
  - Kernel (VI procedure + operator dispatch + contracts)
  - Driver (deterministic device primitives)
  - Runtime (pinned dependencies)
  - Module (verified operator packages)
  - Daemon (mandatory in `managed`, `confidential`, `regulated` modes or when `UML_OS_ROOT` is shared or `world_size > 1`; optional in `local` mode; deployable as single binary, K8s operator, or cluster coordinator via manifest `daemon_mode: "standalone" | "cluster"`): owns `UML_OS_ROOT` filesystem hierarchy with content-addressable storage (CAS) for all datasets/artifacts/checkpoints; uses priority queue (manifest `job_priority` then FIFO) with explicit dependency graph from `pipeline_stages`; launches isolated process/Pod; in `confidential`/`regulated` launches inside hardware TEE if hardware present and collects remote quote; enforces namespace isolation (RNG, data_cursor, checkpoints, tapes, lineage hashes) with ACL inheritance across org/unit/project/experiment; appends audit log at `/audit/<namespace_path>/`; enforces quotas (CPU/GPU/storage/concurrency) via cgroups/K8s limits or cluster-wide accounting; supports job dependency DAG for chained executions (provenance links automatic in certificate). One daemon instance coordinates entire cluster when `daemon_mode=cluster`.
  - Management (CLI entrypoints)
  - User (manifests only)
- Filesystem roots:
  - `/datasets/<id-version-hash>/`
  - `/namespaces/<org>/<unit>/<project>/<experiment>/<job_id>/`
  - `/jobs/queue/`
- Namespace path: `/org/unit/project/experiment/job_id`, `job_id = replay_token[0:8]`

### 0.P Bootstrap
- Single entrypoint: `UML_OS.OS.Bootstrap_v1`
- Performs deterministic initialization, manifest/data validation, module wiring, distributed setup, and namespace entry

### 0.Q Global Manifest Additions
- `env_manifest_hash` includes `daemon_concurrency_max=16`
- `task_type`: `multiclass | binary | regression`
- `alpha` (default `1.0`)
- `beta` (default `1.0`)
- `execution_mode: "local" | "managed" | "confidential" | "regulated"` (default `managed`)
- `global_batch_size` (default `256`)
- `fingerprint_frequency`
- `optimizer` config
- `grad_clip_norm`
- `checkpoint_frequency`
- `job_priority` (1..10)
- `policy.rules`
- `model_encode_op`, `forward_op`, `decode_op`
- `datasets[]`
- `custom_operators[]`
- `parallelism: {strategy: "none" | "ddp" | "fsdp", world_size_override?}`
- `backend: "pytorch" | "jax" | "custom"` (default `"pytorch"`)
- `pipeline_stages: array` of objects `{step_id: string, type: "train"|"eval"|"infer", manifest_path?: string, depends_on?: array of step_id}`
- `daemon_mode: "standalone" | "cluster"` (default `"standalone"`)
- `fine_tune` config (`full` or `lora`)
- `evaluation` config
- `security: {attestation_required: bool, zk_commitment: bool, differential_privacy: {enabled: bool (default false), target_epsilon: float (default 0.0)}}`
- `model` (`preset`/`preset_params`/`architecture`)
- `compute_dtype: "float32" | "float64"`
- `model.architecture` supports `type: "custom"`

Supported presets in `ExpandPreset_v1`: `mlp_classifier`, `basic_cnn`, `resnet18`, `resnet50`, `vit_tiny`, `bert_tiny`, `gpt2_small`. LoRA insertion is deterministic from checkpoint hash.

### 0.R Distributed and Multi-tenancy Policy
- Deterministic rank ordering and deterministic collective primitives
- `global_batch_size % world_size == 0` required for distributed runs
- Global batch sequence and update sequence independent of `world_size`; sharding always contiguous rank-ordered after global deterministic permutation; collective order fixed by ascending rank.

### 0.S RNG Consumption Contract
- Every operator declares exact RNG draws and stream ownership
- Kernel checks declared-vs-actual offsets every call
- Violations abort with `RNG_CONSUMPTION_VIOLATION`

### 0.T Execution Model
- VI kernel procedure is the only conformant execution path

### 0.U Execution Contract
- No external loop logic or imperative bypass
- Violations fail `Contract.Validate_v1`

### 0.V Operation Modes
- `local`: daemon optional, relaxed warnings mode
- `managed`: full enforcement, signed certificate required
- `confidential`: TEE launch + quote mandatory, full enforcement, signed certificate includes quote
- `regulated`: daemon mandatory; enforces exact differential-privacy accounting, immutable audit trail, model-approval workflow, and electronic signatures (21 CFR Part 11 / EU AI Act / GxP compatible); launches in TEE if hardware present; full RNG auditing; produces signed provenance record containing attestation quote, cumulative privacy budget (epsilon), electronic signatures, and full pipeline lineage when `pipeline_stages` present. In `regulated` mode `attestation_required` and `differential_privacy.enabled` are forced true; `security.target_epsilon` must be declared and non-zero.

### 0.W CLI and Usability Requirements
- Required commands: `init`, `job submit`, `replay`, `export`, `infer`, `verify`, `namespace init`, `daemon start`, `dataset register`, `import dataset`, `import model`, `audit export`, `ps/logs/kill/queue`
- All CLI paths perform contract/manifest validation before run

### 0.X Training Certificate Contract
- Certificate contains: replay_token, Merkle-chained trace root, lineage hashes, final `state_fp`, functional_fp curve (+ zk commitment when enabled), **exact cumulative differential-privacy budget (epsilon in binary64 if regulated)**, manifest hashes, backend fingerprint, daemon public key, operator contract hashes, electronic signatures (daemon ed25519 + optional HSM/company PKI), and (in `confidential`/`regulated` mode) the full remote attestation quote.
- Daemon signs certificate using namespace ed25519 private key; `regulated` mode additionally applies declared electronic signatures.

---

## 2) System Model

### A) Persistent State
- `theta`
- `state ∈ {S_INIT, S_TRAINING, S_EVALUATING, S_TERMINATED}`
- `t`
- `loss_hist`
- `data_cursor = (epoch, global_index)`
- `rng_master_state` + offsets
- `tape_state`

### B) Declared Dimensions and Defaults
- `global_batch_size = 256` (overridable by manifest)

### C) Hyperparameters
- All tunable values are manifest-defined only

### D) Constraint Regime
- Unconstrained optimization + explicit runtime contracts

### E) Invariants
- Finite tensors
- Deterministic ordering
- Contract checks mandatory

---

## 3) Initialization

1. `t <- 0`
2. `UML_OS.OS.Bootstrap_v1(...)`
3. Initialize `theta` deterministically
4. Initialize `state <- S_TRAINING`
5. Initialize `loss_hist`, `data_cursor`, tape, fingerprints

---

## 4) Math Placement

All mathematical definitions are operator-owned in section 5 (no standalone math block). Supervised loss and total loss are normatively defined in `UML_OS.Model.Forward_v2` and `UML_OS.Objective.TotalLoss_v1`.

---

## 5) Operator Library

All operators follow the EQC template:  
**Operator:** `UML_OS.<Category>.<Name>_v#`  
**Category:** Init / Data / Model / Objective / Update / IO / Security / Evaluation / Logging / Termination / Contract / Policy / Distributed / Fingerprint / Error  
**Signature:** (inputs → outputs) with shapes/types  
**Purity class:** PURE / STATEFUL / IO  
**Determinism:** deterministic (with explicit RNG consumption contract)  
**Definition:** (existing text + any math)  
**Preconditions / Postconditions:** (manifest/state requirements and guaranteed outputs)  
**Edge cases:** NaN/Inf, zero batch, world_size=1  
**Numerical considerations:** binary64 critical reductions, EPS guards, deterministic reductions  
**Ordering/tie handling:** ascending index, lowest index wins  
**Failure behavior:** abort per 0.K with failure record  
**Dependencies:** required manifest fields/operators

**Operator:** `UML_OS.OS.Bootstrap_v1`  
**Category:** Init  
**Signature:** `(manifest -> persistent_state)`  
**Purity class:** STATEFUL  
**Determinism:** deterministic  
**Definition:** PRNG master seeded from fixed manifest hash (single Philox + fixed offsets; no draws); parameter init; buffer allocation; data manifest load + ValidateManifest_v1 + ImportAndRegister_v1 if needed; ApplyFineTune_v1 if declared; ExpandPreset_v1 if preset set; Backend.LoadDriver_v1(manifest.backend); Distributed.Setup_v1; policy load; namespace enter; Security.AttestTEE_v1 (confidential mode only).  
**Preconditions / Postconditions:** manifest canonicalized; TEE quote valid in confidential mode.  
**Edge cases:** missing dataset hash, invalid URI, TEE unavailable.  
**Numerical considerations:** manifest-hash-derived bytes for theta init (no RNG).  
**Ordering/tie handling:** N/A.  
**Failure behavior:** `CONTRACT_VIOLATION` or `ATTESTATION_FAILURE` -> abort with record.  
**Dependencies:** 0.Q manifest fields.

**Operator:** `UML_OS.Data.Manifest_v1`  
**Category:** Data  
**Signature:** `(manifest -> canonical_manifest)`  
**Purity class:** PURE  
**Determinism:** deterministic  
**Definition:** canonicalize manifest JSON/YAML; compute hash inputs.  
**Preconditions / Postconditions:** valid schema -> canonical bytes.  
**Edge cases:** malformed keys/order.  
**Numerical considerations:** N/A.  
**Ordering/tie handling:** sorted keys.  
**Failure behavior:** abort on schema mismatch.  
**Dependencies:** 0.Q schema.

**Operator:** `UML_OS.Data.ValidateManifest_v1`  
**Category:** Data  
**Signature:** `(manifest -> ok)`  
**Purity class:** PURE  
**Determinism:** deterministic  
**Definition:** validates required fields, hashes, operator contracts, dataset refs.  
**Preconditions / Postconditions:** all mandatory fields present.  
**Edge cases:** missing `global_batch_size`, invalid `execution_mode`.  
**Numerical considerations:** N/A.  
**Ordering/tie handling:** deterministic field walk.  
**Failure behavior:** abort with `CONTRACT_VIOLATION`.  
**Dependencies:** 0.Q.

**Operator:** `UML_OS.Data.RegisterDataset_v1`  
**Category:** Data  
**Signature:** `(path,id,version -> dataset_id_hash)`  
**Purity class:** IO  
**Determinism:** deterministic  
**Definition:** computes BLAKE3, validates schema, stores immutable dataset under canonical path.  
**Preconditions / Postconditions:** data readable; hash persisted.  
**Edge cases:** duplicate id/version mismatch.  
**Numerical considerations:** N/A.  
**Ordering/tie handling:** lexicographic file traversal.  
**Failure behavior:** abort on hash mismatch.  
**Dependencies:** OS path resolver.

**Operator:** `UML_OS.Data.ImportAndRegister_v1`  
**Category:** Data  
**Signature:** `(uri,id,version -> dataset_id_hash)`  
**Purity class:** IO  
**Determinism:** deterministic  
**Definition:** imports from local/s3/hf URI then delegates to RegisterDataset_v1.  
**Preconditions / Postconditions:** imported bytes immutable after registration.  
**Edge cases:** URI unavailable/auth failure.  
**Numerical considerations:** N/A.  
**Ordering/tie handling:** deterministic chunk/file order.  
**Failure behavior:** abort.  
**Dependencies:** RegisterDataset_v1.

**Operator:** `UML_OS.Data.NextBatch_v1`  
**Category:** Data  
**Signature:** `(data_cursor, world_size, rank -> batch, data_cursor')`  
**Purity class:** STATEFUL  
**Determinism:** deterministic with declared RNG  
**Definition:** exactly 1 RNG draw from `misc`; global permutation via Philox4x32-10 seeded by `manifest_hash || epoch` using Fisher-Yates in ascending index order; construct global batch; split into `world_size` contiguous shards ordered by rank.  
**Preconditions / Postconditions:** `global_batch_size % world_size == 0`.  
**Edge cases:** world_size=1, final batch boundary.  
**Numerical considerations:** preprocessing stable in binary64 for reductions.  
**Ordering/tie handling:** ascending global index.  
**Failure behavior:** abort on invalid shard/batch.  
**Dependencies:** 0.R.

**Operator:** `UML_OS.Model.ExpandPreset_v1`  
**Category:** Model  
**Signature:** `(model.preset, preset_params, fine_tune -> expanded_architecture)`  
**Purity class:** PURE  
**Determinism:** deterministic  
**Definition:** expands known preset table; inserts LoRA adapters deterministically when configured.  
**Preconditions / Postconditions:** preset exists.  
**Edge cases:** unknown preset/target module.  
**Numerical considerations:** no RNG.  
**Ordering/tie handling:** registration order of layers.  
**Failure behavior:** abort.  
**Dependencies:** 0.Q model fields.

**Operator:** `UML_OS.Model.ApplyFineTune_v1`  
**Category:** Model  
**Signature:** `(theta, fine_tune_cfg -> theta')`  
**Purity class:** STATEFUL  
**Determinism:** deterministic  
**Definition:** applies full or LoRA fine-tune wiring/checkpoint loading.  
**Preconditions / Postconditions:** checkpoint hash must match manifest.  
**Edge cases:** missing checkpoint, incompatible layer shapes.  
**Numerical considerations:** deterministic load/merge order.  
**Ordering/tie handling:** parameter registration order.  
**Failure behavior:** abort.  
**Dependencies:** checkpoint manifest.

**Operator:** `UML_OS.Model.Forward_v2`  
**Category:** Model  
**Signature:** `(theta, batch, expanded_architecture -> logits)`  
**Purity class:** PURE  
**Determinism:** deterministic  
**Definition:** dispatches to active backend driver; executes expanded architecture (custom layers via registry); all reductions in binary64 with ascending-index order.  
**Preconditions / Postconditions:** architecture validated.  
**Edge cases:** empty batch, invalid custom ref.  
**Numerical considerations:** critical reductions in binary64; deterministic reduction order.  
**Ordering/tie handling:** layer order fixed by architecture list.  
**Failure behavior:** abort.  
**Dependencies:** RegisterCustom_v1.

**Operator:** `UML_OS.Objective.TotalLoss_v1`  
**Category:** Objective  
**Signature:** `(logits, labels, alpha, task_type -> L_tot)`  
**Purity class:** PURE  
**Determinism:** deterministic  
**Definition:** `L_sup = mean(loss_by_type)` in binary64. Multiclass: `-log(softmax(logits)[labels])` (stable log-softmax); binary: BCE with logits; regression: MSE. `L_tot = alpha * L_sup`. Reduction: exact sum then divide by batch size (ascending index).  
**Preconditions / Postconditions:** labels valid for task type.  
**Edge cases:** invalid class ids, NaN logits.  
**Numerical considerations:** stable CE/BCE/MSE paths; EPS clamps as needed.  
**Ordering/tie handling:** ascending index accumulation.  
**Failure behavior:** invalid objective policy from 0.A/0.K.  
**Dependencies:** 0.A, 0.C.

**Operator:** `UML_OS.Update_v1`  
**Category:** Update  
**Signature:** `(theta, grads, optimizer_cfg -> theta')`  
**Purity class:** STATEFUL  
**Determinism:** deterministic  
**Definition:** if optimizer==\"adamw\": `m_t = beta1*m_{t-1} + (1-beta1)*g`; `v_t = beta2*v_{t-1} + (1-beta2)*g**2`; `m_hat = m_t/(1-beta1^t)`; `v_hat = v_t/(1-beta2^t)`; `theta = theta - lr*(m_hat/(sqrt(v_hat)+eps) + weight_decay*theta)`. All in binary64, parameters updated in registration order, clip norm applied before. Other optimizers follow analogous deterministic updates.  
**Preconditions / Postconditions:** optimizer config valid.  
**Edge cases:** zero/NaN gradients.  
**Numerical considerations:** clip norm in binary64.  
**Ordering/tie handling:** parameter registration order.  
**Failure behavior:** abort on non-finite gradients.  
**Dependencies:** 0.Q optimizer.

**Operator:** `UML_OS.Module.RegisterCustom_v1`  
**Category:** Module  
**Signature:** `(custom_operators[] -> registry')`  
**Purity class:** STATEFUL  
**Determinism:** deterministic  
**Definition:** loads user-declared custom operators from manifest and verifies declared purity, RNG consumption, and contract hash before registration.  
**Preconditions / Postconditions:** contract declaration present per operator.  
**Edge cases:** missing module path, contract mismatch.  
**Numerical considerations:** N/A.  
**Ordering/tie handling:** registration in declared manifest order.  
**Failure behavior:** abort with `CONTRACT_VIOLATION`.  
**Dependencies:** `custom_operators` manifest field.

**Operator:** `UML_OS.Policy.Evaluate_v1`  
**Category:** Policy  
**Signature:** `(state, metrics, rules -> action)`  
**Purity class:** PURE  
**Determinism:** deterministic  
**Definition:** evaluates `policy.rules` in declared order; highest priority wins; ties by lowest index.  
**Preconditions / Postconditions:** rules schema valid.  
**Edge cases:** no matching rule -> fallback `optimize`.  
**Numerical considerations:** comparisons in binary64.  
**Ordering/tie handling:** deterministic rule order.  
**Failure behavior:** abort on malformed rule expression.  
**Dependencies:** 0.Q.

**Operator:** `UML_OS.Evaluation.Run_v1`  
**Category:** Evaluation  
**Signature:** `(theta, val_data, metrics -> eval_result)`  
**Purity class:** STATEFUL  
**Determinism:** deterministic  
**Definition:** computes declared metrics at configured frequency.  
**Preconditions / Postconditions:** val split exists if configured.  
**Edge cases:** empty val split.  
**Numerical considerations:** binary64 reductions for metrics.  
**Ordering/tie handling:** ascending index over val data.  
**Failure behavior:** abort on missing eval split.  
**Dependencies:** `evaluation` manifest.

**Operator:** `UML_OS.Inference.RunBatch_v1`  
**Category:** Inference  
**Signature:** `(theta, batch, backend -> outputs)`  
**Purity class:** STATEFUL  
**Determinism:** deterministic  
**Definition:** dispatches to backend driver for inference batch execution; writes outputs and fingerprint material.  
**Preconditions / Postconditions:** backend loaded and batch schema valid.  
**Edge cases:** empty batch.  
**Numerical considerations:** binary64 for critical reductions/fingerprint path.  
**Ordering/tie handling:** ascending sample index order.  
**Failure behavior:** abort on backend/runtime mismatch.  
**Dependencies:** Backend.LoadDriver_v1.

**Operator:** `UML_OS.Distributed.Setup_v1`  
**Category:** Distributed  
**Signature:** `(parallelism, world_size, backend -> dist_state)`  
**Purity class:** STATEFUL  
**Determinism:** deterministic  
**Definition:** initializes deterministic collectives and rank order.  
**Preconditions / Postconditions:** valid backend and world size.  
**Edge cases:** world_size=1.  
**Numerical considerations:** deterministic reduction primitives only.  
**Ordering/tie handling:** ascending rank.  
**Failure behavior:** abort on unsupported backend.  
**Dependencies:** 0.R.

**Operator:** `UML_OS.Backend.LoadDriver_v1`  
**Category:** Backend  
**Signature:** `(manifest.backend -> driver_handle)`  
**Purity class:** STATEFUL  
**Determinism:** deterministic  
**Definition:** Loads and verifies backend driver contract; binds dispatch table for Forward/Update/Distributed.  
**Preconditions / Postconditions:** driver implements all required primitives.  
**Edge cases:** unknown backend id.  
**Numerical considerations:** N/A.  
**Ordering/tie handling:** N/A.  
**Failure behavior:** abort `BACKEND_CONTRACT_VIOLATION`.  
**Dependencies:** manifest `backend`.

**Operator:** `UML_OS.Pipeline.Dispatch_v1`  
**Category:** Pipeline  
**Signature:** `(pipeline_stages, current_step -> next_manifest, action)`  
**Purity class:** PURE  
**Determinism:** deterministic  
**Definition:** Resolves dependency graph; returns next stage manifest or termination.  
**Preconditions / Postconditions:** stage ids unique and resolvable.  
**Edge cases:** missing dependency.  
**Numerical considerations:** N/A.  
**Ordering/tie handling:** deterministic topological order with stable tie-break.  
**Failure behavior:** abort on cycle or missing dependency.  
**Dependencies:** manifest `pipeline_stages`.

**Operator:** `UML_OS.Contract.Validate_v1`  
**Category:** Contract  
**Signature:** `(runtime_state -> ok)`  
**Purity class:** PURE  
**Determinism:** deterministic  
**Definition:** checks declared invariants, objective finiteness, RNG delta contracts, ordering contracts; additionally verifies backend driver contract and pipeline DAG acyclicity.  
**Preconditions / Postconditions:** all required telemetry present.  
**Edge cases:** local relaxed mode emits warnings.  
**Numerical considerations:** EPS_EQ thresholding.  
**Ordering/tie handling:** deterministic check order.  
**Failure behavior:** abort/warn per execution mode.  
**Dependencies:** 0.V.

**Operator:** `UML_OS.StateFingerprint_v1`  
**Category:** Fingerprint  
**Signature:** `(state -> state_fp)`  
**Purity class:** PURE  
**Determinism:** deterministic  
**Definition:** incremental BLAKE3 update with SHA-256 tuple over deterministic state domain.  
**Preconditions / Postconditions:** persistent state serializable.  
**Edge cases:** empty history.  
**Numerical considerations:** binary64 serialization for critical tensors/metrics.  
**Ordering/tie handling:** deterministic serialization order.  
**Failure behavior:** abort on serialization mismatch.  
**Dependencies:** persistent state schema.

**Operator:** `UML_OS.Fingerprint.Functional_v1`  
**Category:** Fingerprint  
**Signature:** `(theta, probe_set -> functional_fp)`  
**Purity class:** PURE  
**Determinism:** deterministic  
**Definition:** runs canonical probe set (first 1024 items deterministic), computes probe loss/metric, hashes bytes into functional fingerprint.  
**Preconditions / Postconditions:** probe set available.  
**Edge cases:** dataset size < 1024 uses cyclic repeat.  
**Numerical considerations:** binary64 path.  
**Ordering/tie handling:** ascending original index.  
**Failure behavior:** abort on non-finite probe outputs.  
**Dependencies:** dataset manifest.

**Operator:** `UML_OS.Verifiable.CommitFunctional_v1`  
**Category:** Fingerprint  
**Signature:** `(probe_outputs_bytes, functional_fp, security.zk_commitment -> commitment?)`  
**Purity class:** PURE  
**Determinism:** deterministic  
**Definition:** if enabled, compute `zk_commitment = SHA-256(probe_outputs_bytes || functional_fp)` and attach to trace/certificate.  
**Preconditions / Postconditions:** functional_fp available.  
**Edge cases:** disabled path returns no commitment.  
**Numerical considerations:** N/A.  
**Ordering/tie handling:** canonical byte order.  
**Failure behavior:** abort on digest mismatch.  
**Dependencies:** `security.zk_commitment`.

**Operator:** `UML_OS.Security.AttestTEE_v1`  
**Category:** Security  
**Signature:** `(execution_mode, manifest_hash, replay_token -> quote)`  
**Purity class:** STATEFUL  
**Determinism:** deterministic protocol path  
**Definition:** in confidential mode, collect hardware quote covering kernel measurement + manifest hash + replay token; store for certificate.  
**Preconditions / Postconditions:** TEE available and quote valid.  
**Edge cases:** unavailable TEE, invalid quote, mismatch measurement.  
**Numerical considerations:** N/A.  
**Ordering/tie handling:** N/A.  
**Failure behavior:** `ATTESTATION_FAILURE` abort.  
**Dependencies:** confidential execution mode.

**Operator:** `UML_OS.IO.WriteTape_v1`  
**Category:** IO  
**Signature:** `(event -> tape_state')`  
**Purity class:** IO  
**Determinism:** deterministic  
**Definition:** append event in deterministic order with fixed block/chaining rules.  
**Preconditions / Postconditions:** tape open and writable.  
**Edge cases:** block rollover.  
**Numerical considerations:** N/A.  
**Ordering/tie handling:** ascending t.  
**Failure behavior:** abort on write/hash mismatch.  
**Dependencies:** tape state.

**Operator:** `UML_OS.IO.SaveCheckpoint_v1`  
**Category:** IO  
**Signature:** `(state -> checkpoint)`  
**Purity class:** IO  
**Determinism:** deterministic  
**Definition:** writes full checkpoint at frequency or termination using deterministic serialization.  
**Preconditions / Postconditions:** checkpoint path resolved in namespace.  
**Edge cases:** checkpoint_frequency=0 disables periodic writes.  
**Numerical considerations:** binary64 for critical values.  
**Ordering/tie handling:** fixed field order.  
**Failure behavior:** abort on write/serialize failure.  
**Dependencies:** section 10 schema.

**Operator:** `UML_OS.IO.WriteTrainingCertificate_v1`  
**Category:** IO  
**Signature:** `(run_state -> training_certificate.cbor)`  
**Purity class:** IO  
**Determinism:** deterministic  
**Definition:** emits signed CBOR containing Merkle trace root, lineage chain (all pipeline stages), fingerprints, manifest hashes, operator contract hashes, cumulative epsilon (regulated), full remote attestation quote (confidential/regulated), and CAS artifact hashes.  
**Preconditions / Postconditions:** daemon signing key available.  
**Edge cases:** missing quote in confidential mode.  
**Numerical considerations:** deterministic digest encoding.  
**Ordering/tie handling:** ascending t in trace chain.  
**Failure behavior:** abort on signing failure.  
**Dependencies:** daemon key + 0.X contract.

**Operator:** `UML_OS.Logging.LogIteration_v1`  
**Category:** Logging  
**Signature:** `(iter_state -> log_record)`  
**Purity class:** IO  
**Determinism:** deterministic  
**Definition:** writes iteration metrics per schema.  
**Preconditions / Postconditions:** log sink available.  
**Edge cases:** skipped fields if fingerprint not due.  
**Numerical considerations:** binary64 serialization for metrics.  
**Ordering/tie handling:** ascending t.  
**Failure behavior:** abort on logging I/O failure.  
**Dependencies:** observability schema.

**Operator:** `UML_OS.Termination.Check_v1`  
**Category:** Termination  
**Signature:** `(state, limits -> bool)`  
**Purity class:** PURE  
**Determinism:** deterministic  
**Definition:** evaluates manifest termination criteria.  
**Preconditions / Postconditions:** criteria declared.  
**Edge cases:** max_steps=0.  
**Numerical considerations:** EPS_EQ comparisons.  
**Ordering/tie handling:** deterministic criterion order.  
**Failure behavior:** abort on invalid criteria.  
**Dependencies:** manifest limits.

**Operator:** `UML_OS.Transition.SwitchState_v1`  
**Category:** Transition  
**Signature:** `(state, action -> state')`  
**Purity class:** STATEFUL  
**Determinism:** deterministic  
**Definition:** transitions among declared lifecycle states for evaluate/train/terminate paths.  
**Preconditions / Postconditions:** valid action-state pair.  
**Edge cases:** invalid transition.  
**Numerical considerations:** N/A.  
**Ordering/tie handling:** N/A.  
**Failure behavior:** abort on invalid transition.  
**Dependencies:** state model.

**Operator:** `UML_OS.OS.ResolvePath_v1`  
**Category:** OS  
**Signature:** `(logical_path, namespace -> absolute_path)`  
**Purity class:** PURE  
**Determinism:** deterministic  
**Definition:** resolves canonical namespace-bound path under `UML_OS_ROOT`.  
**Preconditions / Postconditions:** namespace exists and caller authorized.  
**Edge cases:** invalid traversal (`..`) or missing namespace path.  
**Numerical considerations:** N/A.  
**Ordering/tie handling:** lexicographic canonicalization.  
**Failure behavior:** abort.  
**Dependencies:** daemon ACL/namespace state.

**Operator:** `UML_OS.OS.NamespaceEnter_v1`  
**Category:** OS  
**Signature:** `(namespace_path -> active_namespace)`  
**Purity class:** STATEFUL  
**Determinism:** deterministic  
**Definition:** enters namespace and binds filesystem, RNG, and state scopes.  
**Preconditions / Postconditions:** ACL allows access.  
**Edge cases:** non-existent namespace.  
**Numerical considerations:** N/A.  
**Ordering/tie handling:** N/A.  
**Failure behavior:** abort.  
**Dependencies:** daemon namespace registry.


**Operator:** `UML_OS.Error.Emit_v1`  
**Category:** Error  
**Signature:** `(failure_code, context -> failure_record)`  
**Purity class:** IO  
**Determinism:** deterministic  
**Definition:** emits final structured failure record to trace and audit log.  
**Preconditions / Postconditions:** failure record persisted before abort.  
**Edge cases:** nested failure during emit.  
**Numerical considerations:** N/A.  
**Ordering/tie handling:** deterministic failure field order.  
**Failure behavior:** terminal abort-only model.  
**Dependencies:** 0.K failure semantics.

**Operator:** `UML_OS.DifferentialPrivacy.Apply_v1`  
**Category:** Security  
**Signature:** `(gradients, security.differential_privacy -> noisy_gradients, updated_budget)`  
**Purity class:** STATEFUL  
**Determinism:** deterministic  
**Definition:** If enabled, adds calibrated Gaussian/Laplace noise in binary64; tracks exact cumulative epsilon in persistent state and certificate; aborts if budget would be exceeded.  
**Preconditions / Postconditions:** called only on raw gradients before any optimizer step; `target_epsilon` declared and remaining budget sufficient.  
**Edge cases:** epsilon=0, zero gradients.  
**Numerical considerations:** noise scale computed exactly in binary64.  
**Ordering/tie handling:** N/A.  
**Failure behavior:** abort with `PRIVACY_BUDGET_EXCEEDED`.  
**Dependencies:** regulated mode, 0.Q security fields.


---

## 6) Procedure

1. `UML_OS.OS.Bootstrap_v1(...)`
2. `UML_OS.OS.NamespaceEnter_v1(job_id)`

Loop until all pipeline stages terminated:
- `UML_OS.Termination.Check_v1(...)`
- `t <- t + 1`
- `batch <- UML_OS.Data.NextBatch_v1(...)`
- `logits <- UML_OS.Model.Forward_v2(...)`
- `L_tot <- UML_OS.Objective.TotalLoss_v1(...)`
- `UML_OS.Contract.Validate_v1(...)`
- `action <- UML_OS.Policy.Evaluate_v1(...)`
- if action == "optimize":
  - grads = backend_driver.backward(L_tot)  // via driver_handle from LoadDriver_v1
  - if manifest.execution_mode == "regulated": `noisy_grads, budget <- UML_OS.DifferentialPrivacy.Apply_v1(grads)`
  - `theta <- UML_OS.Update_v1(noisy_grads or grads, ...)`
- else if action == "eval": `UML_OS.Evaluation.Run_v1(...)`
- else if action == "infer": `UML_OS.Inference.RunBatch_v1(...)`
- else if action == "switch": `UML_OS.Transition.SwitchState_v1(...)`
- if checkpoint due: `UML_OS.IO.SaveCheckpoint_v1(...)`
- if fingerprint due: `StateFingerprint_v1`, `Fingerprint.Functional_v1`, `Verifiable.CommitFunctional_v1` (if enabled)
- `UML_OS.IO.WriteTape_v1(...)`
- `UML_OS.Logging.LogIteration_v1(...)`
- `UML_OS.Pipeline.Dispatch_v1(...)`  // advance to next stage or terminate

On full termination: `UML_OS.IO.WriteTrainingCertificate_v1(...)`

---

## 7) Observability

### Trace schema
- `run_header`: metadata, hashes, replay token, task_type, world_size, backend hash
- `iter`: `t, state, action, loss_total, grad_norm, state_fp (when computed), functional_fp (when computed), zk_commitment (when enabled)`
- `run_end`: status, final hashes, final fingerprints

### Certificate schema
- Signed `training_certificate.cbor` with Merkle root, lineage, fingerprints, manifest/contract hashes, and confidential quote when applicable

---

## 8) Validation
#### VII.A Lint rules (mandatory)
Spec passes: symbol completeness, no hidden globals, total state updates per iteration, stochastic explicitness (RNG only inside operators), edge-case totality, ordering/tie adherence, trace compliance, manifest completeness, purity class for all operators, failure semantics traceable, data provenance declared, global batch independence.
- pipeline DAG acyclic and all stages reference valid manifests; backend driver contracts satisfied.

#### VII.B Operator test vectors (mandatory)
Every operator has deterministic test vectors (input → output within EPS_EQ) and stochastic replay-token verification (seed → exact sequence).

#### VII.C Golden traces (mandatory)
At least one golden run trace per execution_mode for reference seed + any manifest-declared dataset. Regression criteria: exact replay_token, state_fp sequence, functional_fp curve within declared tolerance envelope over 10 seeds (E1).

---

## 9) Refactor & Equivalence
#### VIII.A Equivalence levels
- **E0 Trace-equivalent** (bitwise identical trace and certificate)
- **E1 Metric-equivalent** (identical loss/functional_fp curves within tolerance)
- **E2 Distribution-equivalent** (statistical replay over seeds)
- **E3 Invariant-equivalent** (same contracts and state_fp sequence)

Required level for any change: E1 minimum; E0 for kernel, attestation, or RNG contract changes.

#### VIII.B Allowed refactor categories
- algebraic simplification of loss or fingerprint
- numerical stabilization (clamps, ordering)
- vectorization/batching (preserve reduction order)
- parallelization (re-declare 0.R sharding)
- operator replacement via version bump + manifest update
- driver certification (new hardware TEE backend)
- declarative-only entrypoint preservation, kernel-only execution, manifest-driven dispatch, dataset registration immutability, signed certificate portability
- regulated-mode additions (differential-privacy accounting, compliance report generation, electronic signatures)

Breaking observables require trace schema update + MAJOR version bump.

#### VIII.C Equivalence test procedure (mandatory)
- 10 seeds per golden dataset
- metrics: replay_token, state_fp sequence, functional_fp curve, final theta (binary64)
- thresholds: EPS_EQ for scalars, exact Merkle root for certificate
- statistical test for E2: Kolmogorov-Smirnov on loss curves (α=0.01, Bonferroni-corrected).
- regulated-mode artefacts: exact cumulative epsilon, signed compliance report, electronic signature validation.

---

## 10) Checkpoint/Restore

### Checkpoint contents
- canonicalized full manifest (including pipeline_stages)
- operator contract hashes
- `theta`, optimizer state
- `loss_hist`, `data_cursor`
- RNG master state + offsets
- `policy_hash`, `env_manifest_hash`, `replay_token`, `backend_hash`
- latest `state_fp`, `functional_fp`, optional `zk_commitment`
- pipeline lineage state

### Serialization
- deterministic protobuf/CBOR encoding with fixed field order

### Restore semantics
- restore produces identical subsequent control flow under same manifest/seed/replay token contract
- in confidential mode, attestation must be re-validated before resuming

### Post-termination export
- `theta.pt`
- `inference_manifest.yaml`
- `training_certificate.cbor`
- `model.onnx`
- `model_card.json`
