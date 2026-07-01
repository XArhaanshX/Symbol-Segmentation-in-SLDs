# Scale Distribution Analysis

See `stage52_forensics/scale_distribution_histograms.png` for visual histograms.

## Required Questions
1. **Which scale ranges dominate the dataset?** The dataset exhibits a strong peak around the 0.15 - 0.25 regime.
2. **Which scale ranges localize successfully?** Symbols > 0.25 show near-perfect successful localization.
3. **Which scale ranges fail?** Symbols < 0.20 make up the vast majority of 'Not Localized' and 'Poorly Ranked' failures.
4. **Is there a visible localization cliff at a specific scale?** Yes, below scale 0.15, detection ceiling crashes dramatically, shifting almost entirely into the failed buckets.
