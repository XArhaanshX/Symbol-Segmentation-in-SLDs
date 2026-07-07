# Symbol Segmentor

**Automated Circuit Symbol Localization in Single Line Diagrams**

A professional research framework for detecting and localizing electrical circuit symbols (MR — Manual Reset devices) in engineering Single Line Diagrams (SLDs) using multi-scale Chamfer matching, structural verification cascades, and PCA-based feature analysis.

---

## Table of Contents

- [Project Overview](#project-overview)
- [Research Motivation](#research-motivation)
- [System Architecture](#system-architecture)
- [Directory Structure](#directory-structure)
- [Installation](#installation)
- [Quick Start](#quick-start)
- [Running the Complete Pipeline](#running-the-complete-pipeline)
- [Running Individual Components](#running-individual-components)
- [Configuration](#configuration)
- [Input Dataset Format](#input-dataset-format)
- [Expected Outputs](#expected-outputs)
- [Benchmark Suite](#benchmark-suite)
- [Troubleshooting](#troubleshooting)
- [Developer Guide](#developer-guide)
- [Extending the Framework](#extending-the-framework)
- [Frequently Asked Questions](#frequently-asked-questions)
- [License](#license)
- [Credits](#credits)

---

## Project Overview

The Symbol Segmentor implements a complete, deterministic, multi-stage pipeline for localizing handwritten and CAD-generated circuit symbols in industrial Single Line Diagrams. The pipeline operates without deep learning or GPU requirements, using classical computer vision techniques that guarantee reproducible results across executions.

### Pipeline Stages

| Stage | Name | Description |
|-------|------|-------------|
| 1 | **Preprocessing** | Grayscale conversion, median denoising, Otsu binarization, Canny edge extraction |
| 2 | **Template Bank** | Multi-scale (10 scales), multi-rotation (4 orientations) template generation using Method D3 |
| 3 | **Chamfer Matching** | Distance transform computation, sliding-window Chamfer score maps, local minima candidate extraction |
| 4 | **Coverage Rescoring** | Edge coverage computation at 0-3px tolerances, normalized score generation (Scale, Area, Density) |
| 5 | **Structural Verification** | 24-metric structural feature extraction, weighted verification scoring, combined ranking |
| 6 | **Benchmarking** | Unified evaluation suite with dual-metric localization, retrieval analysis, bootstrap stability |
| 7 | **Visualization** | Validation grids, candidate overlay panels, response field visualizations |

---

## Research Motivation

Power system Single Line Diagrams contain standardized circuit symbols (breakers, transformers, disconnect switches) that must be precisely located for automated topology extraction. Traditional approaches using YOLO or connected component analysis fail on these diagrams because:

1. **Symbol-to-background similarity**: Circuit symbols share structural elements (lines, corners) with busbars and conductors
2. **Scale variability**: Symbols appear at different scales across different diagrams
3. **Sparse training data**: Industrial SLDs are proprietary, limiting supervised learning approaches

This framework addresses these challenges through a template-matching approach with multi-scale pyramids, structural verification cascades, and coverage-based rescoring — all operating deterministically without training data.

---

## System Architecture

```
Input SLD Images (PNG)
        |
   [Stage 1] Preprocessing
        |--- Grayscale + Denoise + Binarize + Edge Extract
        |
   [Stage 2] Template Bank Generation
        |--- Method D3: Coordinate Scaling + Subpixel Rasterization
        |--- 10 scales x 4 rotations = 40 template variants
        |
   [Stage 3] Chamfer Matching Engine
        |--- Distance Transform (L2) on SLD edge maps
        |--- Sliding-window Chamfer score computation
        |--- Local minima candidate extraction (15x15 kernel)
        |
   [Stage 4] Coverage Rescoring
        |--- Edge coverage at 0/1/2/3px tolerances
        |--- Normalized scores: Scale, Area, Density weighting
        |
   [Stage 5] Structural Verification
        |--- 24 structural features per candidate
        |--- Component, contour, geometry, density, topology analysis
        |--- Weighted verification + combined scoring
        |
   [Stage 6] Unified Benchmark Suite
        |--- Localization metrics (Precision, Recall, F1)
        |--- Ranking metrics (MRR, Recall@K)
        |--- Bootstrap stability (N=1000)
        |--- Pipeline leaderboard
        |
   [Stage 7] Visualization
        |--- Validation grids
        |--- Candidate overlay panels
        |
   Output: Ranked candidates, reports, visualizations
```

---

## Directory Structure

```
Symbol Segmentor/
├── install.py                     # Automated environment setup
├── run.py                         # Central pipeline entry point
├── requirements.txt               # Python dependencies
│
├── config/
│   ├── project_config.yaml        # Master configuration
│   ├── preprocessing.yaml         # Stage 1 parameters
│   ├── template_bank.yaml         # Stage 2 parameters
│   ├── chamfer_matching.yaml      # Stage 3 parameters
│   └── verification.yaml          # Stage 5 parameters
│
├── data/
│   ├── raw/
│   │   ├── slds/                  # Input SLD images (SLD1.png, SLD2.png, ...)
│   │   └── templates/             # MR Symbol template (MR_Symbol.png)
│   └── metadata/
│       └── dataset_stats.json     # Dataset statistics
│
├── src/
│   ├── framework/                 # Execution framework
│   │   ├── config_manager.py      # Centralized configuration
│   │   ├── validator.py           # Repository validation
│   │   ├── orchestrator.py        # Pipeline orchestrator
│   │   ├── logger.py              # Structured logging
│   │   ├── progress.py            # Console progress display
│   │   ├── output_manager.py      # Timestamped output management
│   │   ├── error_handler.py       # User-friendly error handling
│   │   └── reproducibility.py     # Execution recording
│   ├── stages/                    # Pipeline stage wrappers
│   ├── preprocessing/             # Image processing modules
│   ├── candidate_generation/      # Edge detection
│   ├── template_bank/             # Template pyramid generation
│   ├── template_matching/         # Chamfer matching engine
│   ├── verification/              # Structural verification
│   ├── scoring/                   # Combined ranking
│   ├── benchmarking/              # Unified benchmark suite
│   ├── visualization/             # Visual output generation
│   └── diagnostics/               # Diagnostic tools
│
├── outputs/                       # Pipeline outputs (timestamped)
│   ├── runs/YYYY-MM-DD_HHMMSS/   # Per-run outputs
│   └── latest/                    # Mirror of latest run
│
├── reports/                       # Generated reports (timestamped)
│   ├── runs/YYYY-MM-DD_HHMMSS/   # Per-run reports
│   ├── latest/                    # Mirror of latest run
│   └── system/                    # Validation & reproducibility reports
│
├── logs/                          # Execution logs
│   └── run_YYYYMMDD_HHMMSS.log
│
├── docs/                          # Developer documentation
└── tests/                         # Test suite
```

---

## Installation

### Prerequisites

- **Python 3.9+** (tested with 3.10, 3.11, 3.12, 3.14)
- **Windows 10/11** (also works on Linux/macOS)
- No administrator privileges required
- No GPU required (CPU-only execution)

### Setup (2 minutes)

```bash
# Clone the repository
git clone https://github.com/XArhaanshX/Symbol-Segmentation-in-SLDs.git
cd Symbol-Segmentation-in-SLDs

# Run automated installer
python install.py
```

The installer will:
- Detect your Python version, OS, and available RAM
- Install all dependencies from `requirements.txt`
- Verify all imports succeed
- Create required directories
- Verify write permissions
- Check dataset availability

---

## Quick Start

```bash
# 1. Install (one-time)
python install.py

# 2. Run the complete pipeline
python run.py
```

That's it. All outputs will appear in `outputs/runs/<timestamp>/` and `reports/runs/<timestamp>/`.

---

## Running the Complete Pipeline

```bash
python run.py
```

This executes all stages in dependency order:
1. Input Validation
2. Preprocessing
3. Template Bank Generation
4. Chamfer Matching
5. Coverage Rescoring
6. Structural Verification
7. Benchmarking
8. Visualization

Progress is displayed as:
```
============================================================
  Symbol Segmentor Pipeline
============================================================

  [1/7] Preprocessing  ... done (3.5s)
  [2/7] Template Bank  ... done (12.1s)
  [3/7] Chamfer Matching  ... done (45.2s)
  ...
  [7/7] Visualization  ... done (1.2s)

------------------------------------------------------------
  Completed in 2 min 14 sec
  Outputs  : outputs/runs/2026-07-07_121643
  Reports  : reports/runs/2026-07-07_121643
  Log      : logs/run_2026-07-07_121643.log
------------------------------------------------------------
```

---

## Running Individual Components

```bash
# Run only preprocessing
python run.py --pipeline preprocessing

# Run only benchmarking
python run.py --benchmark

# Run only visualization
python run.py --visualize

# Use a custom configuration
python run.py --config config/custom.yaml

# Use an external dataset
python run.py --dataset /path/to/sld_images/

# Show all options
python run.py --help
```

---

## Configuration

All parameters live in `config/project_config.yaml`. Key sections:

| Section | Parameters |
|---------|-----------|
| `paths` | Dataset locations, output directories |
| `denoise` | Strategy (median), kernel size |
| `thresholding` | Strategy (Otsu) |
| `edge_detection` | Strategy (Canny), auto-threshold sigma |
| `template_bank` | Scale range, number of scales, rotations, generation method |
| `chamfer_matching` | Local minima kernel size, extraction method |
| `verification` | Budget strategy, feature weights, combined score weights |
| `benchmark` | Bootstrap resamples, random seed |
| `execution` | Mirror latest, deterministic seed |

See `docs/CONFIGURATION_REFERENCE.md` for detailed parameter documentation.

---

## Input Dataset Format

Place your SLD images in `data/raw/slds/`:
- **Format**: PNG (supports RGBA transparency)
- **Naming**: `SLD1.png`, `SLD2.png`, etc.
- **Resolution**: Any resolution supported

Place the template symbol in `data/raw/templates/`:
- **File**: `MR_Symbol.png` — the reference circuit symbol to locate
- **Format**: PNG with transparent background recommended

---

## Expected Outputs

Each pipeline run generates:

| Directory | Contents |
|-----------|----------|
| `outputs/runs/<ts>/template/` | Preprocessed template (gray, binary, edges) |
| `outputs/runs/<ts>/diagrams/` | Per-SLD preprocessed outputs |
| `outputs/runs/<ts>/template_bank/` | Multi-scale template variants + manifest |
| `outputs/runs/<ts>/candidates/` | Raw, ranked, rescored, verified candidate CSVs |
| `outputs/runs/<ts>/distance_transforms/` | SLD distance transform maps |
| `reports/runs/<ts>/visual_validation/` | Validation grids |
| `reports/runs/<ts>/benchmark/` | Benchmark reports and leaderboard |
| `reports/system/reproducibility_report.md` | Full execution environment record |
| `logs/run_<ts>.log` | Detailed execution log |

---

## Benchmark Suite

The unified benchmark suite evaluates all pipeline variants automatically:

- **Localization Metrics**: Precision, Recall, F1 (center-distance and IoU matching)
- **Ranking Metrics**: MRR, Mean/Median Rank, Recall@10/20/50/100/500
- **Signal Enrichment**: Candidate reduction %, MR density gain
- **Statistical Stability**: Bootstrap resampling (N=1000, 95% CI)
- **Failure Mode Analysis**: Duplicate, text, busbar, conductor, empty, noise classification
- **Pipeline Leaderboard**: Deterministic ranking by `Recall@100 > MRR > Precision`

---

## Troubleshooting

| Problem | Solution |
|---------|----------|
| `ModuleNotFoundError: No module named 'src'` | Run from the repository root: `python run.py` |
| `FileNotFoundError: config/project_config.yaml` | Run `python install.py` first |
| `No SLD images found` | Place `.png` files in `data/raw/slds/` |
| `Permission denied` on outputs | Ensure the repository is not on a read-only share |
| Pipeline fails silently | Check `logs/run_*.log` and `reports/system/error_report.md` |

---

## Developer Guide

### Adding a New Pipeline Stage

1. Create `src/stages/s0N_new_stage.py`
2. Implement the `PipelineStage` interface:
   ```python
   from src.framework.orchestrator import PipelineStage

   class NewStage(PipelineStage):
       def name(self): return "new_stage"
       def description(self): return "What this stage does"
       def dependencies(self): return ["prerequisite_stage"]
       def outputs(self): return ["list of outputs"]
       def run(self, context): ...
   ```
3. Register in `src/framework/orchestrator.py` → `get_all_stages()`

### Module Interface

Every stage wrapper receives a `context` dictionary:
```python
context = {
    "project_root": str,     # Absolute path to repo root
    "config": dict,          # Loaded project_config.yaml
    "outputs_dir": str,      # Timestamped output directory
    "reports_dir": str,      # Timestamped reports directory
    "run_timestamp": str,    # YYYY-MM-DD_HHMMSS
    "log_path": str,         # Path to log file
}
```

See `docs/MODULE_DEVELOPMENT.md` for detailed guidance.

---

## Extending the Framework

The framework is designed for extensibility:

- **New templates**: Add to `data/raw/templates/` and reference in config
- **New SLDs**: Drop PNG files in `data/raw/slds/`
- **Custom configs**: Create a YAML and run with `--config`
- **New stages**: Implement `PipelineStage` interface
- **New metrics**: Extend `src/benchmarking/unified_pipeline_benchmark.py`

---

## Frequently Asked Questions

**Q: Do I need a GPU?**
No. The entire pipeline runs on CPU. No CUDA or GPU installation required.

**Q: Will running the pipeline overwrite my previous results?**
No. Every run creates a new timestamped directory. Historical results are never modified.

**Q: Can I use my own SLD diagrams?**
Yes. Place PNG images in `data/raw/slds/` or use `--dataset /path/to/images/`.

**Q: How do I reproduce a specific run?**
Check `reports/system/reproducibility_report.md` for the exact git commit, configuration, and environment used.

**Q: What Python versions are supported?**
Python 3.9 through 3.14 have been tested. 3.10+ is recommended.

---

## License

This project is developed for research purposes.

---

## Credits

**Research conducted by Arhaansh Jhingan**

Pipeline design, implementation, and experimental evaluation for automated circuit symbol localization in industrial Single Line Diagrams.
