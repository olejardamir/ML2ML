**# EQC Ecosystem Specification (EQC-ES) v1.13**

**EQC Ecosystem Specification (EQC-ES)** is the single master governance layer for any collection (portfolio) of EQC documents. It enforces modularity, versioning, traceability, and fully deterministic, failsafe change propagation across the entire tree exactly as EQC v1.1 does inside one algorithm (see EQC Block 0.G Operator Manifest, Block III.C No hidden globals, Block IX Checkpoint, and Block 0.L Input/Data Provenance).

Version 1.13 (2026-02-19) is the final, production-ready, self-validating release that closes every remaining architectural blind spot and systemic flaw: the Observer Effect / Non-Functional Transparency, RECOGNIZES upward deadlocks (Reactive-Only Metadata), Tooling Bootstrap Paradox (Migration Mode), Ghost Sub-Portfolio (Namespace Handshake), Temporal Drift Paradox (Environment Entropy Pulse), Namespace Uniqueness in distributed settings (Root Namespace Registry), Ghost Profile Gap (Profile Incubation), Break-Glass Dependency Poisoning (Contamination Flag), and Purity Inheritance Leak (Reduction Audit). All nine reviewer recommendations have been implemented with explicit invariants, YAML schemas, and validation rules.

### 0.5 Quick Impact Analysis Procedure v1.0 (how to use this brain – read this first; see §7 for tooling)

When you add a new EQC document or update an existing one, follow these 4 steps (takes less than 60 seconds):

1. Open this single file (EQC-ES-v1.13.md).
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
Section 5 + §2.2 says: Root EQC-ES must resolve via alias or strict single-version; run full validation.  
You edit this EQC-ES (add alias, update graph, bump version), then run `eqc-es validate`.

**Example 3 – Add new document**  
You add DATASET-001.yaml (Layer 1).  
Section 5 says: Root EQC-ES (MAJOR if namespace conflict), re-lint same-layer.  
Graph shows three algorithm-specs REFERENCE it.  
You edit this EQC-ES + the three algorithm-specs (add to Data Registry and compatibility matrix).

This procedure (v1.0) is versioned here and will be updated only on MAJOR changes to EQC-ES.

### 1. Identity & Purpose (mandatory)
- Portfolio Name: [e.g. MyMetaheuristicSuite]  
- Purpose (1 sentence): Single source of truth that makes every EQC document discoverable, version-compatible, and automatically updatable.  
- Spec Version: EQC-ES-v1.13 | 2026-02-19 | [YourName / Team]  
- Root Document: full path/git-ref to the canonical EQC-v1.1 (or later) guidelines that all others descend from (see §2).  
- Governance Model: central-root (one EQC-ES owns everything) or distributed-with-root (sub-portfolios roll up; see §2.2).  
- **Tooling Version Lock:**  
  ```yaml
  eqc_es_tool:
    min_version: "1.13.0"
    max_version: "1.13.x"
  ```
  `eqc-es validate` fails if the running tool version is outside this range.  
- **Migration Mode (new v1.13):** The CLI accepts `--migration-mode` flag, which temporarily ignores the version lock **only** for `impact` and `generate-migration-plan` commands, allowing users to see the upgrade path during MAJOR ecosystem migrations.

### 2. Document Registry (mandatory)
Machine-readable inventory stored as ecosystem-registry.yaml (human-readable table may be embedded).

Required columns for every EQC document entry:  
- DocID (unique short identifier)  
- Title  
- Type: core-guidelines | algorithm-spec | operator-library | test-suite | golden-trace-set | checkpoint-schema | sidecar-yaml | derived-impl | external-dependency | data-registry | validation-override | other  
- Layer (integer ≥ 0; see §2.4)  
- File Path / Git Ref (relative to portfolio root)  
- Current Version (vX.Y.Z semantic versioning)  
- Status: active | deprecated | frozen | experimental | migrating | provisioning (new v1.13 for profiles)  
- Last Updated (YYYY-MM-DD)  
- Owner (optional)  
- Functional Hash (SHA-256 of code/logic only)  
- Governance Hash (SHA-256 of metadata/salt/equivalence)  
- Tooling Manifest reference (see §7)  
- Data Provenance reference (see §2.6)  
- profile_constraints (excluded_profiles list)  
- side_effect_manifest (concurrency and hidden_globals)  

**Strict Path Resolution:**  
`eqc-es validate` **must** confirm every File Path / Git Ref is resolvable on disk, the target file must exist and be non-empty, and must contain the exact version string declared in the registry.

### 2.2 Distributed Governance + Aliasing Policy + State-Isolation + Conflict Escalation Protocol + Root Authority Rule + Peer-to-Peer Isolation + Namespace Handshake
Each sub-portfolio maintains its own complete EQC-ES-v1.13 file that passes eqc-es validate.  
Top-level EQC-ES imports sub-portfolios via ecosystem-imports key in the registry.  
Version constraints are AND-ed (strictest wins). Empty intersection renders the merged graph invalid.  
Diamond-dependency resolution: Root may alias (e.g. OpLib_v1.1 AS LegacyOpLib) or enforce strict single-version.  
Mandatory State-Isolation Check: verifies no overlapping writes to persistent_state or rng_state unless protected by deterministic reduction (EQC Block 0.E).  
Conflict Escalation Protocol: If aliasing or strict-single-version cannot be auto-resolved, escalate to Root Owner who decides within 24 h and documents decision in ecosystem-validation-log.md with rationale and equivalence test results.  
**Root Authority Rule:** Distributed EQC-ES files are strictly hierarchical.  
**Peer-to-Peer Isolation:** Cross-sub-portfolio dependencies must be registered at the Root level; direct peer-to-peer imports or REFERENCES between sub-portfolios without Root mediation are a BLOCKING ERROR. The overall graph must remain a single Directed Acyclic Graph (DAG) for validation order.  
**Namespace Handshake (new v1.13):** When a DocID moves between sub-portfolios, the Registry maintains a MOVED_TO pointer for one full MAJOR portfolio version to prevent immediate DAG collapse.

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
    status: provisioning   # new v1.13
```
A document is fully validated only if it has successful shadow-traces for every **active** profile **unless** it declares the profile in `excluded_profiles`.  
**Profile Incubation (new v1.13):** New profiles may be added with status: provisioning (non-blocking). They become active only after at least one document provides a Golden Trace for them.

### 2.4 Layered Architecture (anti-cycle rule)
Layer 0: core-guidelines – may IMPORT / EXTEND only Layer 0.  
Layer 1: operator-library, external-dependency, data-registry – may IMPORT / EXTEND Layer 0–1.  
Layer 2: algorithm-spec, checkpoint-schema – may IMPORT / EXTEND Layer 0–2.  
Layer 3: test-suite, golden-trace-set – may IMPORT / EXTEND Layer 0–3.  
Layer 4+: derived-impl, other – may IMPORT / EXTEND Layer 0–4+.  

Rule: A document may only IMPORT or EXTEND from layers ≤ its own layer.  
Metadata Exception: RECOGNIZES may point upward (to higher layers) because it is metadata-only and never influences functional hashes, operator manifests, or logic. RECOGNIZES edges are **Reactive-Only (new v1.13)**: they cannot trigger mandatory re-validation of the target document.  
All document types (including “other”) must declare their edge types and purity class (PURE / STATEFUL / IO) in the registry.

### 2.5 Orphan, Shadowing & Ghost Audit (configurable)
eqc-es validate performs:  
- Orphan check: no incoming edges (except root) → warning.  
- Shadowing Audit: logic 100 % superseded by alias/override → warning.  
- Ghost Document detection: reachable but bypassed → warning.  

Configurable: In strict mode these become blocking errors. In “experimental” status they are non-blocking; after 3 MAJOR portfolio versions they auto-trigger deprecation proposal.

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
- RECOGNIZES – Metadata-only (may point upward per §2.4 exception; omitted from cycle-detection but included in reachability and impact analysis; Reactive-Only).

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
accept_unvalidated_dependency: false   # new v1.13 for Break-Glass
```

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

Legacy Compatibility Shim, Shadow-Trace Requirement + Drift Guardrail, Automated Promotion Path, Portfolio version rule (decision tree) unchanged from v1.12.

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
19. **Functional vs Governance Hash separation:** The Registry tracks Functional Hash (code/logic only) and Governance Hash (metadata/salt/equivalence). A Governance Hash change does **not** require re-running E0/E1 tests if the Functional Hash remains identical.  
20. **Purity Inheritance Invariant:** A document’s purity class is the “least pure” (most side-effect heavy) class of all its IMPORTED or USED operators. A PURE document cannot have STATEFUL dependencies unless encapsulated by a deterministic reduction (EQC Block 0.E). The validator performs Reduction Audit to confirm bit-identical output across multiple serial runs.  
21. **Side-Effect Manifest Invariant:** Every external-dependency must declare a Side-Effect Manifest. If concurrency = CONCURRENCY_UNSAFE, the validator forces serial execution of all shadow-traces involving that dependency.  
22. **Non-Functional Transparency Invariant (new v1.13):** Any document utilizing IO purity class must prove that its side-effects (telemetry, logging, hardware counters) do not mutate the Functional Hash of its consumers under varying thread counts.

### 7. Portfolio Observability & Tooling (mandatory)
Required sidecars at portfolio root: ecosystem-registry.yaml, ecosystem-graph.yaml, ecosystem-compatibility-aggregate.yaml (includes Profile Compatibility Aggregate), ecosystem-validation-log.md (audit trail), data-registry.yaml, migration-plan-template.yaml, portfolio-release-notes-template.md.

Mandatory commands (formal schema):  
- `eqc-es validate` → JSON output with status, errors, warnings, affected_docs.  
- `eqc-es impact --change DOCID@vX.Y.Z` → JSON list of {DocID, required_actions, version_impact}.  
- `eqc-es regenerate-sidecars`.  
- `eqc-es generate-migration-plan`.

Tooling Extensibility: Integrate with CI/CD (GitHub Actions hook: fail on non-zero errors). Link to EQC Block VII lint rules. Tooling Manifest ensures deterministic evolution.  
**Validator Version Lock:** Enforced by the Tooling Version Lock in §1; mismatch is a blocking error.  
**Migration Mode (new v1.13):** `--migration-mode` flag temporarily ignores version lock for impact and generate-migration-plan commands only.

**7.5 Self-Validation (Golden Ecosystem Traces)**  
Portfolio must maintain at least one golden ecosystem trace.  
**Trace Purity Requirement:** Shadow-traces must be executed in a “Clean-Room” state as defined by the Portfolio Checkpoint (§9), ensuring zero interference from previous runs, local caches, or stateful operators (rng_state and persistent cache perfectly reset).  
**Environment Entropy Pulse (new v1.13):** Every 6 months (or on any host-level change), the validator forces a re-validation of the Golden Trace even if no code has changed, to detect silent host-level bit rot.

### 8. Refactoring & Evolution Rules
Same E0–E3 equivalence levels as core EQC Block VIII, plus:  

E-HW (Hardware Equivalence) tier: Maximum allowable divergence between environment profiles for same seed set, defined per EQC document in Block 0.C as EPS_HW.  

E-PORT (Portfolio Equivalence): Graph/registry changes preserve overall outputs across all algorithms (portfolio-wide shadow-trace diffs required).  
Strictest Tolerance Rule: When evaluating portfolio-wide drift for a shared operator, the effective EPS_EQ is the minimum of all EPS_EQ values across all consuming EQC documents.  
Tolerance Inheritance: Higher-layer EQC documents inherit the strictest EPS values of their dependencies for E0/E1 validation.

Staged Transition support: Use Migration Plan Template (YAML with steps, affected DocIDs, equivalence tests, timeline). Atomic PR required.

### 9. Integration with Core EQC Blocks + Portfolio Checkpoint (mandatory)
Every propagation triggers the changed EQC document’s own Block VII and (if applicable) Block VIII.  
**Portfolio Checkpoint (extends EQC Block IX):** Snapshots entire graph, registry, active profiles, Data Registry, and hashes for reproducible rollbacks.  
**Environment Lockfile:** The checkpoint must include the resolved environment_profile manifest (specific container digest, library SHAs, compiler flags), not just the name.  
**Drift Budget Exhaustion:** Cumulative drift is calculated as the Euclidean vector norm (RMS) of metric deviations between the current candidate and the **last MAJOR version’s Golden Trace**. If the norm exceeds 1.5 × EPS_EQ of any root-referenced EQC document, a MAJOR version bump and new Golden Trace are mandatory.  
**Atomic Checkpoint Hash:** The checkpoint must include the SHA-256 hash of the current EQC-ES file itself to prevent detached checkpoints.

### 10. Governance & Lifecycle (mandatory)
Change process: branch → edit → eqc-es validate → eqc-es impact review → update all affected EQC documents → atomic merge.  
Deprecation rules: Deprecated items remain readable for at least one full MAJOR portfolio version + documented grace period (tied to MAJOR versions). Backward-compatibility shims required for frozen EQC documents.  
Portfolio Release Notes Template: Must include summary of impacts, equivalence tests passed, drift reports, and Profile Compatibility Aggregate status.  
Localization Policy: Registry may declare supported languages; all core sections must have English master with optional translations (alt-text for any graphs).  
**Break-Glass / Emergency Override Protocol:** A Type: validation-override document may be added to the registry. It allows the Root Owner to sign a specific Functional Hash as “Accepted” despite a validation failure (hardware non-determinism, etc.), provided a Rationale Sidecar is attached to ecosystem-validation-log.md and a new Golden Trace is recorded. This override is logged permanently and expires after one MAJOR portfolio version unless renewed.  
**Contamination Flag (new v1.13):** Any document that IMPORTS or USES a validation-override document must explicitly declare `accept_unvalidated_dependency: true` in its compatibility.yaml.

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
- Reactive-Only: RECOGNIZES edges that do not trigger mandatory re-validation of the target.  
- Environment Entropy Pulse: Periodic forced re-validation to detect host-level bit rot.


