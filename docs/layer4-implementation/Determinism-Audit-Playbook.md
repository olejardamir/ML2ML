# UML_OS Determinism Audit Playbook
**EQC Compliance:** Merged single-file EQC v1.1 Option A.

**Algorithm:** `UML_OS.Replay.DeterminismAuditPlaybook_v1`
**Purpose (1 sentence):** Consolidate determinism verification rules, evidence bindings, and failure taxonomy for external audits.
**Spec Version:** `UML_OS.Replay.DeterminismAuditPlaybook_v1` | 2026-02-21 | Authors: Olejar Damir
**Normativity Legend:** `docs/layer1-foundation/Normativity-Legend.md`

## 1) Header & Global Semantics
### 0.0 Identity
- **Algorithm:** `UML_OS.Replay.DeterminismAuditPlaybook_v1`
- **Purpose (1 sentence):** Determinism evidence audit playbook.
- **Spec Version:** `UML_OS.Replay.DeterminismAuditPlaybook_v1` | 2026-02-21 | Authors: Olejar Damir
- **Domain / Problem Class:** reproducibility auditing.
### 0.A Objective Semantics
- Map determinism profile rules to observable evidence and deterministic failures.
### 0.B Reproducibility Contract
- Replayable given `(replay_token, determinism_profile_hash, trace_final_hash, checkpoint_hash, certificate_hash)`.
### 0.C Numeric Policy
- E1 tolerances from active profile; default fallback from replay contract.
### 0.D Ordering and Tie-Break Policy
- First divergence is earliest by `(t, operator_seq, field_path)`.
### 0.E Parallel, Concurrency, and Reduction Policy
- Multi-run comparison allowed; summaries reduce deterministically.
### 0.F Environment and Dependency Policy
- Requires env/toolchain hash lock and registry root lock.
### 0.G Operator Manifest
- `UML_OS.Replay.CompareTrace_v1`
- `UML_OS.Replay.VerifyReplayToken_v1`
- `UML_OS.Certificate.VerifyBoundHashes_v1`
### 0.H Namespacing and Packaging
- Audit package path: `audit/determinism/<run_id>/`.
### 0.I Outputs and Metric Schema
- Outputs: `(determinism_audit_report, failure_digest_hash)`.
### 0.J Spec Lifecycle Governance
- Failure digest schema is MAJOR-governed.
### 0.K Failure and Error Semantics
- Determinism violations emit deterministic failure digest.
### 0.L Input/Data Provenance
- Inputs from replay, trace, checkpoint, certificate, error-code contracts.

## 2) Profile-to-Evidence Mapping (Normative)
| profile_rule | evidence_fields | verifier |
|---|---|---|
| `E0 bitwise identity` | `trace_final_hash`, `checkpoint_hash`, critical field bytes | `UML_OS.Replay.CompareTrace_v1` |
| `E1 tolerance` | field-level tolerances + compared values | `UML_OS.Replay.CompareTrace_v1` |
| replay token binding | `replay_token`, `manifest_hash`, `env_manifest_hash` | `UML_OS.Replay.VerifyReplayToken_v1` |
| certificate consistency | bound hashes in signed payload | `UML_OS.Security.VerifyCertificate_v1` |

## 3) Failure Digest (Normative)
- `failure_digest = {failure_code, first_divergence_operator, first_divergence_path, trace_hash_lhs, trace_hash_rhs, evidence_refs}`.
- `failure_digest_hash = SHA-256(CBOR_CANONICAL(["failure_digest_v1", failure_digest]))`.

## 4) Error Taxonomy Reference
- Authoritative codes: `docs/layer1-foundation/Error-Codes.md`.

## 6) Procedure
```text
1. Verify replay-token and environment/registry bindings.
2. Compare trace/checkpoint/certificate commitments by profile rule.
3. Locate first deterministic divergence.
4. Emit determinism_audit_report and failure_digest_hash.
```
