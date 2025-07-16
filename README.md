# EquationCode (EQC) v3.6-OS

**Algorithm:** Deterministic ML Training OS kernel with symbolic prototype augmentation.  
**Purpose (1 sentence):** Execute machine-learning training and lifecycle operations under formal reproducibility, namespace isolation, and deterministic runtime contracts.  
**Spec Version:** EQC-v3.6-OS | 2026-02-17 | Authors: Olejar Damir  
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
- Parallel reductions: fixed 256-element chunks
- Rank aggregation: ascending rank order

### 0.F Environment and Dependency Policy
- Pinned runtime:
  - Python 3.12
  - NumPy 2.1
  - PyTorch 2.4 CPU reference build
- If `distributed_mode != none`, then `world_size` must be power-of-2

### 0.G Operator Manifest
- Removed from manifest surface:
  - `ULF.Random.InitializeParameters_v1`
  - `ULF.Init.LoadPolicy_v1`
  - `ULF.Init.InitializeBuffers_v1`
  - all `ULF.Serving.*`
  - `ULF.Model.MultiHeadAttention_v1`
- Added:
  - `ULF.Data.ValidateManifest_v1`

Active operators:
- `ULF.OS.Bootstrap_v1`
- `ULF.OS.ResolvePath_v1`
- `ULF.OS.NamespaceEnter_v1`
- `ULF.OS.QuotaEnforce_v1`
- `ULF.Data.Manifest_v1`
- `ULF.Data.ValidateManifest_v1`
- `ULF.Data.NextBatch_v1`
- `ULF.Data.StreamingLoader_v1`
- `ULF.Buffer.ShardedDiskRing_v1`
- `ULF.Model.Encode_v1`
- `ULF.Model.Forward_v2`
- `ULF.Objective.TotalLoss_v1`
- `ULF.Update_v1`
- `ULF.Cluster.SphericalKMeans_v1`
- `ULF.Module.ActivateNonParamModule_v1`
- `ULF.Symbolic.DifferentiableEval_v1`
- `ULF.Symbolic.EquationUpdate_v2`
- `ULF.Policy.Evaluate_v1`
- `ULF.Transition.SwitchState_v1`
- `ULF.Contract.Validate_v1`
- `ULF.IO.WriteTape_v1`
- `ULF.Logging.LogIteration_v1`
- `ULF.Termination.Check_v1`
- `ULF.StateFingerprint_v1`
- `ULF.Fingerprint.Functional_v1`
- `ULF.Error.Emit_v1`

### 0.H Namespacing and Packaging
- Fully-qualified names: `ULF.<Category>.<Name>_v#`
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
- Optional YAML config loading allowed
- Canonicalized into manifest before hashing

### 0.N Layered Operating-System Architecture
- Layer ordering:
  - `Kernel -> Driver -> Runtime -> Module -> Daemon -> Management -> User`
- Daemon mandatory when:
  - `world_size > 1`, or
  - more than one job shares `EQC_ROOT`
- Namespace path:
  - `/org/project/experiment/job_id`
  - `job_id = replay_token[0:8]`

### 0.P Bootstrap
- Single entrypoint: `ULF.OS.Bootstrap_v1`
- Must also perform:
  - PRNG init
  - buffer allocation
  - data manifest load + validation
  - policy load
  - namespace enter

### 0.Q Global Manifest Additions
- `env_manifest_hash` must include:
  - `daemon_concurrency_max=16`

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

### I.B Declared Dimensions and Defaults
- `p = 64`
- `k_np = 32`
- `B = 64`
- `N_latent = 1_000_000`

### I.C Hyperparameters
- `probe_interval = 50`
- `sil_thresh = 0.25`
- `sr_refresh_every = 500`
- Removed:
  - `lambda_policy`
  - `hierarchical_prototypes`
  - trainable MI estimator
  - explicit `sr_objective` control (auto-inferred)

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
2. `ULF.OS.Bootstrap_v1(...)`
3. Initialize `theta` from `Normal(0, 0.02)` via Box-Muller using `init` sub-stream
4. Initialize `state <- S_P`
5. Initialize `loss_hist`, `latent_buffer`, `data_cursor`
6. Initialize tape and fingerprints

---

## III · Mathematical Components

### III.A Supervised Loss
- `logits = nn_logits + beta * sym_pred`
- `beta` is learnable scalar
- `L_sup = BCEWithLogitsLoss(logits, y)`
- Reduction in binary64

### III.B Unsupervised Terms
- `L_rec = MSE(x, decoder(z))`, with `decoder(z)` bounded by `tanh(.) / 2`
- `L_KL` = diagonal Gaussian KL
- `L_OT` = sliced Wasserstein-2 with 4 fixed projections from:
  - `SHA-256("ULF_OT" || spec_version || p)`
- `L_covz = ||Cov(z) - I||_F^2`
- `L_aux = lambda_rec*L_rec + lambda_KL*L_KL + lambda_OT*L_OT + lambda_covz*L_covz`

### III.C Total Loss
- `L_tot = alpha * L_sup + L_aux`
- Binary64 fixed term order
- Weight decay applied only inside `ULF.Update_v1` on trainable params

---

## IV · Operator Library

All operators must declare exactly:
- purity
- rng streams used
- deterministic order guarantee

### ULF.OS.Bootstrap_v1
- Purity: STATEFUL
- RNG streams: `init`, `cluster`, `misc`
- Performs:
  - PRNG init (single Philox + fixed offsets)
  - parameter init
  - buffer allocation
  - data manifest load + `ULF.Data.ValidateManifest_v1`
  - policy load
  - namespace enter

### ULF.Policy.Evaluate_v1 (rule engine only)
- Purity: PURE
- RNG streams used: none
- Deterministic priority rule evaluation:
```json
{
  "rules": [
    {"cond": "sil_mean < 0.25 AND state == S_P", "action": "augment", "priority": 10},
    {"cond": "loss_delta > 0.0", "action": "probe", "priority": 5}
  ]
}
```
- Action: highest-priority matched rule; ties by lowest index

### ULF.Model.Encode_v1
- Purity: STATEFUL
- RNG streams: `init`
- Two linear layers + reparameterization (`eps` from Box-Muller)

### ULF.Model.Forward_v2
- Purity: PURE
- RNG streams used: none
- `proto_features = cosine_similarity(z, np.protos)`
- If Symbolic module is loaded:
  - `sym_pred = routed weighted sum of DifferentiableEval_v1`
- Else:
  - `sym_pred = 0`
- `logits = nn_logits + beta * sym_pred`

### ULF.Cluster.SphericalKMeans_v1
- Purity: STATEFUL
- RNG streams: `cluster`
- k-means++ init (deterministic uniform first, then distance-weighted categorical)
- max iterations: 50
- empty cluster policy: keep previous centroid

### ULF.Module.ActivateNonParamModule_v1
- Purity: STATEFUL
- RNG streams: `cluster`
- Steps:
  - use last 5000 latents from buffer
  - run spherical k-means
  - per-cluster run `EquationUpdate_v2`
  - embed each equation tree using SHA-256 per dimension
  - update prototypes:
    - `np.protos = normalize(0.5*centroids + 0.5*E_eq)`
  - store equation trees in `np.protos_equation`
  - emit pretty-equation events
  - set `state <- S_PROTO`

### ULF.Data.NextBatch_v1
- Purity: STATEFUL
- RNG streams: `misc`
- Deterministic epoch shuffle + weighted reservoir from latent difficulty when present

### ULF.IO.WriteTape_v1
- Purity: IO
- RNG streams used: none
- `BLOCK_SIZE = 512`
- `max_events = 500_000`

### ULF.Contract.Validate_v1
- Purity: PURE
- RNG streams used: none
- Runtime checks:
  - KL >= 0 within tolerance
  - covariance PSD checks
  - probability sums
  - gradient clipping bound
- On violation:
  - deterministic failure
  - minimal counterexample snapshot

### ULF.Update_v1
- Purity: STATEFUL
- RNG streams used: none
- Includes gradient, clip, optimizer step, weight decay

### Optional modules only
- `Symbolic`
- `AdvancedPrototype`

---

## V · Observability and Trace

### V.A Logging Rule
- one run_header
- one iter record per loop iteration
- one run_end

### V.B Minimal Trace Schema
- `run_header`: metadata, hashes, replay token
- `iter`: `t, state, action, loss_total, grad_norm, sil_mean, resource_util`
- `run_end`: completion status, final hashes, functional fingerprint

Internal-only fields (not required in minimal public trace):
- policy entropy
- aux-loss breakdown

---

## VI · Algorithm Procedure

1. `ULF.OS.Bootstrap_v1(...)`
2. `ULF.OS.NamespaceEnter_v1(job_id)`
3. if pipeline configured: `ULF.Pipeline.ExecuteDAG_v1(...)`; else continue
4. loop until termination:
   - `ULF.Termination.Check_v1(...)`
   - `t += 1`
   - `ULF.OS.QuotaEnforce_v1(...)`
   - `batch <- ULF.Data.NextBatch_v1(...)`
   - `z <- ULF.Model.Encode_v1(...)`
   - `(logits, sym) <- ULF.Model.Forward_v2(...)`
   - `L_tot <- ULF.Objective.TotalLoss_v1(...)`
   - `ULF.Contract.Validate_v1(...)`
   - `action <- ULF.Policy.Evaluate_v1(...)`
   - dispatch:
     - `optimize -> ULF.Update_v1(...)`
     - `augment -> ULF.Module.ActivateNonParamModule_v1(...)`
     - `probe -> ULF.Cluster.SphericalKMeans_v1(...)` + log silhouette
     - `switch -> ULF.Transition.SwitchState_v1(...)`
   - `ULF.IO.WriteTape_v1(...)`
   - `ULF.Logging.LogIteration_v1(...)`
   - update fingerprints

---

## VII · Validation and Equivalence

- Required equivalence target: **E1 (metric-equivalent)**
- Required golden trace dataset: Fashion-MNIST subset
- E0/E2/E3 are not required for baseline conformance

---

## VIII · Checkpoint and Restore

### VIII.A Checkpoint Contents
- include:
  - `theta`
  - optimizer state
  - single `loss_hist`
  - `latent_buffer`
  - `data_cursor`
  - RNG master + offsets
  - hashes (`policy_hash`, `env_manifest_hash`, `replay_token`)
  - `functional_fp`
- remove:
  - `plateau_count`
  - separate `loss_hist_P` / `loss_hist_PROTO`
  - `active_namespace_stack`

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

This is the final minimal kernelized EQC-v3.6-OS specification.
