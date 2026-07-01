# Repository Structure Guide

This document provides a comprehensive explanation of every directory in the Symbol Segmentor repository, enabling any researcher or engineer to quickly navigate the codebase without prior knowledge of the project's development history.

## High-Level Organization

The repository enforces a strict separation between production code, experimental research, data, generated artifacts, and analysis reports.

```text
Symbol Segmentor/
├── config/        # YAML configuration definitions
├── data/          # Input datasets and intermediate features
├── docs/          # Master documentation and monographs
├── exploration/   # Isolated research code and historical scripts
├── outputs/       # Generated visual and tabular artifacts
├── reports/       # Analytical reports synthesizing research findings
├── src/           # The core production localization pipeline
└── tests/         # Unit and integration test suites
```

---

## Detailed Directory Breakdown

### 1. `src/` (Production Pipeline)
The `src/` directory contains the production-ready code that forms the Symbol Localization pipeline. Everything in `src/` is deterministic, documented, and intended for end-to-end execution.

*   **`pipeline/`**: The orchestration layer. Contains `run_pipeline.py` which strings together all stages.
*   **`preprocessing/`**: The ingestion layer. Converts raw images to grayscale, denoises, and applies Otsu binarization.
*   **`candidate_generation/`**: The first localization step. Applies Canny edge detection and computes distance transforms.
*   **`template_matching/`**: The core geometric matching engine. Executes dense sliding-window Chamfer matching via O(1) filter2D operations.
*   **`template_bank/`**: The template generation engine. Creates the multi-scale, multi-orientation bank using subpixel anti-aliased rasterization (Method D3).
*   **`verification/`**: The discrimination layer. Computes structural features (Euler Number, Stroke Count) and area-coverage metrics to rescore raw candidates.
*   **`scoring/`**: The ranking layer. Combines multiple feature scores into final candidate rankings.
*   **`visualization/`**: The output generation layer. Creates validation grids, bounding box overlays, and candidate galleries.
*   **`benchmarking/`**: The evaluation layer. Immutable, read-only scripts for calculating recall, precision, and hit rates across pipeline variants.
*   **`diagnostics/`**: Specialized validation tools for investigating specific architectural components (e.g., distance transform accuracy).
*   **`common/`**: Shared utilities for file I/O, serialization, and standardized logging.

### 2. `exploration/` (Research & Archival)
The `exploration/` directory isolates experimental code that is NOT part of the production pipeline. The production code must never import from `exploration/`.

*   **`structural_discriminator_research/`**: Scripts used to identify the strongest topological features (like Stroke Count) for separating symbols from false positives.
*   **`symbol_existence_research/`**: Exploratory scripts analyzing binary existence features within candidate patches.
*   **`template_consistency_research/`**: Dedicated research scripts comparing stroke patterns between the query template and localized candidates.
*   **`verification_cascade_research/`**: Scripts exploring the use of discrete pass/fail gates instead of continuous score multipliers.
*   **`archived/`**: Historical artifacts preserved for traceability.
    *   `scripts/`: All original "stage-numbered" development scripts (e.g., `stage3`, `stage5.8`).
    *   `reports/`: 44 historical stage transition and decision support reports.
    *   `scratch/`: Throwaway proof-of-concept scripts.
    *   `misc/`: Old format configs and the original PRD.

### 3. `data/` (Data Lifecycle)
The `data/` directory structures information strictly by its lifecycle state, never by arbitrary chronological stages.

*   **`raw/`**: Immutable input data.
    *   `slds/`: The 10 original Single Line Diagram full-resolution images.
    *   `templates/`: The single 161x103px `MR_Symbol.png` query template.
*   **`intermediate/`**: Data produced midway through the pipeline, useful for caching or downstream research.
    *   `candidate_features/`: Extracted structural/topological CSV features for all 264,852 candidates.
    *   `verification/`: Temporary files generated during verification audits.
*   **`processed/`**: Final datasets ready for benchmarking or external consumption.
    *   `rankings/`: Ranked lists of candidates.
    *   `metrics/`: Final calculated performance metrics.
*   **`metadata/`**: JSON files tracking dataset statistics and structural definitions.

### 4. `reports/` (Analysis & Findings)
The `reports/` directory contains all non-code analytical documentation, grouped logically by the project domain they address.

*   **`preprocessing/`**: Analysis of binarization thresholds and noise profiles.
*   **`template_bank/`**: Statistical validation, topology preservation analysis, and generation strategy comparisons.
*   **`candidate_generation/`**: Assessments of distance transform accuracy and raw Chamfer score distributions.
*   **`coverage_analysis/`**: Deep dives into the redundancy between coverage ratio and Chamfer score.
*   **`structural_analysis/`**: The discriminator leaderboard, feature separability audits (ROC-AUC, Cohen's d), and redundancy analyses.
*   **`verification/`**: Analyses of continuous verification score distributions and discrete cascade gating.
*   **`ranking/`**: Root cause analyses of ranking inversions and scale-performance correlation.
*   **`benchmarking/`**: Output evaluations and competitor analyses.
*   **`visual_validation/`**: Visual audit summaries cross-referencing numerical metrics against human inspection.
*   **`architecture/`**: High-level assessments of missing signals, detection ceilings, and worst-case scenarios.
*   **`experiments/`**: Post-mortems of failed or inconclusive experiments (e.g., area penalization functions).
*   **`archive/`**: Renamed historical stage reports maintained purely for traceability.

### 5. `outputs/` (Generated Artifacts)
The `outputs/` directory clearly separates visual assets for human consumption from tabular data for programmatic consumption.

*   **`visual/`**:
    *   `overlays/`: High-resolution SLDs with bounding boxes indicating candidate detections.
    *   `galleries/`: Collages of cropped candidate patches (e.g., top 100 crops) for rapid visual auditing.
    *   `comparisons/`: Side-by-side visual analyses.
    *   `pipeline_outputs/`: Intermediary visual steps (grayscale, binary, edges).
    *   `diagnostics/`: Visual heatmaps of Chamfer score fields and generated distance transforms.
    *   `template_bank/`: Rendered images of all 40 multi-scale/multi-orientation templates.
*   **`tabular/`**:
    *   `rankings/`: Complete ordered CSV rankings of all candidates per SLD.
    *   `metrics/`: JSON files containing global and per-SLD performance metrics.
    *   `score_maps/`: Large raw `.npy` numpy arrays of the Chamfer distance fields.
    *   `exports/`: General data exports.

### 6. `docs/` (Master Documentation)
High-level guides for adapting, understanding, and reproducing the framework.

*   **`monograph/`**: The complete Master Research Monograph (LaTeX/Markdown) detailing the mathematical and empirical basis of the research.
*   **`PIPELINE_OVERVIEW.md`**: Walkthrough of the production pipeline.
*   **`DATASET_PREPARATION.md`**: Guide for ingesting new data.
*   **`EXPERIMENT_REPRODUCTION.md`**: Guide for reproducing research findings.

### 7. `config/` (Configuration)
Contains all global tuning parameters in YAML format to prevent hardcoding magic numbers in the source tree.

*   `preprocessing.yaml`
*   `template_bank.yaml`
*   `chamfer_matching.yaml`
*   `verification.yaml`

### 8. `tests/`
Reserved for unit and integration test suites enforcing deterministic behavior across the pipeline.
