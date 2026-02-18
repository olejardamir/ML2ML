# UML_OS Execution Certificate Contract
**EQC Compliance:** Merged single-file EQC v1.1 Option A.

**Algorithm:** `UML_OS.Certificate.ExecutionCertificate_v1`  
**Purpose (1 sentence):** Define a signed proof-carrying execution certificate that gates registry, deployment, and audit workflows.  
**Spec Version:** `UML_OS.Certificate.ExecutionCertificate_v1` | 2026-02-18 | Authors: Olejar Damir  
**Domain / Problem Class:** Verifiable execution provenance and policy gating.

---
## 1) Header & Global Semantics
### 0.0 Identity
- **Algorithm:** `UML_OS.Certificate.ExecutionCertificate_v1`
- **Purpose (1 sentence):** Kernel-issued execution proof contract.
- **Spec Version:** `UML_OS.Certificate.ExecutionCertificate_v1` | 2026-02-18 | Authors: Olejar Damir
- **Domain / Problem Class:** Signed execution evidence.
### 0.A Objective Semantics
- Minimize unverifiable releases and non-auditable promotions.
### 0.B Reproducibility Contract
- Replayable given `(manifest_hash, trace_root_hash, checkpoint_merkle_root, determinism_profile_hash)`.
### 0.C Numeric Policy
- Hashes/signatures exact bytes; no tolerance path.
### 0.D Ordering and Tie-Break Policy
- Certificate fields serialized in canonical key order.
### 0.E Parallel, Concurrency, and Reduction Policy
- One certificate per run_id; promotion checks deterministic across replicas.
### 0.F Environment and Dependency Policy
- `trust_mode: "SOFTWARE_ONLY" | "ATTESTED"` (default `SOFTWARE_ONLY`).
### 0.G Operator Manifest
- `UML_OS.Certificate.Build_v1`
- `UML_OS.Certificate.Sign_v1`
- `UML_OS.Certificate.Verify_v1`
- `UML_OS.Certificate.EvidenceValidate_v1`
- `UML_OS.Error.Emit_v1`
### 0.H Namespacing and Packaging
- `UML_OS.Certificate.*` operators are global governance operators.
### 0.I Outputs and Metric Schema
- Outputs: `(execution_certificate, verification_report)`
- Metrics: `certificate_valid`, `evidence_link_coverage`
- Completion status: `success | failed`
### 0.J Spec Lifecycle Governance
- Field additions are MINOR; required-field removals/changes are MAJOR.
### 0.K Failure and Error Semantics
- Abort on invalid signature/evidence mismatch.
### 0.L Input/Data Provenance
- Certificate must bind manifest, trace, checkpoint, sampler, DP, TMMU, backend, and attestation evidence.

---
## 2) System Model
### I.A Persistent State
- certificate registry and trust roots.
### I.B Inputs and Hyperparameters
- `run_id`, `manifest_hash`, `trace_root_hash`, `checkpoint_merkle_root`, `dp_accountant_state_hash?`, `sampler_config_hash`, `dataset_snapshot_id`, `tmmu_plan_hash`, `backend_binary_hash`, `determinism_profile_hash`, `attestation_quote_hash?`.
### I.C Constraints and Feasible Set
- Registry/deploy actions are invalid without a valid certificate.
### I.D Transient Variables
- evidence bundle hash, signature payload, verification diagnostics.
### I.E Invariants and Assertions
- One certificate signs one immutable evidence tuple.

### II.F ExecutionCertificate Structure (Normative)
- Required fields:
  - `certificate_version:string`
  - `run_id:string`
  - `manifest_hash:bytes32`
  - `trace_root_hash:bytes32`
  - `checkpoint_merkle_root:bytes32`
  - `sampler_config_hash:bytes32`
  - `dataset_snapshot_id:string`
  - `tmmu_plan_hash:bytes32`
  - `backend_binary_hash:bytes32`
  - `determinism_profile_hash:bytes32`
  - `step_start:uint64`
  - `step_end:uint64`
  - `signature:bytes`
- Optional fields:
  - `dp_accountant_state_hash:bytes32` (if DP enabled)
  - `attestation_quote_hash:bytes32` (required in `ATTESTED` mode)
  - `determinism_conformance_suite_id:bytes32`
  - `wall_time_start_utc:string` (non-replay-critical metadata)
  - `wall_time_end_utc:string` (non-replay-critical metadata)

Signature scheme (normative):
- canonical payload serialization: canonical CBOR
- signature algorithm: Ed25519

---
## 3) Initialization
1. Load trust mode and signing policy.
2. Validate required evidence hashes.
3. Build canonical signing payload.

---
## 4) Operator Manifest
- `UML_OS.Certificate.Build_v1`
- `UML_OS.Certificate.Sign_v1`
- `UML_OS.Certificate.Verify_v1`
- `UML_OS.Certificate.EvidenceValidate_v1`
- `UML_OS.Error.Emit_v1`

---
## 5) Operator Definitions
External operator reference: `UML_OS.Error.Emit_v1` is defined in `Error-Codes.md`.

**Operator:** `UML_OS.Certificate.Build_v1`  
**Category:** Security  
**Signature:** `(evidence_bundle -> certificate_payload)`  
**Purity class:** PURE  
**Determinism:** deterministic  
**Definition:** canonical payload construction from evidence tuple.

**Operator:** `UML_OS.Certificate.Sign_v1`  
**Category:** Security  
**Signature:** `(certificate_payload, signing_key_ref -> execution_certificate)`  
**Purity class:** IO  
**Determinism:** deterministic payload + deterministic signature algorithm policy  
**Definition:** signs payload; in `ATTESTED` mode key release requires attestation policy pass.

**Operator:** `UML_OS.Certificate.Verify_v1`  
**Category:** Security  
**Signature:** `(execution_certificate, trust_store -> verification_report)`  
**Purity class:** PURE  
**Determinism:** deterministic  
**Definition:** verifies signature, required fields, and trust chain.

**Operator:** `UML_OS.Certificate.EvidenceValidate_v1`  
**Category:** Security  
**Signature:** `(execution_certificate, manifest, trace, checkpoint, replay_context -> report)`  
**Purity class:** PURE  
**Determinism:** deterministic  
**Definition:** validates cross-artifact coherence and rejects mismatched evidence.

---
## 6) Procedure
```text
1. Build_v1(evidence_bundle)
2. Sign_v1(payload, signing_key_ref)
3. Verify_v1(certificate, trust_store)
4. EvidenceValidate_v1(certificate, manifest, trace, checkpoint, replay_context)
5. Return certificate + report
```

---
## 7) Trace & Metrics
### Logging rule
- Every certificate issuance and verification emits deterministic events.
### Trace schema
- `run_header`: certificate_version, trust_mode
- `iter`: run_id, certificate_hash, verify_status
- `run_end`: evidence_validation_status
### Metric schema
- `certificate_valid`, `evidence_mismatch_count`
### Comparability guarantee
- Comparable iff certificate schema, trust roots, and evidence validation rules are identical.

---
## 8) Validation
#### VII.A Lint rules (mandatory)
- required fields complete, signature present, deterministic serialization.
#### VII.B Operator test vectors (mandatory)
- valid signature, invalid signature, missing required evidence, mismatched hash tests.
#### VII.C Golden traces (mandatory)
- golden certificate verification traces.

---
## 9) Refactor & Equivalence
#### VIII.A Equivalence levels
- E0 for certificate bytes and verification verdict.
#### VIII.B Allowed refactor categories
- cryptographic implementation updates preserving inputs/outputs and trust policy.
#### VIII.C Equivalence test procedure (mandatory)
- byte-level compare + deterministic verdict compare.

---
## 10) Checkpoint/Restore
### Checkpoint contents
- last verified certificate hash and trust context hash.
### Serialization
- deterministic CBOR.
### Restore semantics
- restored verifier produces identical verdict on identical evidence bundle.
