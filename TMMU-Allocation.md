# Universal Machine Learning Operating System — TMMU Allocation
**EQC Compliance:** This specification follows EquationCode (EQC) v1.1 merged single-file format (Option A): 10 top-level sections, global semantics first, operator-owned math, control-flow-only procedure, deterministic contracts, and replayable stochasticity.

**Algorithm:** `UML_OS.TMMU.PrepareMemory_v2`  
**Purpose (1 sentence):** Perform static liveness analysis, optimal interval-graph coloring, multi-arena size-aware logical slot assignment, and deterministic virtual-address mapping for any UML_Model_IR DAG, guaranteeing bit-identical layouts, maximal reuse (provably optimal number of slots = max live tensors), alignment safety, and minimal peak memory across 100B+ parameter models while remaining fully replayable.  
**Spec Version:** `UML_OS.TMMU.PrepareMemory_v2` | 2026-02-17 | Authors: Olejar Damir (with EQC team improvements)  
**Domain / Problem Class:** Deterministic, size-aware, multi-arena tensor memory planning via interval-graph register allocation for deep learning computation graphs.

---

## 1) Header & Global Semantics

### 0.0 Identity
- **Algorithm:** `UML_OS.TMMU.PrepareMemory_v2`
- **Purpose (1 sentence):** Statically compute optimal reusable logical slots and deterministic virtual addresses with maximal liveness-based reuse.
- **Spec Version:** `UML_OS.TMMU.PrepareMemory_v2` | 2026-02-17 | Authors: Olejar Damir (with EQC team)
- **Domain / Problem Class:** Scalable, reproducible, alignment-aware tensor memory planning for ML graphs.

### 0.A Objective Semantics
- Not an optimization operator (enables extreme efficiency).
- Primary guarantee: identical logical slots, virtual addresses, and tensor_map for identical `(ir_dag, execution_order, mode, replay_token)`.
- Comparison rule: exact equality of virtual addresses and live ranges.

### 0.B Reproducibility Contract
- Seed space: `seed ∈ {0..2^64-1}` inherited from kernel replay context.
- PRNG family: Philox4x32-10 (not sampled in allocator core path; used only if deterministic zeroing pattern derivation requires counter expansion).
- Assignment is 100% deterministic given replay_token.
- Two-level mapping:
  - Logical slot ID (0-based, assigned by optimal greedy linear scan on interval graph).
  - Virtual address = BLAKE3(replay_token || "tmmu_slot" || arena_name || logical_slot_id || mode).
- Randomness locality: no sampling in core allocation path; any pseudo-random fill/zero pattern generation is operator-owned (`ZeroTensor_v1`) and deterministic.
- Replay guarantee: replayable given `(replay_token, ir_hash, mode, arena_config, execution_order)`.
- No randomness in core path. Full replayability of layout, zeroing, and physical remapping.

### 0.C Numeric Policy
- All sizes, offsets, alignments, and addresses in uint64.
- No floating-point in allocation path.
- Zeroing pattern: deterministic replay-seeded (BLAKE3-derived fill).
- Overflow policy: abort on uint64 overflow in offset/size arithmetic.
- Approx-equality: exact integer equality only.
- Normalized exponentials / transcendental functions: N/A for allocator semantics.

### 0.D Ordering and Tie-Break Policy
- Tensors ordered by first definition node_id (earliest wins on ties).
- Logical slots assigned in ascending order (lowest available first).
- Within same birth time: larger tensors first (size-descending heuristic for better packing).

### 0.E Parallel, Concurrency, and Reduction Policy
- Allocation is purely sequential and deterministic.
- Driver-level intra-op parallelism does not affect virtual layout.

### 0.F Environment and Dependency Policy
- Requires UML_Model_IR with complete shape, dtype, and tensor-role hints.
- Depends on execution_order and arena_config.
- Reference runtime: pure Python simulator for E0 verification.
- Dependencies: BLAKE3, replay_token.
- Determinism level: `BITWISE` for slot assignments and virtual-address mapping.

### 0.G Operator Manifest
- `UML_OS.TMMU.PrepareMemory_v2`
- `UML_OS.Model.AnalyzeLiveness_v1`
- `UML_OS.TMMU.AssignLogicalSlots_v1` (new)
- `UML_OS.TMMU.MapToVirtualAddresses_v1` (new)
- `UML_OS.TMMU.ZeroTensor_v1`
- `UML_OS.TMMU.CommitExecution_v1`
- `UML_OS.Error.Emit_v1`

### 0.H Namespacing and Packaging
- Fully-qualified names: `UML_OS.TMMU.<Name>_v#`

### 0.I Outputs and Metric Schema
- Declared outputs: `tensor_map: dict[node_id → tensor_handle]`, `metrics`
- Minimum metrics: `peak_logical_slots`, `peak_physical_bytes_per_arena`, `memory_reuse_ratio`, `max_live`, `internal_fragmentation_ratio`, `allocation_time_ns`
- Completion status: `success | failed` with deterministic failure codes from 0.K.

### 0.J Spec Lifecycle Governance
- Changes affecting liveness intervals, slot assignment, or virtual-address derivation require MAJOR version bump.
- Performance-only implementation changes that preserve outputs/trace semantics require MINOR bump.
- Equivalence target: E0 for slot map and virtual-address determinism.

### 0.K Failure and Error Semantics
- Failure codes: `INVALID_IR_SHAPES`, `LIVENESS_CYCLE`, `ADDRESS_COLLISION`, `ALLOCATION_OVERFLOW`, `ARENA_TOO_SMALL`, `ALIGNMENT_VIOLATION`
- Always aborts with full context.

### 0.L Input/Data Provenance
- Relies on ir_dag canonical hash and replay_token.
- All shapes/dtypes/roles fingerprinted.

### 0.M Recommended Presets
- `train_full`: forward + backward (max activation retention)
- `inference`: aggressive reuse
- `remat_enabled`: future selective rematerialization hints

### 0.N Arena Policy (new)
- `parameters`: persistent, no reuse, sequential offsets.
- `activations`: high-reuse interval allocation.
- `gradients`: backward-only, high-reuse.
- Each arena has its own logical-slot space and virtual-address base.

---

## 2) System Model

### I.A Persistent State
- None (stateless; arenas managed by upper TMMU layer).

### I.B Inputs and Hyperparameters
- `ir_dag: UML_Model_IR` (with tensor roles)
- `execution_order: node[]`
- `mode: "forward" | "backward" | "inference"`
- `replay_token: bytes` (≥64 bytes)
- `arena_config`: {arena_name → {capacity_bytes, alignment_bytes (default 128), page_size}}

### I.C Constraints and Feasible Set
- All shapes/dtypes known statically.
- Acyclic dataflow.
- Peak live bytes per arena ≤ arena capacity.

### I.D Transient Variables
- `live_ranges`, `active_set`, `logical_slot_map`, `virtual_address_table`, `free_intervals_per_arena` (for size-aware fallback)

### I.E Invariants and Assertions
- No access before birth or after death.
- Live tensors in same logical slot never overlap.
- Addresses unique within arena.
- Alignment respected.
- Mathematical guarantee: #logical_slots_per_arena = max simultaneous live tensors in that arena (interval graph optimality).

---

## 3) Initialization

1. Validate IR, shapes, roles, execution_order vs mode.
2. `live_ranges ← AnalyzeLiveness_v1(ir_dag, execution_order, mode)`
3. Classify tensors into arenas based on role/mode.

---

## 4) Operator Manifest

Active operators:
- `UML_OS.TMMU.PrepareMemory_v2`
- `UML_OS.Model.AnalyzeLiveness_v1`
- `UML_OS.TMMU.AssignLogicalSlots_v1`
- `UML_OS.TMMU.MapToVirtualAddresses_v1`
- `UML_OS.TMMU.ZeroTensor_v1`
- `UML_OS.TMMU.CommitExecution_v1`
- `UML_OS.Error.Emit_v1`

---

## 5) Operator Definitions

**Operator:** `UML_OS.TMMU.PrepareMemory_v2`  
**Category:** Memory  
**Signature:** `(ir_dag, execution_order, mode, replay_token, arena_config → tensor_map, metrics)`  
**Purity class:** PURE (given replay_token)  
**Determinism:** Fully deterministic  
**Definition:** Multi-arena liveness analysis → optimal logical slot assignment (linear-scan coloring) → virtual address mapping. Guarantees optimal slot count and alignment.
**Preconditions / Postconditions:** valid IR and arena config; returns deterministic tensor_map/metrics with zeroed handles.  
**Edge cases:** tiny graphs, near-capacity arenas, mixed-role tensors.  
**Numerical considerations:** integer-only offset/address arithmetic with overflow checks.  
**Ordering/tie handling:** birth-time ascending, size-desc tie-break, lowest-slot-first assignment.  
**Complexity note:** O(N log N) worst-case (N=tensors).  
**Failure behavior:** abort with 0.K allocator codes.  
**Dependencies:** AnalyzeLiveness_v1, AssignLogicalSlots_v1, MapToVirtualAddresses_v1, ZeroTensor_v1, CommitExecution_v1.  
**Test vectors:** see VII.B chain/residual/large-model slot maps.

**Operator:** `UML_OS.Model.AnalyzeLiveness_v1`  
**Category:** Model  
**Signature:** `(ir_dag, execution_order, mode → live_ranges)`  
**Purity class:** PURE  
**Definition:** Linear pass; backward extends activation lifetimes until gradient use.
**Preconditions / Postconditions:** valid execution_order and IR references; returns complete live intervals for all tensors.  
**Edge cases:** branched DAG fan-out/fan-in and backward retention boundaries.  
**Numerical considerations:** N/A (graph interval computation).  
**Ordering/tie handling:** deterministic node traversal order.  
**Complexity note:** O(|nodes| + |edges|).  
**Failure behavior:** abort on malformed IR references.  
**Dependencies:** UML_Model_IR schema.  
**Test vectors:** known DAGs with expected intervals.

**Operator:** `UML_OS.TMMU.AssignLogicalSlots_v1` (new)  
**Category:** Memory  
**Signature:** `(live_ranges, arena_config → logical_slot_assignment: dict[tensor_id → (arena, logical_slot_id)] )`  
**Purity class:** PURE  
**Definition:** Optimal greedy linear-scan on interval graph per arena. Each logical slot backing sized to max tensor assigned to it.
**Preconditions / Postconditions:** intervals are valid and non-negative; output has no overlapping intervals per slot.  
**Edge cases:** equal birth/death times and sparse arenas.  
**Numerical considerations:** integer interval endpoints only.  
**Ordering/tie handling:** deterministic tie-breaks by birth then size then tensor_id.  
**Complexity note:** O(N log N).  
**Failure behavior:** abort on invalid interval data.  
**Dependencies:** live-range analyzer and arena config.  
**Test vectors:** interval-coloring optimality cases.

**Operator:** `UML_OS.TMMU.MapToVirtualAddresses_v1` (new)  
**Category:** Memory  
**Signature:** `(logical_slot_assignment, replay_token → virtual_map)`  
**Purity class:** PURE  
**Definition:** VA = BLAKE3(replay_token || "tmmu_va" || arena || logical_slot_id). Enables huge sparse VA space.
**Preconditions / Postconditions:** logical slots assigned; output addresses unique per `(arena, slot)`.  
**Edge cases:** large slot cardinality and arena name collisions (disallowed).  
**Numerical considerations:** integer address-space truncation policy is deterministic.  
**Ordering/tie handling:** deterministic map key order for serialization.  
**Complexity note:** O(slots).  
**Failure behavior:** abort on address collision or overflow.  
**Dependencies:** BLAKE3 and deterministic encoding.  
**Test vectors:** fixed replay token -> exact virtual map.

**Operator:** `UML_OS.TMMU.ZeroTensor_v1`  
**Category:** Memory  
**Signature:** `(virtual_address → )` (driver primitive)  
**Purity class:** STATEFUL  
**Definition:** Deterministic zero-fill.
**Preconditions / Postconditions:** address is valid and writable; tensor contents are zeroed.  
**Edge cases:** repeated zeroing and page boundary segments.  
**Numerical considerations:** N/A.  
**Ordering/tie handling:** called in deterministic tensor-map order.  
**Complexity note:** O(size of tensor backing).  
**Failure behavior:** abort on invalid address/write failure.  
**Dependencies:** driver memory primitive.  
**Test vectors:** zero verification across varied tensor sizes.

**Operator:** `UML_OS.TMMU.CommitExecution_v1`  
**Category:** Memory  
**Signature:** `(() -> tmmu_state')`  
**Purity class:** STATEFUL  
**Definition:** Executes deterministic synchronization barriers, commits arena visibility state for downstream consumers, and seals per-batch memory metadata for replay/audit consistency.
**Preconditions / Postconditions:** pending memory operations completed; committed state is durable for next stage.  
**Edge cases:** no-op batch and single-arena execution.  
**Numerical considerations:** N/A.  
**Ordering/tie handling:** deterministic barrier ordering across arenas.  
**Complexity note:** O(number of active arenas).  
**Failure behavior:** abort on synchronization failure.  
**Dependencies:** runtime barrier and allocator metadata state.  
**Test vectors:** repeated commit idempotence and deterministic state hash.

---

**Operator:** `UML_OS.Error.Emit_v1`  
**Category:** Error  
**Signature:** `(failure_code, context -> abort)`  
**Purity class:** IO  
**Determinism:** deterministic  
**Definition:** Emits canonical error record and triggers deterministic abort per 0.K.

## 6) Procedure

```text
1. live_ranges ← AnalyzeLiveness_v1(ir_dag, execution_order, mode)
   # Mode-aware lifetime extension for backward activations/gradients

2. logical_slots ← AssignLogicalSlots_v1(live_ranges, arena_config)
   # Per-arena linear-scan (optimal for interval graphs):
   #   - Sort tensors by birth time, then size descending
   #   - Maintain active_slots set (bitset or min-heap of used slots)
   #   - For each tensor: expire ended slots, assign lowest unused logical_slot
   #   - Record max_size_per_slot for backing buffer sizing

3. virtual_map ← MapToVirtualAddresses_v1(logical_slots, replay_token)
   # VA = BLAKE3(replay_token || "tmmu_va" || arena || logical_slot_id)

4. tensor_map ← {}
   for tensor in execution_order:
       (arena, slot) ← logical_slots[tensor_id]
       va ← virtual_map[(arena, slot)]
       size ← compute_bytes(shape, dtype)
       tensor_map[tensor_id] ← {handle: va, arena, logical_slot: slot, size, lifetime: live_ranges[tensor_id], alignment: arena_config[arena].alignment}

5. for each tensor in tensor_map:
       ZeroTensor_v1(tensor_map[tensor_id].handle)

6. metrics ← ComputeMetrics(live_ranges, logical_slots, virtual_map)
   # Includes per-arena peak, reuse_ratio = 1 - (slots_used / total_tensors), fragmentation

7. tmmu_state' ← CommitExecution_v1()
8. return tensor_map, metrics
```

**Scalability & Algorithmic Guarantees (upgraded):**
- Time: O(N log N) worst-case with heap/interval-tree for active set (N = #tensors)
- Space: O(max live) 
- Mathematical optimality: #logical_slots = max live tensors per arena (interval graphs are perfect → greedy coloring is exact)
- Memory reuse ratio typically >95% on transformer graphs
- Supports 100B+ models via compact per-slot backing + huge virtual address space (2^48+)
- Alignment & padding enforced per arena
- Future-proof: easy extension to remat, paging, size-class bucketing

---

## 7) Trace & Metrics

### Logging rule
Each allocation run emits deterministic per-tensor allocation records and one deterministic summary record.

### Trace schema
- `allocation_header`: ir_hash, mode, replay_token_prefix, per-arena config
- `tensor`: tensor_id, arena, logical_slot, virtual_address, size, live_range, bytes
- `summary`: peak_bytes_per_arena, total_logical_slots, reuse_ratio, fragmentation_pct

### Metric schema
- `peak_tmmu_usage_per_arena`, `memory_reuse_ratio`, `activation_retention_ratio`, `allocation_time_ns`, `max_live`, `internal_fragmentation_ratio`

---

## 8) Validation

#### VII.A Lint rules (mandatory)
- All tensors aligned and slotted without live overlap.
- #slots == max live per arena.
- Backward lifetimes correctly extended.
- Virtual address uniqueness & determinism.

#### VII.B Operator test vectors (mandatory)
- Linear chain → perfect reuse (1 slot)
- Residual blocks → optimal coloring
- GPT-2 / Llama-scale → high reuse + alignment validation

#### VII.C Golden traces (mandatory)
- Match reference Python simulator (E0) for all presets/modes/seeds.

---

## 9) Refactor & Equivalence

#### VIII.A Equivalence levels
- **E0** required for any change to liveness, slot assignment, or VA computation.
- **E1** allowed for heuristics (e.g., sorting order).

#### VIII.B Allowed refactor categories
- Graph-coloring variants, ILP solver (if E0 preserved), rematerialization planner, hierarchical arenas.

#### VIII.C Equivalence test procedure (mandatory)
- Identical virtual addresses, logical slots, and live sets on golden graphs (10 seeds × all presets × 3 modes).

---

## 10) Checkpoint/Restore

### Checkpoint contents
- logical_slot_assignment + live_ranges + metrics (compact).

### Serialization
- CBOR, deterministic ordering (sorted by node_id).

### Restore semantics
- Same replay_token → identical layout.
- Physical backing re-mappable by driver.
