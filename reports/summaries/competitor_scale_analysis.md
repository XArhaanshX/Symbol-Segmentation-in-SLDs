# Competitor Scale Analysis

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

- Mean Scale Ratio (Competitor/True): 1.079
- Median Scale Ratio: 1.000
- Std Dev: 0.132

## Required Questions
1. **Do competitors tend to be smaller than true symbol candidates?** No, mean scale ratio > 1 implies they are larger.
2. **Do competitors tend to be larger than true symbol candidates?** Yes.
3. **Are ranking failures associated with significant scale mismatches?** Yes, false positives exploit larger scales.
4. **Is historical scale bias still influencing ranking behavior after Stage 4 rescoring?** Yes, the bias persists despite Stage 4 normalization.
