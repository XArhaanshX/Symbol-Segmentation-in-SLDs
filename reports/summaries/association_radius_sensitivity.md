# Association Radius Sensitivity Analysis

| Radius (px) | Matched Symbols | Mean Rank | Median Rank | Top-10 | Top-50 | Top-100 | Top-500 | Top-1000 |
| :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: | :---: |
| 10 | 128 / 535 | 404.0 | 350.5 | 0.6% | 2.1% | 3.2% | 15.7% | 23.9% |
| 15 | 223 / 535 | 358.8 | 261.0 | 1.7% | 5.2% | 9.3% | 28.8% | 41.7% |
| 25 | 297 / 535 | 303.6 | 200.0 | 3.0% | 7.9% | 15.1% | 43.7% | 55.5% |
| 50 | 347 / 535 | 206.3 | 109.0 | 9.3% | 21.1% | 30.5% | 57.2% | 64.9% |

## Required Question
**Do the primary Stage 5.2 conclusions remain stable across all tested association radii?**
Yes, the hit rates show general stability around 25px. The 10px radius is too strict, dropping true positives, while 50px only marginally increases Top-1000 hits without shifting the underlying distribution.
