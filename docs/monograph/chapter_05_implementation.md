# Chapter 5 — Implementation

## 5.1 Repository Architecture

The production codebase is organized into a semantic hierarchy following the restructuring completed in Phase 6 of the project timeline. The repository separates production code, exploration research, outputs, and documentation:

```
Symbol Segmentor/
│
├── Data/
│   ├── raw/
│   │   ├── slds/              # Original SLD images (SLD1–SLD12)
│   │   └── symbols/           # MR_Symbol.png template
│   └── processed/             # Preprocessed intermediates
│
├── src/
│   ├── common/                # Shared utilities
│   │   ├── logging_utils.py   # Structured logging
│   │   └── io_utils.py        # Image I/O helpers
│   │
│   ├── pipeline/              # Stage 1 & 2: Preprocessing + Template Bank
│   │   ├── pipeline.py        # Orchestrator (Stage 1)
│   │   ├── image_loader.py    # RGBA/RGB image loading
│   │   ├── grayscale.py       # Grayscale conversion
│   │   ├── denoise.py         # Median filtering
│   │   ├── thresholding.py    # Otsu binarization
│   │   └── pyramid.py         # Method D3 template generation (Stage 2)
│   │
│   ├── candidate_generation/  # Stage 3: Chamfer matching
│   │   ├── edge_detection.py  # Canny edge extraction
│   │   └── ...
│   │
│   ├── template_matching/     # Stage 3: Core matching engine
│   │   └── chamfer_matching.py # Dense sliding-window Chamfer
│   │
│   ├── verification/          # Stage 4 & 5: Rescoring + Verification
│   │   ├── coverage_rescoring.py    # Coverage×Area rescoring
│   │   ├── coverage_audit.py        # Coverage diagnostic analysis
│   │   └── structural_verification.py # 25-feature structural verification
│   │
│   └── exploration/           # Research experiments (read-only diagnostics)
│       ├── unified_pipeline_benchmark.py  # Cross-pipeline evaluation
│       └── nms_diagnostic_evaluation.py   # NMS IoU sweep analysis
│
├── exploration/
│   └── archived/
│       ├── scripts/           # Historical research scripts
│       │   ├── stage5_8_structural_discovery.py
│       │   ├── stage5_9_discriminator_integration.py
│       │   └── ...
│       └── misc/
│           └── PRD_Symbol_Localization.md  # Original PRD (2304 lines)
│
├── config/
│   ├── preprocessing.yaml     # Stage 1 parameters
│   ├── template_bank.yaml     # Stage 2 parameters
│   └── stage5_verification.yaml # Stage 5 weights
│
├── outputs/
│   ├── template/              # Preprocessed template outputs
│   ├── template_bank/         # Generated template variants + manifest
│   │   ├── scales/            # Scale-only variants
│   │   ├── rotations/         # Scale+rotation variants
│   │   └── template_bank_manifest.csv
│   ├── diagrams/              # Per-SLD preprocessing outputs
│   ├── distance_transforms/   # Per-SLD DT images (.tiff)
│   ├── candidates/            # Candidate CSVs (all rankings)
│   ├── nms_overlays/          # NMS diagnostic outputs
│   └── tabular/               # Benchmark metrics and exports
│
├── reports/                   # 33 report subdirectories + forensic artifacts
│   ├── benchmark/             # Unified pipeline benchmark reports
│   ├── nms/                   # NMS diagnostic reports
│   ├── stage58_forensics/     # Structural discriminator forensics
│   ├── stage59_forensics/     # Discriminator integration forensics
│   └── ...
│
└── docs/
    ├── project_master_retrospective.md  # Canonical project history
    └── monograph/                        # This document
```

## 5.2 Configuration Management

All pipeline parameters are externalized into YAML configuration files, ensuring no hardcoded magic numbers in production code. Each configuration file is validated at load time with explicit error reporting.

### 5.2.1 Preprocessing Configuration (`config/preprocessing.yaml`)

```yaml
pipeline:
  save_intermediate: true

preprocessing:
  median_kernel: 3
  canny_low: 50
  canny_high: 150
```

### 5.2.2 Template Bank Configuration (`config/template_bank.yaml`)

```yaml
scale_min: 0.15
scale_max: 0.40
num_scales: 10
scale_spacing_strategy: "linear"
rotations: [0, 90, 180, 270]
generation_method: "D3"
```

The `generation_method: "D3"` parameter is enforced at runtime — any other value causes an immediate halt with error reporting. This prevents accidental regression to the failed Method A.

### 5.2.3 Verification Configuration (`config/stage5_verification.yaml`)

```yaml
candidate_budget_strategy: "PER_SLD_TOP_N"
verification_candidate_limit: 1000
component_weight: 0.15
contour_weight: 0.10
geometry_weight: 0.15
density_weight: 0.10
occupancy_weight: 0.10
topology_weight: 0.15
similarity_weight: 0.15
verification_weight: 0.60
coverage_area_weight: 0.40
```

## 5.3 Traceability Framework

Every report and output artifact includes a standardized traceability header documenting:
- **Generation Timestamp**: When the artifact was created
- **Template Bank Version**: Which template bank was used (e.g., `Stage2_D3_v1`)
- **Candidate Dataset Source**: Which candidate CSV was consumed
- **Manifest Version**: Template bank manifest path
- **Configuration Source**: Which YAML configuration drove the computation

This traceability pattern is implemented consistently across all production and exploration scripts, enabling any artifact to be traced back to its inputs and parameters.

Example traceability header (from `structural_verification.py`):

```markdown
<!-- Traceability Header -->
- **Generation Timestamp**: 2026-06-18 14:32:01
- **Template Bank Version**: Stage2_D3_v1
- **Stage 4 Candidate Source**: ranked_by_coverage_area.csv
- **Manifest Version**: outputs/template_bank/template_bank_manifest.csv
- **Candidate Budget Strategy**: PER_SLD_TOP_N
- **Verification Candidate Limit**: 1000
<!-- End Traceability Header -->
```

## 5.4 Immutability Framework

The unified pipeline benchmark (`src/exploration/unified_pipeline_benchmark.py`) implements a strict immutability protocol:

1. **Pre-execution hashing**: SHA-256 checksums computed for all input artifacts before evaluation begins
2. **Post-execution verification**: Checksums recomputed after all evaluations complete
3. **Violation detection**: Any checksum mismatch triggers an immediate halt with `IMMUTABILITY VIOLATION` error

This ensures that benchmark evaluations are strictly read-only — no input dataset is modified during the evaluation process.

## 5.5 Dependency Stack

```
opencv-python >= 4.8.0    # Core image processing, DT, edge detection
numpy >= 1.24.0           # Array operations
scipy >= 1.10.0           # Minimum filters, spatial operations
scikit-learn >= 1.3.0     # PCA (planned), metrics
scikit-image >= 0.21.0    # Skeletonization (Stage 5.8)
matplotlib >= 3.7.0       # Visualization, histograms
pyyaml >= 6.0             # Configuration loading
networkx >= 3.0           # Graph features (Stage 5.8)
pandas >= 2.0             # Tabular data handling (benchmarks)
```

All dependencies are CPU-only. No GPU-accelerated libraries (CUDA, cuDNN, TensorFlow, PyTorch) are used.

## 5.6 Error Handling and Halt Protocol

The codebase implements a consistent error handling pattern:

1. **Configuration errors**: Generate `reports/stage{N}_configuration_error.md` and `sys.exit(1)`
2. **Missing dependencies**: Generate `reports/stage{N}_missing_dependencies.md` and `sys.exit(1)`
3. **Candidate survival violations**: Print `FATAL: Candidate survival mismatch!` and `sys.exit(1)`
4. **Method validation**: Enforce `generation_method == "D3"` at runtime

This fail-fast approach ensures that no pipeline stage operates on invalid or incomplete inputs.

---

*Forensic Source References:*
- *Repository restructuring: `reports/restructure/traceability_preservation_report.md`*
- *Pipeline orchestrator: `src/pipeline/pipeline.py`*
- *Template bank generator: `src/pipeline/pyramid.py`*
- *Immutability verification: `src/exploration/unified_pipeline_benchmark.py`, lines 47–87*
