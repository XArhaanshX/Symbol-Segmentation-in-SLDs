# Experiment Reproduction Guide

The Symbol Segmentor framework is built on a history of empirical research spanning template generation strategies, structural separability analysis, and continuous score integration. 

This document explains how to reproduce the major historical experiments that define the current architecture. All experimental scripts have been safely preserved in the `exploration/` directory.

## 1. Template Generation Dilution Analysis (Stage 2)

**Objective**: Prove that standard pixel-domain image resizing (Method A) destroys thin-line topology at extreme minification, and validate Method D3 (Coordinate Scaling) as the solution.

**Script**: `exploration/archived/scripts/template_generation_methods.py` (Note: This script exists historically in the repository, you can find the related validation in `src/template_bank/template_validation.py`)

**Reproduction Steps**:
1. Open `config/template_bank.yaml`.
2. Change the generation method from `D3` back to `A` (standard resize).
3. Run `python src/template_bank/template_validation.py`.
4. Check `outputs/visual/template_bank/`. At scale 0.15, the generated Method A template will be completely blank (0 edge pixels). 
5. Revert configuration to `D3` and re-run. The templates will maintain perfect 1-pixel continuity down to scale 0.09.

**Outputs Produced**:
*   Images in `outputs/visual/template_bank/`

---

## 2. Structural Discriminator Discovery (Stage 5.8)

**Objective**: Determine which of the 25 calculated topological features possesses the strongest statistical power to separate true MR symbols from False Positives.

**Script**: `exploration/structural_discriminator_research/scripts/structural_discovery.py`

**Reproduction Steps**:
1. Ensure the candidate feature dataset exists: `data/intermediate/candidate_features/structural_discriminator_features.csv`.
2. Run `python exploration/structural_discriminator_research/scripts/structural_discovery.py`.
3. The script will calculate the ROC-AUC, Cohen's *d*, and distribution overlap for all 25 features against 4 defined groups (True Positives, Dominant FPs, Hard Negatives, Background).

**Outputs Produced**:
*   `reports/structural_discriminators/discriminator_leaderboard.md` (identifies Stroke_Count as #1)
*   `reports/structural_discriminators/feature_separability_audit.md`
*   Histogram plots in `outputs/visual/diagnostics/`

---

## 3. Continuous Score Integration Failure (Stage 5.9)

**Objective**: Demonstrate the "Separability vs. Ranking" paradox. Specifically, show that although Stroke_Count has massive separability (AUC=0.951), integrating it into the scoring formula as a continuous multiplier completely collapses candidate ranking.

**Script**: `exploration/archived/scripts/stage5_9_discriminator_integration.py` (Renamed in archive)

**Reproduction Steps**:
1. Locate the script in `exploration/archived/scripts/stroke_integration_experiments.py`.
2. Execute the script. It will run 5 competitive experiments (`BASE`, `EXP_A`, `EXP_B`, `EXP_C`, `EXP_D`). Each experiment uses a different exponential decay penalty based on `Stroke_Count`.
3. The script evaluates the resulting rankings using the benchmarking module.

**Outputs Produced**:
*   `reports/archive/stroke_integration_best_selection.md`
*   The results will show `BASE` (no structural multiplier) achieving a Top-100 Hit Rate of ~5.8%, while all stroke integration variants (`EXP_A` through `D`) drop to 0.0%–2.7%.

---

## 4. Coverage Ratio Redundancy (Stage 4 Analysis)

**Objective**: Prove that `Coverage Ratio` is not an orthogonal feature to `Chamfer Score`, and that small-template False Positives frequently possess higher coverage than large-template True Positives.

**Script**: `exploration/archived/scripts/stage4_rank_analysis.py` (Renamed in archive)

**Reproduction Steps**:
1. Execute `python exploration/archived/scripts/coverage_area_rescoring_analysis.py`.
2. The script computes the Pearson correlation coefficient ($r$) between raw Chamfer Score and Coverage Ratio across all 264,852 candidates.

**Outputs Produced**:
*   `reports/archive/coverage_discriminative_power_assessment.md`
*   The output will demonstrate a correlation of $r \approx -0.90$, proving the two metrics are fundamentally mathematically entangled.

---

## 5. Verification Cascade Evaluation (Stage 5.10)

**Objective**: Explore discrete structural gates (pass/fail thresholds) as an alternative to the failed continuous score multipliers.

**Script**: `exploration/verification_cascade_research/scripts/verification_cascade_discovery.py`

**Reproduction Steps**:
1. Navigate to `exploration/verification_cascade_research/scripts/`.
2. Execute the cascade discovery scripts in sequence (parts 1 through 5).
3. Run the visual audit generation script: `python exploration/verification_cascade_research/scripts/cascade_visual_audit.py`.

**Outputs Produced**:
*   Reports generated in `reports/verification_cascades/`.
*   The visual audit overlays generated in `outputs/visual/overlays/` will reveal that while numerical metrics appeared to improve, visually, the top candidates remained false positives (the Stage 5.10 Paradox).

---

## Rule for Future Experiments

When designing new research experiments (e.g., implementing PCA Subspace Verification):
1. **Never** modify `src/` directly until the math is proven on a subset of the dataset.
2. Build your experiment script in `exploration/[your_research_topic]/scripts/`.
3. Read intermediate data from `data/intermediate/`.
4. Output analysis to `reports/experiments/`.
5. Only migrate the logic into `src/` once the metrics unequivocally demonstrate an improvement in the `unified_pipeline_benchmark`.
