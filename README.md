# Universal Machine Learning Operating System (UML_OS) v3.10-OS

**Algorithm:** Deterministic training OS kernel with operator contracts and namespace isolation.  
**Purpose (1 sentence):** Execute machine-learning training and lifecycle operations under formal reproducibility, namespace isolation, and deterministic runtime contracts.  
**Spec Version:** UML_OS-v3.10-OS | 2026-02-17 | Authors: Olejar Damir  
**Domain / Problem Class:** Reproducible training with optional online symbolic prototype augmentation (default workload).

---

## 0 · Header, Provenance, and Global Semantics

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
- Single master stream with fixed sub-stream offsets:
  - `init`
  - `cluster`
  - `misc`
- Replay token:
  - `replay_token = SHA-256(spec_version || policy_hash || env_manifest_hash || seed)`

### 0.C Numeric Policy
- Core arithmetic for loss/metric/termination: IEEE-754 binary64
- Parameters may be binary32; all loss reductions remain binary64
- Rounding mode: round-to-nearest ties-to-even
- Fast-math: forbidden
- Constants:
  - `EPS_EQ = 1e-10`
  - `EPS_DENOM = 1e-12`
  - `EPS_PROB = 1e-15`
- Clamps:
  - `exp` argument to `[-80, 80]`
  - denominator `max(den, EPS_DENOM)`
  - probabilities clamped to `[EPS_PROB, 1]`, then renormalized
- All reductions: deterministic ascending-index order

### 0.D Ordering and Tie-Break Policy
- Index base: `0-based`
- Stable sort required
- Ties: lowest index wins
- Fixed action order: `["optimize", "probe", "switch", "augment"]`

### 0.E Parallel, Concurrency, and Reduction Policy
- Parallel reductions: fixed 256-element chunks, performed in ascending global index order (ranks sorted 0..world_size-1).
- Rank aggregation: ascending rank order.
- When world_size > 1, every reduction uses deterministic collective primitives (see 0.R).

### 0.F Environment and Dependency Policy
- Pinned runtime:
  - Python 3.12
  - NumPy 2.1
  - PyTorch 2.4 (CPU reference build; CUDA 12.1 build permitted when hardware present)
- At startup: `torch.use_deterministic_algorithms(True)`, `torch.backends.cudnn.deterministic = True`, `torch.backends.cudnn.benchmark = False`, `torch.set_float32_matmul_precision('highest')`.
- If `distributed_mode != none`, world_size may be any positive integer; no power-of-2 restriction.

### 0.G Operator Manifest
- Removed from manifest surface:
  - `UML_OS.Random.InitializeParameters_v1`
  - `UML_OS.Init.LoadPolicy_v1`
  - `UML_OS.Init.InitializeBuffers_v1`
  - all `UML_OS.Serving.*`
  - `UML_OS.Model.MultiHeadAttention_v1`
- Added:
  - `UML_OS.Data.ValidateManifest_v1`

Active operators:
- `UML_OS.OS.Bootstrap_v1`
- `UML_OS.OS.ResolvePath_v1`
- `UML_OS.OS.NamespaceEnter_v1`
- `UML_OS.OS.QuotaEnforce_v1`
- `UML_OS.Data.Manifest_v1`
- `UML_OS.Data.ValidateManifest_v1`
- `UML_OS.Data.NextBatch_v1`
- `UML_OS.Data.StreamingLoader_v1`
- `UML_OS.Buffer.ShardedDiskRing_v1`
- `UML_OS.Model.Encode_v1`
- `UML_OS.Model.Forward_v2`
- `UML_OS.Model.Decode_v1`
- `UML_OS.Objective.TotalLoss_v1`
- `UML_OS.Update_v1`
- `UML_OS.Symbolic.DifferentiableEval_v1`
- `UML_OS.Module.RegisterCustom_v1`
- `UML_OS.Policy.Evaluate_v1`
- `UML_OS.Transition.SwitchState_v1`
- `UML_OS.Contract.Validate_v1`
- `UML_OS.IO.WriteTape_v1`
- `UML_OS.Logging.LogIteration_v1`
- `UML_OS.Termination.Check_v1`
- `UML_OS.StateFingerprint_v1`
- `UML_OS.Fingerprint.Functional_v1`
- `UML_OS.Error.Emit_v1`
- Symbolic operators are loaded only when `enable_symbolic=true` and `workload=hybrid_symbolic`.

### 0.H Namespacing and Packaging
- Fully-qualified names: `UML_OS.<Category>.<Name>_v#`
- Sidecar mapping required: operator -> module/function

### 0.I Outputs and Metric Schema
- Outputs:
  - `theta_final`
  - `trace`
  - `checkpoint`
  - `tape_digest`
- Minimum metric schema:
  - `loss_total`
  - `grad_norm`
  - `functional_fp`

### 0.J Spec Lifecycle Governance
- Reproducibility-breaking changes require MAJOR bump

### 0.K Failure and Error Semantics
- Global error model: abort-only
- Final failure record includes:
  - `t`
  - `failure_code`
  - `failure_operator`
  - `replay_token`
  - `rng_fingerprint_t`
  - `state_fp_t`

### 0.L Input/Data Provenance
- Dataset id/version/hashes required
- Parsing strictness required

### 0.M Declarative Configuration
- YAML config loading allowed
- Canonicalized into manifest before hashing

### 0.N Layered Operating-System Architecture
- Layer ordering:
  - Kernel (VI procedure + operator dispatch + contracts)
  - Driver (device collectives, I/O, deterministic primitives)
  - Runtime (pinned Python/NumPy/PyTorch)
  - Module (verified operator packages loaded from manifest)
  - Daemon (optional in `simple` and `standard` modes for single-node execution; mandatory in `strict` mode or when UML_OS_ROOT is shared or world_size > 1; single process per host): owns UML_OS_ROOT filesystem hierarchy; uses simple FIFO submission queue (atomic file locks); launches each job as isolated process; enforces per-namespace isolation of RNG state, data_cursor, checkpoints, and tapes; performs basic quota checks on storage and concurrent jobs only (no weighted fair-share CPU/GPU slicing).
  - Management (CLI entrypoints)
  - User (manifests only)
- UML_OS_ROOT filesystem (enforced by daemon and `Bootstrap_v1`):
  - `/datasets/<id-version-hash>/` (immutable, validated)
  - `/namespaces/<org>/<unit>/<project>/<experiment>/<job_id>/` (isolated: checkpoints, tapes, latent_buffer shards, rng_states, loss_hist; child namespaces inherit parent resource defaults and data access unless overridden)
  - `/jobs/queue/` (shared atomic queue files for cross-host visibility when shared FS used; each daemon polls/claims via file locks).
- Namespace path: `/org/unit/project/experiment/job_id` where `job_id = replay_token[0:8]`.
- Daemon scheduler: simple FIFO submission queue (atomic file locks); no weighted fair-share CPU/GPU slicing.

### 0.P Bootstrap
- Single entrypoint: `UML_OS.OS.Bootstrap_v1`
- Must also perform:
  - PRNG init
  - buffer allocation
  - data manifest load + validation
  - policy load
  - namespace enter

### 0.Q Global Manifest Additions
- `env_manifest_hash` must include:
  - `daemon_concurrency_max=16`
- `task_type` (`multiclass | binary | regression`)
- `alpha`, `lambda_rec`, `lambda_KL`, `lambda_OT`, `lambda_covz` (defaults in III.C when absent)
- `beta` (default `1.0`)
- `mode: "standard"`
- `workload: "pure_nn"` (default; only other value `"hybrid_symbolic"` when `enable_symbolic=true`)
- `enable_symbolic: false`
- `fingerprint_frequency: int` (overridden by mode unless explicitly set)
- `optimizer: {type: "AdamW" | "SGD" | "RMSprop", lr: float, betas: [float, float] (optional), weight_decay: float (default 0), momentum: float (default 0)}`
- `grad_clip_norm: float (default 1.0)`
- `preprocessing: {mode: "full" | "subsample_10M", ...}` (defaults to "full")
- `policy.rules` (array of `{\"cond\": \"...\", \"action\": \"...\", \"priority\": int}`; evaluated in declared order)
- `model_encode_op`, `forward_op`, `decode_op`, `augment_op` (fully-qualified operator names; default to listed `UML_OS.*_v#`)
- `datasets` array: each entry `{id, version, hash, split: train|val}`
- `custom_operators: array of {name, module_path, contract}` (optional)
- all other values previously in I.C (`probe_interval`, `sil_thresh`, etc.)

### 0.Q.1 Manifest Resource and Inheritance Schema
```yaml
mode: "standard"
workload: "pure_nn"
enable_symbolic: false
resources:
  requested_cpus: 4          # integer
  requested_gpus: 1          # integer
  allow_preempt: false
inheritance:
  parent_namespace: null     # or path string; inherits defaults
optimizer: {type: "AdamW", lr: 1e-3, weight_decay: 1e-2}
grad_clip_norm: 1.0
```

### 0.R Distributed and Multi-tenancy Policy
- Communication: PyTorch distributed (`gloo` CPU / `nccl` CUDA), ranks sorted ascending by `(hostname hash, rank)`.
- Data sharding: global permutation, then each rank processes slice `rank::world_size`.
- Global operations (clustering, fingerprint aggregation): rank 0 computes, others receive via `Broadcast`; RNG draws only on rank 0 where declared.
- `latent_buffer`: sharded by `sample_index % world_size`; `AllGather` only when required by operator (e.g., augment).
- Daemon enforces isolation, quotas, and schedules jobs across namespaces with fair-share priority based on manifest-declared resources.
- Checkpoint/restore restores exact global `data_cursor`, sharded `latent_buffer`, and synchronized RNG master state.
- In `simple` mode multi-node is forbidden; collectives use default PyTorch ordering.

### 0.S RNG Consumption Contract
- Every operator declaration in IV must contain exactly one line: `RNG consumption: exactly K draws from stream S`.
- `K` is fixed non-negative integer; `S` is one of `init`, `cluster`, `misc`, or `none`.
- Kernel records pre-call offset per sub-stream.
- After operator return, kernel computes delta-offset for every used stream.
- If any delta differs from declared `K`, emit failure record:
  - `failure_code = RNG_CONSUMPTION_VIOLATION`
  - include expected/actual deltas and `replay_token`
  - abort (0.K).
- Philox4x32-10 calls are strictly sequential within each sub-stream; no skipping or reseeding.
- All operators not explicitly listed with non-zero `K` must declare `RNG consumption: exactly 0 draws from stream none`.

### 0.T Execution Model
- The kernel (VI procedure) is the sole allowed execution path for C0/C1 conformance.
- Standard usage supplies only data manifest and configuration manifest; no external training-loop code is executed or required.

### 0.U Execution Contract
- The VI kernel procedure is the only permitted execution engine.
- All training occurs inside declared operators.
- External imperative training loops or ad-hoc calls outside VI steps are forbidden and cause `Contract.Validate_v1` failure with full counterexample.

### 0.V Operation Modes
- Manifest field: `mode: "simple" | "standard" | "strict"` (default: "standard").
- `simple`: daemon optional (single-process only; multi-node forbidden); RNG consumption auditing disabled (warnings logged only); `StateFingerprint_v1` and `Functional_v1` computed only at termination and every checkpoint; `Contract.Validate_v1` relaxed (warnings only, no abort on KL/covariance/probability edge cases); no latent_buffer allocation; workload forced to `pure_nn`; fingerprint_frequency fixed at 200.
- `standard`: daemon optional for single-node (mandatory if UML_OS_ROOT shared or world_size > 1); full RNG auditing; fingerprints every 50 steps or on any `action` change; full `Contract.Validate_v1`; fingerprint_frequency = 50; workload = `pure_nn` by default.
- `strict`: daemon mandatory for any shared-root or world_size > 1; full enforcement of all contracts, barriers, and collectives; fingerprint_frequency = 10; enables all optional features.
- All later sections reference these exact definitions for conditional behavior.

### 0.W CLI and Usability Requirements
- Required entrypoints (implemented in Management layer):
  - `uml_os init <project_path>` -> creates skeleton `data_manifest.yaml` and `config_manifest.yaml` with mode=standard, workload=pure_nn.
  - `uml_os train <config_manifest.yaml>` -> runs Bootstrap + VI kernel.
  - `uml_os replay <replay_token>` -> restores exact checkpoint and re-runs.
  - `uml_os export <checkpoint_dir>` -> produces uml_export/ (see VIII.C).
  - `uml_os daemon start [--root UML_OS_ROOT]` (for shared-root or strict mode).
- All CLI commands auto-validate manifest against operator contracts before launch.

---

## I · System Model

### I.A Persistent State
- `theta`
- `state in {S_P, S_PROTO}`
- `t`
- `loss_hist` (single history, tagged with state)
- `data_cursor = (epoch, index, permutation)`
- `rng_master_state` + sub-stream offsets
- `tape_state`

### I.B Declared Dimensions and Defaults
- Declared dimensions and defaults (overridable in manifest, used when absent):
  - `latent_dim p = 64`
  - `num_prototypes k_np = 32`
  - `batch_size B = 64`

### I.C Hyperparameters
- All tunable values are taken exclusively from the manifest (see 0.Q).
- No hard-coded defaults except loss lambdas in III.C.

### I.D Constraint Regime
- Unconstrained core optimization with runtime contracts

### I.E Invariants
- Finite tensors after each update
- Probability vectors sum to 1 within tolerance
- Gradient clipping bounds honored exactly
- Tape symbol validation enforced

### I.F Transient Variables
- Iteration-local only unless promoted to persistent state

---

## II · Initialization

1. `t <- 0`
2. `UML_OS.OS.Bootstrap_v1(...)`
3. Initialize `theta` deterministically from manifest-hash-derived bytes (no RNG draws)
4. Initialize `state <- S_P`
5. Initialize `loss_hist`, `latent_buffer`, `data_cursor`
6. Initialize tape and fingerprints

---

## III · Mathematical Components (default: pure_nn workload)

### III.A Supervised Loss
- `logits = nn_logits + beta * sym_pred` (beta from manifest)
- `task_type` from manifest (default: multiclass).
- multiclass: `L_sup = CrossEntropyLoss(logits, y)` (integer labels `0..C-1`, reduction in binary64, ascending-index order)
- binary: `L_sup = BCEWithLogitsLoss(logits, y)`
- regression: `L_sup = MSELoss(logits, y)`

### III.B Unsupervised Terms (applied only when `workload=hybrid_symbolic` and `enable_symbolic=true`)
- Preprocessing (once at bootstrap): per-feature standardization to mean 0, std 1 in binary64. Each rank computes local Welford sufficient statistics on its data shard in ascending global index order. Rank 0 aggregates via AllReduce, computes exact global μ and σ, broadcasts. Stats stored as `preprocess_stats.bin` and hashed into `env_manifest_hash`.
- `recon = UML_OS.Model.Decode_v1(z)` (clamped to preprocessing range)
- `L_rec = MSE(x_preprocessed, recon)`
- `L_KL` = diagonal Gaussian KL divergence
- `L_OT` = sliced Wasserstein-2 distance using exactly 4 projections generated once via Philox4x32-10 from seed `SHA-256("UML_OS_OT" || spec_version || latent_dim)`
- `L_covz = ||Cov(z) - I||_F^2`
- `L_aux = lambda_rec*L_rec + lambda_KL*L_KL + lambda_OT*L_OT + lambda_covz*L_covz` (lambdas from manifest)

### III.C Total Loss
- `L_tot = alpha * L_sup + L_aux` (binary64, fixed term order; alpha, lambdas from manifest; defaults `alpha=1.0`, `lambda_rec=1.0`, `lambda_KL=0.001`, `lambda_OT=0.01`, `lambda_covz=0.001`).

---

## IV · Operator Library

All operators must declare exactly:
- purity
- rng streams used
- deterministic order guarantee

### UML_OS.OS.Bootstrap_v1
- Purity: STATEFUL
- RNG consumption: exactly 0 draws from stream `none`
- Performs:
  - PRNG master seeded from fixed manifest hash (single Philox + fixed offsets; no draws)
  - parameter init
  - buffer allocation
  - data manifest load + `UML_OS.Data.ValidateManifest_v1`
  - policy load
  - namespace enter

### UML_OS.Policy.Evaluate_v1 (rule engine only)
- Purity: PURE
- RNG consumption: exactly 0 draws from stream `none`
- Loads `policy.rules` from manifest.
- Evaluates conditions in array order.
- Selects highest-priority matching rule; ties broken by lowest array index.
- Supported conditions: `sil_mean`, `loss_delta`, `grad_norm`, `resource_util`, `(t mod X)`, `state`.

### UML_OS.Model.Encode_v1
- Purity: STATEFUL
- RNG consumption: exactly 2 draws from stream `init`
- Two linear layers + reparameterization (`eps` from Box-Muller)

### UML_OS.Model.Forward_v2
- Purity: PURE
- RNG consumption: exactly 0 draws from stream `none`
- `proto_features = cosine_similarity(z, np.protos)`
- `weights = softmax(proto_features / 0.05)` (fixed temperature for routing stability)
- `sym_pred = sum(weights_i * DifferentiableEval_v1(np.protos_equation[i], z))`
- `logits = nn_logits + beta * sym_pred`

### UML_OS.Model.Decode_v1
- Purity: PURE
- RNG consumption: exactly 0 draws from stream `none`
- Returns reconstructed `x` from `z` using decoder parameters in `theta`; output clamped to match preprocessing range.

### UML_OS.Module.RegisterCustom_v1
- Purity: STATEFUL
- RNG consumption: exactly 0 draws from stream `none`
- Loads user-declared modules from manifest `custom_operators` array (each entry: fully-qualified name, module path, contract declaration `{purity, rng_consumption}`).
- Kernel verifies: (a) purity by double execution on fixed test input (must match exactly), (b) exact declared RNG delta, (c) contract hash.
- Registers only if all pass; otherwise aborts with `CONTRACT_VIOLATION`.

### UML_OS.Data.NextBatch_v1
- Purity: STATEFUL
- RNG consumption: exactly 1 draw from stream `misc`
- Global deterministic permutation from `manifest_hash + epoch`.
- Local shard: `indices[rank::world_size]`.
- Preprocess batch with stored normalization stats.

### UML_OS.IO.WriteTape_v1
- Purity: IO
- RNG consumption: exactly 0 draws from stream `none`
- `BLOCK_SIZE = 512`
- `max_events = 500_000`

### UML_OS.Contract.Validate_v1
- Purity: PURE
- RNG consumption: exactly 0 draws from stream `none`
- Runtime checks:
  - KL >= 0 within tolerance
  - covariance PSD checks
  - probability sums
  - gradient clipping bound
- On violation:
  - deterministic failure
  - minimal counterexample snapshot

### UML_OS.Update_v1
- Purity: STATEFUL
- RNG consumption: exactly 0 draws from stream `none`
- Computes gradients; clips by manifest `grad_clip_norm` using L2 norm in binary64; applies optimizer step using manifest `optimizer` config (AdamW/SGD/RMSprop with declared lr/betas/weight_decay/momentum); applies weight decay if declared.

### UML_OS.StateFingerprint_v1
- Purity: PURE
- RNG consumption: exactly 0 draws from stream `none`
- Lightweight incremental fingerprint: maintain running BLAKE3 hash (128-bit) across run.
- At each call: update with `SHA-256( t || state || data_cursor_hash || rng_offsets || np.protos_hash || equations_hash || loss_hist_last256_hash || theta_incremental_hash || opt_state_hash )`.
- `theta_incremental_hash` updated after every `Update_v1` as `BLAKE3(prev || serialized_param_deltas in registration order)`.
- Result stored as 32-byte `state_fp` (for trace and equivalence only).

### UML_OS.StateFingerprint_v1 and UML_OS.Fingerprint.Functional_v1
- Called only every `fingerprint_frequency` steps (per 0.V) or when action in {"augment","switch"} or at termination/checkpoint.

## V · Observability and Trace

### V.A Logging Rule
- one run_header
- one iter record per loop iteration
- one run_end

### V.B Minimal Trace Schema
- `run_header`: metadata, hashes, replay token, `task_type`, `world_size`, `backend_hash`
- `iter`: `t, state, action, loss_total, grad_norm, state_fp (only when computed), functional_fp (only when computed)`
- `run_end`: completion status, final hashes, functional fingerprint, `task_type`, `world_size`, `backend_hash`

Internal-only fields (not required in minimal public trace):
- policy entropy
- aux-loss breakdown

### V.C Functional Fingerprint Definition
**UML_OS.Fingerprint.Functional_v1**
- Purity: PURE
- RNG consumption: exactly 0 draws from stream `none`
- Canonical probe set:
  - first 1024 samples from dataset declared in manifest (validation split if present, otherwise training split)
  - strict ascending original-index order, no shuffle/permutation
  - if dataset size < 1024, cyclic repeat from start
- Dtype: binary64 for all forward-pass and loss computations
- Execution: inference mode (no gradients), current `theta`, current `np.protos`, current equation trees
- Output:
  - `functional_fp = SHA-256(probe_loss_bytes || probe_metric_bytes || task_type || spec_version)`
  - `probe_loss` and `probe_metric` are binary64 scalars (mean over probe set)
- Called only as required by VI; stored in trace and checkpoints

---

## VI · Algorithm Procedure

1. `UML_OS.OS.Bootstrap_v1(...)`
2. `UML_OS.Module.LoadDeclaredModules_v1(...)` (verifies contract hashes and registers operators from manifest)
3. `UML_OS.OS.NamespaceEnter_v1(job_id)`
4. loop until termination:
   - `UML_OS.Termination.Check_v1(...)`
   - `t += 1`
   - `UML_OS.OS.QuotaEnforce_v1(...)`
   - `batch <- UML_OS.Data.NextBatch_v1(...)`
   - `z <- UML_OS.Model.Encode_v1(...)`
   - `recon <- UML_OS.Model.Decode_v1(...)`
   - `(logits, sym) <- UML_OS.Model.Forward_v2(...)`
   - `L_tot <- UML_OS.Objective.TotalLoss_v1(...)`
   - `UML_OS.Contract.Validate_v1(...)` (strictness per mode 0.V)
   - `action <- UML_OS.Policy.Evaluate_v1(...)`
   - dispatch using manifest-declared operator names
   - `current_state_fp <- UML_OS.StateFingerprint_v1(...)` only if required by mode/frequency or action in {"augment","switch"}
   - `current_functional_fp <- UML_OS.Fingerprint.Functional_v1(...)` only if required by mode/frequency or action in {"augment","switch"}
   - if world_size > 1: deterministic barrier
   - `UML_OS.IO.WriteTape_v1(...)`
   - `UML_OS.Logging.LogIteration_v1(...)`

---

## VIII · Checkpoint and Restore

### VIII.A Checkpoint Contents
- include:
  - full manifest copy (canonicalized)
  - loaded module contract hashes
  - `theta`
  - optimizer state
  - single `loss_hist`
  - `latent_buffer`
  - `data_cursor`
  - RNG master + offsets
  - hashes (`policy_hash`, `env_manifest_hash`, `replay_token`, `backend_hash`)
  - `functional_fp`

### VIII.B Serialization
- protobuf with `deterministic=True`

### VIII.C Post-termination Export
On normal termination: kernel writes deterministic `uml_export/` directory in namespace root containing:
- `theta.pt` (PyTorch state_dict, deterministic serialization)
- `protos.npy` (centroids, binary64)
- `equations.json` (array of ASTs, one per prototype; canonical string + node list)
- `inference_manifest.yaml` (minimal manifest + preprocess_stats.bin hash for inference replay)
All paths and filenames fixed; content order by ascending prototype index.

---

## IX · Conformance and Change Control

### IX.A Conformance Levels
- `C0`: spec-complete implementation
- `C1`: R1 statistical replay conformance

### IX.B C1 Requirements
- identical:
  - `policy_hash`
  - `env_manifest_hash`
  - `replay_token`
  - `functional_fp`
- loss curve must match declared tolerance envelope over 10 seeds

### IX.C Change Control
- any reproducibility-breaking change requires MAJOR bump
- Required equivalence target: **E1 (metric-equivalent)**
- Required golden trace dataset: any manifest-declared dataset that matches declared `task_type`, dimension constraints, and produces metric-equivalent trace within tolerance envelope over 10 seeds.
- E1 requires matching:
  - `replay_token`
  - `state_fp` sequence
  - `functional_fp` curve
  within the declared tolerance envelope over 10 seeds.

---

## X · Compatibility Boundary

The following are normative compatibility boundaries for UML_OS-v3.10-OS:
1. Declarative manifests only. Sole entrypoints are the required CLI commands (0.W). The VI kernel procedure is the sole execution path. No external training-loop code, user callbacks, imperative mutations, or Python control flow outside declared operators is executed or permitted. Any attempt causes `Contract.Validate_v1` failure (severity per mode) with full counterexample and abort.

2. Daemon is optional in simple/standard modes for single-node; mandatory in strict mode or shared-root/multi-node. All job submission and isolation routes exclusively through CLI + daemon when present.

3. Deterministic distributed collectives and declared RNG locality.
- Collective ordering, rank ordering, and rank-0-only RNG behavior for declared operators are mandatory.
- Implementations that use flexible or user-defined distributed graphs without these fixed contracts are non-conformant.

4. Manifest-driven operator registry and policy dispatch.
- Operator selection, module loading, and policy rules must come from the manifest and verified contract hashes.
- User callbacks or ad-hoc Python control flow for core dispatch are non-conformant.

5. Operator-level reproducibility auditing.
- Per-operator RNG consumption accounting, `StateFingerprint_v1`, functional fingerprint generation, and canonical manifest-bound checkpoint restore are required.
- Logging-only or seed-only reproducibility approaches are insufficient for C0/C1 conformance.

This boundary defines UML_OS as a self-contained training operating system kernel with declarative user input and contract-enforced execution.
