# Reproducibility Report

## Execution Metadata

| Field | Value |
|---|---|
| Timestamp | 2026-07-07_122718 |
| Git Commit | `1d5da7787fe3e59e5d2da3348afd526db5d8c54e` |
| Git Branch | `main` |
| Python Version | `3.14.3 (tags/v3.14.3:323c59a, Feb  3 2026, 16:04:56) [MSC v.1944 64 bit (AMD64)]` |
| Operating System | Windows 11 (AMD64) |
| Runtime | 0m 38s |
| Random Seed | `42` (deterministic) |
| Log File | `logs\run_2026-07-07_122718.log` |

## Configuration Snapshot

```yaml
benchmark:
  bootstrap_resamples: 1000
  enabled: true
  random_seed: 42
chamfer_matching:
  candidate_extraction_method: local_minima
  local_minima_kernel_size: 15
  score_map_storage_format: npy
denoise:
  kernel_size: 3
  strategy: median
edge_detection:
  auto_sigma: 0.33
  auto_threshold: true
  strategy: canny
execution:
  deterministic_seed: 42
  mirror_latest: true
logging:
  console_level: WARNING
  file_level: DEBUG
paths:
  logs: logs
  metadata: data/metadata
  mr_symbol: data/raw/templates/MR_Symbol.png
  outputs: outputs
  raw_slds: data/raw/slds
  raw_templates: data/raw/templates
  reports: reports
pipeline:
  save_intermediate: true
  validation_targets:
  - MR_Symbol
  - SLD1
  - SLD4
  - SLD11
template_bank:
  generation_method: D3
  num_scales: 10
  rotations:
  - 0
  - 90
  - 180
  - 270
  scale_max: 0.4
  scale_min: 0.15
  scale_spacing_strategy: linear
thresholding:
  strategy: otsu
verification:
  candidate_budget_strategy: PER_SLD_TOP_N
  component_weight: 0.1
  contour_weight: 0.1
  coverage_area_weight: 0.4
  density_weight: 0.1
  geometry_weight: 0.2
  occupancy_weight: 0.1
  similarity_weight: 0.3
  topology_weight: 0.1
  verification_candidate_limit: 1000
  verification_weight: 0.6
visualization:
  enabled: true
  target_slds:
  - SLD1
  - SLD4
  - SLD11
```

## Installed Packages

| Package | Version |
|---|---|
| GitPython | 3.1.46 |
| ImageIO | 2.37.3 |
| Jinja2 | 3.1.6 |
| Markdown | 3.10.2 |
| MarkupSafe | 3.0.3 |
| PyJWT | 2.12.1 |
| PyMuPDF | 1.27.2.3 |
| PyPDF2 | 3.0.1 |
| PyYAML | 6.0.3 |
| Pygments | 2.19.2 |
| absl-py | 2.4.0 |
| aiohappyeyeballs | 2.6.1 |
| aiohttp | 3.13.3 |
| aiohttp-retry | 2.9.1 |
| aiosignal | 1.4.0 |
| altair | 6.0.0 |
| annotated-doc | 0.0.4 |
| annotated-types | 0.7.0 |
| anyio | 4.12.1 |
| arxiv | 2.4.1 |
| asyncio | 4.0.0 |
| attrs | 26.1.0 |
| blinker | 1.9.0 |
| brotli | 1.2.0 |
| cachetools | 7.0.3 |
| catboost | 1.2.10 |
| certifi | 2026.2.25 |
| cffi | 2.0.0 |
| charset-normalizer | 3.4.4 |
| click | 8.3.1 |
| colorama | 0.4.6 |
| contourpy | 1.3.3 |
| cssselect2 | 0.9.0 |
| cycler | 0.12.1 |
| datasets | 4.6.1 |
| defusedxml | 0.7.1 |
| dill | 0.4.0 |
| docker | 7.1.0 |
| emoji | 2.15.0 |
| et_xmlfile | 2.0.0 |
| fastapi | 0.135.3 |
| feedparser | 6.0.12 |
| filelock | 3.25.0 |
| flatbuffers | 25.12.19 |
| fonttools | 4.62.1 |
| fpdf2 | 2.8.7 |
| frozenlist | 1.8.0 |
| fsspec | 2026.2.0 |
| gitdb | 4.0.12 |
| graphviz | 0.21 |
| h11 | 0.16.0 |
| hf-xet | 1.3.2 |
| httpcore | 1.0.9 |
| httplib2 | 0.31.2 |
| httpx | 0.28.1 |
| huggingface_hub | 1.6.0 |
| idna | 3.11 |
| joblib | 1.5.3 |
| jsonschema | 4.26.0 |
| jsonschema-specifications | 2025.9.1 |
| kiwisolver | 1.5.0 |
| lazy-loader | 0.5 |
| lightgbm | 4.6.0 |
| lxml | 6.0.2 |
| markdown-it-py | 3.0.0 |
| markdown_pdf | 1.13.1 |
| matplotlib | 3.10.8 |
| mdurl | 0.1.2 |
| mediapipe | 0.10.33 |
| mpmath | 1.3.0 |
| multidict | 6.7.1 |
| multiprocess | 0.70.18 |
| narwhals | 2.17.0 |
| networkx | 3.6.1 |
| numpy | 2.4.2 |
| opencv-contrib-python | 4.13.0.92 |
| opencv-python | 4.13.0.92 |
| openpyxl | 3.1.5 |
| packaging | 26.0 |
| pandas | 2.3.3 |
| patsy | 1.0.2 |
| pdflatex | 0.1.3 |
| pillow | 12.1.1 |
| pip | 25.3 |
| plantuml | 0.3.0 |
| plotly | 6.7.0 |
| propcache | 0.4.1 |
| protobuf | 6.33.5 |
| pyarrow | 23.0.1 |
| pycparser | 3.0 |
| pydantic | 2.12.5 |
| pydantic_core | 2.41.5 |
| pydeck | 0.9.1 |
| pydyf | 0.12.1 |
| pyparsing | 3.3.2 |
| pyphen | 0.17.2 |
| python-dateutil | 2.9.0.post0 |
| python-docx | 1.2.0 |
| python-multipart | 0.0.24 |
| python-pptx | 1.0.2 |
| pytz | 2026.1.post1 |
| pywin32 | 311 |
| referencing | 0.37.0 |
| reportlab | 4.5.0 |
| requests | 2.32.5 |
| rich | 14.3.3 |
| rpds-py | 0.30.0 |
| scikit-image | 0.26.0 |
| scikit-learn | 1.8.0 |
| scipy | 1.17.1 |
| seaborn | 0.13.2 |
| setuptools | 81.0.0 |
| sgmllib3k | 1.0.0 |
| shellingham | 1.5.4 |
| six | 1.17.0 |
| smmap | 5.0.2 |
| sounddevice | 0.5.5 |
| starlette | 1.0.0 |
| statsmodels | 0.14.6 |
| streamlit | 1.55.0 |
| sympy | 1.14.0 |
| tabulate | 0.10.0 |
| tenacity | 9.1.4 |
| threadpoolctl | 3.6.0 |
| tifffile | 2026.5.2 |
| tinycss2 | 1.5.1 |
| tinyhtml5 | 2.1.0 |
| toml | 0.10.2 |
| torch | 2.12.0 |
| torchvision | 0.27.0 |
| tornado | 6.5.4 |
| tqdm | 4.67.3 |
| twilio | 9.10.4 |
| typer | 0.24.1 |
| typing-inspection | 0.4.2 |
| typing_extensions | 4.15.0 |
| tzdata | 2025.3 |
| urllib3 | 2.6.3 |
| uvicorn | 0.44.0 |
| watchdog | 6.0.0 |
| weasyprint | 69.0 |
| webencodings | 0.5.1 |
| websockets | 16.0 |
| xgboost | 3.2.0 |
| xlsxwriter | 3.2.9 |
| xxhash | 3.6.0 |
| yarl | 1.23.0 |
| zopfli | 0.4.3 |

## Generated Outputs (554 files)

- `candidates\ranked_by_combined_score.csv`
- `candidates\ranked_by_coverage_area.csv`
- `candidates\ranked_by_coverage_scale.csv`
- `candidates\ranked_by_verification.csv`
- `candidates\ranked_candidates.csv`
- `candidates\raw_candidates.csv`
- `candidates\rescored_candidates.csv`
- `candidates\verified_candidates.csv`
- `chamfer_visualizations\SLD11_top_10_overlay.png`
- `chamfer_visualizations\SLD11_top_25_overlay.png`
- `chamfer_visualizations\SLD11_top_50_overlay.png`
- `chamfer_visualizations\SLD11_worst_25_overlay.png`
- `chamfer_visualizations\SLD1_top_10_overlay.png`
- `chamfer_visualizations\SLD1_top_25_overlay.png`
- `chamfer_visualizations\SLD1_top_50_overlay.png`
- `chamfer_visualizations\SLD1_worst_25_overlay.png`
- `chamfer_visualizations\SLD4_top_10_overlay.png`
- `chamfer_visualizations\SLD4_top_25_overlay.png`
- `chamfer_visualizations\SLD4_top_50_overlay.png`
- `chamfer_visualizations\SLD4_worst_25_overlay.png`
- `diagrams\SLD10\binary.png`
- `diagrams\SLD10\edges.png`
- `diagrams\SLD10\gray.png`
- `diagrams\SLD11\binary.png`
- `diagrams\SLD11\edges.png`
- `diagrams\SLD11\gray.png`
- `diagrams\SLD12\binary.png`
- `diagrams\SLD12\edges.png`
- `diagrams\SLD12\gray.png`
- `diagrams\SLD1\binary.png`
- `diagrams\SLD1\edges.png`
- `diagrams\SLD1\gray.png`
- `diagrams\SLD2\binary.png`
- `diagrams\SLD2\edges.png`
- `diagrams\SLD2\gray.png`
- `diagrams\SLD3\binary.png`
- `diagrams\SLD3\edges.png`
- `diagrams\SLD3\gray.png`
- `diagrams\SLD4\binary.png`
- `diagrams\SLD4\edges.png`
- `diagrams\SLD4\gray.png`
- `diagrams\SLD7\binary.png`
- `diagrams\SLD7\edges.png`
- `diagrams\SLD7\gray.png`
- `diagrams\SLD8\binary.png`
- `diagrams\SLD8\edges.png`
- `diagrams\SLD8\gray.png`
- `diagrams\SLD9\binary.png`
- `diagrams\SLD9\edges.png`
- `diagrams\SLD9\gray.png`
- ... and 504 more

## Generated Reports (17 files)

- `coverage_metrics_dataset.csv`
- `stage4_candidate_survival_audit.md`
- `stage4_feasibility_assessment.md`
- `stage4_rescoring_methodology.md`
- `stage5_budget_validation.md`
- `stage5_candidate_survival_audit.md`
- `stage5_verification_methodology.md`
- `stage6_readiness.md`
- `structural_feature_statistics.md`
- `template_similarity_statistics.md`
- `verification_feature_contribution.md`
- `verification_ranking_analysis.md`
- `verification_score_distribution.md`
- `visual_validation\MR_Symbol_validation_grid.png`
- `visual_validation\SLD11_validation_grid.png`
- `visual_validation\SLD1_validation_grid.png`
- `visual_validation\SLD4_validation_grid.png`
