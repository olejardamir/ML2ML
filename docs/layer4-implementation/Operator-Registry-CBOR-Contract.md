# UML_OS Operator Registry CBOR Contract
**EQC Compliance:** Merged single-file EQC v1.1 Option A.

**Algorithm:** `UML_OS.Registry.OperatorRegistryCBOR_v1`
**Purpose (1 sentence):** Define the canonical machine-readable `operator_registry.cbor` artifact used by codegen, lint, runtime validation, and release evidence.
**Spec Version:** `UML_OS.Registry.OperatorRegistryCBOR_v1` | 2026-02-19 | Authors: Olejar Damir
**Domain / Problem Class:** Operator interface artifact governance.

---
## 1) Header & Global Semantics
### 0.0 Identity
- **Algorithm:** `UML_OS.Registry.OperatorRegistryCBOR_v1`
- **Purpose (1 sentence):** Canonical registry artifact for operator contracts.
### 0.A Objective Semantics
- Ensure a single deterministic source for operator signatures and constraints.
### 0.B Reproducibility Contract
- Artifact replayable and hash-identical from `(operator_entries, schema_digests, error_registry_hash, cbor_profile_hash)`.
### 0.C Numeric Policy
- N/A except deterministic integer ordering and binary-safe digest handling.
### 0.D Ordering and Tie-Break Policy
- Operator records sorted by `(operator_id, version)`; fields sorted by canonical CBOR rules.
### 0.E Parallel, Concurrency, and Reduction Policy
- Registry generation may parallelize parsing, but final merge order is deterministic.
### 0.F Environment and Dependency Policy
- Canonical serialization uses `docs/layer1-foundation/Canonical-CBOR-Profile.md`.
### 0.G Operator Manifest
- `UML_OS.Registry.BuildOperatorRegistryArtifact_v1`
- `UML_OS.Registry.ValidateOperatorRegistryArtifact_v1`
- `UML_OS.Implementation.SpecLint_v1`
- `UML_OS.Error.Emit_v1`
### 0.H Namespacing and Packaging
- Canonical artifact path: `contracts/operator_registry.cbor`.
### 0.I Outputs and Metric Schema
- Outputs: `(operator_registry_cbor, operator_registry_root_hash, validation_report)`.
### 0.J Spec Lifecycle Governance
- Field-set or digest preimage change is MAJOR.
### 0.K Failure and Error Semantics
- Invalid records or digest mismatches fail deterministically.
### 0.L Input/Data Provenance
- Inputs include API interface contracts, mapping contracts, and error registry snapshot.

---
## 2) System Model
### I.A Persistent State
- Registry artifact history and published root hashes.
### I.B Inputs and Hyperparameters
- Operator entries, schema digests, error-code allowlists, purity classes, capability requirements.
### I.C Constraints and Feasible Set
- `operator_id` unique per version; no duplicate `(operator_id, version)` entries.
### I.D Transient Variables
- parse table, normalized entry list, digest resolution cache.
### I.E Invariants and Assertions
- `signature_digest` must match canonical preimage formula from `docs/layer1-foundation/Operator-Registry-Schema.md`.

### II.F Canonical Artifact Schema (Normative)
```yaml
operator_registry:
  registry_version: string
  generated_at: date
  entries:
    - operator_id: string
      version: string
      surface: string
      method: string
      request_schema_digest: bytes32
      response_schema_digest: bytes32
      signature_digest: bytes32
      side_effects: [enum]
      allowed_error_codes: [enum]
      purity_class: enum
      required_capabilities: [string]
```

### II.G Artifact Hash (Normative)
- `operator_registry_root_hash = SHA-256(CBOR_CANONICAL(["operator_registry_v1", operator_registry]))`
- This hash must match `operator_contracts_root_hash` in `docs/layer2-specs/Execution-Certificate.md`.

---
## 3) Procedure
```text
1. Load operator entries from docs/layer1-foundation/API-Interfaces.md and docs/layer4-implementation/Code-Generation-Mapping.md
2. Resolve digest_refs using docs/layer1-foundation/Digest-Catalog.md
3. Normalize + validate entry schema
4. Encode canonical CBOR and compute operator_registry_root_hash
5. Emit artifact and validation report
```

---
## 4) Validation
- Golden vectors for serialization and digest stability.
- Cross-check against `docs/layer1-foundation/Operator-Registry-Schema.md`.
- Cross-check signatures against `docs/layer4-implementation/Backend-Adapter-Guide.md`.

---
## 5) Wiring References
- `docs/layer1-foundation/API-Interfaces.md`
- `docs/layer1-foundation/Operator-Registry-Schema.md`
- `docs/layer1-foundation/Digest-Catalog.md`
- `docs/layer4-implementation/Code-Generation-Mapping.md`
- `docs/layer4-implementation/Backend-Adapter-Guide.md`
- `docs/layer4-implementation/Repo-Layout-and-Interfaces.md`
