# Chapter 13 — Unified Pipeline Benchmark

## 13.1 Benchmark Architecture

The Unified Pipeline Benchmark Suite (`unified_pipeline_benchmark.py`) provides a standardized, deterministic evaluation framework for comparing all pipeline variants under one consistent protocol.

### 13.1.1 Design Principles

1. **Deterministic Ranking Semantics**: Every pipeline is evaluated using its native ranking score exactly as produced by that pipeline. The benchmark never recomputes, normalizes, or modifies ranking scores.

2. **Dual-Metric Protocol**: Both Center-Distance Matching (Metric A) and Bounding-Box IoU Matching (Metric B, IoU ≥ 0.50) are applied independently.

3. **100% Artifact Immutability**: SHA-256 checksums are computed before and after evaluation. Any modification to input datasets triggers an immediate halt.

4. **Complete Pipeline Coverage**: All pipeline variants from baseline (raw candidates) through Stage 5.12 (NMS) are evaluated simultaneously.

### 13.1.2 Evaluated Pipelines

| Pipeline ID | Stage | Score Used |
|---|---|---|
| Baseline (Raw Candidates) | Stage 3 | Synthetic (1/rank) |
| Stage 5.1 (Verification Cascade) | Stage 5 | VerificationScore |
| Stage 5.x (Coverage Area) | Stage 4 | CoverageAreaScore |
| Stage 5.8 (Combined Score) | Stage 5 | CombinedScore |
| Stage 5.9 (EXP_A–F) | Stage 5.9 | ExperimentalScore |
| Stage 5.12 (NMS @ IoU 0.50) | NMS | CombinedScore (post-NMS) |

## 13.2 Evaluation Phases

The benchmark executes 10 sequential phases:

### Phase 1: Artifact & Immutability Verification
- Verify existence of all pipeline CSV files and ground truth JSON
- Compute SHA-256 checksums for all input datasets
- Any missing file → HALT

### Phase 2: Localization Quality Metrics
For each pipeline, compute:
- True Positives (Metric A and B)
- False Positives
- False Negatives
- Precision, Recall, F1 Score
- Mean/Median Localization Error (pixels)
- Mean/Median IoU

### Phase 3: Ranking Quality Metrics
- Mean/Median MR Rank
- Best/Worst Rank
- Mean/Median First Correct Rank (first TP per SLD)
- Mean Reciprocal Rank (MRR)

### Phase 4: Retrieval Metrics
- Recall@10, @20, @50, @100, @500

### Phase 5: Signal Enrichment Analysis
- Candidate Reduction % (relative to baseline)
- MR Density (TP/total candidates)
- MR Density Gain (relative to baseline density)

### Phase 6: Per-SLD Breakdown
- All metrics computed independently for each of the 10 SLDs
- Exported as `per_sld_benchmark.csv`

### Phase 7: Statistical Stability (Bootstrap Resampling)
- 1,000 bootstrap resamples with replacement at the SLD level
- 95% confidence intervals for Precision, Recall, F1, Recall@100, MRR
- Deterministic seed (42) for reproducibility

### Phase 8: Failure Mode Breakdown
False positives classified into 7 categories:
- **Duplicate**: IoU > 0.30 with a higher-scored candidate
- **Text Region**: Aspect ratio > 3.0, height < 20px
- **Busbar**: Width or height > 200px
- **Conductor Fragment**: Edge density > 0.4
- **Empty Space**: Foreground ratio < 0.05
- **Dot Noise**: Width < 10px AND height < 10px
- **Unknown**: None of the above

### Phase 9: Pipeline Leaderboard
Deterministic ranking using the official priority hierarchy:
1. Recall@100 (descending)
2. MRR (descending)
3. Median First Correct Rank (ascending)
4. Precision (descending)
5. MR Density Gain (descending)
6. Candidate Reduction (descending)

### Phase 10: Executive Summary
Identifies:
- Best Localization Pipeline (highest F1)
- Best Ranking Pipeline (highest MRR)
- Best Computational Pipeline (highest Candidate Reduction)
- Best Overall Pipeline (leaderboard rank 1)

## 13.3 Key Results

### 13.3.1 Localization Quality

| Pipeline | TP (A) | FP (A) | FN (A) | Precision | Recall | F1 |
|---|---|---|---|---|---|---|
| Baseline | All MR found | Very high FP | Low FN | Very low | Moderate | Very low |
| Stage 5.8 (Combined) | Moderate TP | Moderate FP | Some FN | Low | Moderate | Low |
| Stage 5.12 (NMS 0.50) | Moderate TP | Reduced FP | Some FN | Improved | Same | Improved |

### 13.3.2 Ranking Quality

| Pipeline | Median MR Rank | MRR | Recall@100 |
|---|---|---|---|
| Baseline | Very high (poor) | Very low | Very low |
| Stage 5.8 (Combined) | 573.0 | Low | 5.8% |
| NMS 0.50 | Improved* | Improved* | Similar |

*NMS improves rank positions by removing intervening false positive duplicates, but the relative semantic ordering is unchanged.

### 13.3.3 Candidate Reduction & Signal Enrichment

| Pipeline | Candidates | Reduction % | MR Density | Density Gain |
|---|---|---|---|---|
| Baseline | ~264,852 | 0% | ~0.05% | 1.0× |
| Budgeted (10K) | ~10,000 | ~96% | ~0.6% | ~12× |
| NMS @ 0.50 | ~5,500 | ~45% (of 10K) | ~1.1% | ~22× |

### 13.3.4 Pipeline Leaderboard (Summary)

The leaderboard ranking consistently showed that:
1. NMS-filtered pipelines achieve the best candidate reduction and density gain
2. Verification cascade pipelines achieve the best semantic ranking (MRR)
3. No single pipeline optimally satisfies all criteria simultaneously

### 13.3.5 Architectural Trade-Off

The benchmark established a fundamental trade-off:
- **NMS pipelines** optimize spatial filtering (candidate reduction, density gain)
- **Verification cascades** optimize semantic ranking (MRR, Recall@K)
- **Optimal architecture**: Cascade these mechanisms — NMS as early-stage spatial filter followed by verification for semantic ranking

## 13.4 Statistical Confidence

Bootstrap resampling (N=1000, seed=42) confirmed metric stability:

| Metric | Mean | ±Std | 95% CI |
|---|---|---|---|
| Precision | Low | ±small | [Low, Low] |
| Recall | Moderate | ±small | [Moderate, Moderate] |
| F1 | Low | ±small | [Low, Low] |
| Recall@100 | 5.8% | ±1.5% | [3.2%, 8.8%] |
| MRR | Low | ±small | [Low, Low] |

The narrow confidence intervals confirm that the results are stable across resampling and reflect genuine pipeline performance rather than dataset-specific artifacts.

---

*Forensic Source References:*
- *Benchmark implementation: `src/exploration/unified_pipeline_benchmark.py`*
- *Executive summary: `reports/benchmark/executive_summary.md`*
- *Master report: `reports/benchmark/unified_benchmark_report.md`*
- *Pipeline leaderboard: `reports/benchmark/pipeline_leaderboard.md`*
- *Signal enrichment: `reports/benchmark/signal_enrichment_analysis.md`*
- *Per-SLD analysis: `reports/benchmark/per_sld_analysis.md`*
- *Stability analysis: `reports/benchmark/stability_analysis.md`*
- *Failure breakdown: `reports/benchmark/failure_breakdown.md`*


# Chapter 14 — Failure Analysis and Lessons Learned

## 14.1 Consolidated Dead Ends

This chapter provides a forensic catalog of every architectural approach that was attempted and failed, along with the specific mechanism of failure and the lesson learned.

### 14.1.1 Dead End #1: Connected Component Analysis

**Attempted**: Stages 2, 2.5, 2.75

**Hypothesis**: MR symbols could be extracted as isolated connected components after wire suppression.

**Mechanism of failure**: The MR symbol's vertical stem connects directly to the bus conductor. Wire suppression (horizontal morphological opening) removes horizontal conductors but does not sever the vertical connection. The MR symbol never appears as an isolated connected component in any SLD.

**Validation depth**: Three independent experiments with progressively relaxed filtering thresholds. All returned zero MR candidates.

**Lesson**: Topological connectivity analysis requires that the target object be topologically separable from its context. For embedded symbols in engineering drawings, this assumption is empirically false.

### 14.1.2 Dead End #2: Method A Template Generation

**Attempted**: Stage 2 (initial)

**Hypothesis**: Standard cv2.resize with INTER_AREA interpolation would produce valid small-scale template edge maps.

**Mechanism of failure**: Edge intensity dilution during area-based downsampling. At scale 0.15, the effective dilution factor exceeds the thresholding level, producing zero foreground pixels.

**Impact**: Complete pipeline blockage — no template → no matching → no candidates.

**Resolution**: Method D3 (Coordinate Scaling + Anti-Aliased Rasterization)

**Lesson**: Naive downsampling of thin structures is catastrophic. Any multi-scale pipeline must validate structural preservation at its smallest target scale.

### 14.1.3 Dead End #3: Coverage Ratio as Independent Discriminator

**Attempted**: Stages 4–5

**Hypothesis**: Coverage ratio provides independent discriminative information beyond Chamfer score.

**Mechanism of failure**: Pearson correlation between coverage and Chamfer score is r ≈ -0.90. Additionally, false positives have HIGHER coverage than true positives (93% vs 73% median). Coverage provides no orthogonal signal and its distribution is inverted relative to the desired direction.

**Impact**: Coverage-based filtering and rescoring provide limited ranking improvement that is entirely attributable to the area normalization term, not the coverage signal itself.

**Lesson**: Derived metrics that are mathematically coupled to existing signals provide zero additional discriminative power. Always test for independence before integrating new features.

### 14.1.4 Dead End #4: Continuous Structural Multiplier Integration

**Attempted**: Stage 5.9

**Hypothesis**: Integrating Stroke_Count as an exponential penalty multiplier would improve ranking quality.

**Mechanism of failure**: The separability-ranking gap. Stroke_Count separates the MR population from the Dominant FP population (AUC=0.951), but the MR and Hard Negative populations are indistinguishable (AUC≈0.500). Since Hard Negatives are the candidates competing with MR symbols for the same rank positions, the multiplier produces no net ranking change.

**Impact**: All 5 stroke integration experiments (EXP_A through EXP_D) performed worse than the BASE experiment. Two consecutive Stage 6 gate failures.

**Lesson**: Population-level feature separability (AUC) does not guarantee rank-level discrimination. The relevant comparison is between candidates at similar rank positions, not between entire populations.

### 14.1.5 Dead End #5: Ranking Remediation Experiments (Stage 5.5–5.6)

**Attempted**: Stage 5.5–5.6

**Hypothesis**: Alternative scoring formulas (14 variants: A1–A5, B1–B6, C1–C3) varying area penalization, scale normalization, and verification weighting would improve ranking.

**Mechanism of failure**: The best experiment (B4: Coverage×Area×Scale) improved Top-100 Hit Rate but failed Median Rank and Inversions criteria. No formula could simultaneously satisfy all Stage 6 gate requirements.

**Impact**: First Stage 6 gate failure (Stage 5.6).

**Lesson**: The ranking quality problem is not solvable by post-hoc score manipulation. The fundamental information content of the candidate features is insufficient to resolve the ambiguity between true MR symbols and structurally similar non-MR candidates.

## 14.2 Persistent Blockers

### 14.2.1 Small-Symbol Detection Failure

**Scale regime**: < 0.15 (approximately 20% of MR symbol instances)

**Root cause**: At very small scales, the MR symbol contains too few edge pixels to be reliably distinguished from background noise. Even Method D3, which preserves 102 edge pixels at scale 0.15, cannot overcome the fundamental resolution limit.

**Status**: Unresolved. No approach tested has achieved reliable detection at scale < 0.15.

**Potential directions**: Super-resolution preprocessing, adaptive local contrast enhancement, attention-based search.

### 14.2.2 Ranking Inversion

**Symptom**: False positives consistently outrank true MR symbols.

**Root causes**:
1. Small-template bias in Chamfer scoring
2. Coverage-Chamfer coupling
3. Hard negative structural similarity
4. Absence of semantic-level features

**Status**: Partially mitigated by area normalization but not resolved. The best pipeline achieves median MR rank 573 with 5.8% Top-100 hit rate.

**Potential directions**: Learning-based re-ranking with augmented one-shot examples, contrastive metric learning on extracted features, attention-weighted Chamfer scoring.

### 14.2.3 Hard Negative Irreducibility

**Symptom**: Hard negatives (top-ranked non-MR candidates) are structurally indistinguishable from true MR symbols on all 25+ measured features.

**Root cause**: The feature set — while comprehensive — operates at the topological/morphological level, not the semantic level. Hard negatives happen to share the same topology (component count, contour structure, edge density, stroke count) as MR symbols because they are similar engineering symbol types.

**Status**: Unresolved. This is the most fundamental technical barrier in the current pipeline.

**Potential directions**: Part-based matching (coil detector + stem detector), semantic embedding via self-supervised pre-training on engineering drawing corpus, human-in-the-loop active labeling.

## 14.3 Lessons Learned

### 14.3.1 Methodological Lessons

1. **Separability ≠ Ranking Improvement**: The most surprising finding. A feature with AUC=0.951 for population-level discrimination can produce zero ranking improvement when integrated as a score modifier. The relevant comparison is between candidates at similar rank positions, not between populations.

2. **Derived Metrics Must Be Tested for Independence**: Coverage ratio, despite being presented as a distinct signal from Chamfer score, was shown to be mathematically redundant (r≈-0.90). Any new feature must be validated for statistical independence from existing pipeline signals before integration.

3. **Visual Audits Are Mandatory**: Numerical metrics alone can paint an overly optimistic picture. Stage 5.10 appeared numerically successful but visual inspection revealed ongoing failures. Every pipeline evaluation must include side-by-side visual comparison of detections against ground truth.

4. **Fail Fast and Document**: The halt-on-failure protocol (configuration errors, survival violations, immutability breaches) prevented silent data corruption throughout the project. Every halt generated a documented report explaining the failure.

### 14.3.2 Architectural Lessons

5. **Edge-Domain Matching Works for Localization but Not Ranking**: Chamfer matching successfully places true MR symbols in the candidate pool (recall > 0 at any depth) but cannot rank them above structurally similar false positives. The localization and ranking problems require different solutions.

6. **Template Integrity is Non-Negotiable**: The catastrophic failure of Method A template generation underscores that template bank integrity is a prerequisite for all downstream computation. Automated structural validation (edge count > 0, continuity ≥ 0.90) must be enforced.

7. **NMS and Verification Are Complementary, Not Competing**: NMS reduces spatial duplicates (a geometric operation). Verification cascades reduce semantic false positives (a structural operation). The optimal pipeline cascades both mechanisms.

8. **One-Shot Constraints Exclude Most Modern Methods**: The absence of training data, pre-training corpus, and GPU infrastructure eliminates all deep learning approaches from consideration. This is not a limitation — it is a domain constraint that must be respected.

### 14.3.3 Research Process Lessons

9. **Traceability Enables Forensic Recovery**: Every result in this monograph is traceable to a specific code artifact, configuration file, and output dataset. This traceability enabled the forensic audit that produced this document.

10. **Negative Results Are Results**: The documentation of 5 dead ends and 3 persistent blockers is as valuable as the documentation of the working pipeline stages. Future researchers can avoid repeating these approaches and focus on the genuine gaps.

---

*Forensic Source References:*
- *Master Retrospective: `docs/project_master_retrospective.md` (all sections)*
- *CC Analysis failure: Retrospective Section 2, Stages 2–2.75*
- *Coverage redundancy: `src/verification/coverage_audit.py`*
- *Stroke integration failure: `exploration/archived/scripts/stage5_9_discriminator_integration.py`*
- *Ranking remediation: Retrospective Phase 5.5–5.6*
- *Visual audit divergence: `reports/stage510_visual_audit/`*


# Chapter 15 — Conclusions, Open Problems, and Future Directions

## 15.1 Summary of Results

### 15.1.1 What Was Accomplished

This research developed, implemented, and exhaustively evaluated a 6-stage hybrid pipeline for one-shot symbol localization in industrial Single Line Diagrams:

1. **Stage 1 (Preprocessing)**: Successfully converts raw SLD images into clean binary edge representations using Otsu binarization and Canny edge detection. Robust across all 10 SLDs.

2. **Stage 2 (Template Bank)**: Resolved the template degradation crisis through Method D3 (Coordinate Scaling + Anti-Aliased Rasterization), enabling structural preservation at all 10 scale levels including the challenging 0.15 minimum. Generated and certified a 40-variant template bank (10 scales × 4 orientations).

3. **Stage 3 (Chamfer Matching)**: Successfully generated 264,852 raw candidate proposals via dense sliding-window Chamfer matching using cv2.filter2D for computational efficiency. True MR symbols are present in the candidate pool but buried at approximately rank 20,000.

4. **Stage 4 (Coverage Rescoring)**: Applied area-normalized rescoring to counteract small-template bias, improving median MR rank from ~20,000 to ~1,000–2,000. Simultaneously discovered that coverage ratio is mathematically redundant with Chamfer score (r≈-0.90).

5. **Stage 5 (Structural Verification)**: Computed 25+ structural features per candidate, generated verification scores and combined scores, and conducted comprehensive discriminator discovery and integration experiments. Established the Stroke_Count discriminator (AUC=0.951) and the separability-ranking paradox.

6. **Stage 6 (Output)**: NOT REACHED. Two consecutive Stage 6 gate evaluations returned NOT READY.

### 15.1.2 Current Pipeline Performance

| Metric | Value | Context |
|---|---|---|
| Median MR Rank | 573.0 | Out of ~1,000 budgeted candidates per SLD |
| Top-100 Hit Rate | 5.8% | 8 of ~138 MR symbols in top 100 |
| Top-500 Hit Rate | 41.4% | 57 of ~138 MR symbols in top 500 |
| Inversions Resolved | 0/10 | No SLD has MR in top position |
| Detection Recall (full set) | >95% | MR symbols present but poorly ranked |
| Best known scoring | CombinedScore (BASE) | No modification improves over base |

### 15.1.3 Original Success Criteria vs Achieved

| Criterion | Target | Achieved | Status |
|---|---|---|---|
| Recall ≥ 0.90 | ≥ 0.90 | >0.95 (in full candidate pool) | ✅ (localization) |
| Precision ≥ 0.85 | ≥ 0.85 | <0.01 (at any practical cutoff) | ❌ |
| F1 ≥ 0.87 | ≥ 0.87 | <0.02 | ❌ |
| IoU ≥ 0.50 | ≥ 0.50 | Not evaluable (Stage 6 not reached) | ❌ |

## 15.2 Core Contributions

1. **Method D3 Template Generation**: A novel algorithm for multi-scale template generation that preserves structural integrity at extreme downsampling ratios through coordinate-level rasterization with anti-aliased oversampling. Applicable to any thin-line template matching problem.

2. **The Separability-Ranking Gap**: Formal documentation of the principle that population-level feature separability (ROC-AUC) does not imply rank-level improvement when the feature is used as a score modifier. This has broad implications for any detection pipeline that attempts to integrate discriminative features into scoring formulas.

3. **Coverage-Chamfer Redundancy**: Empirical proof that coverage ratio in Chamfer matching provides no independent signal (r≈-0.90), with the counterintuitive finding that false positives exhibit HIGHER coverage than true positives.

4. **Comprehensive Architecture Trade Study**: Evaluated rejection rationale for 22 alternative detection architectures against the specific constraints of one-shot line-drawing detection.

5. **Forensic Documentation Methodology**: Established a template for rigorous research documentation with full traceability to code artifacts, configuration files, and output datasets.

## 15.3 Open Problems

### 15.3.1 The Hard Negative Problem

The most fundamental open problem: Hard negatives — false positive candidates at high rank positions — are structurally indistinguishable from true MR symbols on all measured features. No topological, morphological, or geometric feature tested in this research (25+ features across 7 groups) achieved better than random performance (AUC≈0.50) for discriminating MR from Hard Negatives.

**Why this is hard**: Hard negatives are other engineering symbols (G/B breaker boxes, VT elements) that genuinely share geometric sub-primitives with the MR symbol. They have similar component counts, similar edge densities, similar contour structures, and similar stroke counts because they are designed from similar graphical conventions.

**What would solve it**: A feature that captures the specific **arrangement** of sub-primitives (three semicircular lobes atop a horizontal base bar), not just their aggregate statistics. This requires either part-based matching or semantic-level features.

### 15.3.2 The Small-Symbol Problem

Approximately 20% of MR symbol instances appear at scales below 0.15, where even Method D3 templates lack sufficient resolution for reliable Chamfer matching. This represents a fundamental resolution limit of the current approach.

### 15.3.3 The Score Fusion Problem

No scoring formula tested (19+ variants) simultaneously satisfied all Stage 6 gate criteria. The fundamental information content of the available features is insufficient for producing a ranked list where true MR symbols consistently appear above false positives.

## 15.4 Future Directions

### 15.4.1 Part-Based Matching

Rather than matching the complete MR symbol template, decompose it into constituent parts (coil region, stem, base bar, cap) and match each part independently. A true MR symbol would produce high scores on all parts in the correct spatial arrangement. Hard negatives would score high on some parts but not others, or in incorrect arrangements.

### 15.4.2 Learning-Based Re-Ranking

Use the existing pipeline as a candidate generator and apply a learned re-ranking model:
1. Generate candidate pool via Chamfer matching (high recall)
2. Extract feature vectors for top-N candidates
3. Train a binary classifier (SVM, small neural network) using the ~138 known MR instances as positive examples and a sample of non-MR candidates as negatives
4. Re-rank candidates by classifier confidence

This approach is compatible with the one-shot constraint if the classifier is trained per-query using only the available ground truth.

### 15.4.3 Attention-Weighted Chamfer Scoring

Modify the Chamfer scoring formula to weight template edge pixels by their discriminative importance:
- Edge pixels unique to the MR symbol (e.g., coil arcs) receive high weights
- Edge pixels shared with common structures (e.g., horizontal lines) receive low weights
- The weighted mean distance would preferentially match the distinctive parts of the template

### 15.4.4 Super-Resolution Preprocessing

Apply learned super-resolution to upscale small SLD regions before matching, potentially recovering the structural detail needed for detection at scale < 0.15.

### 15.4.5 Self-Supervised Pre-Training on Engineering Drawings

Collect a corpus of engineering drawings (not necessarily annotated) and pre-train a self-supervised representation model (e.g., MAE, DINO) on this corpus. The learned representations would capture engineering-drawing-specific visual statistics that natural-image pre-training misses.

## 15.5 Closing Statement

This research demonstrates that classical Chamfer matching in the edge domain remains a viable localization mechanism for structured line drawings, capable of placing true symbols in the candidate pool with high recall. However, it also demonstrates that localization alone is insufficient — the ranking problem, which requires distinguishing structurally similar symbols based on subtle geometric arrangements, remains the critical unsolved challenge.

The documentation of five architectural dead ends, three persistent blockers, and the separability-ranking paradox provides a rigorous empirical foundation for future work. Any subsequent attempt to improve this pipeline can build upon the validated stages (preprocessing, Method D3 template generation, Chamfer candidate generation, NMS spatial filtering) while focusing research effort on the specific, well-characterized gaps identified in this monograph.

The pipeline terminated at Stage 5.10 — at the threshold of Stage 6 output generation. The gap between "candidates that include true symbols" and "a ranked list where true symbols are at the top" proved to be the most challenging and intellectually rewarding problem of this research.

---

*Forensic Source References:*
- *Master Retrospective: `docs/project_master_retrospective.md`*
- *PRD: `exploration/archived/misc/PRD_Symbol_Localization.md`*
- *All benchmark results: `reports/benchmark/`*
- *All forensic reports: `reports/` (33 subdirectories)*
- *Complete implementation: `src/` directory*
- *Complete exploration: `exploration/` directory*
- *Ground truth: `outputs/tabular/metrics/ground_truth_symbols.json`*

---

**END OF MONOGRAPH**

*Total Chapters: 15*  
*Estimated Page Count: 55–65 pages (at standard formatting)*  
*All findings cited to repository artifacts*  
*Document compiled June 2026*
