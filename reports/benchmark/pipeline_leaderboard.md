# Unified Pipeline Benchmark Suite — Unified Pipeline Leaderboard

This leaderboard ranks all localization pipelines deterministically based on the official priority hierarchy: `Recall@100` > `MRR` > `Median First Correct Rank` > `Precision` > `MR Density Gain` > `Candidate Reduction`. No subjective ranking is permitted.

## Official Pipeline Leaderboard

| Rank | Pipeline | Recall@100 | MRR | Med First Corr | Precision | Recall | F1 Score | Recall@10 | Recall@20 | Recall@50 | Recall@500 | Mean Rank | Median Rank | Cand Red % | Density Gain |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 1 | Stage 5.12 (NMS @ IoU 0.50) | 0.3065 | 0.6792 | 1.5 | 0.0634 | 0.6336 | 0.1153 | 0.0710 | 0.1252 | 0.2112 | 0.5888 | 156.9 | 104.0 | 98.0% | 32.31x |
| 2 | Stage 5.x (Coverage Area) | 0.2710 | 0.6867 | 1.5 | 0.0020 | 0.9720 | 0.0039 | 0.0692 | 0.1159 | 0.1963 | 0.5533 | 2147.1 | 333.5 | 0.0% | 1.00x |
| 3 | Stage 5.1 (Verification Cascade) | 0.2710 | 0.6833 | 1.5 | 0.0347 | 0.6486 | 0.0659 | 0.0710 | 0.1159 | 0.1963 | 0.5533 | 232.8 | 140.0 | 96.2% | 17.67x |
| 4 | Stage 5.8 (Combined Score) | 0.2710 | 0.6833 | 1.5 | 0.0347 | 0.6486 | 0.0659 | 0.0710 | 0.1159 | 0.1963 | 0.5533 | 232.8 | 140.0 | 96.2% | 17.67x |
| 5 | Stage 5.9 (EXP_A) | 0.2710 | 0.6833 | 1.5 | 0.0347 | 0.6486 | 0.0659 | 0.0710 | 0.1159 | 0.1963 | 0.5533 | 232.6 | 140.0 | 96.2% | 17.67x |
| 6 | Stage 5.9 (EXP_B) | 0.2710 | 0.6833 | 1.5 | 0.0347 | 0.6486 | 0.0659 | 0.0710 | 0.1159 | 0.1963 | 0.5533 | 232.6 | 140.0 | 96.2% | 17.67x |
| 7 | Stage 5.9 (EXP_C) | 0.2710 | 0.6833 | 1.5 | 0.0347 | 0.6486 | 0.0659 | 0.0710 | 0.1159 | 0.1963 | 0.5533 | 232.6 | 140.0 | 96.2% | 17.67x |
| 8 | Stage 5.9 (EXP_D) | 0.2710 | 0.6833 | 1.5 | 0.0347 | 0.6486 | 0.0659 | 0.0710 | 0.1159 | 0.1963 | 0.5533 | 232.6 | 140.0 | 96.2% | 17.67x |
| 9 | Stage 5.9 (EXP_E) | 0.2710 | 0.6833 | 1.5 | 0.0347 | 0.6486 | 0.0659 | 0.0710 | 0.1159 | 0.1963 | 0.5626 | 227.6 | 140.0 | 96.2% | 17.67x |
| 10 | Stage 5.9 (EXP_F) | 0.2710 | 0.6833 | 1.5 | 0.0347 | 0.6486 | 0.0659 | 0.0710 | 0.1159 | 0.1963 | 0.5626 | 227.6 | 140.0 | 96.2% | 17.67x |
| 11 | Baseline (Raw Candidates) | 0.1907 | 0.8153 | 1.0 | 0.0020 | 0.9720 | 0.0039 | 0.0692 | 0.1009 | 0.1589 | 0.4037 | 5564.1 | 1042.0 | 0.0% | 1.00x |
