# Astrocytech Conformance Kit

Internal Codename: **UML_OS**

This repository contains the deterministic runtime specifications, capability contracts, and conformance tooling for the Astrocytech ecosystem.

## Quick Start
1. Ensure you have Python 3.12+
2. Install dependencies: `pip install -e .`
3. Run sanity checks: `python tools/validate_data_integrity.py`

## Structure
* `contracts/`: CBOR/JSON source of truth for capabilities.
* `docs/`: Layered specification architecture.
* `tools/`: Automation and verification suite.
