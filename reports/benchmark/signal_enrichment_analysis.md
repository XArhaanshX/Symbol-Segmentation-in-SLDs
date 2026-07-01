# Unified Pipeline Benchmark Suite — Signal Enrichment Analysis

This report quantifies candidate concentration and structural filtering effectiveness across all evaluated pipeline variants.

## Candidate Reduction & Signal Enrichment Table

| Pipeline | Initial Candidates | Final Candidates | Candidate Reduction % | MR Density | MR Density Gain |
|---|---|---|---|---|---|
| Baseline (Raw Candidates) | 264852 | 264852 | 0.0% | 0.0020 | 1.00x |
| Stage 5.1 (Verification Cascade) | 264852 | 10000 | 96.2% | 0.0347 | 17.67x |
| Stage 5.x (Coverage Area) | 264852 | 264852 | 0.0% | 0.0020 | 1.00x |
| Stage 5.8 (Combined Score) | 264852 | 10000 | 96.2% | 0.0347 | 17.67x |
| Stage 5.9 (EXP_A) | 264852 | 10000 | 96.2% | 0.0347 | 17.67x |
| Stage 5.9 (EXP_B) | 264852 | 10000 | 96.2% | 0.0347 | 17.67x |
| Stage 5.9 (EXP_C) | 264852 | 10000 | 96.2% | 0.0347 | 17.67x |
| Stage 5.9 (EXP_D) | 264852 | 10000 | 96.2% | 0.0347 | 17.67x |
| Stage 5.9 (EXP_E) | 264852 | 10000 | 96.2% | 0.0347 | 17.67x |
| Stage 5.9 (EXP_F) | 264852 | 10000 | 96.2% | 0.0347 | 17.67x |
| Stage 5.12 (NMS @ IoU 0.50) | 264852 | 5344 | 98.0% | 0.0634 | 32.31x |

## Key Observations
- **Baseline Density**: The baseline candidate pool contains a vast majority of background noise, resulting in low initial MR Density.
- **NMS Effectiveness**: Non-Maximum Suppression achieves substantial candidate reduction by eliminating spatial duplicates, significantly increasing MR Density Gain without altering semantic ranking scores.
