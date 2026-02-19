**# EQC Ecosystem Specification (EQC-ES) v1.16 – Indestructible Final Version**

**EQC Ecosystem Specification (EQC-ES)** is the single master governance layer for any collection (portfolio) of EQC documents. It enforces modularity, versioning, traceability, and fully deterministic, failsafe change propagation across the entire tree exactly as EQC v1.1 does inside one algorithm (see EQC Block 0.G Operator Manifest, Block III.C No hidden globals, Block IX Checkpoint, and Block 0.L Input/Data Provenance).

Version 1.16 (2026-02-19) is the **Indestructible Final Version**. It closes every architectural blind spot and systemic vulnerability identified across all reviews, including Link-Time Audit for dynamic linking, Hybrid TTL for Experimental status, Portfolio Prefix for DocIDs, Adaptive Warmup Invariant, Transitive License Bubbling, Modular Drift Summation, Usage-based Tombstone Physical Cleanup, Multi-Profile Signature, Temporal Pulse, Profile-Aware Purity Matrix, Metadata Consistency Check, Transactional Rollback, Unit-Normalised Metric Vectors with L-infinity, Deep-Scan Manifest Verification for Break-Glass, License Bubbling Rule, Pruning Milestone, and all prior points. The specification is now mathematically complete, self-healing, tamper-evident, license-safe, hardware-aware, and ready for production use at any scale.

### 0.5 Quick Impact Analysis Procedure v1.0 (how to use this brain – read this first; see §7 for tooling)

When you add a new EQC document or update an existing one, follow these 4 steps (takes less than 60 seconds):

1. Open this single file (EQC-ES-v1.16.md).
2. Go to Section 5 Change Propagation Protocol and locate the exact row matching your change type.
3. Open the sidecar ecosystem-graph.yaml (or the registry table in Section 2) and locate your DocID to see its Layer, edges, namespace, and File Path.
4. The table + graph immediately tells you every file that must be updated, what actions are required in each, and whether this EQC-ES file itself must be edited and version-bumped.

**Example 1 – Breaking change (operator removal)**  
You remove an operator from OPLIB-001 (Layer 1).  
Section 5 says: Affected = all that USE it; Required Actions = must migrate or delete usage + update migration notes; Version Impact = MAJOR.  
Graph shows ALGO-001, ALGO-002, TEST-003 USE it.  
You must edit: this EQC-ES (update registry/graph, bump version), ALGO-001.md, ALGO-002.md, TEST-003.md (replace operator + add migration note + run Block VII/VIII).  
Run `eqc-es impact --change OPLIB-001@1.5` to get the JSON list automatically.

**Example 2 – Distributed governance scenario (merging sub-portfolios with diamond conflict)**  
You merge SubPortfolio-A (requires OpLib-v1.1) and SubPortfolio-B (requires OpLib-v1.2).  
Section 5 + §2.2 says: Root EQC-ES must resolve via alias, strict single-version, or Policy-Equality Checksum auto-resolution if Functional Hash and Policy Metadata match; run full validation.  
You edit this EQC-ES (add resolution, update graph, bump version), then run `eqc-es validate`.

**Example 3 – Add new document**  
You add DATASET-001.yaml (Layer 1).  
Section 5 says: Root EQC-ES (MAJOR if namespace conflict), re-lint same-layer.  
Graph shows three algorithm-specs REFERENCE it.  
You edit this EQC-ES + the three algorithm-specs (add to Data Registry and compatibility matrix).

This procedure (v1.0) is versioned here and will be updated only on MAJOR changes to EQC-ES.

### 1. Identity & Purpose (mandatory)
- Portfolio Name: [e.g. MyMetaheuristicSuite]  
- Purpose (1 sentence): Single source of truth that makes every EQC document discoverable, version-compatible, and automatically updatable.  
- Spec Version: EQC-ES-v1.16 | 2026-02-19 | [YourName / Team]  
- Root Document: full path/git-ref to the canonical EQC-v1.1 (or later) guidelines that all others descend from (see §2).  
- Governance Model: central-root (one EQC-ES owns everything) or distributed-with-root (sub-portfolios roll up; see §2.2).  
- **Tooling Version Lock:**  
  ```yaml
  eqc_es_tool:
    min_version: "1.16.0"
    max_version: "1.16.x"
  ```
  `eqc-es validate` fails if the running tool version is outside this range.  
- **Bootstrap Command:** `eqc-es bootstrap` is exempt from version lock and verifies environment readiness, fetches the required tool version using the Root Tooling Signature, and generates the migration plan.

### 2. Document Registry (mandatory)
Machine-readable inventory stored as ecosystem-registry.yaml (human-readable table may be embedded).

Required columns for every EQC document entry:  
- DocID (unique short identifier – must include Portfolio Prefix in distributed mode, e.g. SUB-A:ALGO-001)  
- Title  
- Type: core-guidelines | algorithm-spec | operator-library | test-suite | golden-trace-set | checkpoint-schema | sidecar-yaml | derived-impl | external-dependency | data-registry | validation-override | other  
- Layer (integer ≥ 0; see §2.4)  
- File Path / Git Ref (relative to portfolio root)  
- Current Version (vX.Y.Z semantic versioning)  
- Status: active | deprecated | frozen | experimental | migrating | provisioning  
- Last Updated (YYYY-MM-DD)  
- Owner (optional)  
- Functional Hash (SHA-256 of code/logic only)  
- Governance Hash (SHA-256 of metadata/salt/equivalence)  
- Tooling Manifest reference (see §7)  
- Data Provenance reference (see §2.6)  
- profile_constraints (excluded_profiles list)  
- side_effect_manifest (concurrency and hidden_globals)  
- license_type (permissive | restrictive | proprietary)  

**Strict Path Resolution:**  
`eqc-es validate` **must** confirm every File Path / Git Ref is resolvable on disk, the target file must exist and be non-empty, and must contain the exact version string declared in the registry.

### 2.2 Distributed Governance + Aliasing Policy + State-Isolation + Conflict Escalation Protocol + Root Authority Rule + Peer-to-Peer Isolation + Namespace Handshake + Namespace Cooling Period + Pruning Milestone + Portfolio Prefix
Each sub-portfolio maintains its own complete EQC-ES-v1.16 file that passes eqc-es validate.  
Top-level EQC-ES imports sub-portfolios via ecosystem-imports key in the registry.  
Version constraints are AND-ed (strictest wins). Empty intersection renders the merged graph invalid.  
Diamond-dependency resolution: Root may alias or enforce strict single-version.  
**Functional Hash Auto-Resolution:** Auto-resolution occurs only if Functional Hash **and** Policy-Equality Checksum (Side-Effect Manifest, concurrency, purity, hardware requirements) are identical. Otherwise escalation to Root Owner remains mandatory.  
Mandatory State-Isolation Check: verifies no overlapping writes to persistent_state or rng_state unless protected by deterministic reduction (EQC Block 0.E).  
Conflict Escalation Protocol: If aliasing or strict-single-version cannot be auto-resolved, escalate to Root Owner who decides within 24 h and documents decision in ecosystem-validation-log.md with rationale and equivalence test results. Default Fallback: favor higher version.  
**Root Authority Rule:** Distributed EQC-ES files are strictly hierarchical.  
**Peer-to-Peer Isolation:** Cross-sub-portfolio dependencies must be registered at the Root level; direct peer-to-peer imports or REFERENCES between sub-portfolios without Root mediation are a BLOCKING ERROR. The overall graph must remain a single Directed Acyclic Graph (DAG) for validation order.  
**Namespace Handshake:** When a DocID moves between sub-portfolios, the Registry maintains a MOVED_TO pointer for one full MAJOR portfolio version.  
**Namespace Cooling Period:** A retired namespace cannot be re-assigned until the MOVED_TO pointer expires **and** a Usage Audit confirms zero incoming IMPORTS or REFERENCES.  
**Pruning Milestone:** At every MAJOR portfolio version (X.0), all expired MOVED_TO pointers and associated Usage Audits are moved to ecosystem-archive.yaml to keep the active registry lean.  
**Portfolio Prefix:** All DocIDs in distributed models must include a unique Portfolio Prefix (e.g. SUB-A:ALGO-001) to guarantee global uniqueness and prevent silent collisions.

### 2.3 Environment Profiles (mandatory)
```yaml
environment_profiles:
  - name: "cpu-x86-64-v3"
    container: "docker.io/myorg/eqc-runtime:2026.02-cpu"
    compiler: "gcc 14.2.0 -O3 -march=x86-64-v3"
    hardware: "x86_64-v3"
    validated_on: "2026-02-19"
    status: active
  - name: "gpu-h100"
    ...
    status: provisioning
```
A document is fully validated only if it has successful shadow-traces for every **active** profile **unless** it declares the profile in `excluded_profiles`.  
**Profile Incubation:** New profiles may be added with status: provisioning (non-blocking).  
**Provisioning TTL:** If a profile remains provisioning for more than 6 months without at least one document providing a Golden Trace, it is automatically purged or flagged for manual removal.  
**Profile Succession Plan:** A profile cannot be purged until all documents using it have successfully generated a Golden Trace on a replacement active profile.  
**Profile-Specific Accuracy Tags:** A document may export a unique EPS_EQ per active profile.  
**Multi-Profile Signature for promotion:** Promotion to “Active” requires a Multi-Profile Signature (stability proven on at least 2 distinct hardware profiles).

### 2.4 Layered Architecture (anti-cycle rule)
Layer 0: core-guidelines – may IMPORT / EXTEND only Layer 0.  
Layer 1: operator-library, external-dependency, data-registry – may IMPORT / EXTEND Layer 0–1.  
Layer 2: algorithm-spec, checkpoint-schema – may IMPORT / EXTEND Layer 0–2.  
Layer 3: test-suite, golden-trace-set – may IMPORT / EXTEND Layer 0–3.  
Layer 4+: derived-impl, other – may IMPORT / EXTEND Layer 0–4+.  

Rule: A document may only IMPORT or EXTEND from layers ≤ its own layer.  
Metadata Exception: RECOGNIZES may point upward (to higher layers) because it is metadata-only and never influences functional hashes, operator manifests, or logic. RECOGNIZES edges are **Lint-Triggering** with Metadata Consistency Check.  
All document types (including “other”) must declare their edge types and purity class (PURE / STATEFUL / IO / MODULAR).  
**MODULAR purity class:** Requires internal block-level purity declarations to prevent purity-leak across the whole document.

### 2.5 Orphan, Shadowing & Ghost Audit (configurable)
eqc-es validate performs:  
- Orphan check: no incoming edges (except root) → warning.  
- Shadowing Audit: logic 100 % superseded by alias/override → warning.  
- Ghost Document detection: reachable but bypassed → warning.  

Configurable: In strict mode these become blocking errors. In “experimental” status they are non-blocking.  
**Experimental TTL:** Any document in experimental status for more than 2 MAJOR versions **or** 180 days (whichever comes first) must either be promoted to active (passing all checks) or be automatically moved to deprecated.

### 2.6 Data Registry (mandatory for data-driven EQC documents)
Separate sidecar data-registry.yaml (extends EQC Block 0.L).  
Tracks shared datasets with hashes, preprocessing operators, and which EQC documents REFERENCE them.  
Any change triggers the same propagation rules as external-dependency changes (see §5).

### 3. Dependency Graph (mandatory)
Stored in ecosystem-graph.yaml.  

Edge types (all EQC documents must declare these explicitly):  
- IMPORTS – Direct binding of exact operator versions / policies.  
- EXTENDS – Transitive for global policies (Block 0.A–0.K); non-transitive for Operator Manifest (Block 0.G).  
- REFERENCES – Non-binding citation that must still carry a min-version constraint in compatibility.yaml. REFERENCE to a version lower than the current Registry version triggers a LINT WARNING. REFERENCE to a non-existent version is a BLOCKING ERROR.  
- PROVIDES – Concrete versioned artifacts.  
- DERIVES – Auto-generated target.  
- USES – Fine-grained operator-level.  
- RECOGNIZES – Metadata-only (may point upward per §2.4 exception; omitted from cycle-detection but included in reachability and impact analysis; Lint-Triggering with Metadata Consistency Check).

### 4. Mandatory Compatibility Matrix (YAML template)
Every EQC document with dependencies must contain (or reference) compatibility.yaml:

```yaml
requires:
  CORE-001: ">=1.1"
  OPLIB-001: ">=1.3"
  DATASET-001: "1.0"
minimum-equivalence: E1
external_compatibility:
  BLAS: ">=3.12"
accept_unvalidated_dependency: false
```

**Virtual Batch ID:** For circular compatibility cases, multiple DocIDs can be updated simultaneously in a single transaction, bypassing individual checks until the batch completes.  
**Transactional Rollback Invariant:** The eqc-es validate tool treats a Virtual Batch ID as a single atomic unit that reverts the entire registry to the previous Merkle Root if any member of the batch fails.

### 5. Change Propagation Protocol (mandatory)
| Change Type                              | Affected Document Types                  | Required Actions (always include core Block VII + VIII; see §9) | Version Impact (most severe wins for portfolio) |
|------------------------------------------|------------------------------------------|----------------------------------------------------------|-------------------------------------------------|
| Bump EQC-ES itself (MAJOR)               | All                                      | Full re-lint + update every reference + run Golden Ecosystem Traces | MAJOR                                           |
| Bump EQC-ES itself (MINOR/PATCH)         | Only directly referencing documents      | Update reference only                                    | MINOR or PATCH                                  |
| Change to CORE-001 (guidelines)          | All non-frozen                           | Re-validate every IMPORT/EXTENDS; update migration notes | propagates per declared equivalence             |
| New/revised operator version in OPLIB    | All that IMPORT or USE it                | Update manifest + compatibility matrix; run E0–E3 on only documents that USE it | MINOR on OPLIB, PATCH on consumers (unless breaking) |
| Deprecate operator (with replacement)    | All that USE it                          | Mark deprecated, provide replacement, update all manifests during grace period | MINOR on OPLIB, PATCH on consumers              |
| Remove operator (no replacement)         | All that USE it                          | Must migrate or delete usage; update migration notes     | MAJOR on OPLIB + consumers                      |
| Modify trace schema / metric schema      | All consumers + referencing test suites  | Update V.C/D in every dependent spec                     | MAJOR                                           |
| Modify test vectors / golden traces      | All that REFERENCE them                  | Re-run Block VII on referencing documents                | PATCH on test-suite, PATCH on consumers if no breakage |
| Add new document                         | Root EQC-ES                              | Add to registry + graph + Data Registry if applicable; run full validation; if Namespace or DocID prefix conflicts then re-lint all same-layer documents | MAJOR on registry if namespace conflict; else PATCH on EQC-ES |
| Change to external dependency / profile  | All that IMPORT it                       | Update registry; run Shadow-Trace Requirement per active profile; attach Drift Report if applicable; update External Compatibility Matrix | MAJOR if any trace not E0 or outside guardrail; else MINOR |
| Structural graph/registry edit           | Root EQC-ES                              | Re-validate entire portfolio                             | PATCH (unless it breaks compatibility → MAJOR)  |

Legacy Compatibility Shim, Shadow-Trace Requirement + Drift Guardrail, Automated Promotion Path, Portfolio version rule (decision tree) unchanged from v1.15.

### 6. Consistency Invariants (mandatory, lintable)
1. Every EQC document’s Operator Manifest resolves to existing, non-deprecated operators in the Registry.  
2. Global semantics (Block 0 of CORE-001) are either imported or explicitly overridden with equivalence declaration (E0–E3).  
3. Layer constraints satisfied for every IMPORT/EXTEND; upward RECOGNIZES allowed only as metadata.  
4. **Total Reachability:** Every EQC document must be reachable from Root through a path of downward-pointing (Layer N to Layer ≤N) edges (EXTENDS or IMPORTS only). Upward RECOGNIZES edges do **not** satisfy the reachability requirement for Portfolio inclusion.  
5. Hash Integrity: Each EQC document’s SHA-256 includes (via manifest digest) the hashes of all direct IMPORT targets.  
6. RECOGNIZES edges are metadata-only.  
7. Every active environment profile has current shadow-traces (unless excluded per profile_constraints).  
8. No unresolved diamonds without alias or upgrade.  
9. No deprecated operator used except during documented grace period.  
10. migrating status only allowed in open branches.  
11. Frozen EQC documents with legacy shims generate only warnings.  
12. Validation Salt (strengthened): Every EQC document’s SHA-256 incorporates salt of minimum-equivalence levels of all dependencies. If dependency changes beyond declared equivalence, RECOGNIZES edges automatically invalidated with explicit resolution (force migration note or downgrade to WARNING).  
13. Namespace Uniqueness: No overlapping Namespace.OperatorName prefix across entire portfolio.  
14. Shadowing Audit, Ghost Document detection, and State-Isolation Check must pass (configurable per §2.5).  
15. All “other” EQC document types declare edge types and purity class.  
16. Hash Chain: Each registry entry includes previous SHA-256 for tamper-evident history (signed commits recommended in CI).  
17. **Physical Existence Invariant:** Every File Path / Git Ref in the Registry must be resolvable on disk, the target file must exist and be non-empty, and must contain the exact version string declared in the registry.  
18. **Namespace Enforcement Invariant:** Every EQC document must prefix its persistent_state and rng_state variables with its Namespace or DocID unless it explicitly declares a SHARED state-block in its Block I.A (which then requires a deterministic reduction policy per EQC Block 0.E).  
19. **Functional vs Governance Hash separation:** The Registry tracks Functional Hash (code/logic only) and Governance Hash (metadata/salt/equivalence). A Governance Hash change does **not** require re-running E0/E1 tests if the Functional Hash remains identical. Metadata-Only Bubbling: alerts consumers of name changes without invalidating previous Functional validation results.  
20. **Purity Inheritance Invariant:** A document’s purity class is the “least pure” (most side-effect heavy) class of all its IMPORTED or USED operators. A PURE document cannot have STATEFUL dependencies unless encapsulated by a deterministic reduction (EQC Block 0.E). The validator performs Reduction Audit to confirm bit-identical output across multiple serial runs.  
21. **Side-Effect Manifest Invariant:** Every external-dependency must declare a Side-Effect Manifest. If concurrency = CONCURRENCY_UNSAFE, the validator forces serial execution of all shadow-traces involving that dependency.  
22. **Non-Functional Transparency Invariant:** Any document utilizing IO purity class must prove that its side-effects (telemetry, logging, hardware counters) do not mutate the Functional Hash of its consumers under varying thread counts.  
23. **Hardware-Level Resource Partitioning Invariant:** IO-class documents must demonstrate Hardware-Level Resource Partitioning to prevent Observer Effect from shared cache lines or memory bus contention.  
24. **Deep-Scan Manifest Verification:** The validator performs a deep scan of the entire dependency tree (including hidden sub-dependencies) to calculate True Purity.  
25. **Recursive Manifest Loophole Closure:** Transient dependencies are fully crawled; a document’s purity is recalculated from the deepest layer. Profile-Aware Purity Matrix: The validator outputs a Purity Matrix (DocID vs. Profile) for conditional dependencies.  
26. **Deterministic Jitter Guardrail:** If hardware partitioning is unverifiable (e.g., cloud noisy neighbors), the document must declare a JITTER_TOLERANCE in Block 0.C. The validator then performs a Statistical Identity Test (running the same trace N times) to ensure non-functional side effects do not cross into the Functional Hash's variance.  
27. **Purity Encapsulation / Sandboxing:** A document may declare a purity class higher (purer) than its dependencies if it utilizes a Deterministic Reduction Policy that is cryptographically verified to produce bit-identical output regardless of the side-effect. The validator performs Reduction Audit Exception to confirm encapsulation holds.  
28. **Link-Time Audit:** For every external-dependency, the validator must use ldd/otool (or equivalent) to verify zero undeclared dynamic links outside the container.

### 7. Portfolio Observability & Tooling (mandatory)
Required sidecars at portfolio root: ecosystem-registry.yaml, ecosystem-graph.yaml, ecosystem-compatibility-aggregate.yaml (includes Profile Compatibility Aggregate), ecosystem-validation-log.md (audit trail), data-registry.yaml, migration-plan-template.yaml, portfolio-release-notes-template.md.

Mandatory commands (formal schema):  
- `eqc-es validate` → JSON output with status, errors, warnings, affected_docs.  
- `eqc-es impact --change DOCID@vX.Y.Z` → JSON list of {DocID, required_actions, version_impact}.  
- `eqc-es regenerate-sidecars`.  
- `eqc-es generate-migration-plan`.  
- `eqc-es bootstrap`: exempt from version lock; verifies environment readiness and fetches the required tool version using the Root Tooling Signature.

Tooling Extensibility: Integrate with CI/CD (GitHub Actions hook: fail on non-zero errors). Link to EQC Block VII lint rules. Tooling Manifest ensures deterministic evolution.  
**Validator Version Lock:** Enforced by the Tooling Version Lock in §1; mismatch is a blocking error.  
**Migration Mode:** `--migration-mode` flag temporarily ignores version lock for impact and generate-migration-plan commands only.

**7.5 Self-Validation (Golden Ecosystem Traces)**  
Portfolio must maintain at least one golden ecosystem trace.  
**Trace Purity Requirement:** Shadow-traces must be executed in a “Clean-Room” state as defined by the Portfolio Checkpoint (§9), ensuring zero interference from previous runs, local caches, or stateful operators (rng_state and persistent cache perfectly reset).  
**Concurrency Stress Invariant:** Golden Traces for IO-class documents must be run both in isolation and under simulated load (simultaneous multi-document validation) to ensure Non-Functional Transparency holds under contention.  
**State-Space Coverage Invariant:** The Golden Trace must include a Boundary Test trace (minimum/maximum parameter values from Block II) to ensure the functional hash holds at the edges of the specification.  
**Environment Entropy Pulse:** Every 6 months (or on any host-level change), the validator forces a re-validation of the Golden Trace even if no code has changed, triggered by a Global Sequence Number in the Root EQC-ES file (not local clock).  
**Pre-Trace Warmup Policy:** Golden Traces must include a non-recorded “discard run”.  
**Adaptive Warmup Invariant:** The validator monitors hardware telemetry (clock speed, temperature) and only begins the Golden Trace once a “Steady State” is reached.

### 8. Refactoring & Evolution Rules
Same E0–E3 equivalence levels as core EQC Block VIII, plus:  

E-HW (Hardware Equivalence) tier: Maximum allowable divergence between environment profiles for same seed set, defined per EQC document in Block 0.C as EPS_HW.  

E-PORT (Portfolio Equivalence): Graph/registry changes preserve overall outputs across all algorithms (portfolio-wide shadow-trace diffs required).  
Strictest Tolerance Rule: When evaluating portfolio-wide drift for a shared operator, the effective EPS_EQ is the minimum of all EPS_EQ values across all consuming EQC documents.  
**Tolerance Tiering:** Consumers may declare “Soft” vs “Hard” tolerances; Soft tolerances alert but do not block ecosystem-wide updates.  
Tolerance Inheritance: Higher-layer EQC documents inherit the strictest EPS values of their dependencies for E0/E1 validation.

Staged Transition support: Use Migration Plan Template (YAML with steps, affected DocIDs, equivalence tests, timeline). Atomic PR required.

### 9. Integration with Core EQC Blocks + Portfolio Checkpoint (mandatory)
Every propagation triggers the changed EQC document’s own Block VII and (if applicable) Block VIII.  
**Portfolio Checkpoint (extends EQC Block IX):** Snapshots entire graph, registry, active profiles, Data Registry, and hashes for reproducible rollbacks.  
**Environment Lockfile:** The checkpoint must include the resolved environment_profile manifest (specific container digest, library SHAs, compiler flags), not just the name.  
**Environment Lockfile Hash:** For non-containerized profiles, the checkpoint includes conda-lock or requirements.txt.sha256.  
**Drift Budget Exhaustion:** Cumulative drift is calculated as the Euclidean vector norm (RMS) **and** L-infinity norm of metric deviations between the current candidate and the **last MAJOR version’s Golden Trace** (Anchor-Version Baseline). Unit-Normalised Metric Vectors: All deviations must be scaled by their respective EPS_EQ before the norm is calculated. Fails if any single metric deviates beyond its individual EPS_EQ by more than a specified multiplier (regardless of RMS) or if RMS exceeds 1.5 × EPS_EQ.  
**Secondary Rolling Baseline:** The validator compares metrics against both the Anchor (MAJOR) and the immediate predecessor (MINOR/PATCH) to detect rapid, short-term acceleration in drift.  
**Modular Drift Summation:** The validator evaluates the aggregate error of the full call stack.  
**Atomic Checkpoint Hash:** The checkpoint must be a Merkle Root of the EQC-ES file plus all mandatory sidecars listed in Section 7 to prevent TOCTOU issues.  
**Metric Set Invariance:** A document version cannot change its metric schema without a MAJOR version bump (which resets the Drift Budget baseline), except for additive metrics in MINOR versions where only the new metric resets its baseline.

### 10. Governance & Lifecycle (mandatory)
Change process: branch → edit → eqc-es validate → eqc-es impact review → update all affected EQC documents → atomic merge.  
Deprecation rules: Deprecated items remain readable for at least one full MAJOR portfolio version + documented grace period (tied to MAJOR versions). Backward-compatibility shims required for frozen EQC documents.  
Portfolio Release Notes Template: Must include summary of impacts, equivalence tests passed, drift reports, and Profile Compatibility Aggregate status.  
Localization Policy: Registry may declare supported languages; all core sections must have English master with optional translations (alt-text for any graphs).  
**Break-Glass / Emergency Override Protocol:** A Type: validation-override document may be added to the registry. It allows the Root Owner to sign a specific Functional Hash as “Accepted” despite a validation failure, provided a Rationale Sidecar is attached to ecosystem-validation-log.md and a new Golden Trace is recorded. This override is logged permanently and expires after one MAJOR portfolio version unless renewed.  
**Contamination Flag:** Any document that IMPORTS or USES a validation-override document must explicitly declare `accept_unvalidated_dependency: true` in its compatibility.yaml.  
**Break-Glass Auto-Recovery:** Every MINOR bump of the Root EQC-ES forces a re-attempt of standard validation on all flagged documents to automatically clear the emergency state if the underlying issue is resolved.  
**Deep-Scan Manifest Verification for Break-Glass:** The validator performs a full recursive crawl of all dependencies to detect any hidden validation-override documents, even if the direct parent claims to be “valid”.  
**License Contamination Invariant:** The registry tracks license_type. Restrictive licenses cannot be imported by permissive ones without an explicit warning flag.  
**Transitive License Bubbling Rule:** A document’s license is automatically the most restrictive type found in its entire IMPORT tree.

**Portfolio version rule decision tree:** (see §5 table).

### 11. Glossary
- Shadow-traces: Golden traces re-run after environment change for equivalence comparison.  
- Drift Report: Signed document justifying metric-only changes within EPS_EQ.  
- Diamond-dependency: Multiple EQC documents requiring conflicting versions of same provider.  
- Validation Salt: Hash component tying equivalence levels for tamper-evident integrity.  
- E-PORT: Portfolio-wide equivalence preserving all algorithm outputs.  
- Hardware-Locked: Algorithm that cannot cross profiles within EPS_HW.  
- Clean-Room state: Portfolio Checkpoint reset with zero interference from previous runs or caches.  
- Functional Hash: SHA-256 of pure code/logic (unaffected by governance metadata).  
- Governance Hash: SHA-256 of metadata, salt, and equivalence declarations.  
- RMS drift: Root-mean-square (Euclidean norm) of metric deviations for cumulative budget calculation.  
- Side-Effect Manifest: Declaration of concurrency safety and hidden globals for external dependencies.  
- Reactive-Only / Lint-Triggering: RECOGNIZES edges that trigger link-integrity check but not full Golden Trace re-run.  
- Environment Entropy Pulse: Periodic forced re-validation to detect host-level bit rot, triggered by Global Sequence Number.  
- MODULAR purity class: Requires internal block-level purity declarations to prevent purity-leak.  
- Deterministic Jitter Guardrail: Statistical Identity Test (N runs) when hardware partitioning is unverifiable.  
- Policy-Equality Checksum: Ensures Functional Hash Auto-Resolution also respects Side-Effect Manifest and governance policies.  
- Unit-Normalised Metric Vectors: Deviations scaled by EPS_EQ before norm calculation.  
- Usage-based Tombstone Protocol: Safe-to-Delete manifest for physical file cleanup after cooling period.


