# Command Line Reference

## Synopsis

```
python run.py [OPTIONS]
```

## Options

| Option | Argument | Description |
|--------|----------|-------------|
| (none) | — | Run the complete pipeline (all stages) |
| `--benchmark` | — | Run only the benchmarking stage |
| `--visualize` | — | Run only the visualization stage |
| `--pipeline` | `NAME` | Run only stages whose name contains `NAME` |
| `--dataset` | `PATH` | Override the SLD dataset directory |
| `--config` | `FILE` | Use a custom YAML configuration file |
| `-h`, `--help` | — | Display help and exit |

## Examples

### Run Everything
```bash
python run.py
```

### Preprocessing Only
```bash
python run.py --pipeline preprocessing
```

### Benchmark Only
```bash
python run.py --benchmark
```

### Custom Configuration
```bash
python run.py --config config/experiment_a.yaml
```

### External Dataset
```bash
python run.py --dataset C:\datasets\new_slds\
```

### Combined Flags
```bash
python run.py --pipeline preprocessing --config custom.yaml --dataset ./test_slds/
```

## Exit Codes

| Code | Meaning |
|------|---------|
| 0 | All stages completed successfully |
| 1 | One or more stages failed (see error report) |

## Environment Variables

None required.  All configuration is through `config/project_config.yaml` or CLI flags.

## Installation Command

```bash
python install.py
```

No flags are needed.  The installer is fully automatic.
