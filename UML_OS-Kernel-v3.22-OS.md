# Universal Machine Learning Operating System (UML_OS) v3.22-OS
**EQC Compliance:** This specification follows the merged single-file format of EquationCode (EQC) v1.1 (Option A) with the required 10 top-level sections and all mandatory invariants (global semantics first, control-flow-only procedure, versioned operators, purity/RNG contracts, total state updates, trace schema, equivalence levels, lint rules, checkpoint replay guarantees).

**Algorithm:** Deterministic training OS kernel with operator contracts, namespace isolation, and hardware attestation.  
**Purpose (1 sentence):** Execute declarative machine learning training, evaluation, inference, and confidential operations under contract-enforced determinism, namespace isolation, hardware-rooted attestation, and verifiable provenance.  
**Spec Version:** UML_OS-v3.22-OS | 2026-02-17 | Authors: Olejar Damir  
**Domain / Problem Class:** Reproducible neural-network training, evaluation, inference, and confidential lifecycle management.

---

## 1) Header & Global Semantics

### 0.0 Identity
- **Algorithm:** Deterministic training OS kernel with operator contracts, namespace isolation, and hardware attestation.
- **Purpose (1 sentence):** Execute declarative machine learning training, evaluation, inference, and confidential operations under contract-enforced determinism, namespace isolation, hardware-rooted attestation, and verifiable provenance.
- **Spec Version:** UML_OS-v3.22-OS | 2026-02-17 | Authors: Olejar Damir
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
- Seed space: `seed ∈ {0..2^64-1}`
- PRNG family: Philox4x32-10
- Single master stream with fixed sub-stream offsets: `init`, `cluster`, `misc`
- Randomness locality: all sampling occurs **only inside operators**
- Replay guarantee: replayable given `(seed, PRNG family, numeric policy, ordering policy, parallel policy, environment policy)`
- Replay token: `replay_token = SHA-256(CBOR(["replay_token_v1", spec_version, policy_hash, env_manifest_hash, uint64(seed)]))`
- Replay context must also bind:
  - `sampler_config_hash`,
  - `tmmu_plan_hash`,
  - `dp_accountant_state_hash`,
  - `determinism_profile_hash`,
  - backend runtime fingerprint.
- Canonical hash/input encoding rule (global): all hash inputs are domain-separated CBOR arrays; strings encoded UTF-8; integers encoded as unsigned big-endian logical values via CBOR major type.

### 0.C Numeric Policy
- Core arithmetic (loss, metrics, termination, fingerprints, gradient norms, DP accounting, critical reductions): IEEE-754 binary64 with deterministic ascending-index order and EPS guards.
- Model parameters, optimizer state, intermediates, non-critical computations: manifest.compute_dtype (float32 default).
- Critical reductions and fingerprints: binary64, deterministic ascending-index order
- All reductions (including all-reduce, gradient norm, loss summation) use Kahan compensated summation or pairwise tree reduction in binary64 with fixed ascending-index order; E0 bitwise guarantees apply within a fixed `(world_size, collective algorithm, rank order, driver build, math flags)` equivalence class.
- Rounding mode: round-to-nearest ties-to-even
- Fast-math: forbidden
- Constants: `EPS_EQ = 1e-10`, `EPS_DENOM = 1e-12`, `EPS_PROB = 1e-15`
- Clamps: `exp` argument `[-80, 80]`; denominator `max(den, EPS_DENOM)`; probabilities `[EPS_PROB, 1]` then renormalize
- NaN/Inf policy: NaN/±Inf ranked as `+Inf` (see 0.A); abort per 0.K on critical paths
- Normalized exponentials: stable log-sum-exp required in all softmax / log-probability paths
- Approx-equality: `a ≈ b` iff `|a - b| ≤ EPS_EQ`

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
- Each backend driver (loaded via `UML_OS.Backend.LoadDriver_v1`) must implement deterministic forward/backward passes with fixed ascending-index reduction order, deterministic collectives (all-reduce, broadcast) using ascending-rank ring topology, RNG forwarding from kernel master streams with declared offsets, exact operator contracts for all dispatched primitives, and must pass the mandatory ReproducibilityTest suite. The suite requires E0 equivalence within a declared backend/hardware equivalence class (same build/profile), and E1 vs certified CPU reference on larger workloads. Driver verification (including binary/manifest hash check) is mandatory inside `Contract.Validate_v1` before any dispatch.
- Driver interface contract (mandatory for LoadDriver_v1): Implements Forward_v2/Backward_v1/Inference.RunBatch_v1 on UML_Model_IR DAG using only deterministic primitives; no exposed user-callable loops; supports memory-zeroing hooks, TMMU allocation/liveness hints, and TEE quote collection; declares exact op-to-primitive mapping. Passes mandatory ReproducibilityTest suite (E0 on tiny graphs vs certified CPU reference in binary64; E1 on larger workloads) before dispatch. In regulated mode only drivers from the configured signed registry are accepted.
- Determinism level: `BITWISE` for critical observables (`loss_total`, `grad_norm`, fingerprints, `state_fp`) within a declared adapter/hardware equivalence class; `TOLERANCE` for raw model parameters.
- `state_fp` canonicalization rule: compute from quantized parameter view `q(theta)=round(theta*2^24)/2^24` in binary64 with fixed ordering, so tolerance-level parameter drift does not violate fingerprint comparability policy.

### 0.G Operator Manifest
Active operator wiring is declared in section `4) Operator Manifest`.

### 0.H Namespacing and Packaging
- Fully-qualified names: `UML_OS.<Category>.<Name>_v#`
- Sidecar mapping required: operator -> module/function

### 0.I Outputs and Metric Schema
- Declared outputs: `theta_final`, `trace`, `checkpoint`, `tape_digest`, `training_certificate`
- Minimum metric schema: `loss_total`, `grad_norm`, `functional_fp`
- Completion status: `success | terminated | failed` with deterministic reason codes.

### 0.J Spec Lifecycle Governance
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
  - Daemon (mandatory in managed, confidential, regulated modes or when UML_OS_ROOT shared or world_size > 1; optional/in-process in local): Central OS service layer. Owns immutable CAS at UML_OS_ROOT, deterministic scheduling (job_priority + FIFO + BLAKE3(CBOR(["daemon_sched_v1", manifest_hash, hardware_attest_id, job_id])) for reproducible allocation), launches isolated per-job process/Pod with namespace isolation (RNG/data_cursor/checkpoints/tapes/lineage) and explicit tensor.zero_() + sync barriers on every boundary, enforces quotas/RBAC/audits, coordinates TEE quotes and heterogeneous drivers. In local mode Bootstrap_v1 embeds equivalent in-process functionality (identical contracts, replay_token, fingerprints, certificate). Deployable as single binary or K8s operator. The daemon also registers the Tensor Memory Management Unit (TMMU) that exclusively owns and controls every tensor pointer across the job lifetime. Allocations, frees, device-to-device transfers and zeroing occur only via TMMU. Addressing is arena/offset based (injective deterministic layout) as delegated to `TMMU-Allocation.md` (`MapToVirtualAddresses_v1`) and versioned there. TMMU performs static liveness analysis on UML_Model_IR (shapes known) to enable deterministic slot reuse within safety margins; enforces tensor.zero_() + synchronization barriers on every stage, job, and namespace boundary for isolation; blocks any backend direct allocation. This guarantees identical virtual address plans and deterministic layout decisions within a declared hardware/driver equivalence class.
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
- `execution_mode: "local" | "managed" | "confidential" | "regulated"` (default `managed`)
- `global_batch_size` (default `256`)
- `fingerprint_frequency`
- `optimizer` config
- `grad_clip_norm`
- `checkpoint_frequency`
- `job_priority` (1..10)
- `policy.rules`
- `datasets: object` (keys = dataset_keys e.g. "train", "val", "test"; each value = `{id: string, version: string, hash: string}`)
- `data: {sampler_block_size?: integer (default 1048576)}`
- `custom_operators[]`
- `parallelism: {strategy: "none" | "ddp" | "fsdp" | "tensor_parallel" | "pipeline_parallel" | "hybrid", world_size_override?, sharding_config?: object}`
- `manifest_inheritance: {parent_manifest_path?: string}` (resolved and merged by daemon in Bootstrap_v1; child may override only non-security fields; security parameters inherited strictly)
- `hardware_affinity: {gpu_ids?: array of int, cpu_cores?: array of int}` (optional; daemon pins for deterministic scheduling)
- `profile: "research" | "enterprise" | "regulated"` (Bootstrap_v1 expands to execution_mode-appropriate defaults for security, quotas, evaluation metrics, pipeline_stages, and pipeline checks). If pipeline_stages absent, default is: research = [{step_id:"train",type:"train"},{step_id:"eval",type:"eval",depends_on:["train"]}], enterprise = [{step_id:"train",type:"train"},{step_id:"eval",type:"eval",depends_on:["train"]},{step_id:"infer",type:"infer",depends_on:["eval"]}], regulated = same as enterprise plus DP-forced augment stage if augment_config present.
- `backend: "pytorch" | "jax" | "custom"` (default `"pytorch"`)
- `pipeline_stages: array` of objects `{step_id: string, type: "train"|"eval"|"infer"|"augment", manifest_path?: string, depends_on?: array of step_id, dataset_key?: string}`
- `resource_requests: {cpus: int, gpus: int, memory_gb: float} (global or per-stage in pipeline_stages objects; daemon scheduler enforces)`
- `rbac: {principals: array, permissions: map}` (optional; daemon enforces on NamespaceEnter_v1 and critical ops).
- `storage: {backend: "local" | "s3-compatible" | "gcs", endpoint?: string, bucket?: string, credentials_secret?: string}` (daemon uses for all CAS reads/writes; credentials_secret resolved securely by daemon only)
- `monitoring_export: {prometheus_endpoint?: string, log_sink?: string}` (daemon pushes deterministic metrics, audit summaries, and usage records; optional)
- `rbac_source: "local" | "ldap" | "oidc"` (default "local"; daemon integrates for `NamespaceEnter_v1` and critical ops)
- `environment: {requirements_hash?: string (BLAKE3 of pinned pip freeze / conda env or equivalent), container_image?: string}`
- `daemon_mode: "standalone" | "cluster"` (default `"standalone"`)
- `distributed: {timeout_seconds: int (default 300)}`
- `fine_tune` config (`full` or `lora`)
- `evaluation` config
- `security: {attestation_required: bool, functional_commitment: bool (default false), differential_privacy: {enabled: bool (default false), target_epsilon: float (default 0.0)}}`
- `model` (`preset`/`preset_params`/`architecture`)
- `compute_dtype: "float32" | "float64"`
- `model.architecture` supports `type: "custom"`

Supported presets in `ExpandPreset_v1`: `mlp_classifier`, `basic_cnn`, `resnet18`, `resnet50`, `vit_tiny`, `bert_tiny`, `gpt2_small`. LoRA insertion is deterministic from checkpoint hash.

### 0.R Distributed and Multi-tenancy Policy
- Deterministic rank ordering and deterministic collective primitives
- `global_batch_size % world_size == 0` required for distributed runs
- Global batch sequence is world-size invariant by data contract; update values are E0 only within fixed distributed configuration and E1 across compatible re-shards; sharding remains contiguous rank-ordered after global deterministic permutation; collective order fixed by ascending rank.
- In `daemon_mode=cluster`, all collectives respect manifest `distributed.timeout_seconds` (default 300); any timeout or communication error aborts deterministically with `DISTRIBUTED_COMMUNICATION_FAILURE` record (included in trace and certificate).
- Declared parallelism.strategy is implemented by the loaded driver under Contract.Validate_v1 and the ReproducibilityTest suite (sharding of model parameters and data consistent with NextBatch_v2 and UML_Model_IR node annotations). Hybrid strategies combine via manifest-defined stage or node partitioning.

### 0.S RNG Consumption Contract
- Every operator declares exact RNG draws and stream ownership
- Kernel checks declared-vs-actual offsets every call
- Violations abort with `RNG_CONSUMPTION_VIOLATION`

### 0.T Execution Model
- VI kernel procedure is the only conformant execution path

### 0.U Execution Contract
- All execution occurs exclusively through the VI kernel procedure in section 6 and registered, contract-validated operators/drivers. No user-provided training/evaluation/inference loops or direct backend calls permitted; manifest declares the complete computation graph. In managed/confidential/regulated modes, daemon and drivers sandbox execution: any non-registered library primitive call, unapproved import, or side effect triggers CONTRACT_VIOLATION abort with telemetry recorded in Contract.Validate_v1. Custom logic permitted only via RegisterCustom_v1 operators that pass full Contract.Validate_v1 (purity, RNG consumption, ordering, determinism, IR mapping). Violations abort with CONTRACT_VIOLATION.

### 0.V Operation Modes
- `local`: daemon optional, relaxed warnings mode
- `managed`: full enforcement, signed certificate required
- `confidential`: TEE launch + quote mandatory, full enforcement, signed certificate includes quote
- `regulated`: daemon mandatory; enforces exact differential-privacy accounting, immutable append-only audit trail, and electronic signatures. Launches inside hardware TEE if present. If Security.AttestTEE_v1 fails at any point, kernel issues immediate termination, executes deterministic best-effort zeroization hooks for owned memory regions, records zeroization evidence, and aborts. Full RNG auditing; produces signed provenance record.

### 0.W CLI and Usability Requirements
- Required commands (prioritized entrypoints): `umlos quickstart [template: classification|regression|pipeline|regulated]` (creates minimal ready-to-run manifest.yaml + project layout + example pipeline under current dir; runnable in <10 s), `umlos run manifest.yaml`, `umlos validate`, `umlos doctor`, `umlos replay <token>`, `umlos certificate verify`, `umlos migrate <legacy_path> [options] --output-dir .` (analyzes common training scripts/notebooks, generates runnable UML_OS manifest.yaml + IR; runs Contract.Validate_v1 on result), plus `job submit`/`export`/`infer`/`namespace init`/`daemon start`/`dataset register`/`import`/`audit export`/`ps/logs/kill/queue`. All CLI paths perform full Contract.Validate_v1 + manifest validation before any action.

### 0.X Training Certificate Contract
- Certificate contains: replay_token, Merkle-chained trace root, lineage hashes, final `state_fp`, functional_fp curve (+ functional_commitment when enabled), **exact cumulative differential-privacy budget (epsilon in binary64 if regulated)**, ir_hash, scheduler_assignment_hash, total_compute_fp (summed GPU/CPU seconds from audit), compliance_artifacts hash (regulated mode), manifest hashes, backend fingerprint, driver_hashes: map of used backend names to their verification hashes, daemon public key, operator contract hashes, electronic signatures (daemon ed25519 + optional HSM/company PKI), and (in `confidential`/`regulated` mode) the full remote attestation quote.
- Daemon signs certificate using namespace ed25519 private key; `regulated` mode additionally applies declared electronic signatures.
- `augment_metadata` for each symbolic stage (if present)

### 0.Y UML_Model_IR
Neutral declarative ML-ISA (Instruction Set Architecture) used by all Model/* system calls and drivers.
- Nodes: array of `{node_id: string, instr: string (from mandatory base set: MATMUL, CONV2D, LAYERNORM, ATTENTION, RESIDUAL_ADD, GELU, SOFTMAX, etc.), params: dict, inputs: array of node_id or 'input_data', shape_in/out: tuple(s)}`
- For parallel strategies nodes include optional sharding_spec resolved by driver into device placement.
- Execution: strict topological order (stable sort by node_id on ties).
- All presets expand to valid ML-ISA. Custom layers via RegisterCustom_v1 declare full instruction mapping.
- Drivers translate ML-ISA → native executable under Contract.Validate_v1 (E0 within declared backend/hardware equivalence class; CPU reference used for E1 semantic checks).
- Canonical CBOR serialization (fixed field order) for all hashing.

### 0.Z Logging Contract (fulfills Block V.A)
`UML_OS.IO.WriteTape_v1` serves as the canonical `LogIteration` operator. Every iteration appends a structured trace record containing all required V.B fields (`t`, `state`, `action`, `loss_total`, `grad_norm`, `state_fp`, `functional_fp`, `replay_token`/fingerprint, etc.).

---

## 2) System Model

### I.A Persistent State
- `theta`
- `state ∈ {S_INIT, S_TRAINING, S_EVALUATING, S_TERMINATED}`
- `t`
- `loss_hist`
- `data_cursors: map<string, (epoch: int, global_index: int)>` (key = dataset_key).
- `rng_master_state` + offsets
- `tape_state`

### I.B Inputs and Hyperparameters
All immutable inputs and hyperparameters are declared in the YAML manifest (see `0.Q Global Manifest Additions`). Key declared items: `global_batch_size`, optimizer config, `pipeline_stages`, `security.{attestation_required, differential_privacy}`, `compute_dtype`, and related runtime policy fields.

### I.C Constraints and Feasible Set
Unconstrained optimization problem. All runtime contracts (driver determinism, purity, RNG consumption, ordering) are enforced by `UML_OS.Contract.Validate_v1` and backend driver verification.

### I.D Transient Variables
- `batch`, `logits`, `L_tot`, `action`, `grads`, `noisy_grads`, `grad_norm`, `eval_result`, `outputs`
- Transients are iteration-local and cannot be referenced across iterations unless promoted into persistent state.

### I.E Invariants and Assertions
- Finite tensors
- Deterministic ordering
- Contract checks mandatory

### Architecture Overview (Document Wiring)
- Core execution specs: `Data-NextBatch.md`, `ModelIR-Executor.md`, `TMMU-Allocation.md`, `DifferentialPrivacy-Apply.md`.
- Interface and type contracts: `API-Interfaces.md`, `Data-Structures.md`, `Config-Schema.md`.
- Reliability and observability contracts: `Error-Codes.md`, `Trace-Sidecar.md`, `Checkpoint-Schema.md`, `Replay-Determinism.md`.
- Delivery and compliance contracts: `Backend-Adapter-Guide.md`, `Security-Compliance-Profile.md`, `Dependency-Lock-Policy.md`, `Deployment-Runbook.md`.
- Planning and execution governance: `Implementation-Roadmap.md`, `Code-Generation-Mapping.md`, `Test-Plan.md`, `Performance-Plan.md`.
- Lifecycle and governance extensions: `Experiment-Tracking.md`, `Model-Registry.md`, `Monitoring-Policy.md`, `Evaluation-Harness.md`, `Data-Lineage.md`, `Pipeline-Orchestrator.md`, `Execution-Certificate.md`.
- Coding acceleration contracts: `Reference-Implementations.md`, `Test-Vectors-Catalog.md`, `Repo-Layout-and-Interfaces.md`.
- Wiring invariant: all operator names referenced across documents must be fully qualified and versioned. Shared operators may be imported by reference from dedicated contract documents (for example `UML_OS.Error.Emit_v1` in `Error-Codes.md`).

---

## 3) Initialization

1. `t <- 0`
2. `persistent_state <- UML_OS.OS.Bootstrap_v1(manifest)`
3. `canonical_manifest <- UML_OS.Data.Manifest_v1(manifest)` then `UML_OS.Data.ValidateManifest_v1(canonical_manifest)`
4. `active_namespace <- UML_OS.OS.NamespaceEnter_v1(namespace_path)`
5. `driver <- UML_OS.Backend.LoadDriver_v1(manifest.backend)` then `dist_state <- UML_OS.Distributed.Setup_v1(...)`
6. Initialize `theta` deterministically from manifest/seed contract
7. Initialize `state <- S_TRAINING`, `loss_hist`, `data_cursors`, tape, fingerprints, and RNG offsets
8. Run `UML_OS.Contract.Validate_v1(...)` before entering the main procedure loop

---

## 4) Operator Manifest

Active operators (exact wiring table):
- `UML_OS.OS.Bootstrap_v1`
- `UML_OS.OS.ResolvePath_v1`
- `UML_OS.OS.NamespaceEnter_v1`
- `UML_OS.Data.Manifest_v1`
- `UML_OS.Data.ValidateManifest_v1`
- `UML_OS.Data.NextBatch_v2`
- `UML_OS.Data.RegisterDataset_v1`
- `UML_OS.Data.ImportAndRegister_v1`
- `UML_OS.Model.Forward_v2`
- `UML_OS.Model.ExpandPreset_v1`
- `UML_OS.Model.ApplyFineTune_v1`
- `UML_OS.Objective.TotalLoss_v1`
- `UML_OS.Update_v1`
- `UML_OS.Module.RegisterCustom_v1`
- `UML_OS.Policy.Evaluate_v1`
- `UML_OS.Contract.Validate_v1`
- `UML_OS.IO.WriteTape_v1`
- `UML_OS.IO.SaveCheckpoint_v1`
- `UML_OS.IO.WriteTrainingCertificate_v1`
- `UML_OS.State.Journal_v1`
- `UML_OS.Termination.Check_v1`
- `UML_OS.StateFingerprint_v1`
- `UML_OS.Fingerprint.Functional_v1`
- `UML_OS.Error.Emit_v1`
- `UML_OS.Distributed.Setup_v1`
- `UML_OS.Evaluation.Run_v1`
- `UML_OS.Security.AttestTEE_v1`
- `UML_OS.Verifiable.CommitFunctional_v1`
- `UML_OS.DifferentialPrivacy.Apply_v3`
- `UML_OS.Backend.LoadDriver_v1`
- `UML_OS.Pipeline.Dispatch_v1`
- `UML_OS.Inference.RunBatch_v1`
- `UML_OS.Model.Backward_v1`
- `UML_OS.Symbolic.Augment_v1`
- `UML_OS.Security.VerifyCertificate_v1`
- `UML_OS.Transition.SwitchState_v1`

---

## 5) Operator Definitions

External operator reference: `UML_OS.Error.Emit_v1` is defined normatively in `Error-Codes.md` and imported by reference.

**Kernel System Call Interface**  
All system calls follow the EQC template and may be invoked **only** through the VI kernel procedure in section 6. No user code may call backend primitives, torch.add, jax ops, or any library function directly. Every tensor allocation, forward/backward step, or state mutation must be a syscall. Violations trigger CONTRACT_VIOLATION abort.

**Operator:** `UML_OS.OS.Bootstrap_v1`  
**Category:** Init  
**Signature:** `(manifest -> persistent_state)`  
**Purity class:** STATEFUL  
**Determinism:** deterministic  
**Definition:** PRNG master seeded from fixed manifest hash (single Philox + fixed offsets; no draws); parameter init; buffer allocation; data manifest load + ValidateManifest_v1 + ImportAndRegister_v1 if needed; ApplyFineTune_v1 if declared; ExpandPreset_v1 if preset set; Backend.LoadDriver_v1(manifest.backend); Distributed.Setup_v1; policy load; namespace enter; Security.AttestTEE_v1 (confidential mode only); resolve and merge `manifest_inheritance` if declared; apply `profile`-specific defaults and materialize default pipeline_stages if absent per 0.Q profile rule; resolve and merge manifest_inheritance before pipeline materialization; set `hardware_affinity` pinning if specified; if environment.requirements_hash declared and execution_mode != "local": compute current environment BLAKE3 hash from pinned runtime manifest and abort with CONTRACT_VIOLATION on mismatch; in local mode emit deterministic warning record only (no abort); if execution_mode == "local" and manifest.legacy_import_path is present: perform best-effort structural analysis of standard framework training code (PyTorch nn.Module/DataLoader loops, Lightning/HF/JAX equivalents) to emit equivalent UML_Model_IR DAG, pipeline_stages, and minimal manifest; register converted components via RegisterCustom_v1 and ExpandPreset_v1; write conversion report to tape.  
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

**Operator:** `UML_OS.Data.NextBatch_v2`  
**Category:** Data  
**Signature:** `(dataset_key, world_size, rank -> batch, data_cursor')`  
**Purity class:** STATEFUL  
**Determinism:** deterministic with declared RNG  
**Definition:** Uses manifest.datasets[dataset_key]. Implements memory-efficient deterministic global sampling independent of dataset size. Epoch permutation seeded by `BLAKE3(CBOR(["nextbatch_epoch_seed_v1", manifest_hash, uint64(epoch)]))` using Philox4x32-10. Partition into blocks of size manifest.data.sampler_block_size (default 1<<20). Materialize only the block permutation list (size N/B, always ≪ dataset size); within each block compute intra-block positions via the bijective mapping specified in `Data-NextBatch.md` (`SeededIntraBlockMap_v1`) with explicit short-tail handling. For any global position p compute originating sample index in O(1) per sample after block list is built. Form global batches sequentially from the virtual sequence; split into contiguous rank-ordered shards. Guarantees identical global batch sequence across world_size values; update dynamics are E0 only within fixed distributed configuration and E1 across compatible re-shards. Eval and infer stages always use strict ascending original index order (no shuffle). Updates only data_cursors[dataset_key].  
**Preconditions / Postconditions:** `global_batch_size % world_size == 0`.  
**Edge cases:** world_size=1, final batch boundary.  
**Numerical considerations:** preprocessing stable in binary64 for reductions.  
**Ordering/tie handling:** ascending global index.  
**Failure behavior:** abort on invalid shard/batch.  
**Dependencies:** 0.R.

**Operator:** `UML_OS.Model.ExpandPreset_v1`  
**Category:** Model  
**Signature:** `(model.preset, preset_params, fine_tune -> uml_model_ir_dag)`  
**Purity class:** PURE  
**Determinism:** deterministic  
**Definition:** expands known preset table into UML_Model_IR DAG; inserts LoRA adapters deterministically when configured.  
**Preconditions / Postconditions:** preset exists.  
**Edge cases:** unknown preset/target module.  
**Numerical considerations:** no RNG.  
**Ordering/tie handling:** registration order of layers.  
**Failure behavior:** abort.  
**Dependencies:** 0.Q model fields.

**Operator:** `UML_OS.Model.ApplyFineTune_v1`  
**Category:** Model  
**Signature:** `(theta, fine_tune_cfg, uml_model_ir_dag -> theta')`  
**Purity class:** STATEFUL  
**Determinism:** deterministic  
**Definition:** applies full or LoRA fine-tune wiring/checkpoint loading on UML_Model_IR DAG.  
**Preconditions / Postconditions:** checkpoint hash must match manifest.  
**Edge cases:** missing checkpoint, incompatible layer shapes.  
**Numerical considerations:** deterministic load/merge order.  
**Ordering/tie handling:** parameter registration order.  
**Failure behavior:** abort.  
**Dependencies:** checkpoint manifest.

**Operator:** `UML_OS.Model.Forward_v2`  
**Category:** Model  
**Signature:** `(theta, batch, uml_model_ir_dag -> logits)`  
**Purity class:** PURE  
**Determinism:** deterministic  
**Definition:** dispatches to active backend driver; executes UML_Model_IR DAG (custom layers via registry); all reductions in binary64 with ascending-index order.  
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
**Definition:** if optimizer==\"adamw\": `m_t = beta1*m_{t-1} + (1-beta1)*g`; `v_t = beta2*v_{t-1} + (1-beta2)*g**2`; `m_hat = m_t/(1-beta1^t)`; `v_hat = v_t/(1-beta2^t)`; `theta = theta - lr*(m_hat/(sqrt(v_hat)+eps) + weight_decay*theta)`. Optimizer moments, bias corrections, and parameter updates performed in manifest.compute_dtype; gradient norm for clipping and all scalar reductions computed in binary64 (ascending registration order); weight_decay applied after the adaptive step (standard decoupled AdamW). Other optimizers follow analogous deterministic updates in the same dtype policy.  
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
**Definition:** loads user-declared custom operators from manifest and verifies declared purity, RNG consumption, contract hash, and UML_Model_IR DAG mapping before registration.  
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
**Signature:** `(theta, dataset_key, metrics -> eval_result)`  
**Purity class:** STATEFUL  
**Determinism:** deterministic  
**Definition:** computes declared metrics at configured frequency; uses manifest.datasets[dataset_key]; deterministic full pass in ascending original index order (no shuffle; fixed seed=0 if any ordering needed).  
**Preconditions / Postconditions:** val split exists if configured.  
**Edge cases:** empty val split.  
**Numerical considerations:** binary64 reductions for metrics.  
**Ordering/tie handling:** ascending index over val data.  
**Failure behavior:** abort on missing eval split.  
**Dependencies:** `evaluation` manifest.

**Operator:** `UML_OS.Inference.RunBatch_v1`  
**Category:** Inference  
**Signature:** `(theta, dataset_key -> outputs)`  
**Purity class:** STATEFUL  
**Determinism:** deterministic  
**Definition:** uses manifest.datasets[dataset_key]; dispatches driver for inference (full pass or per-batch as configured); writes outputs and fingerprint material.  
**Preconditions / Postconditions:** backend loaded and batch schema valid.  
**Edge cases:** empty batch.  
**Numerical considerations:** binary64 for critical reductions/fingerprint path.  
**Ordering/tie handling:** ascending sample index order.  
**Failure behavior:** abort on backend/runtime mismatch.  
**Dependencies:** Backend.LoadDriver_v1.

**Operator:** `UML_OS.Model.Backward_v1`
**Category:** Model
**Signature:** `(L_tot, theta, ir_graph -> grads, grad_norm)`
**Purity class:** STATEFUL
**Determinism:** deterministic
**Definition:** Compute partial derivatives following ir_graph in reverse topological order. For each instruction the driver executes the corresponding gradient kernel; if the backend instruction is non-deterministic, driver falls back to binary64 CPU reference path. Global gradient norm computed with Kahan summation in binary64 (ascending index). If DP is disabled and `grad_clip_norm` is declared, apply `g = g * min(1, clip_norm / (norm + EPS_EQ))`; if DP is enabled, return unclipped gradients and perform clipping only inside `UML_OS.DifferentialPrivacy.Apply_v3`.
**Preconditions / Postconditions:** Forward_v2 completed on same ir_graph; L_tot finite; grads returned in exact theta registration order.
**Edge cases:** single micro-batch, world_size=1.
**Numerical considerations:** Critical layers (embeddings, norms) accumulated in binary64 before cast to compute_dtype.
**Ordering/tie handling:** ascending index.
**Failure behavior:** abort on INF_GRADIENT or NAN_GRADIENT per 0.K.
**Dependencies:** loaded driver, ir_graph from Bootstrap.

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
**Definition:** Loads and verifies backend driver contract (including binary/manifest hash check against any regulated-mode registry); binds dispatch table for Forward/Update/Distributed/Backward; runs minimal ReproducibilityTest subset on load (E0 on tiny graphs); aborts with `BACKEND_CONTRACT_VIOLATION` on failure.  
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
**Signature:** `(probe_outputs_bytes, functional_fp, security.functional_commitment -> commitment?)`  
**Purity class:** PURE  
**Determinism:** deterministic  
**Definition:** if enabled, compute `functional_commitment = SHA-256(CBOR(["functional_commitment_v1", probe_outputs_bytes, functional_fp]))` and attach to trace/certificate.  
**Preconditions / Postconditions:** functional_fp available.  
**Edge cases:** disabled path returns no commitment.  
**Numerical considerations:** N/A.  
**Ordering/tie handling:** canonical byte order.  
**Failure behavior:** abort on digest mismatch.  
**Dependencies:** `security.functional_commitment`.

**Operator:** `UML_OS.Security.VerifyCertificate_v1`
**Category:** Security
**Signature:** `(certificate_path, expected_replay_token? -> valid: bool, report: dict)`
**Purity class:** IO
**Determinism:** deterministic
**Definition:** Loads signed CBOR; verifies daemon/HSM/electronic signatures, Merkle trace root, all pipeline lineage hashes, state_fp/functional_fp consistency (within EPS_EQ where applicable), privacy budget <= target (if present), and attestation quote (if confidential/regulated). Returns structured report with per-section pass/fail.
**Preconditions / Postconditions:** certificate readable and schema-valid.
**Edge cases:** missing quote, signature mismatch, token mismatch.
**Numerical considerations:** binary64 EPS_EQ for fingerprint checks.
**Ordering/tie handling:** N/A.
**Failure behavior:** returns false + detailed report (non-abort).
**Dependencies:** 0.X.

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

**Operator:** `UML_OS.State.Journal_v1`
**Category:** IO
**Signature:** `(event -> journal_state')`
**Purity class:** IO
**Determinism:** deterministic
**Definition:** Write-ahead log: append cryptographically chained record (`BLAKE3(CBOR(["journal_link_v1", previous_hash, event, uint64(t)]))`) to journal before any state mutation is visible.
**Preconditions / Postconditions:** journal open; hash chain preserved.
**Failure behavior:** abort on write failure.

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


**Operator:** `UML_OS.DifferentialPrivacy.Apply_v3`  
**Category:** Security  
**Signature:** `(gradients, security.differential_privacy -> noisy_gradients, updated_budget)`  
**Purity class:** STATEFUL  
**Determinism:** deterministic  
**Definition:** If enabled (forced true in regulated mode), first clips per-sample gradients to `manifest.grad_clip_norm` (default 1.0 if unset) in binary64, averages with ascending global index order, then adds isotropic Gaussian noise ~ N(0, σ²) using deterministic moments accountant (δ=1e-5 fixed, exact composition per standard reference implementation). RNG for noise drawn from declared stream. Cumulative privacy loss tracked exactly in binary64. Aborts with PRIVACY_BUDGET_EXCEEDED if cumulative ε exceeds target_epsilon. Noise applied to averaged gradients before Update_v1.
**Preconditions / Postconditions:** called only on raw gradients before any optimizer step; `target_epsilon` declared and remaining budget sufficient.  
**Edge cases:** epsilon=0, zero gradients.  
**Numerical considerations:** noise scale computed exactly in binary64.  
**Ordering/tie handling:** N/A.  
**Failure behavior:** abort with `PRIVACY_BUDGET_EXCEEDED`.  
**Dependencies:** regulated mode, 0.Q security fields.

**Operator:** `UML_OS.Symbolic.Augment_v1`
**Category:** Symbolic
**Signature:** `(theta_snapshot, dataset_subset, augment_config -> theta', augment_metadata)`
**Purity class:** STATEFUL
**Determinism:** deterministic (with declared RNG consumption)
**Definition:** Applies sequence of deterministic non-learning transforms declared in augment_config (array of objects `{transform_type: "prune_magnitude" | "quantize_int8" | "sparsify" | "custom", params: dict}`). Operates on frozen theta_snapshot using subset from dataset_key. All operations deterministic (no RNG unless explicitly declared in custom); critical reductions in binary64. Returns theta' and augment_metadata (applied transforms list, activation statistics hashes).
**Preconditions / Postconditions:** stage type "augment"; previous stage completed; `augment_config` declared in stage manifest.
**Edge cases:** empty subset, no rules declared.
**Numerical considerations:** deterministic reductions and ordering in binary64.
**Ordering/tie handling:** rule application order from manifest.
**Failure behavior:** abort per 0.K on contract violation.
**Dependencies:** stage type "augment", manifest `augment_config`.


---

## 6) Procedure

```text
1. UML_OS.OS.Bootstrap_v1(...)
2. UML_OS.OS.NamespaceEnter_v1(job_id)
3. UML_OS.Backend.LoadDriver_v1(manifest.backend)
4. UML_OS.Pipeline.Dispatch_v1(...)  // resolves initial stage
5. state <- UML_OS.Transition.SwitchState_v1(S_INIT, current_stage.type)

Loop until Pipeline.Dispatch_v1 returns termination:
- UML_OS.Termination.Check_v1(...) (scoped to current stage)
- t <- t + 1
- UML_OS.Contract.Validate_v1(...)
- if current_stage.type == "augment":
  state <- UML_OS.Transition.SwitchState_v1(state, "train")
  theta, augment_metadata <- UML_OS.Symbolic.Augment_v1(...)
- else:
  dataset_key <- current_stage.dataset_key or default-per-type
  if current_stage.type == "train":
    state <- UML_OS.Transition.SwitchState_v1(state, "train")
    batch <- UML_OS.Data.NextBatch_v2(dataset_key, ...)
    logits <- UML_OS.Model.Forward_v2(...)
    L_tot <- UML_OS.Objective.TotalLoss_v1(...)
    action <- UML_OS.Policy.Evaluate_v1(...)
    if action == "optimize":
      grads = UML_OS.Model.Backward_v1(L_tot, theta)  # unclipped when DP is enabled
      if manifest.execution_mode == "regulated": noisy_grads, budget <- UML_OS.DifferentialPrivacy.Apply_v3(grads)
      theta <- UML_OS.Update_v1(noisy_grads or grads, ...)
    else if action == "eval" or current_stage.type == "eval":
      state <- UML_OS.Transition.SwitchState_v1(state, "eval")
      UML_OS.Evaluation.Run_v1(theta, dataset_key, ...)
    else if action == "infer":
      state <- UML_OS.Transition.SwitchState_v1(state, "infer")
      UML_OS.Inference.RunBatch_v1(theta, dataset_key)
  else if current_stage.type == "eval":
    state <- UML_OS.Transition.SwitchState_v1(state, "eval")
    UML_OS.Evaluation.Run_v1(theta, dataset_key, ...)
  else if current_stage.type == "infer":
    state <- UML_OS.Transition.SwitchState_v1(state, "infer")
    UML_OS.Inference.RunBatch_v1(theta, dataset_key)
- if checkpoint due: UML_OS.IO.SaveCheckpoint_v1(...)
- if fingerprint due: StateFingerprint_v1, Fingerprint.Functional_v1, Verifiable.CommitFunctional_v1 (if enabled)
- UML_OS.IO.WriteTape_v1(...) (includes stage transition and usage record)
- UML_OS.State.Journal_v1(...)
- current_stage = UML_OS.Pipeline.Dispatch_v1(...)  // advance or terminate

On full termination:
- state <- UML_OS.Transition.SwitchState_v1(state, "terminate")
- UML_OS.Security.VerifyCertificate_v1(output_certificate_path)  // self-verify before signing final certificate
- UML_OS.IO.WriteTrainingCertificate_v1(...)
```

---

## 7) Trace & Metrics

### Logging rule
Each iteration must emit one canonical trace record via `UML_OS.IO.WriteTape_v1` with required V.B fields for the active task type.

### Trace schema (minimum required)
- `run_header`: metadata, hashes, replay_token, task_type, world_size, backend_hash
- `iter`: `t, stage_id, operator_id, operator_seq, rank, status, loss_total?, grad_norm?, state_fp?, functional_fp?, rng_offset_before?, rng_offset_after?, state?, action?`
- `run_end`: status, final hashes, final fingerprints

### Metric schema
- `loss_total`, `grad_norm`, `functional_fp`, `cumulative_epsilon` (regulated mode)

### Comparability guarantee
Two implementations/runs are comparable if they share identical trace schema, metric schema, replay_token definition, objective preorder, and constraint policy (E0 for bitwise, E1 for metric).
- `state`/`action` are mandatory only for RL task types; optional otherwise.

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
- `loss_hist`, `data_cursors`
- RNG master state + offsets
- `policy_hash`, `env_manifest_hash`, `replay_token`, `backend_hash`
- latest `state_fp`, `functional_fp`, optional `functional_commitment`
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
