# Unified Pipeline Benchmark Suite — Executive Benchmark Summary

## Executive Overview
This executive summary synthesizes the findings of the Unified Pipeline Benchmark Suite. Every major localization pipeline developed throughout this project was evaluated under one identical dual-metric evaluation protocol, preserving native ranking semantics and 100% artifact immutability.

## Definitive Pipeline Designations

### 1. Best Localization Pipeline: `Stage 5.12 (NMS @ IoU 0.50)`
- **Dataset**: `C:\Users\arhaa\OneDrive\Symbol Segmentor\outputs\nms_overlays\iou_050\filtered_candidates.csv`
- **Metric**: F1 Score (Metric A)
- **Measured Value**: `0.1153` (Precision `0.0634`, Recall `0.6336`)
- **Source Report**: `reports/benchmark/unified_benchmark_report.md`

### 2. Best Ranking Pipeline: `Baseline (Raw Candidates)`
- **Dataset**: `C:\Users\arhaa\OneDrive\Symbol Segmentor\outputs\tabular\exports\raw_candidates.csv`
- **Metric**: Mean Reciprocal Rank (MRR)
- **Measured Value**: `0.8153` (Recall@100 `0.1907`)
- **Source Report**: `reports/benchmark/pipeline_leaderboard.md`

### 3. Best Computational Pipeline: `Stage 5.12 (NMS @ IoU 0.50)`
- **Dataset**: `C:\Users\arhaa\OneDrive\Symbol Segmentor\outputs\nms_overlays\iou_050\filtered_candidates.csv`
- **Metric**: Candidate Reduction % & MR Density Gain
- **Measured Value**: `98.0%` reduction (`32.31x` density gain)
- **Source Report**: `reports/benchmark/signal_enrichment_analysis.md`

### 4. Best Overall Pipeline: `Stage 5.12 (NMS @ IoU 0.50)`
- **Dataset**: `C:\Users\arhaa\OneDrive\Symbol Segmentor\outputs\nms_overlays\iou_050\filtered_candidates.csv`
- **Metric**: Official Leaderboard Priority Hierarchy (`Recall@100` > `MRR` > `Med First Corr`)
- **Measured Value**: Recall@100 `0.3065`, MRR `0.6792`
- **Source Report**: `reports/benchmark/pipeline_leaderboard.md`

## Architectural Trade-Off Analysis
> [!WARNING]
> **Objective Divergence**: Different pipeline stages optimize distinct objectives. For instance, NMS pipelines excel at Candidate Reduction and MR Density Gain (filtering out spatial duplicates), whereas Verification Cascade pipelines excel at semantic ranking (MRR and Recall@K). Rather than declaring a single subjective winner, system architects should cascade these mechanisms: utilizing NMS as a lightweight early-stage filter to maximize density, followed by structural verification cascades to maximize MRR.
