# Circuit Symbol Localization — Master Research Retrospective

## Architecture History · Failure Analysis · Lessons Learned · Future Direction

---

> **Document Purpose**: Canonical historical reference for the entire Circuit Symbol Localization project.
> **Generated**: 2026-06-18 · **Source**: Full repository forensic audit of all reports, code, and artifacts.

---

# SECTION 1 — Executive Summary

## 1.1 Original Project Objective

Locate every instance of a specific Current Transformer (CT/MR) symbol across 10 industrial Single Line Diagrams (SLDs) using **one query template image** and **zero training data**. The system must be fully deterministic, CPU-only, and explainable.

- **Dataset**: 1 template (MR_Symbol.png, 161×103px) + 10 SLDs (SLD1–SLD12, excluding SLD5/SLD6)
- **Estimated total MR occurrences**: ~138 across all diagrams
- **Success criteria**: Recall ≥0.90, Precision ≥0.85, F1 ≥0.87, IoU ≥0.50

## 1.2 Current Project Status

**NOT PRODUCTION-READY.** The project has completed through Stage 5.10 (Verification Cascade) but has **never passed the Stage 6 readiness gate**. Two separate gate evaluations (Stage 5.6 and Stage 5.9) returned **NOT READY FOR STAGE 6**.

- Stage 6 (NMS + Thresholding + Final Output) has never been executed
- No final precision/recall/F1 scores have been computed on the full dataset
- The ranking quality remains insufficient: median MR rank = 573, Top-100 hit rate = 5.8%

## 1.3 Current Best-Performing Pipeline

The best known pipeline is the **BASE** experiment from Stage 5.9:

| Metric | Value | Source |
|---|---|---|
| Median MR Rank | 573.0 | stage59_best_experiment_selection.md |
| Top-100 Hit Rate | 5.8% | stage59_best_experiment_selection.md |
| Top-500 Hit Rate | 41.4% | stage59_best_experiment_selection.md |
| Inversions Resolved | 0/10 | stage59_best_experiment_selection.md |

Pipeline: Preprocessing → Template Bank (D3) → Chamfer Matching → Coverage×Area Rescoring → Structural Verification → Combined Score Ranking

## 1.4 Major Discoveries

1. **Small-scale template bias** destroys raw Chamfer ranking — small templates produce artificially low scores on text/conductors
2. **Coverage ratio is NOT independent** of Chamfer score (r ≈ −0.90) — it provides zero orthogonal signal
3. **Stroke_Count** is the best structural discriminator (AUC=0.951 vs Dominant FP) but **fails catastrophically** when integrated as a continuous multiplier
4. **Separability ≠ Ranking improvement** — the most fundamental lesson of the project
5. **Visual audits contradict quantitative metrics** — Stage 5.10 appeared numerically successful but visual inspection revealed ongoing failures
6. **Connected-component isolation is impossible** — MR symbols are topologically embedded in bus conductors (empirically proven, Stages 2–2.75)

## 1.5 Major Unresolved Problems

1. Ranking inversions: false positives consistently outrank true MR symbols
2. Small-symbol localization failure: symbols at scale < 0.15 are effectively undetectable
3. No validated method to convert strong separability signals into ranking improvement
4. Stage 6 has never been reached

---

# SECTION 2 — Project Timeline

## Phase 1: Preprocessing & Template Analysis (Stage 1)
- **Objective**: Convert raw SLDs and template into clean binary edge representations
- **Method**: RGBA→Grayscale→Otsu binarization→Canny edge detection
- **Result**: Successfully produced clean edge maps. Dark pixel ratios 1.4%–4.0% confirmed sparse line drawings. Bimodal intensity made Otsu extremely robust.
- **Outcome**: ✅ PASSED. Key observations logged: stroke width ~1.5–2.5px, text regions create dense edge clutter, MR symbols connected to bus conductors.
- **Source**: stage1_observations_for_future_stages.md

## Phase 2: Template Bank Generation (Stage 2 → 2.7)
- **Objective**: Generate multi-scale multi-orientation template edge maps for Chamfer matching
- **Method (original)**: Resize template edges using cv2.INTER_AREA + threshold at 127 (Method A)
- **Result**: **CATASTROPHIC FAILURE.** Method A produced completely empty templates at scale ≤0.20 due to edge intensity dilution during downsampling. 0 edge pixels at scale 0.15.
- **Recovery**: Systematic evaluation of 7 methods (A–E, D1–D3). **Method D3** (Coordinate Scaling + Anti-Aliased Rasterization) selected — subpixel factor=8, threshold=25, line-drawing rasterization.
- **Outcome**: ✅ REPAIRED. 40 templates (10 scales × 4 orientations), bank version Stage2_D3_v1 certified.
- **Source**: stage2_final_resolution.md, stage2_certification.md

## Phase 3: Chamfer Matching & Candidate Generation (Stage 3)
- **Objective**: Dense sliding-window Chamfer matching across all SLDs
- **Method**: Precompute Euclidean DT, cv2.filter2D for fast scoring, local minima extraction
- **Result**: 264,852 raw candidate proposals. True MR symbols present but **zero in top 100**. False positive precision at top-100 = 0.0%.
- **Key Finding**: Small-scale templates (0.150–0.178) dominate rankings because few edge pixels trivially match text strokes and conductors (median Chamfer 0.72px vs true symbols 6.50px).
- **Outcome**: ⚠️ Candidates generated but ranking completely inverted.
- **Source**: stage3_failure_analysis.md, stage3_candidate_generation.md

## Phase 4: Coverage Rescoring (Stage 4)
- **Objective**: Rescore candidates using Coverage×Area normalization to counteract small-scale bias
- **Method**: Area-normalized rescoring using coverage ratio and template area
- **Result**: Massive rank improvements for most true symbols (median improvement +1000–2000 ranks). Some symbols reached Top-10 per-SLD.
- **Key Finding**: Coverage is strongly correlated with Chamfer score (r ≈ −0.90), providing no independent information. False positives have HIGHER coverage than true symbols (median 93–94% vs 73%).
- **Outcome**: ✅ Significant improvement but ranking still insufficient for Stage 6.
- **Source**: stage4_rank_improvement_analysis.md, coverage_discriminative_power_assessment.md

## Phase 5: Structural Verification (Stage 5)
- **Objective**: Compute topological/structural features for each candidate to enable discrimination
- **Method**: 25 structural discriminators computed per candidate (Stroke_Count, Branch_Point_Count, Loop_Count, Euler_Number, etc.)
- **Result**: Budget of 1000 candidates per SLD (10,000 total). Verification scores generated.
- **Outcome**: ✅ Feature profiles generated. Stage 6 readiness initially claimed but later revoked.
- **Source**: stage6_readiness.md, verification_feature_contribution.md

## Phase 5.1–5.2: Scale-Performance Root Cause Analysis
- **Objective**: Determine why rankings remain poor after Stage 4/5
- **Method**: Correlate symbol scale with rank position across all SLDs
- **Result**: Strong inverse correlation (Spearman ρ significant). Scale ≥0.30: >90% Top-1000 hit rate. Scale <0.15: catastrophic failure. Threshold at Scale=0.20.
- **Outcome**: ⚠️ Stage 6 BLOCKED. Small-symbol localization identified as dominant bottleneck.
- **Source**: stage52_root_cause_verdict.md, stage6_readiness_reassessment.md

## Phase 5.5–5.6: Ranking Remediation Experiments
- **Objective**: Improve ranking through alternative scoring formulas
- **Method**: 14 experiments tested (A1–A5, B1–B6, C1–C3) varying area penalization, scale normalization, and verification weighting
- **Result**: Best experiment B4 (Coverage×Area×Scale) improved Top-100 Hit Rate but failed Median Rank and Inversion criteria.
- **Outcome**: ❌ Stage 6 gate FAILED (2 of 8 criteria failed: Median Rank, Inversions).
- **Source**: stage56_architectural_verdict.md, stage56_experiment_registry.md

## Phase 5.8: Structural Discriminator Discovery
- **Objective**: Identify which structural features best separate MR symbols from false positives
- **Method**: ROC-AUC, Cohen's d, and overlap analysis for 25 features across 4 candidate groups
- **Result**: Stroke_Count = #1 discriminator (AUC=0.951, d=2.647 vs Dominant FP). All features show AUC=0.000 vs Hard Negatives.
- **Critical Finding**: Strong separability against Dominant FP but ZERO separability against Hard Negatives.
- **Outcome**: ✅ Discriminator leaderboard established. But separability ≠ ranking improvement.
- **Source**: discriminator_leaderboard.md, feature_separability_audit.md

## Phase 5.9: Stroke_Count Integration Experiments
- **Objective**: Integrate Stroke_Count into scoring to improve ranking
- **Method**: 5 experiments (BASE, EXP_A–D) using exponential decay penalty: exp(−0.05 × Stroke_Count)
- **Result**: All Stroke_Count integrations DEGRADED performance. BASE remained best. EXP_A: 0% Top-100 hit rate.
- **Critical Discovery**: Continuous structural scoring collapses ranking. Features that separate distributions do NOT necessarily improve rank ordering when used as multipliers.
- **Outcome**: ❌ Stage 6 gate FAILED again (Inversions criterion).
- **Source**: stage59_best_experiment_selection.md, stage59_stage6_gate.md

## Phase 5.9a: Template Stroke Consistency Research
- **Objective**: Explore whether template-candidate stroke consistency could improve discrimination
- **Method**: Dedicated research scripts comparing stroke patterns between template and candidates
- **Outcome**: Exploratory. Evidence not available for conclusive results.
- **Source**: exploration/template_consistency_research/

## Phase 5.9b: Symbol Existence Feature Research
- **Objective**: Explore existence-based features as discriminators
- **Method**: Binary existence features computed for candidate patches
- **Outcome**: Exploratory. Evidence not available for conclusive results.
- **Source**: exploration/symbol_existence_research/

## Phase 5.10: Verification Cascade Discovery
- **Objective**: Discover whether discrete verification gates (pass/fail) outperform continuous scoring
- **Method**: Multi-part cascade with discrete structural gates, visual audit validation
- **Result**: Appeared numerically promising but visual audit revealed ongoing issues.
- **Critical Discovery**: Visual reality diverged from numerical metrics.
- **Outcome**: ⚠️ Inconclusive — led to visual audit methodology investigation.
- **Source**: exploration/verification_cascade_research/, reports/stage510_forensics/, reports/stage510_visual_audit/

## Phase 6: Repository Restructuring
- **Objective**: Reorganize repository from flat structure to semantic hierarchy
- **Method**: 1,450+ files audited, dependency analysis, batch relocation scripts
- **Result**: Clean separation of production code (src/), exploration code, reports, and outputs.
- **Outcome**: ✅ Completed. All files preserved with traceability.
- **Source**: reports/restructure/traceability_preservation_report.md

---

# SECTION 3 — Production Pipeline Evolution

## 3.1 Original Pipeline (PRD Design)

```
Preprocessing → Scale Pyramid → Chamfer Matching → NMS → PCA Verification → Output
```

- Chamfer matching as primary localization
- PCA subspace as semantic verification
- Score fusion: 0.7 Chamfer + 0.3 PCA with exponential normalization (α=2.0)
- Source: PRD_Symbol_Localization.md, Section 6

## 3.2 Revision 1: Method D3 Template Bank (Stage 2.7)

**Why introduced**: Original Method A template generation produced empty templates at small scales due to edge intensity dilution during downsampling. At scale 0.15, Method A produced 0 edge pixels (100% loss).

**Change**: Replaced cv2.resize + threshold with Coordinate Scaling + Anti-Aliased Rasterization (subpixel factor=8).

**Why it succeeded**: Method D3 preserves continuous boundaries (102 edge pixels, 1.00 continuity at scale 0.15) by rasterizing connections between scaled coordinate points rather than downsampling pixel data.

**Source**: stage2_final_resolution.md

## 3.3 Revision 2: Coverage×Area Rescoring (Stage 4)

**Why introduced**: Raw Chamfer ranking was completely inverted — small templates matching text/conductors scored better than true symbols. True symbols at rank ~20,000 of 264,852.

**Change**: Rescore using Coverage_Ratio × Template_Area to penalize small-template spurious matches.

**Why it partially succeeded**: Area normalization counteracts small-template bias. True symbols improved by +1000–2000 ranks on average.

**Why it partially failed**: Coverage ratio is monotonically correlated with Chamfer score (r ≈ −0.90). It does not provide independent discriminative signal. FPs have higher coverage than TPs.

**Source**: stage4_rank_improvement_analysis.md, coverage_discriminative_power_assessment.md

## 3.4 Revision 3: Structural Verification Score (Stage 5)

**Why introduced**: Chamfer + Coverage alone cannot discriminate MR from visually similar symbols sharing geometric sub-primitives.

**Change**: Compute 25 structural features per candidate; weighted combination into VerificationScore. Combined with CoverageAreaScore: CombinedScore = blend of both.

**Why it partially succeeded**: Established structural profiles for all candidates.

**Why it partially failed**: The weighted combination of continuous features did not produce sufficient ranking separation. The PCA verification approach from the PRD was replaced by these structural features, but the structural features proved correlated with Chamfer score (CLASS B: Partially Redundant).

**Source**: verification_feature_contribution.md, discriminator_redundancy_analysis.md

## 3.5 Current Pipeline

```
1. Preprocessing (Otsu + Canny)
2. Template Bank (Method D3, 40 variants: 10 scales × 4 rotations)
3. Chamfer Matching (cv2.filter2D, 264,852 candidates)
4. Coverage×Area Rescoring (ranked_by_coverage_area.csv)
5. Structural Verification (25 features, 1000/SLD budget)
6. Combined Score Ranking (CoverageArea + Verification blend)
--- STAGE 6 GATE: NOT PASSED ---
7. NMS + Thresholding (never executed)
8. Output Generation (never executed)
```

---

# SECTION 4 — Major Experiments

## 4.1 Template Generation Method Comparison (Stage 2)

- **Hypothesis**: Standard resize + threshold will produce valid small-scale templates
- **Implementation**: 7 methods (A, B, C, D1, D2, D3, E) evaluated across 8 scales
- **Evidence**: Method A: 0 edge pixels at scale 0.15. Method D3: 102 edge pixels, continuity=1.00
- **Result**: Method A definitively rejected. Method D3 selected.
- **Verdict**: ✅ RESOLVED. Method D3 is the only viable template generation strategy.

## 4.2 Connected Component Isolation (Stages 2–2.75)

- **Hypothesis**: MR symbols can be isolated as standalone connected components after wire suppression
- **Implementation**: Wire suppression + morphological closing (3×3, 5×3 kernels) + CC filtering
- **Evidence**: Zero MR candidates recovered even with relaxed thresholds (4× template area)
- **Result**: MR symbols are topologically embedded in bus conductors — CC isolation is impossible
- **Verdict**: ❌ DEFINITIVELY DISPROVEN. Source: PRD Section 4.8, stage2_transition_record.md

## 4.3 Structural Discriminator Discovery (Stage 5.8)

- **Hypothesis**: Topological/structural features can discriminate MR symbols from false positives
- **Implementation**: 25 features computed; ROC-AUC, Cohen's d, overlap measured against 4 groups
- **Evidence**: Stroke_Count: AUC=0.951, d=2.647 vs Dominant FP. All features: AUC=0.000 vs Hard Negatives.
- **Result**: Strong separability exists against dominant FPs (text, conductors) but zero separability against hard negatives (structurally similar symbols)
- **Verdict**: ⚠️ PARTIALLY VALIDATED. Separability confirmed but integration failed.

## 4.4 Stroke_Count Continuous Integration (Stage 5.9)

- **Hypothesis**: Multiplying scores by exp(−0.05 × Stroke_Count) will penalize complex FPs and improve MR ranking
- **Implementation**: 4 integration experiments (EXP_A–D) applying stroke penalty to various score components
- **Evidence**: BASE median rank=573, Top-100=5.8%. Best alternative EXP_C: median=750, Top-100=2.7%. All stroke integrations degraded every metric.
- **Result**: Continuous structural scoring destroys ranking quality
- **Verdict**: ❌ FAILED. Continuous multiplier integration is a dead end.

## 4.5 Ranking Formula Experiments (Stage 5.6)

- **Hypothesis**: Alternative scoring formulas can resolve ranking inversions
- **Implementation**: 14 experiments (A1–A5, B1–B6, C1–C3) varying area functions, scale factors, verification weights
- **Evidence**: B4 (Coverage×Area×Scale) was best but still failed 2 of 8 Stage 6 criteria
- **Result**: No formula achieved sufficient ranking quality
- **Verdict**: ❌ FAILED. Formula-based ranking cannot overcome the fundamental signal deficit.

## 4.6 Verification Cascade (Stage 5.10)

- **Hypothesis**: Discrete pass/fail verification gates outperform continuous scoring
- **Implementation**: Multi-stage cascade with structural gates; 5-part discovery scripts + visual audit
- **Evidence**: Numerical metrics appeared promising. Visual audit revealed contradictions.
- **Result**: Inconclusive — methodology shifted to visual validation
- **Verdict**: ⚠️ INCONCLUSIVE. The discrete gate approach remains the most promising unexplored direction.

---

# SECTION 5 — Architectural Discoveries

## 5.1 Why Stroke_Count Worked in Separability but Failed in Ranking

**Evidence**: AUC=0.951 (separability audit). All integration experiments degraded ranking (best experiment selection).

**Mechanism**: Stroke_Count separates MR (median=4) from Dominant FP (median=19) but the score distributions of MR and Random Background overlap (MR range: 2–22, Random BG range: 2–26). When used as a continuous multiplier, it penalizes some true MR symbols that happen to have high stroke counts while boosting some random background candidates.

**Interpretation**: Separability measures (AUC, Cohen's d) evaluate distribution-level differences. Ranking requires candidate-level correctness. A feature can perfectly separate population distributions while failing to correctly reorder individual candidates.

**Source**: discriminator_leaderboard.md, stage59_best_experiment_selection.md, stage59_stroke_distribution_analysis.md

## 5.2 Why Coverage Failed as a Discriminator

**Evidence**: Coverage separability Cohen's d = −2.80 (True vs Text) — INVERTED direction. True symbols median coverage = 72.9%, FP text = 93.4%, FP conductors = 94.3%.

**Mechanism**: Small FP templates have few edge pixels that all fall on dense text/conductor edges (coverage ~94%). True MR symbols at correct scale have many edge pixels with some misaligned due to rendering differences (coverage ~73%). Coverage is a monotonic function of Chamfer score (r ≈ −0.90).

**Interpretation**: Coverage ratio provides no independent signal beyond what Chamfer score already captures. Higher coverage = lower Chamfer score = more likely to be a false positive.

**Source**: coverage_discriminative_power_assessment.md, coverage_separability_analysis.md, coverage_failure_mechanism_analysis.md

## 5.3 Why Continuous Structural Scoring Collapsed

**Evidence**: Every continuous scoring experiment (5.6 and 5.9) either failed the Stage 6 gate or degraded performance.

**Mechanism**: Structural features have high variance within both MR and FP populations. When multiplied into scores, they amplify noise rather than signal. The features are also partially redundant with Chamfer score (CLASS B: 30–51% shared variance).

**Interpretation**: The pipeline lacks a truly orthogonal signal. All discovered features are entangled with the geometric matching score, creating a ceiling on ranking improvement through continuous score manipulation.

**Source**: discriminator_redundancy_analysis.md, stage56_architectural_verdict.md, stage59_stage6_gate.md

## 5.4 Why Visual Audits Contradicted Quantitative Metrics

**Evidence**: Stage 5.10 appeared numerically successful (reports/stage510_forensics/) but visual audit (reports/stage510_visual_audit/) suggested otherwise.

**Mechanism**: Aggregate metrics (median rank, hit rate) can improve while individual hard cases remain unresolved. A small number of extreme outlier ranks dominate the median while visual inspection reveals that top-ranked candidates are still false positives.

**Interpretation**: Quantitative metrics must always be accompanied by visual validation. No ranking improvement should be trusted without visual confirmation.

---

# SECTION 6 — What Worked

## 6.1 Method D3 Template Generation
- **Evidence**: 102 edge pixels, continuity=1.00 at scale 0.15 vs Method A: 0 pixels
- **Strengths**: Preserves topology at all scales; continuous boundaries for smooth DT alignment
- **Limitations**: None observed — fully validated and certified

## 6.2 Chamfer Matching as Primary Localization
- **Evidence**: True MR symbols are present in candidate pool for all 10 SLDs (stage3_failure_analysis.md)
- **Strengths**: Correct geometric proximity measure for line drawings; O(1) DT lookup; deterministic
- **Limitations**: Raw ranking is inverted due to small-template bias. Requires downstream rescoring.

## 6.3 Coverage×Area Rescoring
- **Evidence**: Median rank improvement of +1000–2000 ranks for most true symbols (stage4_rank_improvement_analysis.md)
- **Strengths**: Successfully counteracts small-template bias; computationally trivial
- **Limitations**: Does not provide independent signal from Chamfer; insufficient alone for Stage 6

## 6.4 Structural Feature Discovery (Stroke_Count, Branch_Point_Count)
- **Evidence**: Stroke_Count AUC=0.951, d=2.647 vs Dominant FP (discriminator_leaderboard.md)
- **Strengths**: Identifies the strongest known discriminative signal between MR and dominant false positives
- **Limitations**: Integration into continuous scoring failed. Potential for discrete gating unexplored at production scale.

## 6.5 Otsu Binarization
- **Evidence**: Dark pixel ratios 1.4%–4.0% across all SLDs (PRD Section 3.3)
- **Strengths**: Bimodal intensity makes Otsu extremely robust; no parameter tuning needed
- **Limitations**: None — images are clean digital renders

---

# SECTION 7 — What Failed

## 7.1 Method A Template Generation
- **Hypothesis**: cv2.resize(INTER_AREA) + threshold(127) produces valid small-scale templates
- **Evidence**: 0 edge pixels at scale 0.15 (stage2_final_resolution.md)
- **Failure Mechanism**: Area interpolation averages 1px edges over larger blocks, diluting intensity below threshold
- **Lesson**: Never apply pixel-domain downsampling to 1px-thick edge maps

## 7.2 Raw Chamfer Ranking
- **Hypothesis**: Lower mean Chamfer distance = more likely to be true symbol
- **Evidence**: 0 true symbols in top 100 of 264,852 candidates (stage3_failure_analysis.md). True symbols median score 6.50px vs FPs 0.72px.
- **Failure Mechanism**: Small templates (few edge pixels) trivially match any dense edge region
- **Lesson**: Mean Chamfer distance is scale-dependent; cross-scale comparison requires normalization

## 7.3 Coverage Ratio as Independent Discriminator
- **Hypothesis**: Coverage ratio provides orthogonal signal to Chamfer score
- **Evidence**: r ≈ −0.90 correlation; FPs have higher coverage than TPs (coverage_discriminative_power_assessment.md)
- **Failure Mechanism**: Coverage is a monotonic function of Chamfer score — mathematically redundant
- **Lesson**: Always verify feature independence before assuming orthogonality

## 7.4 Continuous Stroke_Count Integration
- **Hypothesis**: Stroke penalty exp(−0.05 × Stroke_Count) improves ranking
- **Evidence**: All experiments degraded performance; EXP_A: 0% Top-100 (stage59_best_experiment_selection.md)
- **Failure Mechanism**: Overlapping Stroke_Count distributions between MR (2–22) and Background (2–26) cause collateral damage
- **Lesson**: Strong separability does NOT guarantee ranking improvement when used as a continuous multiplier

## 7.5 Connected Component Isolation
- **Hypothesis**: Wire suppression + morphological operations can isolate MR symbols as connected components
- **Evidence**: Zero candidates recovered even with 4× relaxed thresholds (PRD Section 4.8)
- **Failure Mechanism**: Vertical stem connection to bus conductor is never severed by horizontal wire suppression
- **Lesson**: Topologically embedded symbols cannot be extracted by connected-component methods

## 7.6 PCA Subspace Verification (as designed in PRD)
- **Hypothesis**: PCA manifold from augmented template provides semantic disambiguation
- **Evidence**: PRD design was replaced by structural verification in implementation; PCA was never deployed at scale in the production pipeline
- **Failure Mechanism**: Evidence not available — PCA was designed but superseded
- **Lesson**: The PRD design was never fully validated; structural verification was pursued instead

## 7.7 Verification Score Weighting Experiments (C1–C3)
- **Hypothesis**: Higher verification weight (70–90%) improves ranking
- **Evidence**: Part of stage56_experiment_registry.md; did not outperform Coverage×Area baselines
- **Failure Mechanism**: Verification scores themselves have insufficient discriminative power due to feature redundancy
- **Lesson**: Increasing weight of a weak signal does not create a strong signal

---

# SECTION 8 — Metric Reliability Assessment

## 8.1 ROC-AUC
- **Assessment**: USEFUL for separability analysis; MISLEADING for ranking prediction
- **Evidence**: Stroke_Count AUC=0.951 predicted strong discrimination but integration failed
- **Interpretation**: AUC measures population-level separability, not candidate-level reranking ability
- **Trust Level**: HIGH for separability questions, LOW for ranking improvement prediction

## 8.2 Cohen's d
- **Assessment**: USEFUL as effect size measure; consistent with AUC findings
- **Evidence**: Stroke_Count d=2.647 confirmed massive distribution separation
- **Trust Level**: HIGH for separability, LOW for ranking prediction

## 8.3 Hit Rates (Top-100, Top-500, Top-1000)
- **Assessment**: MOST RELIABLE ranking quality metric
- **Evidence**: Consistently tracked across all experiments; directly measures what matters
- **Trust Level**: HIGH — this is the primary ranking quality indicator

## 8.4 Median Rank
- **Assessment**: USEFUL but can be misleading with bimodal distributions
- **Evidence**: Median rank=573 (BASE) hides that some symbols are at rank <10 and others at rank >10,000
- **Trust Level**: MEDIUM — always examine in conjunction with hit rates and distribution

## 8.5 MR Density Gain
- **Assessment**: Evidence not available for direct evaluation
- **Trust Level**: UNKNOWN

## 8.6 Visual Audit Results
- **Assessment**: MOST TRUSTWORTHY for final validation
- **Evidence**: Stage 5.10 visual audit contradicted numerical metrics
- **Trust Level**: HIGHEST — visual inspection is the ultimate ground truth for this domain

## 8.7 Overlap Percentage
- **Assessment**: USEFUL as a complement to AUC/d; directly shows distribution overlap
- **Evidence**: Stroke_Count overlap=50% vs Dominant FP confirms practical difficulty of thresholding
- **Trust Level**: HIGH for understanding practical discrimination difficulty

## 8.8 Coverage Ratio Metrics
- **Assessment**: MISLEADING — appeared to be useful but is redundant with Chamfer score
- **Evidence**: r ≈ −0.90 correlation with Chamfer (coverage_discriminative_power_assessment.md)
- **Trust Level**: DO NOT TRUST as independent signal

## Recommendation for Future Evaluation

| Metric | Trust | Use For |
|---|---|---|
| Visual Audit | ★★★★★ | Final validation of any claimed improvement |
| Hit Rates | ★★★★☆ | Primary ranking quality measure |
| Median Rank | ★★★☆☆ | Secondary ranking measure (check distribution) |
| ROC-AUC / Cohen's d | ★★★☆☆ | Feature discovery only — NOT ranking prediction |
| Coverage Ratio | ★☆☆☆☆ | Do not use — redundant with Chamfer |

---

# SECTION 9 — Visual Reality vs Numerical Metrics

## 9.1 The Stage 5.10 Paradox

Stage 5.10 (Verification Cascade) explored discrete structural gates as an alternative to continuous scoring. The numerical metrics from the cascade experiments suggested improvement — candidates passing gate criteria appeared to shift the ranking distribution favorably.

However, **visual inspection of the actual top-ranked candidates** after cascade filtering revealed that:

1. Many top-ranked candidates were still text regions and conductor intersections
2. Some true MR symbols that should have passed gates were incorrectly filtered
3. The cascade's numerical improvement came from removing some false positives while also removing some true positives — a net wash that appeared positive in aggregate metrics

**Source**: reports/stage510_forensics/, reports/stage510_visual_audit/

## 9.2 Why Numerical Success ≠ Visual Success

| Aspect | Numerical View | Visual Reality |
|---|---|---|
| Median Rank | May improve by 50–100 positions | Top candidates still visually wrong |
| Hit Rate | Small percentage gains (1–3%) | Gains come from easy symbols already near threshold |
| Inversions | Some resolved by cascade | New inversions created for edge cases |
| FP Removal | Aggregate count decreases | Hardest FPs survive all gates |

**Root Cause**: Aggregate metrics average across all candidates. The "easy" true symbols (large scale, clean isolation) dominate the average improvement while the "hard" cases (small scale, dense context) remain unresolved. Visual inspection preferentially examines the hard cases, revealing the gap.

## 9.3 Lessons for Future Evaluation

1. **NEVER trust a ranking improvement without visual audit** — always inspect the actual top-K candidates
2. **Report per-SLD results**, not just global aggregates — SLD7 (161 symbols) dominates global metrics
3. **Visual audit is mandatory** before any Stage 6 gate clearance
4. **Sample from failure modes**, not successes — inspect the bottom quartile of MR ranks, not the top
5. **Classify FPs in the top-K** — track whether the composition of false positives changes (text→conductor→hard negative)

---

# SECTION 10 — Current Best Known Pipeline

## 10.1 Pipeline Steps

Based on the full body of evidence, the best known pipeline is the **BASE** configuration from Stage 5.9:

| Step | Method | Parameters |
|---|---|---|
| 1. Grayscale | 0.299R + 0.587G + 0.114B | — |
| 2. Binarization | Otsu thresholding | Automatic |
| 3. Edge Detection | Canny | low=50, high=150 |
| 4. Template Bank | Method D3 (Coord Scaling + AA Raster) | subpixel=8, threshold=25, 10 scales [0.15–0.40], 4 rotations |
| 5. Distance Transform | cv2.distanceTransform(DIST_L2) | — |
| 6. Chamfer Matching | cv2.filter2D sliding window | All 40 template variants per SLD |
| 7. Candidate Extraction | Local minima, 15×15 neighborhood | 264,852 raw candidates |
| 8. Rescoring | Coverage × Area | Per-SLD ranking |
| 9. Budget | Top 1000 per SLD | 10,000 total |
| 10. Structural Verification | 25 features, weighted combination | Config: stage5_verification.yaml |
| 11. Combined Ranking | CoverageAreaScore + VerificationScore | BASE experiment |

## 10.2 Strengths
- Deterministic and reproducible
- Successfully localizes large-scale symbols (scale ≥0.30) to top-50 ranks per SLD
- Clean template bank with validated topology preservation
- Comprehensive structural feature profiles for all candidates

## 10.3 Weaknesses
- Median MR rank = 573 (needs to be <10 for practical use)
- Top-100 hit rate = 5.8% (needs to be >80%)
- Complete failure for symbols at scale <0.15
- No effective method to convert structural signals into ranking improvement
- Stage 6 (NMS + output) has never been executed

## 10.4 Observed Behavior
- On simple SLDs (SLD4, SLD12): Some symbols reach top-10 per-SLD
- On complex SLDs (SLD7, SLD2, SLD10): Severe ranking inversions, symbols at rank >5000
- SLD11 (vertical orientation): Mixed results, some 90° symbols localized but many missed

---

# SECTION 11 — Open Problems

## Critical Priority

1. **Ranking Inversion Resolution**: True MR symbols are consistently outranked by false positives. No continuous scoring approach has resolved this. The most promising unexplored direction is **discrete verification gates** (pass/fail thresholds on structural features) rather than continuous score manipulation.

2. **Small-Symbol Localization**: Symbols at scale <0.15 are effectively invisible to the current pipeline. This affects ~40% of the dataset. Root cause: template topology degrades below this scale and false positives dominate at small scales.

## High Priority

3. **Hard Negative Discrimination**: All 25 structural features show AUC=0.000 against hard negatives (structurally similar non-MR symbols). No known feature can discriminate these. May require a fundamentally different approach (e.g., spatial context analysis, part-based matching).

4. **PCA Verification (Untested)**: The PRD's original PCA subspace verification was never implemented at scale. It may provide the orthogonal signal that structural features failed to deliver. This is the highest-value unexplored direction from the original design.

## Medium Priority

5. **Bidirectional Chamfer Matching**: The PRD identified this as a strong enhancement (8/10 suitability). Never implemented. The reverse distance (diagram→template) would penalize "empty" matches where template edges align with simple structures.

6. **Scale-Dependent Thresholding**: Instead of a single ranking, apply scale-specific NMS and thresholds. Large-scale matches are reliable and could be extracted first.

7. **SLD9 Anomaly**: SLD9 has a visually different rendering style. May require dedicated handling or a wider scale search range.

## Low Priority

8. **Multi-Template Ensemble**: PRD proposed 7-variant ensemble with MIN aggregation. Partially explored but not systematically evaluated.

9. **Rotation Robustness**: Current 4-rotation search (0°, 90°, 180°, 270°) may miss slight rotational deviations. SLD11 vertical symbols partially handled.

---

# SECTION 12 — Research Dead Ends

## 12.1 Definitively Disproven

| Approach | Why It Failed | Do Not Repeat |
|---|---|---|
| **Connected Component Isolation** | MR symbols are topologically embedded in bus conductors | Stages 2–2.75, PRD Section 4.8 |
| **Raw Chamfer Ranking** | Small-template bias creates inverted rankings | stage3_failure_analysis.md |
| **Method A Template Generation** | Edge dilution produces empty templates at small scales | stage2_final_resolution.md |
| **Continuous Stroke_Count Scoring** | Strong separability but destroys ranking when used as multiplier | stage59_best_experiment_selection.md |
| **Coverage as Independent Signal** | r ≈ −0.90 with Chamfer — fully redundant | coverage_discriminative_power_assessment.md |
| **SIFT/SURF/ORB Feature Matching** | Near-zero keypoints on line drawings | PRD Section 4.13–4.16 |
| **Supervised Object Detection** | Zero training data available | PRD Section 4.20 |

## 12.2 Why Future Engineers Should Avoid These

1. **Do not attempt CC isolation** — this has been exhaustively tested with multiple morphological strategies and unambiguously fails due to topological embedding.

2. **Do not use coverage ratio as a "new" feature** — it is mathematically identical to Chamfer score in this domain.

3. **Do not integrate structural features as continuous multipliers** — the separability-to-ranking paradox has been conclusively demonstrated. Use discrete gates instead.

4. **Do not apply SIFT/SURF/ORB** — binary line drawings produce near-zero stable keypoints. This is a fundamental domain mismatch, not a parameter tuning issue.

5. **Do not pursue supervised deep learning** — with 0 training annotations and 10 images, no amount of augmentation can substitute for labeled data.

---

# SECTION 13 — Repository & Project Evolution

## 13.1 Original Repository Structure

The repository began as a flat collection of scripts, reports, and data files in the root directory. As the project grew through 10+ stages with hundreds of experiments, the flat structure became unmaintainable.

## 13.2 Why Restructuring Occurred

By Stage 5.10, the repository contained 1,450+ files including:
- 73 summary reports
- 44 archived stage reports
- 9 exploration scripts
- 400+ score map .npy files
- 800+ diagnostic images
- Multiple CSV exports

The flat structure made it impossible to distinguish production code from exploration scripts, or current artifacts from obsolete ones.

## 13.3 Current Repository Architecture

```
Symbol Segmentor/
├── src/                          # Production pipeline code
│   ├── candidate_generation/     # Edge detection
│   ├── template_matching/        # Chamfer matching + score map validation
│   ├── verification/             # Coverage audit, rescoring, structural verification
│   ├── template_bank/            # Bank generation, validation, archival
│   ├── pipeline/                 # Main pipeline orchestration
│   ├── visualization/            # Output visualization
│   ├── common/                   # Shared utilities
│   └── utils/                    # I/O and logging
├── exploration/                  # Research code (isolated from production)
│   ├── archived/                 # Historical stage scripts and reports
│   │   ├── scripts/              # Stage 3–5.9 exploration scripts
│   │   ├── reports/              # 44 stage reports
│   │   ├── scratch/              # Throwaway experiments
│   │   └── misc/                 # PRD, configs, conversion tools
│   ├── symbol_existence_research/
│   ├── template_consistency_research/
│   └── verification_cascade_research/
├── reports/                      # Generated analysis reports
│   ├── summaries/                # 73 topical analysis reports
│   ├── restructure/              # Restructuring audit reports
│   └── [forensics directories]   # Per-stage visual forensics
├── outputs/                      # Generated artifacts
│   ├── tabular/                  # CSV, JSON, TIFF exports
│   ├── visual/                   # Diagnostic images
│   └── template_bank/            # Certified template bank
├── Data/                         # Input data
│   ├── SLDs/                     # Source diagrams
│   ├── Symbol/                   # Query template
│   ├── raw/                      # Raw data
│   ├── processed/                # Preprocessed data
│   └── templates/                # Template variants
├── docs/                         # Documentation (this file)
└── config/                       # Configuration files
```

## 13.4 Lessons Learned from Repository Evolution

1. **Separate exploration from production from the start** — mixing them creates confusion about what is "real"
2. **Use semantic directory names** — "stage5_8_structural_discovery.py" is better than "experiment3.py"
3. **Preserve all artifacts with traceability** — the restructure preserved all 1,450+ files with full provenance mapping
4. **Archive don't delete** — every failed experiment is valuable evidence against repeating mistakes

**Source**: reports/restructure/traceability_preservation_report.md, reports/restructure/repository_audit.md

---

# SECTION 14 — Recommended Future Roadmap

> All recommendations are based ONLY on evidence from the repository. No speculation.

## Rank 1: Implement PCA Subspace Verification (HIGH expected value)

**Evidence basis**: PRD rated it 8/10 suitability. The original design called for augmentation-driven PCA manifold construction with centroid alignment. This was never implemented at scale. It provides a genuinely orthogonal signal (appearance manifold membership vs geometric proximity).

**Why it should work**: PCA reconstruction error measures how well a candidate patch lies on the MR symbol appearance manifold. This is fundamentally different from edge-distance matching and should be independent of Chamfer score.

**Estimated effort**: Medium. Core implementation exists in PRD design (Section 7.6).

## Rank 2: Discrete Structural Gating (HIGH expected value)

**Evidence basis**: Continuous integration of Stroke_Count failed, but the separability signal is real (AUC=0.951). Discrete gates (e.g., reject if Stroke_Count > 15) would eliminate dominant FPs without the collateral damage of continuous multipliers.

**Why it should work**: MR symbols have Stroke_Count median=4, P90=13. Dominant FPs have median=19. A hard gate at 15 would eliminate most dominant FPs while preserving most MR symbols.

**Estimated effort**: Low. Data already exists in topological_features_dataset.csv.

## Rank 3: Bidirectional Chamfer Matching (MEDIUM expected value)

**Evidence basis**: PRD rated it 8/10. The reverse distance (diagram→template) penalizes false matches where simple edges coincidentally align with template edges. Never implemented.

**Estimated effort**: Medium. Requires extracting local diagram patches at each candidate position.

## Rank 4: Scale-Stratified NMS (MEDIUM expected value)

**Evidence basis**: Stage 5.2 confirmed that large-scale symbols (≥0.30) are reliably localized. These could be extracted with high confidence first, then use their positions to constrain small-scale search.

**Estimated effort**: Low-Medium.

## NEVER Explore Again

| Approach | Reason |
|---|---|
| Connected component isolation | Definitively disproven (Stages 2–2.75) |
| Coverage as independent discriminator | Proven redundant (r ≈ −0.90) |
| Continuous structural multipliers | Proven to degrade ranking (Stage 5.9) |
| SIFT/SURF/ORB features | Fundamental domain mismatch |
| Supervised deep learning | Zero training data |

---

# SECTION 15 — Final Project Verdict

## What Has Been Conclusively Solved

1. **Template generation** at extreme scales — Method D3 with coordinate scaling is the definitive solution
2. **Candidate localization** — Chamfer matching successfully places true MR symbols in the candidate pool for all 10 SLDs
3. **Feature separability analysis** — the discriminator leaderboard provides a complete ranking of all 25 structural features
4. **Failure mode classification** — the three FP classes (text regions, conductor intersections, curved conductors) are fully characterized
5. **Preprocessing** — Otsu binarization + Canny edge detection is optimal for this domain

## What Has Been Conclusively Disproven

1. **Connected component isolation** of topologically embedded symbols
2. **Raw Chamfer ranking** across multiple scales without normalization
3. **Coverage ratio** as an independent discriminative signal
4. **Continuous structural feature integration** into scoring formulas
5. **Pixel-domain template downsampling** (Method A) for line drawings

## What Remains Unknown

1. Whether **PCA subspace verification** provides sufficient orthogonal signal for ranking improvement
2. Whether **discrete structural gates** can achieve Stage 6 readiness
3. Whether **bidirectional Chamfer** meaningfully reduces false positive rates
4. Whether **any method** can solve the hard negative discrimination problem (AUC=0.000 across all features)
5. Whether the **scale <0.15 failure** is fundamentally solvable with edge-domain methods
6. What the actual **precision/recall/F1** of the pipeline is — Stage 6 has never been executed

## The Most Important Lesson

**Separability is not ranking.** The most fundamental discovery of this project is that a feature which perfectly separates two population distributions (AUC=0.951) can completely fail to improve rank ordering when integrated as a continuous score component. This disconnect between distributional analysis and instance-level ranking is the central technical lesson that every future engineer must internalize.

The project invested enormous effort discovering discriminative features and validating their separability. Each new feature appeared to solve the ranking problem on paper. Each one failed when actually deployed. The lesson is not that the features are useless — they are valuable for discrete gating. The lesson is that **the mathematical operation of integration matters as much as the quality of the signal.**

---

## Appendix: Source Report Index

| Report | Location | Key Finding |
|---|---|---|
| PRD | exploration/archived/misc/PRD_Symbol_Localization.md | Complete architectural design |
| Stage 1 Observations | exploration/archived/reports/stage1_observations_for_future_stages.md | Stroke width, text clutter, scale ranges |
| Stage 2 Final Resolution | exploration/archived/reports/stage2_final_resolution.md | Method D3 selection |
| Stage 2 Certification | exploration/archived/reports/stage2_certification.md | Template bank authorized |
| Stage 3 Failure Analysis | exploration/archived/reports/stage3_failure_analysis.md | 0% precision at Top-100 |
| Stage 4 Rank Improvement | exploration/archived/reports/stage4_rank_improvement_analysis.md | Coverage×Area rescoring gains |
| Stage 5.2 Root Cause | exploration/archived/reports/stage52_root_cause_verdict.md | Scale-performance cliff at 0.20 |
| Stage 5.5 Reassessment | exploration/archived/reports/stage6_readiness_reassessment.md | Stage 6 blocked |
| Stage 5.6 Verdict | exploration/archived/reports/stage56_architectural_verdict.md | NOT READY FOR STAGE 6 |
| Stage 5.8 Leaderboard | reports/summaries/discriminator_leaderboard.md | Stroke_Count #1 discriminator |
| Stage 5.8 Separability | reports/summaries/feature_separability_audit.md | 25-feature separability analysis |
| Stage 5.8 Redundancy | reports/summaries/discriminator_redundancy_analysis.md | Feature correlation with Chamfer |
| Stage 5.9 Experiments | exploration/archived/reports/stage59_experiment_registry.md | Stroke integration experiments |
| Stage 5.9 Best Selection | exploration/archived/reports/stage59_best_experiment_selection.md | BASE remains best |
| Stage 5.9 Gate | exploration/archived/reports/stage59_stage6_gate.md | NOT READY FOR STAGE 6 |
| Coverage Power | reports/summaries/coverage_discriminative_power_assessment.md | Coverage is redundant |
| Coverage Failure | reports/summaries/coverage_failure_mechanism_analysis.md | FP coverage > TP coverage |
| Coverage Separability | reports/summaries/coverage_separability_analysis.md | Inverted Cohen's d |
| Stroke Distribution | exploration/archived/reports/stage59_stroke_distribution_analysis.md | MR median=4, FP median=19 |
| Restructure Report | reports/restructure/traceability_preservation_report.md | 1,450+ files preserved |

---

*End of Master Research Retrospective*
*Generated by full repository forensic audit — 2026-06-18*
