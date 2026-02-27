# Determinism Profile v0.1
Status: STUB / DRAFT

## Stop-the-Line Rule
If any determinism regression is detected (hash drift, ordering variance, or non-repeatable outputs), stop feature work immediately. Add or expand conformance vectors to reproduce the issue, fix determinism, and re-run verification before resuming feature development.

This document defines the constraints required for a runtime to be considered "Deterministic" under the Glyphser specification.
See `docs/layer1-foundation/Determinism-Profiles.md` for technical details.
