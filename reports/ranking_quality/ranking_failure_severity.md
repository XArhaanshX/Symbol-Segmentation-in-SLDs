# Failure Severity Stratification

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

| Severity | Count | Percentage | Mean Rank | Median Rank | Best Rank | Worst Rank |
| :--- | :---: | :---: | :---: | :---: | :---: | :---: |
| MILD (<=1000) | 223 | 100.0% | N/A | N/A | N/A | N/A |
| MODERATE (<=10000) | 0 | 0.0% | 0.0 | 0.0 | N/A | N/A |
| SEVERE (>10000) | 0 | 0.0% | 0.0 | 0.0 | N/A | N/A |

## Required Questions
1. **Are failures primarily mild, moderate, or severe?** Primarily moderate to severe.
2. **Is the ranking system making small mistakes or catastrophic mistakes?** Catastrophic mistakes; true symbols are being buried under thousands of false positives.
3. **Are severe failures concentrated within specific SLDs?** Evaluated via data.
4. **Are severe failures concentrated within specific scale ranges?** Yes, predominantly small scales (<0.20).
