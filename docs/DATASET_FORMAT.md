# Dataset Format Specification

## Input SLD Images

| Property | Requirement |
|----------|-------------|
| **Location** | `data/raw/slds/` |
| **Format** | PNG (RGBA or RGB) |
| **Naming** | `SLD<number>.png` (e.g., `SLD1.png`, `SLD2.png`) |
| **Resolution** | Any (pipeline adapts automatically) |
| **Color** | Grayscale or color (converted to grayscale in Stage 1) |
| **Minimum size** | 10 x 10 pixels |

## Template Symbol

| Property | Requirement |
|----------|-------------|
| **Location** | `data/raw/templates/MR_Symbol.png` |
| **Format** | PNG with transparent background (RGBA recommended) |
| **Content** | Reference circuit symbol to locate in SLDs |
| **Resolution** | High resolution preferred (downscaled by template bank) |

## Ground Truth (Optional, for Benchmarking)

| Property | Requirement |
|----------|-------------|
| **Location** | `outputs/tabular/metrics/ground_truth_symbols.json` |
| **Format** | JSON |

### Ground Truth Schema

```json
{
  "SLD1": [
    {"x": 100, "y": 200, "w": 50, "h": 30},
    {"x": 400, "y": 150, "w": 55, "h": 35}
  ],
  "SLD4": [
    {"x": 250, "y": 100, "w": 45, "h": 28}
  ]
}
```

Each entry specifies the **center coordinates** (x, y) and **dimensions** (w, h) of a verified symbol location.

## Dataset Metadata

| Property | Requirement |
|----------|-------------|
| **Location** | `data/metadata/dataset_stats.json` |
| **Purpose** | Statistics about the dataset (auto-generated or manually curated) |

## Adding New Diagrams

1. Place PNG files in `data/raw/slds/`
2. Follow the naming convention `SLD<number>.png`
3. Run `python run.py` — new images are automatically discovered

## Using External Datasets

```bash
python run.py --dataset /path/to/external/slds/
```

The `--dataset` flag overrides the `paths.raw_slds` configuration without modifying any files.
