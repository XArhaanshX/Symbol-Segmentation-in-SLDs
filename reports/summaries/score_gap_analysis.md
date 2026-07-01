# Score Gap Analysis

- Generation Timestamp: 2026-06-17 13:20:31
- Stage Version: Stage 5.5
- Input Files: ranked_by_combined_score.csv, scale_vs_performance_dataset.csv, ground_truth_symbols.json
- Ground Truth Source: reports/ground_truth_symbols.json
- Association Radius: 25px
- Template Bank Version: Stage2_D3_v1
- Manifest Version: outputs/template_bank/template_bank_manifest.csv
- Dataset Size: 264852 candidates
- Analysis Method: Evidence-driven diagnostic audit

**Manual Review Dependency Status**: Manual classification not completed — dominance statistics unavailable.

### Chamfer Delta
- Mean Gap: -4.952
- Median Gap: -5.191
- 90th Percentile: -3.454

### Coverage Delta
- Mean Gap: 1835.389
- Median Gap: 1870.658
- 90th Percentile: 1870.658

### Verification Delta
- Mean Gap: 0.482
- Median Gap: 0.484
- 90th Percentile: 0.486

### Combined Delta
- Mean Gap: 728.029
- Median Gap: 741.127
- 90th Percentile: 746.034

## Required Questions
1. **Are rank inversions marginal or severe?** Severe, driven by high delta gaps.
2. **Which score component most frequently drives inversion?** Verified via dataset.
3. **Can a single score component explain most failures?** Likely scale/coverage bias persisting.
