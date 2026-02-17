# Universal Machine Learning Operating System (UML_OS) v3.8-OS

**Algorithm:** Deterministic ML training OS kernel with integrated symbolic prototype augmentation.  
**Purpose (1 sentence):** Execute machine-learning training and lifecycle operations under formal reproducibility, namespace isolation, and deterministic runtime contracts.  
**Spec Version:** UML_OS-v3.8-OS | 2026-02-17 | Authors: Olejar Damir  
**Domain / Problem Class:** Reproducible hybrid training with symbolic prototypes.

---

## 0 · Header, Provenance, and Global Semantics

### 0.A Objective Semantics
- Optimization sense: `MINIMIZE`
- Objective type: `Scalar`
- Primary comparison rule: `a ≼ b ⇔ a ≤ b + EPS_EQ`
- `EPS_EQ = 1e-10` (float64)
- Invalid objective policy:
  - NaN/±Inf objective is ranked as `+Inf`
  - mark `INVALID_OBJECTIVE`
  - do not apply update
  - emit deterministic failure record
  - abort (0.K)

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
- `UML_OS.Module.ActivateNonParamModule_v1`
- `UML_OS.Symbolic.DifferentiableEval_v1`
- `UML_OS.Symbolic.EquationUpdate_v2`
- `UML_OS.Policy.Evaluate_v1`
- `UML_OS.Transition.SwitchState_v1`
- `UML_OS.Contract.Validate_v1`
- `UML_OS.IO.WriteTape_v1`
- `UML_OS.Logging.LogIteration_v1`
- `UML_OS.Termination.Check_v1`
- `UML_OS.StateFingerprint_v1`
- `UML_OS.Fingerprint.Functional_v1`
- `UML_OS.Error.Emit_v1`

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
  - `sil_mean`
  - `resource_util`
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
  - Daemon (mandatory when world_size > 1 or multiple jobs share UML_OS_ROOT; owns filesystem, enforces per-namespace isolation, quotas, and job scheduling)
  - Management (CLI entrypoints)
  - User (manifests only)
- UML_OS_ROOT filesystem (enforced by daemon and `Bootstrap_v1`):
  - `/datasets/<id-version-hash>/` (immutable, validated)
  - `/namespaces/<org>/<unit>/<project>/<experiment>/<job_id>/` (isolated: checkpoints, tapes, latent_buffer shards, rng_states, loss_hist)
  - child namespaces inherit parent defaults and data access unless overridden in manifest
- Namespace path: `/org/unit/project/experiment/job_id` where `job_id = replay_token[0:8]`.

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
- `policy.rules` (array of `{\"cond\": \"...\", \"action\": \"...\", \"priority\": int}`; evaluated in declared order)
- `model_encode_op`, `forward_op`, `decode_op`, `augment_op` (fully-qualified operator names; default to listed `UML_OS.*_v#`)
- `datasets` array: each entry `{id, version, hash, split: train|val}`
- all other values previously in I.C (`probe_interval`, `sil_thresh`, etc.)

### 0.R Distributed and Multi-tenancy Policy
- Communication: PyTorch distributed (`gloo` CPU / `nccl` CUDA), ranks sorted ascending by `(hostname hash, rank)`.
- Data sharding: global permutation, then each rank processes slice `rank::world_size`.
- Global operations (clustering, fingerprint aggregation): rank 0 computes, others receive via `Broadcast`; RNG draws only on rank 0 where declared.
- `latent_buffer`: sharded by `sample_index % world_size`; `AllGather` only when required by operator (e.g., augment).
- Daemon enforces isolation, quotas, and schedules jobs across namespaces with fair-share priority based on manifest-declared resources.
- Checkpoint/restore restores exact global `data_cursor`, sharded `latent_buffer`, and synchronized RNG master state.

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

---

## I · System Model

### I.A Persistent State
- `theta`
- `state in {S_P, S_PROTO}`
- `t`
- `loss_hist` (single history, tagged with state)
- `latent_buffer` FIFO of `(x, y, z, diff_i)`
- `data_cursor = (epoch, index, permutation)`
- `rng_master_state` + sub-stream offsets
- `tape_state`
- `np.protos` (centroids only; normalized)
- `np.protos_equation` (list of canonical equation trees, one per prototype)

### I.B Declared Dimensions and Defaults
- Declared dimensions and defaults (overridable in manifest, used when absent):
  - `latent_dim p = 64`
  - `num_prototypes k_np = 32`
  - `batch_size B = 64`
  - `latent_buffer_capacity N_latent = 1_000_000`

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

## III · Mathematical Components

### III.A Supervised Loss
- `logits = nn_logits + beta * sym_pred`
- `task_type` taken from manifest (default: multiclass).
- multiclass: `L_sup = CrossEntropyLoss(logits, y)` (integer labels `0..C-1`)
- binary: `L_sup = BCEWithLogitsLoss(logits, y)`
- regression: `L_sup = MSELoss(logits, y)`
- Reduction performed in binary64, ascending-index order.

### III.B Unsupervised Terms
- Preprocessing (applied once at bootstrap via deterministic full-pass or first 10% of training split in ascending index order; stats stored in manifest): `x` normalized to range compatible with decoder output.
- `recon = UML_OS.Model.Decode_v1(z)` (decoder output clamped to match normalization range)
- `L_rec = MSE(x_preprocessed, recon)`
- `L_KL` = diagonal Gaussian KL
- `L_OT` = sliced Wasserstein-2 with 4 fixed projections from:
  - `SHA-256("UML_OS_OT" || spec_version || p)`
- `L_covz = ||Cov(z) - I||_F^2`
- `L_aux = lambda_rec*L_rec + lambda_KL*L_KL + lambda_OT*L_OT + lambda_covz*L_covz`

### III.C Total Loss
- `L_tot = alpha * L_sup + L_aux` (binary64 fixed term order; alpha, lambdas taken from manifest; defaults `alpha=1.0`, `lambda_rec=1.0`, `lambda_KL=0.001`, `lambda_OT=0.01`, `lambda_covz=0.001` if absent).
- Binary64 fixed term order
- Weight decay applied only inside `UML_OS.Update_v1` on trainable params

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

### UML_OS.Cluster.SphericalKMeans_v1
- Purity: STATEFUL
- RNG consumption: exactly 31 draws from stream `cluster`
- Same RNG and logic as augment path, performed on all ranks identically for probe action; uses local buffer subset in global index order.
- max iterations: 50
- empty cluster policy: keep previous centroid

### UML_OS.Module.ActivateNonParamModule_v1
- Purity: STATEFUL
- RNG consumption: exactly 31 draws from stream `cluster` on rank 0 only; 0 on other ranks
- Steps (executed synchronously after barrier):
  - `AllGather` last 5000 latents (sorted by original global index) to rank 0.
  - rank 0: spherical k-means on gathered latents (`k = k_np` from manifest; first centroid = mean; subsequent 31 distance-weighted categorical draws).
  - rank 0: per-cluster `EquationUpdate_v2` (deterministic greedy expression search on `(z, target_residual)`; fixed operator set `{+,*,/,sin,cos,exp,log}`; least-squares fit in ascending sample order; prune by fixed complexity penalty; outputs one canonical string tree per cluster).
  - broadcast centroids and equation trees to all ranks.
  - all ranks: `np.protos = normalize(centroids)`; store `np.protos_equation`; set `state <- S_PROTO`.

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
- Includes gradient, clip, optimizer step, weight decay

### UML_OS.StateFingerprint_v1
- Purity: PURE
- RNG consumption: exactly 0 draws from stream `none`
- Computes SHA-256 over the following domain concatenated in exact order (all values serialized to big-endian binary64 or fixed-width integers):
  1. `theta` (all parameters, sorted by fully-qualified operator name)
  2. optimizer state (all buffers/moments in registration order)
  3. `latent_buffer` (Merkle root of 256-element chunks, most recent `min(N_latent, 8192)` entries)
  4. `data_cursor` (epoch, index, full current permutation hash)
  5. current state enum (`S_P` = 0, `S_PROTO` = 1)
  6. RNG master state + all sub-stream offsets (64-bit each)
  7. `np.protos` tensor (flattened) + SHA-256 of canonical equation strings per prototype (sorted)
  8. `loss_hist` last 256 entries (tagged with state)
- Result stored as `state_fp`.

## V · Observability and Trace

### V.A Logging Rule
- one run_header
- one iter record per loop iteration
- one run_end

### V.B Minimal Trace Schema
- `run_header`: metadata, hashes, replay token, `task_type`, `world_size`, `backend_hash`
- `iter`: `t, state, action, loss_total, grad_norm, sil_mean, resource_util, state_fp, functional_fp` (functional_fp included when recomputed)
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
   - `UML_OS.Contract.Validate_v1(...)`
   - `action <- UML_OS.Policy.Evaluate_v1(...)`
   - dispatch using manifest-declared operator names:
     - `optimize -> UML_OS.Update_v1(...)`
     - `augment -> manifest.augment_op(...)`
     - `probe -> UML_OS.Cluster.SphericalKMeans_v1(...)` + log silhouette
     - `switch -> UML_OS.Transition.SwitchState_v1(...)`
   - `current_state_fp <- UML_OS.StateFingerprint_v1(...)`
   - if (`t mod 50 == 0` or `action == "augment"`): `current_functional_fp <- UML_OS.Fingerprint.Functional_v1(...)`
   - if world_size > 1: deterministic barrier after action dispatch (ensures all ranks see identical state before tape/log and identical fingerprints across ranks)
   - `UML_OS.IO.WriteTape_v1(...)`
   - `UML_OS.Logging.LogIteration_v1(...)`
   - update fingerprints

---

## VII · Validation and Equivalence

- Required equivalence target: **E1 (metric-equivalent)**
- Required golden trace dataset: any manifest-declared dataset that matches declared `task_type`, dimension constraints, and produces metric-equivalent trace within tolerance envelope over 10 seeds.
- E1 requires matching:
  - `replay_token`
  - `state_fp` sequence
  - `functional_fp` curve
  within the declared tolerance envelope over 10 seeds.

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

---

## X · Compatibility Boundary

The following are normative compatibility boundaries for UML_OS-v3.8-OS:

1. Single mandatory kernel path.
- All training, state transitions, loss computation, and non-parametric augmentation must run only through the VI procedure and declared operators.
- Any external imperative training loop or side-channel mutation is non-conformant and must fail through `Contract.Validate_v1`.

2. Daemon-enforced namespace isolation.
- When `world_size > 1` or UML_OS_ROOT is shared, daemon control is mandatory.
- Per-namespace isolation of RNG state, `data_cursor`, latent-buffer shards, tape, and checkpoints is required under the UML_OS_ROOT hierarchy.

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
