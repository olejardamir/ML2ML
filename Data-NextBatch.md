# Universal Machine Learning Operating System — Data NextBatch
**EQC Compliance:** This specification follows EquationCode (EQC) v1.1 merged single-file format (Option A): 10 top-level sections, global semantics first, operator-owned math, control-flow-only procedure, deterministic contracts, and replayable stochasticity.

**Algorithm:** `UML_OS.Data.NextBatch_v2`  
**Purpose (1 sentence):** Deliver fully deterministic, memory-efficient, world_size-independent global batch sampling with block-shuffled epoch permutations for training and strict sequential access for evaluation/inference, scalable to 100 B+ sample datasets with O(1) per-sample index resolution after O(num_blocks) preprocessing.  
**Spec Version:** `UML_OS.Data.NextBatch_v2` | 2026-02-18 | Authors: Olejar Damir (with EQC team improvements)  
**Domain / Problem Class:** Deterministic data loading and shuffling for reproducible large-scale distributed ML training and evaluation.

---

## 1) Header & Global Semantics

### 0.0 Identity
- **Algorithm:** `UML_OS.Data.NextBatch_v2`
- **Purpose (1 sentence):** Memory-efficient deterministic global sampling with epoch-wise seeded shuffling that is independent of world_size and rank.
- **Spec Version:** `UML_OS.Data.NextBatch_v2` | 2026-02-18 | Authors: Olejar Damir
- **Domain / Problem Class:** Scalable deterministic data iteration for any dataset cardinality.

### 0.A Objective Semantics
- Not an optimization operator.
- Primary guarantee: identical global virtual sequence for any (world_size, rank) pair given identical manifest/seed/dataset_cardinality.
- Comparison rule: exact index equality (uint64).

### 0.B Reproducibility Contract
- Seed space: `seed ∈ {0..2^64-1}` derived deterministically.
- PRNG family: `Philox4x32-10`
- Randomness locality: only inside `SeededBlockPermute_v1` and `SeededIntraBlockMap_v1`
- Replay guarantee: fully replayable given `(manifest_hash, dataset_key, epoch, global_position, world_size, rank, sampler_block_size)`
- Replay token contribution: `data_replay_t = SHA-256(kernel_replay_token || "nextbatch" || dataset_key || epoch || global_position || world_size || rank)`

### 0.C Numeric Policy
- All indices, cardinalities, positions: uint64 (no wrap-around overflow; explicit bounds checks)
- Block arithmetic: exact integer division/modulo
- No floating-point in core path
- Constants: `DEFAULT_BLOCK_SIZE = 1_048_576` (2^20)

### 0.D Ordering and Tie-Break Policy
- Index base: 0-based
- Global batch formation: ascending global virtual position
- Tie break: lowest original index wins (only relevant for boundary handling)

### 0.E Parallel, Concurrency, and Reduction Policy
- Global batch sequence **independent** of `world_size`
- Sharding: contiguous rank-ordered slices of the global virtual sequence (`global_batch_size % world_size == 0` enforced)
- `world_size=1`: full global batch
- No collectives required; pure local computation

### 0.F Environment and Dependency Policy
- Reference runtime: CPU/GPU agnostic (pure index math)
- Dependencies: manifest.datasets[dataset_key] must contain `cardinality: uint64`, `id`, `version`, `hash`
- `manifest.data.sampler_block_size: uint64` (default 1_048_576)

### 0.G Operator Manifest
- `UML_OS.Data.NextBatch_v2`
- `UML_OS.Data.SeededBlockPermute_v1` (internal helper)
- `UML_OS.Data.SeededIntraBlockMap_v1` (internal helper)
- `UML_OS.Error.Emit_v1`

### 0.H Namespacing and Packaging
- Fully-qualified names: `UML_OS.Data.<Name>_v#`

### 0.I Outputs and Metric Schema
- Declared outputs: `(batch_sample_indices: uint64[], data_cursor')`
- Minimum metrics: `epoch`, `global_position`, `is_shuffled`, `effective_batch_size`, `blocks_materialized`

### 0.J Spec Lifecycle Governance
- Reproducibility-breaking changes to sequence formation, sharding, or cursor progression require MAJOR version bump.
- Non-breaking performance-only changes (cache/prefetch without sequence changes) require MINOR bump.
- Equivalence target: E0 exact index-sequence equivalence.

### 0.K Failure and Error Semantics
- Global error model: abort-only
- Failure codes: `INVALID_DATASET_KEY`, `CARDINALITY_MISMATCH`, `BATCH_SIZE_INCONSISTENT`, `GLOBAL_POSITION_EXCEEDS_CARDINALITY`, `INVALID_STAGE_TYPE`
- Failure record fields: `t`, `failure_code`, `dataset_key`, `data_replay_t`

### 0.L Input/Data Provenance
- `dataset_cardinality` must match registered immutable dataset hash

### 0.M Recommended Presets
- `train_shuffle`: block-based + train mode
- `eval_sequential`: no-shuffle + ascending indices
- `streaming_infinite`: wrap-around with epoch seed rotation

---

## 2) System Model

### I.A Persistent State
- `data_cursors: map<string, {epoch: uint64, global_index: uint64}>` (per dataset_key)

### I.B Inputs and Hyperparameters
- `dataset_key: string`
- `world_size: uint32`
- `rank: uint32` (0-based)
- `global_batch_size: uint64` (from manifest)
- `stage_type: "train" | "eval" | "infer"`

### I.C Constraints and Feasible Set
- `global_batch_size % world_size == 0`
- `global_batch_size > 0`
- `dataset_key` exists in manifest.datasets
- `cardinality >= global_batch_size` (soft; wrap supported for streaming)

### I.D Transient Variables
- `N`, `epoch_seed`, `block_order`, `current_block_perms` (lazy map)

### I.E Invariants and Assertions
- Same `(manifest_hash, epoch, global_position)` → identical sample index
- Eval/infer: sample_indices == [global_pos, global_pos+1, …] % N
- Train: permutation is a bijection over [0 … N-1]
- Cursor only advances on successful batch return

---

## 3) Initialization

1. `cursor <- data_cursors.get(dataset_key, {epoch:0, global_index:0})`
2. `N <- manifest.datasets[dataset_key].cardinality`
3. If new epoch (`cursor.global_index == 0` or wrapped): compute `epoch_seed = BLAKE3(manifest_hash || dataset_key || cursor.epoch)[0:16]` (Philox seed)

---

## 4) Operator Manifest

Active operators:
- `UML_OS.Data.NextBatch_v2`
- `UML_OS.Data.SeededBlockPermute_v1`
- `UML_OS.Data.SeededIntraBlockMap_v1`
- `UML_OS.Error.Emit_v1`

---

## 5) Operator Definitions

**Operator:** `UML_OS.Data.NextBatch_v2`  
**Category:** Data  
**Signature:** `(dataset_key, world_size, rank, stage_type -> batch_sample_indices: uint64[], data_cursor')`  
**Purity class:** STATEFUL  
**Determinism:** deterministic (RNG only inside helpers for train shuffling)  
**Definition:** Computes the next micro-batch of original sample indices according to global virtual order. Guarantees identical sequence across any distributed configuration.

**Operator:** `UML_OS.Data.SeededBlockPermute_v1`  
**Category:** Data  
**Signature:** `(num_blocks, epoch_seed -> block_order: uint64[])`  
**Purity class:** PURE  
**Determinism:** deterministic  
**Definition:** Fisher-Yates shuffle of [0 … num_blocks-1] using Philox seeded by epoch_seed. Materializes only O(num_blocks) memory.

**Operator:** `UML_OS.Data.SeededIntraBlockMap_v1`  
**Category:** Data  
**Signature:** `(block_id, local_pos, block_size, epoch_seed, N -> original_index: uint64)`  
**Purity class:** PURE  
**Determinism:** deterministic  
**Definition:** Computes intra-block permutation via seeded reversible mapping (Philox counter mode + modular arithmetic with good mixing). O(1) per call; no storage beyond seed.

---

## 6) Procedure

```text
1. cursor = data_cursors[dataset_key] or init {epoch=0, global_index=0}
2. N = manifest.datasets[dataset_key].cardinality
3. global_pos = cursor.global_index
4. global_batch_size = manifest.global_batch_size
5. If global_batch_size % world_size != 0: Error.Emit_v1(BATCH_SIZE_INCONSISTENT); abort
6. micro_batch_size = global_batch_size // world_size
7. rank_start = rank * micro_batch_size

8. if stage_type in {"eval", "infer"}:
       is_shuffled = false
       batch_positions = [global_pos + rank_start + i for i in 0..micro_batch_size-1]
       batch_indices = [p % N for p in batch_positions]
   else:
       is_shuffled = true
       block_size = manifest.data.sampler_block_size or DEFAULT_BLOCK_SIZE
       num_blocks = ceil(N / block_size)
       block_order = SeededBlockPermute_v1(num_blocks, epoch_seed)

       batch_indices = []
       for i in 0..micro_batch_size-1:
           p = global_pos + rank_start + i
           if p >= N:  # wrap or drop_last logic per manifest.drop_last
               if manifest.drop_last: break
               p = p % N
           block_id_global = p // block_size
           perm_block_id = block_order[block_id_global]
           local_pos = p % block_size
           orig_idx = SeededIntraBlockMap_v1(perm_block_id, local_pos, block_size, epoch_seed, N)
           batch_indices.append(orig_idx)

9. cursor.global_index += global_batch_size
10. if cursor.global_index >= N:
        cursor.epoch += 1
        cursor.global_index = 0   # start new epoch
11. data_cursors[dataset_key] = cursor
12. return batch_indices, cursor
```

**Scalability & Algorithmic Guarantees (v2):**
- Memory: O(num_blocks) worst-case (~1 MiB for 1 B samples with 1 M block_size); lazy per-batch block materialization possible in future.
- Time: O(micro_batch_size) per call with O(1) intra-block mapping.
- Exact bijection in train mode; perfect reproducibility across restarts, world_size, hardware.
- Supports streaming/infinite datasets via modular wrap + epoch seed rotation.
- drop_last behavior is configurable via manifest (`drop_last=false` default).

---

## 7) Trace & Metrics

### Trace schema (minimum required)
- `run_header`: `dataset_key`, `cardinality`, `sampler_block_size`, `is_shuffled_per_stage`
- `iter`: `t`, `epoch`, `global_position`, `is_shuffled`, `micro_batch_size`, `data_replay_t`
- `run_end`: final epoch count, total_samples_seen

### Metric schema
- `epoch`, `global_position`, `effective_batch_size`, `blocks_materialized_this_epoch`

---

## 8) Validation

#### VII.A Lint rules (mandatory)
Passes symbol completeness, deterministic ordering, total state updates (only cursor), explicit RNG locality, edge-case totality.

#### VII.B Operator test vectors (mandatory)
- world_size=1, rank=0: full global sequence matches sequential + shuffle
- world_size=8, any rank: contiguous shards reconstruct global sequence exactly
- N=10^9+, block_size=1M: no OOM, identical across runs
- eval mode: always sequential indices
- checkpoint/restore mid-epoch: identical continuation

#### VII.C Golden traces (mandatory)
Golden runs for N=10^6, 10^9 with multiple world_sizes; exact index sequences verified.

---

## 9) Refactor & Equivalence

#### VIII.A Equivalence levels
- E0: exact sample index sequences and cursor state
- E1: identical training dynamics (loss curves within noise)

#### VIII.B Allowed refactor categories
- Intra-block mapping optimization (Feistel, AES-based, etc.) preserving bijection
- Prefetch / cache-friendly block loading
- Weighted/class-balanced extensions (with manifest flag and extra seed stream)

#### VIII.C Equivalence test procedure (mandatory)
- 5 seeds × 3 world_sizes × 2 modes
- Compare full batch index sequences (exact match required for E0)

---

## 10) Checkpoint/Restore

### Checkpoint contents
- `data_cursors` map (epoch + global_index per dataset_key only)

### Serialization
- Deterministic CBOR with fixed field order

### Restore semantics
- Identical subsequent batch sequences under same manifest/seed
- Mid-epoch restore supported (no re-shuffle of current epoch)
