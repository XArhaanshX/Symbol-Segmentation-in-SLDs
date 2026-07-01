# Unified Pipeline Benchmark Suite — Master Evaluation Report

## Mandatory Execution Rule (Patch U-01I)
> [!IMPORTANT]
> **Deterministic Ranking Semantics**: Every pipeline was evaluated using its native ranking score exactly as produced by that pipeline (`CombinedScore`, `VerificationScore`, `CoverageScore`, `ExperimentalScore`, etc.). The benchmark never recomputes, normalizes, or modifies ranking scores. Original ranking semantics are strictly preserved.

## Section 1: Localization Quality Metrics
*These metrics evaluate only localization performance. No ranking metric is used here.*

| Pipeline | Total Candidates | TP (A) | FP (A) | FN (A) | Precision (A) | Recall (A) | F1 (A) | Mean Loc Err (px) | Med Loc Err (px) | Mean IoU | Med IoU |
|---|---|---|---|---|---|---|---|---|---|---|---|
| Baseline (Raw Candidates) | 264852 | 520 | 264332 | 15 | 0.0020 | 0.9720 | 0.0039 | 35.01 | 33.24 | 0.5376 | 0.5081 |
| Stage 5.1 (Verification Cascade) | 10000 | 347 | 9653 | 188 | 0.0347 | 0.6486 | 0.0659 | 31.91 | 29.07 | 0.5507 | 0.5182 |
| Stage 5.x (Coverage Area) | 264852 | 520 | 264332 | 15 | 0.0020 | 0.9720 | 0.0039 | 32.15 | 28.90 | 0.5376 | 0.5081 |
| Stage 5.8 (Combined Score) | 10000 | 347 | 9653 | 188 | 0.0347 | 0.6486 | 0.0659 | 31.91 | 29.07 | 0.5507 | 0.5182 |
| Stage 5.9 (EXP_A) | 10000 | 347 | 9653 | 188 | 0.0347 | 0.6486 | 0.0659 | 31.90 | 29.07 | 0.5507 | 0.5182 |
| Stage 5.9 (EXP_B) | 10000 | 347 | 9653 | 188 | 0.0347 | 0.6486 | 0.0659 | 31.90 | 29.07 | 0.5507 | 0.5182 |
| Stage 5.9 (EXP_C) | 10000 | 347 | 9653 | 188 | 0.0347 | 0.6486 | 0.0659 | 31.90 | 29.07 | 0.5507 | 0.5182 |
| Stage 5.9 (EXP_D) | 10000 | 347 | 9653 | 188 | 0.0347 | 0.6486 | 0.0659 | 31.90 | 29.07 | 0.5507 | 0.5182 |
| Stage 5.9 (EXP_E) | 10000 | 347 | 9653 | 188 | 0.0347 | 0.6486 | 0.0659 | 31.27 | 29.07 | 0.5507 | 0.5182 |
| Stage 5.9 (EXP_F) | 10000 | 347 | 9653 | 188 | 0.0347 | 0.6486 | 0.0659 | 31.27 | 29.07 | 0.5507 | 0.5182 |
| Stage 5.12 (NMS @ IoU 0.50) | 5344 | 339 | 5005 | 196 | 0.0634 | 0.6336 | 0.1153 | 30.18 | 27.29 | 0.5507 | 0.5182 |

## Section 2: Ranking Quality Metrics
*These metrics evaluate only ranking quality. No localization metric is used here.*

| Pipeline | Mean MR Rank | Median MR Rank | Best Rank | Worst Rank | Mean First Correct Rank | Median First Correct Rank | Mean Reciprocal Rank (MRR) |
|---|---|---|---|---|---|---|---|
| Baseline (Raw Candidates) | 5564.1 | 1042.0 | 1 | 47943 | 3.5 | 1.0 | 0.8153 |
| Stage 5.1 (Verification Cascade) | 232.8 | 140.0 | 1 | 1000 | 2.1 | 1.5 | 0.6833 |
| Stage 5.x (Coverage Area) | 2147.1 | 333.5 | 1 | 16116 | 2.0 | 1.5 | 0.6867 |
| Stage 5.8 (Combined Score) | 232.8 | 140.0 | 1 | 1000 | 2.1 | 1.5 | 0.6833 |
| Stage 5.9 (EXP_A) | 232.6 | 140.0 | 1 | 1000 | 2.1 | 1.5 | 0.6833 |
| Stage 5.9 (EXP_B) | 232.6 | 140.0 | 1 | 1000 | 2.1 | 1.5 | 0.6833 |
| Stage 5.9 (EXP_C) | 232.6 | 140.0 | 1 | 1000 | 2.1 | 1.5 | 0.6833 |
| Stage 5.9 (EXP_D) | 232.6 | 140.0 | 1 | 1000 | 2.1 | 1.5 | 0.6833 |
| Stage 5.9 (EXP_E) | 227.6 | 140.0 | 1 | 950 | 2.1 | 1.5 | 0.6833 |
| Stage 5.9 (EXP_F) | 227.6 | 140.0 | 1 | 950 | 2.1 | 1.5 | 0.6833 |
| Stage 5.12 (NMS @ IoU 0.50) | 156.9 | 104.0 | 1 | 611 | 2.3 | 1.5 | 0.6792 |

## Section 3: Official Retrieval Metrics (Patch U-01B)
*These represent the official retrieval metrics for pipeline comparison.*

| Pipeline | Recall@10 | Recall@20 | Recall@50 | Recall@100 | Recall@500 |
|---|---|---|---|---|---|
| Baseline (Raw Candidates) | 0.0692 | 0.1009 | 0.1589 | 0.1907 | 0.4037 |
| Stage 5.1 (Verification Cascade) | 0.0710 | 0.1159 | 0.1963 | 0.2710 | 0.5533 |
| Stage 5.x (Coverage Area) | 0.0692 | 0.1159 | 0.1963 | 0.2710 | 0.5533 |
| Stage 5.8 (Combined Score) | 0.0710 | 0.1159 | 0.1963 | 0.2710 | 0.5533 |
| Stage 5.9 (EXP_A) | 0.0710 | 0.1159 | 0.1963 | 0.2710 | 0.5533 |
| Stage 5.9 (EXP_B) | 0.0710 | 0.1159 | 0.1963 | 0.2710 | 0.5533 |
| Stage 5.9 (EXP_C) | 0.0710 | 0.1159 | 0.1963 | 0.2710 | 0.5533 |
| Stage 5.9 (EXP_D) | 0.0710 | 0.1159 | 0.1963 | 0.2710 | 0.5533 |
| Stage 5.9 (EXP_E) | 0.0710 | 0.1159 | 0.1963 | 0.2710 | 0.5626 |
| Stage 5.9 (EXP_F) | 0.0710 | 0.1159 | 0.1963 | 0.2710 | 0.5626 |
| Stage 5.12 (NMS @ IoU 0.50) | 0.0710 | 0.1252 | 0.2112 | 0.3065 | 0.5888 |
