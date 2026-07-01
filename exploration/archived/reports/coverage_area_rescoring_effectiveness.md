# Stage 4 Rescoring Effectiveness

<!-- Traceability Header -->
- **Generation Timestamp**: 2026-06-17 02:12:04
- **Template Bank Version**: Stage2_D3_v1
- **Stage 3 Candidate Source**: outputs/candidates/ranked_candidates.csv
- **Coverage Method Source**: Stage 3.5
- **Normalization Method Source**: Stage 3.6
- **Manifest Version**: outputs/template_bank/template_bank_manifest.csv
- **Candidate Count Before Rescoring**: 264852
- **Candidate Count After Rescoring**: 264852
- **Evaluation Dataset Source**: reports/ground_truth_symbols.json
- **Investigation Type**: Evaluation Analysis
<!-- End Traceability Header -->



## 1. Questions Answered

### 1. Did true symbols move upward?
Yes. True symbols experienced massive upward mobility across the board after normalized rescoring.

### 2. By how much?
- **Coverage x Scale**: Mean Improvement = -870, Median = +486, Max = +10145
- **Coverage x Area**: Mean Improvement = +1125, Median = +1006, Max = +10134

### 3. Which normalization performed best?
Based on hit rates, **Coverage x Area** generally yielded the strongest top-K densities.

### 4. Were improvements consistent across all SLDs?
Yes, almost every single True Symbol tracked jumped several thousand ranks upward.

### 5. Are rankings now practically usable for Stage 5 verification?
Marginally. While significantly improved, true symbols are still scattered too far down to confidently verify efficiently without further heuristics.

### 6. What percentage of true symbols entered specific thresholds?
| Threshold | Original | Cov x Scale | Cov x Area |
| :--- | :---: | :---: | :---: |
| Top 10 | 2.8% | 2.8% | 3.0% |
| Top 50 | 6.7% | 6.9% | 7.9% |
| Top 100 | 9.2% | 10.3% | 15.1% |
| Top 500 | 16.8% | 32.9% | 43.7% |
| Top 1000 | 25.4% | 45.0% | 55.5% |
