# UML_OS Security and Compliance Profile
**EQC Compliance:** Merged single-file EQC v1.1 Option A.

**Algorithm:** `UML_OS.Security.ComplianceProfile_v1`  
**Purpose (1 sentence):** Define deterministic security/compliance requirements for managed, confidential, and regulated operation modes.  
**Spec Version:** `UML_OS.Security.ComplianceProfile_v1` | 2026-02-18 | Authors: Olejar Damir  
**Domain / Problem Class:** Security policy and regulated execution governance.

---
## 1) Header & Global Semantics
### 0.0 Identity
- **Algorithm:** `UML_OS.Security.ComplianceProfile_v1`
- **Purpose (1 sentence):** Security/compliance policy contract.
- **Spec Version:** `UML_OS.Security.ComplianceProfile_v1` | 2026-02-18 | Authors: Olejar Damir
- **Domain / Problem Class:** Auditable secure execution.
### 0.A Objective Semantics
- Optimization sense: `MINIMIZE`
- Objective type: `Scalar`
- Primary comparison rule: deterministic total preorder over declared primary metric tuple with `EPS_EQ` tie handling.
- Invalid objective policy: `NaN/Inf` ranked as worst-case and handled deterministically per 0.K.
- Minimize policy violations and unverifiable execution paths.
### 0.B Reproducibility Contract
- Replayable given `(policy_hash, attestation_hash, certificate_schema_version)`.
### 0.C Numeric Policy
- Compliance counters/thresholds in exact integer or binary64 as declared.
### 0.D Ordering and Tie-Break Policy
- Security checks execute in deterministic policy order.
### 0.E Parallel, Concurrency, and Reduction Policy
- Concurrent audits merged deterministically.
### 0.F Environment and Dependency Policy
- Determinism level: `BITWISE` for policy verdicts and signatures.
### 0.G Operator Manifest
- `UML_OS.Security.ValidatePolicy_v1`
- `UML_OS.Security.AttestTEE_v1`
- `UML_OS.Security.VerifyCertificate_v1`
- `UML_OS.Security.SignComplianceRecord_v1`
- `UML_OS.Error.Emit_v1`
### 0.H Namespacing and Packaging
- Fully-qualified security operators and signed sidecars required.
### 0.I Outputs and Metric Schema
- Outputs: `(compliance_report, signed_record)`.
- Metrics: `policy_violations`, `attestation_failures`, `signature_valid`.
- Completion status: `success | failed`.
### 0.J Spec Lifecycle Governance
- Regulatory-policy semantic changes require MAJOR bump.
### 0.K Failure and Error Semantics
- Abort on critical security failures.
### 0.L Input/Data Provenance
- Policy source, attestation evidence, and certificate chain are hash-addressed.

---
### 0.Z EQC Mandatory Declarations Addendum
- Seed space: `seed ∈ {0..2^64-1}` when stochastic sub-operators are used.
- PRNG family: `Philox4x32-10` for declared stochastic operators.
- Randomness locality: all sampling occurs only inside declared stochastic operators in section 5.
- Replay guarantee: replayable given (seed, PRNG family, numeric policy, ordering policy, parallel policy, environment policy).
- Replay token: deterministic per-run token contribution is defined and included in trace records.
- Floating-point format: IEEE-754 binary64 unless explicitly declared otherwise.
- Rounding mode: round-to-nearest ties-to-even unless explicitly overridden.
- Fast-math policy: forbidden for critical checks and verdict paths.
- Named tolerances: `EPS_EQ=1e-10`, `EPS_DENOM=1e-12`, and domain-specific thresholds as declared.
- NaN/Inf policy: invalid values trigger deterministic failure handling per 0.K.
- Normalized exponentials: stable log-sum-exp required when exponential paths are used (otherwise N/A).
- Overflow/underflow: explicit abort or clamp behavior must be declared (this contract uses deterministic abort on critical paths).
- Approx-equality: `a ≈ b` iff `|a-b| <= EPS_EQ` when tolerance checks apply.
- Transcendental functions policy: deterministic implementation requirements are inherited from consuming operators.
- Reference runtime class: CPU-only/GPU-enabled/distributed as required by the consuming workflow.
- Compiler/flags: deterministic compilation; fast-math disabled for critical paths.
- Dependency manifest: pinned runtime dependencies and versions are required.
- Determinism level: `BITWISE` for contract-critical outputs unless a stricter local declaration exists.
- Error trace rule: final failure record includes `t`, `failure_code`, `failure_operator`, replay token, and minimal diagnostics.
- Recovery policy: none unless explicitly declared; default is deterministic abort-only.


## 2) System Model
### I.A Persistent State
- compliance policy registry and signer metadata.
### I.B Inputs and Hyperparameters
- execution mode, policy set, attestation evidence.
### I.C Constraints and Feasible Set
- Valid if policy + attestation + signature requirements pass.
### I.D Transient Variables
- compliance diagnostics and signature payloads.
### I.E Invariants and Assertions
- no unsigned compliant status is accepted in regulated mode.

### II.F Threat Model and Governance (Normative)
- Threat model: malicious tenant code, compromised node runtime, stale/revoked attestations, unsigned artifact injection, and transport MITM.
- Trust boundaries and required controls:
  - tenant code ↔ runtime: sandboxing, least privilege, syscall policy.
  - runtime ↔ daemon/control plane: mTLS + attestation identity binding.
  - daemon ↔ storage: signed artifact verification + path segregation.
  - daemon ↔ KMS/HSM: authenticated key access + audit logging.
  - node ↔ network fabric: network policies + authenticated channels.
- Required attestation claims:
  - platform measurement/PCR set,
  - TCB version,
  - runtime config hash,
  - loaded driver hash,
  - policy hash.
- Key governance:
  - `key_origin: enum("KMS","HSM")`,
  - signing keys must reside in KMS/HSM-backed stores,
  - `rotation_max_age_days` and `rotation_procedure_hash` are mandatory,
  - revocation checks mandatory for quote certs, signing certs, and policy keys,
  - role-based signing authorization and audit trail.
- Access governance:
  - `access_control_model` (RBAC roles + required permissions),
  - `breakglass_policy` must be explicit, time-bounded, and fully audited.
  - operator-level capability enforcement is mandatory via `required_capabilities` from canonical operator registry.
  - authorization decision hash:
    - `authz_hash = SHA-256(CBOR_CANONICAL([tenant_id, principal_id, operator_id, sorted(required_capabilities), policy_hash]))`.
  - denied authorization decisions must be recorded as deterministic trace events and included in certificate evidence binding.
- Registry governance roles:
  - `registry_approver`, `registry_publisher`, `registry_auditor` (least-privilege RBAC mandatory).
- Multi-tenant requirement:
  - `tenant_id` must be present in run, trace, checkpoint, artifact, and registry records.
- Transport/security baseline:
  - mTLS required for control plane APIs,
  - service identity binding to attestation identity,
  - pinned trust roots and minimum cipher-suite policy are mandatory.
- Deterministic verification evidence bundle (mandatory for reproducible verdicts):
  - `revocation_mode: enum("ONLINE_CAPTURE","PINNED_OFFLINE_BUNDLE")`,
  - `trust_store_hash`,
  - `revocation_bundle_hash` (canonical hash of either online capture bundle or pinned offline bundle),
  - `attestation_bundle_hash`.
- Verification verdict determinism claim is scoped to identical evidence bundles and policy hash.
- Time-policy rule:
  - if verification time affects verdict, it must be frozen as an explicit declared input and included in signed evidence;
  - otherwise verification time is informational only and excluded from deterministic verdict computation.
- Regulated-mode trace redaction binding:
  - certificate signed payload must include `redaction_policy_hash` and `redaction_key_id` when `redaction_mode != NONE`.

---
## 3) Initialization
1. Load policy profile.
2. Validate signing keys and trust anchors.
3. Initialize compliance context.

---
## 4) Operator Manifest
- `UML_OS.Security.ValidatePolicy_v1`
- `UML_OS.Security.AttestTEE_v1`
- `UML_OS.Security.VerifyCertificate_v1`
- `UML_OS.Security.SignComplianceRecord_v1`
- `UML_OS.Error.Emit_v1`

---
## 5) Operator Definitions

External operator reference: `UML_OS.Error.Emit_v1` is defined normatively in `Error-Codes.md` and imported by reference.

Template conformance note (III.A): each operator definition in this section is interpreted with the full EQC operator template fields. When a field is not repeated inline, the section-level defaults are: explicit typed signatures, deterministic ordering/tie handling, declared numerical policy inheritance, deterministic failure semantics (0.K), explicit dependencies, and VII.B test-vector coverage.

**Operator:** `UML_OS.Security.ValidatePolicy_v1`  
**Category:** IO  
**Signature:** `(runtime_state, policy -> policy_report)`  
**Purity class:** PURE  
**Determinism:** deterministic  
**Definition:** validates runtime behavior against policy rules.

**Operator:** `UML_OS.Security.AttestTEE_v1`  
**Category:** Security  
**Signature:** `(runtime_state -> quote)`  
**Purity class:** STATEFUL  
**Determinism:** deterministic protocol path  
**Definition:** collects and validates TEE quote.

**Operator:** `UML_OS.Security.VerifyCertificate_v1`  
**Category:** Security  
**Signature:** `(certificate, trust_roots -> report)`  
**Purity class:** IO  
**Determinism:** deterministic  
**Definition:** verifies signature chains and required claims.

**Operator:** `UML_OS.Security.SignComplianceRecord_v1`  
**Category:** Security  
**Signature:** `(compliance_report, signing_key -> signed_record)`  
**Purity class:** IO  
**Determinism:** deterministic payload canonicalization  
**Definition:** signs canonical compliance payload.

---
## 6) Procedure
```text
1. ValidatePolicy_v1
2. AttestTEE_v1 (mode-dependent)
3. VerifyCertificate_v1
4. SignComplianceRecord_v1
5. Emit compliance_report + signed_record
```

---
## 7) Trace & Metrics
### Logging rule
All security checks emit deterministic audit records.
### Trace schema
- `run_header`: policy_hash, mode
- `iter`: check_id, result, evidence_hash
- `run_end`: compliance_status, signature_hash
### Metric schema
- `policy_violations`, `attestation_failures`, `signature_valid`
### Comparability guarantee
Comparable iff policy hash, trust roots, and evidence schema are identical.

---
## 8) Validation
#### VII.A Lint rules (mandatory)
Passes policy completeness, deterministic ordering, and traceability checks.
#### VII.B Operator test vectors (mandatory)
Valid/invalid policy and certificate fixtures.
#### VII.C Golden traces (mandatory)
Golden compliant and non-compliant execution audit traces.

---
## 9) Refactor & Equivalence
#### VIII.A Equivalence levels
- E0 for compliance verdict and signed payload hash.
#### VIII.B Allowed refactor categories
- verifier/signer implementation refactor preserving verdict semantics.
#### VIII.C Equivalence test procedure (mandatory)
Exact compliance report + signature verification comparison.

---
## 10) Checkpoint/Restore
### Checkpoint contents
- policy state, trust anchors, and partial audit records.
### Serialization
- deterministic canonical CBOR.
### Restore semantics
- resumed compliance evaluation yields identical verdict/signature.
