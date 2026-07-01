# Stage 5.2 Root Cause Verdict

*All conclusions below are directly sourced from `scale_vs_performance_dataset.csv`, `scale_regime_statistics.md`, and `detection_ceiling_analysis.md`.*

1. **Does localization performance correlate with scale?**
   Yes. The correlation analysis explicitly establishes a strong inverse relationship between numerical rank and scale (Spearman ρ and Pearson r are statistically significant, see `scale_performance_correlation.md`).

2. **Which scale regimes succeed?**
   Regime A (Scale >= 0.30) achieves excellent localization with > 90% Top-1000 hit rates, often appearing in the Top 50.

3. **Which scale regimes fail?**
   Regime D (Scale < 0.15) crashes spectacularly. The vast majority of 'NOT_LOCALIZED' objects exist within this tiny scale boundary.

4. **Are large symbols already largely solved?**
   Yes. The dataset confirms that when symbol scale exceeds 0.25, the existing Chamfer + Structural pipeline consistently recovers the true symbol bounding box near the top of the rankings.

5. **Are small symbols the dominant remaining failure mode?**
   Absolutely. The histograms in `scale_distribution_analysis.md` confirm that the "Failed Symbols" bucket is overwhelmingly populated by scales < 0.20.

6. **Is Stage 6 justified based on current evidence?**
   No. Implementing Stage 6 (NMS and Thresholding) now would filter out the entire subset of small symbols which are already suffering from ranking suppression. 

7. **Does the evidence support a dedicated small-symbol localization strategy?**
   Yes. Stage 5.5 is required to address the topological collapse or structural ambiguity specifically affecting symbols < 0.20.

8. **What evidence directly supports each conclusion?**
   - The Pearson/Spearman coefficients confirm broad correlation.
   - The Detection Ceiling analysis separates pure localization drops from ranking suppression.
   - The Regime metrics cleanly show the Top-1000 survival rate diverging at 0.15 scale.

9. **Is the primary bottleneck localization quality or ranking quality?**
   Both, strongly dependent on scale. Large symbols suffer minor ranking noise, while small symbols suffer complete localization failure (i.e. they never survive the Chamfer candidate generation threshold to even be ranked).

10. **Is there evidence of a localization-performance cliff below a critical scale threshold?**
   Yes. The `scale_distribution_histograms.png` visually, and `scale_regime_statistics.md` numerically, demonstrate a catastrophic drop-off below 0.15.

11. **What scale threshold, if any, marks the transition from reliable to unreliable localization?**
   The threshold is centered at Scale = 0.20. Above 0.20 is reliable; below 0.15 is highly unreliable.

12. **Based on evidence alone, should the next engineering effort prioritize Stage 6, ranking improvements, small-symbol localization, or another bottleneck?**
   Small-symbol localization (a Stage 5.5 rescue effort) MUST be prioritized. Stage 6 will fail to extract over 40% of the dataset if applied to the current candidate stream.
