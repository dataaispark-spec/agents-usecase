# Changelog

## [1.2.1] — 2026-09-01

### Verified demo release

- Removed all committed `fraud_agents/__pycache__` bytecode
- CI simplified to lab path: unit tests + `demo_check` + `demo_emulator` (no Docker Hub secrets required for green CI)
- Added `scripts/demo_emulator.py` — headless DEMO.md flow
- Demo verified: impossible_travel → REVIEW → human confirm → flywheel; normal → AUTO_APPROVE

## [1.2.0] — 2026-09-01

- Slimmed repo: removed bundles, unused modules, outdated docs
- Minimal `requirements.txt`; clear README

## [1.1.2] — 2026-09-01

- `demo_check.py`, harness unit tests (16)

## [1.1.1] — 2026-09-01

- Rename to bfsi-agents-fraud-lab

## [1.1.0] — 2026-09-01

- Lab deploy: db factory, Docker overlay
