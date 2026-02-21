# UML_OS Tooling Suite Contract
**EQC Compliance:** Merged single-file EQC v1.1 Option A.

**Algorithm:** `UML_OS.Implementation.ToolingSuiteContract_v1`  
**Purpose (1 sentence):** Define deterministic tool interfaces, output schemas, and hash commitments for first-party UML_OS tooling.  
**Spec Version:** `UML_OS.Implementation.ToolingSuiteContract_v1` | 2026-02-21 | Authors: Olejar Damir  
**Normativity Legend:** `docs/layer1-foundation/Normativity-Legend.md`

---
## 1) Header & Global Semantics
### 0.0 Identity
- **Algorithm:** `UML_OS.Implementation.ToolingSuiteContract_v1`
- **Purpose (1 sentence):** Deterministic tooling interoperability.
### 0.A Objective Semantics
- Tooling outputs are machine-verifiable and replayable.
### 0.B Reproducibility Contract
- Replayable given `(tool_id, tool_version, input_bundle_hash, output_schema_version, canonical_profile_id)`.
### 0.C Numeric Policy
- Numeric outputs use explicit scalar types; no locale-sensitive formatting.
### 0.D Ordering and Tie-Break Policy
- All object outputs are canonical CBOR maps; arrays with ordering semantics use deterministic sort keys defined per tool.
### 0.E Parallel, Concurrency, and Reduction Policy
- Parallel execution allowed; output merge is deterministic fail-dominant.
### 0.F Environment and Dependency Policy
- Canonical serialization profile is `CanonicalSerialization_v1`.
### 0.G Referenced Operators (Template-only)
- Template-only: listed operators are roadmap entry-points and are non-normative until each has a contract definition and a registry row.
- `UML_OS.Tooling.ManifestInit_v1`
- `UML_OS.Tooling.MigrationAssist_v1`
- `UML_OS.Tooling.ReplayShadowMonitor_v1`
- `UML_OS.Tooling.TraceSemanticDiff_v1`
- `UML_OS.Error.Emit_v1`
### 0.H Namespacing and Packaging
- Tool IDs: `umlos-init`, `umlos-migrate-assist`, `umlos-replay-monitor`, `umlos-trace-diff`.
### 0.I Outputs and Metric Schema
- Outputs: `(tooling_report, tooling_bundle_hash, tooling_verdict)`.
### 0.J Spec Lifecycle Governance
- Output schema changes are MAJOR-governed.
### 0.K Failure and Error Semantics
- Any schema violation in emitted tool output is deterministic failure.
### 0.L Input/Data Provenance
- Tool inputs and outputs must be content-addressed.

### 0.Z EQC Mandatory Declarations Addendum
- `stochastic_used: false`
- `seed_space: N/A`
- `prng_family: N/A`
- `rng_ownership: N/A`
- `numeric_kernel: N/A`
- `tolerances: N/A`
- `determinism_level: BITWISE`
- `error_trace: inherited from docs/layer1-foundation/Error-Codes.md`

---
## 2) Tool Output Schemas (Normative)
### I.A `umlos init`
- Output schema:
  - `manifest_path:string`
  - `manifest_hash:bytes32`
  - `validation_report_hash:bytes32`
  - `profile_id:enum(core|enterprise|regulated)`

### I.B `umlos migrate-assist`
- Output schema:
  - `input_artifact_hash:bytes32`
  - `migrated_artifact_hash:bytes32`
  - `migration_report_hash:bytes32`
  - `equivalence_verdict:enum(pass|fail)`

### I.C `umlos replay-monitor`
- Output schema:
  - `run_id:string`
  - `shadow_replay_trace_hash:bytes32`
  - `divergence_summary_hash:bytes32`
  - `monitor_verdict:enum(pass|fail)`

### I.D `umlos trace-diff`
- Output schema:
  - `lhs_trace_hash:bytes32`
  - `rhs_trace_hash:bytes32`
  - `first_divergence_path:string`
  - `determinism_class:enum(E0|E1|E2)`
  - `diff_report_hash:bytes32`

---
## 3) Hash Commitments (Normative)
- Tooling bundle identity:
  - `tooling_bundle_hash = SHA-256(CBOR_CANONICAL(["tooling_suite_v1", tool_outputs_map]))`
- Per-tool output identity:
  - `tool_output_hash = SHA-256(CBOR_CANONICAL(["tool_output_v1", [tool_id, output_object]]))`

---
## 4) Procedure
```text
1. Execute each enabled tooling component with canonical input artifacts.
2. Validate each emitted output object against its schema.
3. Compute per-tool output hashes and aggregate tooling_bundle_hash.
4. Emit deterministic tooling_report and final tooling_verdict.
```

---
## 6) Procedure
```text
1. Execute each enabled tooling component with canonical input artifacts.
2. Validate each emitted output object against its schema.
3. Compute per-tool output hashes and aggregate tooling_bundle_hash.
4. Emit deterministic tooling_report and final tooling_verdict.
```
