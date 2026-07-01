# Circuit Symbol Localization

A research framework for deterministically locating specific circuit symbols (Current Transformers/MRs) in complex, highly-dense industrial Single Line Diagrams (SLDs) using zero training data.

## Project Overview

This repository contains the complete research codebase, analysis reports, and artifact generation pipeline for the Circuit Symbol Localization project. The system is designed to localize symbols using only a single query template, overcoming the severe limitations of standard deep learning approaches which require massive annotated datasets.

**Status: Experimental / Not Production Ready.** The pipeline currently successfully localizes symbols at scales $\ge0.20$ but struggles with severe ranking inversions for small-scale symbols ($\le0.15$) due to extreme topological density and edge matching ambiguity.

## Motivation & Research Objectives

Industrial electrical engineering relies on complex schematic diagrams where critical components are embedded in dense networks of intersecting wires and text annotations. 
- **The Data Constraint**: There is zero annotated training data available.
- **The Scale Problem**: The target symbol appears at scales ranging from $0.09\times$ to $0.40\times$ the reference template size.
- **The Topological Problem**: Symbols are structurally embedded in bus conductors, making simple connected-component isolation mathematically impossible.

**Objective**: Develop a deterministic, CPU-only, explainable computer vision pipeline that can achieve $\ge0.90$ recall and $\ge0.85$ precision across 10 highly variable real-world SLDs using a single $161\times103$px template image.

## Repository Structure

The repository has been fully refactored from a chronological development log into a modular research framework.

*   **`src/`**: The core production localization pipeline.
*   **`data/`**: Datasets (raw SLDs, templates) and extracted intermediate features.
*   **`exploration/`**: Isolated research code (e.g., structural discriminator discovery, verification cascades) and historical stage scripts.
*   **`reports/`**: Topic-based analysis reports synthesizing findings from all experiments.
*   **`outputs/`**: Generated visual diagnostics (overlays, galleries, score maps) and tabular rankings.
*   **`docs/`**: Master documentation and monographs.
*   **`config/`**: YAML configuration definitions for all pipeline stages.

For a complete explanation of every directory, see [docs/REPOSITORY_STRUCTURE.md](docs/REPOSITORY_STRUCTURE.md).

## Pipeline Architecture

The pipeline consists of the following core stages:

1.  **Preprocessing**: Otsu binarization and Canny edge detection.
2.  **Template Bank**: Generation of a multi-scale, multi-orientation template bank using subpixel coordinate-scaled anti-aliased rasterization (Method D3).
3.  **Candidate Generation**: Fast dense Chamfer matching via distance transforms to propose candidate locations.
4.  **Rescoring**: Normalizing raw Chamfer scores using Coverage $\times$ Area metrics to counteract small-template bias.
5.  **Structural Verification**: Extracting 25 topological features (Stroke Count, Euler Number, etc.) for high-confidence discrimination.

For a detailed walkthrough, see [docs/PIPELINE_OVERVIEW.md](docs/PIPELINE_OVERVIEW.md).

## Installation & Dependencies

```bash
# Clone the repository
git clone https://github.com/organization/symbol-segmentor.git
cd symbol-segmentor

# Create virtual environment
python -m venv .venv
source .venv/bin/activate  # On Windows: .venv\Scripts\activate

# Install requirements
pip install -r requirements.txt
```

*Note: The project heavily relies on `opencv-python`, `numpy`, `scipy`, `scikit-image`, and `pandas`.*

## Running the Pipeline

To run the end-to-end production pipeline on the provided SLDs:

```bash
python src/pipeline/run_pipeline.py
```

This script orchestrates the full sequence, writing intermediate files to `data/intermediate/` and final visual outputs to `outputs/visual/`.

### Running Individual Modules

Individual pipeline stages can be validated independently:

```bash
# Validate template bank generation
python src/template_bank/template_validation.py

# Run distance transform diagnostic
python src/diagnostics/distance_transform_validation.py
```

## Running Experiments

Research experiments are safely isolated in the `exploration/` directory.

```bash
# Run structural discriminator feature analysis
python exploration/structural_discriminator_research/scripts/structural_discovery.py
```

For full reproduction instructions of all historical experiments, refer to [docs/EXPERIMENT_REPRODUCTION.md](docs/EXPERIMENT_REPRODUCTION.md).

## Using a New SLD Dataset

The framework is designed to be adaptable to new datasets. To ingest new electrical diagrams or a new query template, refer to the step-by-step guide in [docs/DATASET_PREPARATION.md](docs/DATASET_PREPARATION.md).

### Expected Folder Structure for New Datasets
```text
data/
├── raw/
│   ├── slds/
│   │   ├── NEW_SLD1.png
│   │   └── ...
│   └── templates/
│       └── NEW_SYMBOL.png
```

## Output Descriptions

The pipeline generates two primary classes of outputs:

1.  **Visual (`outputs/visual/`)**:
    *   `overlays/`: Bounding boxes drawn over original SLDs indicating detections.
    *   `galleries/`: Cropped patches of top-ranked candidates for visual audits.
    *   `diagnostics/`: Heatmaps of Chamfer score fields and distance transforms.
2.  **Tabular (`outputs/tabular/`)**:
    *   `rankings/`: CSV files containing ranked lists of candidates per SLD with all score components.
    *   `metrics/`: JSON files tracking recall, median rank, and hit rates.

## Benchmarking Workflow

To objectively evaluate pipeline performance modifications without risking regression:

```bash
python src/benchmarking/unified_pipeline_benchmark.py
```
This read-only suite enforces strict immutability and generates a deterministic pipeline leaderboard.

## Reproducing the Research

The original research path — including discoveries regarding connected-component failure, template generation dilution, and the separability-vs-ranking paradox — is fully documented and reproducible. See [docs/EXPERIMENT_REPRODUCTION.md](docs/EXPERIMENT_REPRODUCTION.md).

## Extending the Framework

Future engineers looking to extend this framework should focus on:
1.  **Discrete Structural Gating**: Replacing continuous score multipliers with hard pass/fail gates based on topological features.
2.  **PCA Subspace Verification**: Implementing the original PRD design for semantic manifold disambiguation.

*WARNING: Do not attempt Connected Component extraction or continuous structural score integration. These paths have been definitively disproven.*

## Troubleshooting

- **Empty Templates Generated**: Ensure you are using `Method D3` configuration in `config/template_bank.yaml`. Pixel-domain downsampling (Method A) destroys edges at scale <0.20.
- **Top Detections are all Text**: This is the known small-template bias. Ensure the `coverage_rescoring` module is running.
- **Path/Import Errors**: Ensure you are running scripts from the repository root directory to maintain correct relative path resolution.

## Citation & Credits

Research conducted by **Arhaansh Jhingan**.

When referencing this project or its findings regarding topological constraint matching in line drawings, please cite the Master Monograph located in `docs/monograph/`.
