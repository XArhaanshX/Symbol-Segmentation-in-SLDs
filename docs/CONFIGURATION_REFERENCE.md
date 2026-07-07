# Configuration Reference

## Overview

All configurable parameters live in `config/project_config.yaml`.  This document describes every parameter, its default value, and valid ranges.

## Paths

```yaml
paths:
  raw_slds: "data/raw/slds"           # Directory containing SLD PNG images
  raw_templates: "data/raw/templates"  # Directory containing template PNG images
  mr_symbol: "data/raw/templates/MR_Symbol.png"  # Path to the MR symbol
  metadata: "data/metadata"           # Dataset metadata directory
  outputs: "outputs"                  # Base output directory
  reports: "reports"                  # Base reports directory
  logs: "logs"                        # Log file directory
```

All paths are **relative to the repository root**.

## Pipeline (Stage 1)

```yaml
pipeline:
  save_intermediate: true              # Save gray/binary/edge images
  validation_targets:                  # SLDs to generate validation grids for
    - "MR_Symbol"
    - "SLD1"
    - "SLD4"
    - "SLD11"
```

## Denoising

```yaml
denoise:
  strategy: "median"     # Options: "median", "none"
  kernel_size: 3          # Odd integer >= 3. Larger = more blur
```

## Thresholding

```yaml
thresholding:
  strategy: "otsu"        # Options: "otsu"
```

## Edge Detection

```yaml
edge_detection:
  strategy: "canny"       # Options: "canny"
  auto_threshold: true    # If true, uses median-based auto thresholds
  auto_sigma: 0.33        # Sigma for auto threshold: lower=±33% of median
```

## Template Bank (Stage 2)

```yaml
template_bank:
  scale_min: 0.15         # Minimum scale factor (float, 0 < min < max)
  scale_max: 0.40         # Maximum scale factor
  num_scales: 10          # Number of linearly-spaced scales
  scale_spacing_strategy: "linear"  # Options: "linear"
  rotations: [0, 90, 180, 270]     # Rotation angles in degrees
  generation_method: "D3"           # Must be "D3"
```

## Chamfer Matching (Stage 3)

```yaml
chamfer_matching:
  local_minima_kernel_size: 15      # Odd integer. Morphological kernel for local minima
  candidate_extraction_method: "local_minima"  # Options: "local_minima"
  score_map_storage_format: "npy"   # Options: "npy"
```

## Structural Verification (Stage 5)

```yaml
verification:
  candidate_budget_strategy: "PER_SLD_TOP_N"  # Options: "GLOBAL_TOP_N", "PER_SLD_TOP_N"
  verification_candidate_limit: 1000           # Maximum candidates to verify

  # Feature weights (must sum to approximately 1.0)
  component_weight: 0.10
  contour_weight: 0.10
  geometry_weight: 0.20
  density_weight: 0.10
  occupancy_weight: 0.10
  topology_weight: 0.10
  similarity_weight: 0.30

  # Combined score weights
  verification_weight: 0.60
  coverage_area_weight: 0.40
```

## Benchmarking

```yaml
benchmark:
  enabled: true                # Set to false to skip benchmarking
  bootstrap_resamples: 1000    # Number of bootstrap iterations
  random_seed: 42              # Deterministic seed for reproducibility
```

## Visualization

```yaml
visualization:
  enabled: true
  target_slds:                 # SLDs to generate visual overlays for
    - "SLD1"
    - "SLD4"
    - "SLD11"
```

## Logging

```yaml
logging:
  console_level: "WARNING"    # Console output: DEBUG, INFO, WARNING, ERROR
  file_level: "DEBUG"         # Log file detail: DEBUG, INFO, WARNING, ERROR
```

## Execution

```yaml
execution:
  mirror_latest: true          # Copy run outputs to outputs/latest/
  deterministic_seed: 42       # Global random seed
```

## Using Custom Configurations

```bash
# Create a copy and modify
cp config/project_config.yaml config/experiment_1.yaml
# Edit experiment_1.yaml
python run.py --config config/experiment_1.yaml
```
