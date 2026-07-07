# System Architecture

## Overview

The Symbol Segmentor uses a layered architecture separating the **execution framework** (orchestration, logging, configuration) from the **research logic** (preprocessing, matching, verification).

## Architecture Layers

### Layer 1: Entry Points

| File | Purpose |
|------|---------|
| `install.py` | Environment setup, dependency installation, directory creation |
| `run.py` | CLI parsing, framework initialization, stage execution |

Both inject the project root into `sys.path` at startup, eliminating the `ModuleNotFoundError` that occurs when running scripts directly.

### Layer 2: Execution Framework (`src/framework/`)

| Module | Responsibility |
|--------|---------------|
| `config_manager.py` | Loads `config/project_config.yaml`, provides `get_config()` and `resolve_path()` |
| `validator.py` | Pre-flight checks: datasets, configs, permissions, metadata |
| `orchestrator.py` | Stage discovery, dependency resolution (topological sort), execution |
| `logger.py` | Dual-channel logging: verbose file + clean console |
| `progress.py` | `[n/total] StageName ... done (Xs)` display |
| `output_manager.py` | Timestamped directories, `latest/` mirroring |
| `error_handler.py` | Exception → human-readable report with cause/fix |
| `reproducibility.py` | Git hash, Python version, packages, config snapshot |

### Layer 3: Stage Wrappers (`src/stages/`)

Each wrapper:
1. Patches hardcoded paths in the original module
2. Validates prerequisites
3. Delegates to the original `main()` function
4. Reports success/failure via structured logging

### Layer 4: Research Modules (`src/preprocessing/`, `src/template_matching/`, etc.)

Original algorithm implementations. **These are never modified by the framework.**

## Data Flow

```
config/project_config.yaml
        │
        ▼
   run.py (CLI + config loading)
        │
        ▼
   framework/validator.py (pre-flight checks)
        │
        ▼
   framework/orchestrator.py (resolve stage order)
        │
        ▼
   stages/s01_preprocessing.py ──► src/preprocessing/*
   stages/s02_template_bank.py ──► src/template_bank/*
   stages/s03_chamfer_matching.py ──► src/template_matching/*
   stages/s04_coverage_rescoring.py ──► src/verification/coverage_rescoring.py
   stages/s05_verification.py ──► src/verification/structural_verification.py
   stages/s06_benchmarking.py ──► src/benchmarking/*
   stages/s07_visualization.py ──► src/visualization/*
        │
        ▼
   outputs/runs/<timestamp>/  +  reports/runs/<timestamp>/
```

## Key Design Principles

1. **No algorithm modification**: Framework changes orchestration only
2. **Path injection**: All hardcoded `BASE_DIR` values are patched at runtime
3. **Fail-forward**: Stage failures are caught; remaining stages continue
4. **Deterministic execution**: Random seed = 42, fixed across all runs
5. **Zero manual configuration**: `install.py` + `run.py` handles everything
