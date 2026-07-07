# Pipeline Execution Guide

## Overview

The pipeline is executed through a single command: `python run.py`.  This document describes the execution flow, stage ordering, and runtime behavior.

## Execution Flow

1. **CLI Parsing** — `argparse` processes `--benchmark`, `--visualize`, `--pipeline`, `--dataset`, `--config`
2. **Configuration Loading** — `config/project_config.yaml` is read (or custom via `--config`)
3. **Logging Setup** — Creates `logs/run_YYYYMMDD_HHMMSS.log`
4. **Output Directories** — Creates `outputs/runs/<ts>/` and `reports/runs/<ts>/`
5. **Repository Validation** — Checks datasets, configs, permissions
6. **Stage Discovery** — Imports all stage wrappers from `src/stages/`
7. **Dependency Resolution** — Topological sort based on `dependencies()`
8. **Stage Execution** — Runs each stage with shared `context` dict
9. **Reproducibility Report** — Records git hash, packages, config
10. **Latest Mirroring** — Copies outputs to `outputs/latest/`

## Stage Dependencies

```
preprocessing
    └── template_bank
            └── chamfer_matching
                    └── coverage_rescoring
                            └── verification
                                    └── benchmarking
preprocessing
    └── visualization
```

## CLI Reference

| Flag | Effect |
|------|--------|
| (none) | Run all stages in order |
| `--benchmark` | Run only benchmarking |
| `--visualize` | Run only visualization |
| `--pipeline NAME` | Run stages matching NAME |
| `--dataset PATH` | Override SLD directory |
| `--config FILE` | Use custom config file |
| `--help` | Show help |

## Output Organization

Each run creates:
```
outputs/runs/2026-07-07_121643/
├── template/           # Preprocessed template
├── diagrams/           # Per-SLD preprocessed outputs
│   ├── SLD1/
│   ├── SLD2/
│   └── ...
├── template_bank/      # Generated templates + manifest
├── distance_transforms/ # DT maps
├── score_maps/         # Chamfer score maps
├── candidates/         # CSV candidate files
└── ...

reports/runs/2026-07-07_121643/
├── visual_validation/  # Validation grids
├── benchmark/          # Benchmark reports
└── ...
```

Historical runs are never overwritten.

## Error Behavior

- All exceptions are caught at the stage level
- A human-readable error report is generated at `reports/system/error_report.md`
- The pipeline continues with remaining stages where possible
- No Python tracebacks are displayed to the user
- Full tracebacks are logged to the log file
