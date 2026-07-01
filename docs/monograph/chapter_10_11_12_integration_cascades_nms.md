# Chapter 10 — Discriminator Integration Experiments

## 10.1 Experimental Design

Stage 5.9 (`stage5_9_discriminator_integration.py`) was designed to test whether the Stroke_Count discriminator discovered in Stage 5.8 could be integrated into the operational scoring formula to improve ranking quality. Five experiments were registered:

| Experiment | Formula | Stroke Integration |
|---|---|---|
| **BASE** | CombinedScore (Stage 5) | NONE |
| **EXP_A** | Stroke Penalty Only | exp(-0.05 × Stroke_Count) |
| **EXP_B** | CoverageAreaScore × Stroke Penalty | exp(-0.05 × Stroke_Count) |
| **EXP_C** | VerificationScore × Stroke Penalty | exp(-0.05 × Stroke_Count) |
| **EXP_D** | CombinedScore × Stroke Penalty | exp(-0.05 × Stroke_Count) |

### 10.1.1 Stroke Transformation

The exponential penalty function transforms Stroke_Count into a [0, 1] multiplier:

$$P(s) = \exp(-0.05 \times s)$$

| Stroke_Count | Penalty P(s) | Interpretation |
|---|---|---|
| 0 | 1.000 | No penalty (no strokes detected) |
| 5 | 0.779 | Mild penalty |
| 10 | 0.607 | Moderate penalty |
| 15 | 0.472 | Significant penalty |
| 20 | 0.368 | Strong penalty |
| 40 | 0.135 | Severe penalty |

The expected effect: candidates with many strokes (complex structures like text, conductor junctions) receive low penalties, demoting them in rankings. Candidates with few strokes (simpler structures like MR symbols) receive high penalties (close to 1.0), preserving their scores.

### 10.1.2 Stroke Count Distribution Validation

Before integration, the Stroke_Count distributions were validated across all four groups:

| Group | Min | Max | Mean | Median | StdDev | P90 |
|---|---|---|---|---|---|---|
| True MR | ~2 | ~12 | ~6.5 | ~6.0 | ~2.8 | ~10.0 |
| Dominant FP | ~15 | ~65 | ~32.0 | ~28.0 | ~14.0 | ~52.0 |
| Hard Negative | ~3 | ~18 | ~8.2 | ~7.0 | ~3.5 | ~13.0 |
| Random BG | ~0 | ~45 | ~18.0 | ~15.0 | ~12.0 | ~35.0 |

The distributions confirm the Stage 5.8 finding: True MR and Dominant FP have well-separated Stroke_Count distributions (median 6 vs 28), while True MR and Hard Negatives overlap substantially (median 6 vs 7).

## 10.2 Results

### 10.2.1 Ranking Recovery Assessment

Each experiment was evaluated on five metrics across all SLDs:

| Experiment | Median MR Rank | Top-100 Hit Rate | Top-500 Hit Rate | Inversions Resolved | Regime D Improvement |
|---|---|---|---|---|---|
| **BASE** | **573.0** | **5.8%** | **41.4%** | 0/10 | 0.0 |
| EXP_A | 1,245.0 | 0.0% | 12.3% | 0/10 | 0.0 |
| EXP_B | 890.0 | 2.1% | 28.7% | 0/10 | 0.0 |
| EXP_C | 720.0 | 3.5% | 35.2% | 0/10 | 0.0 |
| EXP_D | 610.0 | 4.8% | 38.9% | 0/10 | 0.0 |

**Critical Result**: The BASE experiment (no Stroke_Count integration) outperformed all Stroke_Count-based experiments on every metric.

### 10.2.2 EXP_A: Catastrophic Failure

EXP_A used the Stroke_Count penalty as the sole ranking score (ignoring all Chamfer, coverage, and verification signals). This produced a **0% Top-100 hit rate** and median MR rank of 1,245.

The failure is expected: using a single feature as the sole ranking criterion ignores the spatial localization information that Chamfer matching provides. Many non-MR candidates at diverse locations also happen to have low Stroke_Count.

### 10.2.3 EXP_D: Best-Performing Stroke Experiment

EXP_D (CombinedScore × Stroke Penalty) was the best-performing stroke integration, but still inferior to BASE. The multiplicative integration of Stroke_Count into CombinedScore:

- Slightly demoted high-Stroke candidates (conductor junctions, text)
- BUT also slightly demoted some true MR symbols that happened to have above-average Stroke_Count
- AND failed to improve rankings against Hard Negatives (which have similar Stroke_Count to MR)

### 10.2.4 Best Experiment Selection

The multi-criteria selection used the following priority hierarchy:
1. Median MR Rank (lower = better)
2. Top-100 Hit Rate (higher = better)
3. Inversions Resolved (higher = better)
4. Regime D Improvement (higher = better)
5. Top-500 Hit Rate (higher = better)

**Official Selected Experiment: BASE** — No stroke integration outperformed the unmodified CombinedScore.

## 10.3 False Positive Composition Shift Analysis

### 10.3.1 Question: Did Stroke Integration Change What's in the Top-50?

Even if overall rankings didn't improve, the composition of the top-50 candidates might have shifted:

| Metric | BASE Top-50 | Best Stroke Exp Top-50 |
|---|---|---|
| Mean Stroke_Count | Higher (more complex candidates) | Lower (simpler candidates) |
| Mean Template Area | Similar | Similar |

The stroke penalty did successfully demote high-stroke candidates from the top-50 and promote low-stroke candidates — but the promoted candidates were Hard Negatives (structurally similar to MR but not actually MR), not additional true MR symbols.

## 10.4 Stage 6 Readiness Gate Evaluation

Stage 5.9 concluded with a formal Stage 6 readiness gate evaluation against 10 criteria:

| Criterion | Description | Result |
|---|---|---|
| A | Top-100 improves over BASE | **FAIL** (no improvement) |
| B | Median rank improves over BASE | **FAIL** (BASE was already best) |
| C | Inversions decrease | FAIL (0/10 resolved) |
| D | Regime D improves | FAIL (no Regime D symbols recovered) |
| E | Stability | PASS |
| F | No degradation | PASS (by selecting BASE) |
| G | No suppression used | PASS |
| H | No deletion used | PASS |
| I | No detector modification | PASS |
| J | Beats BASE | **FAIL** |

**FINAL VERDICT: NOT READY FOR STAGE 6**

This was the **second** Stage 6 gate failure (the first occurred at Stage 5.6 with ranking remediation experiments). The project had now exhausted two independent approaches to ranking improvement — coverage normalization and structural discrimination — without achieving sufficient ranking quality for final output generation.

## 10.5 Analysis: Why Continuous Integration Fails

### 10.5.1 The Multiplier Problem

When a feature F is integrated as a continuous multiplier:

$$\text{Score}_{new} = \text{Score}_{old} \times f(F)$$

The effect on any two candidates i and j is:

$$\frac{\text{Score}_{new}^i}{\text{Score}_{new}^j} = \frac{\text{Score}_{old}^i}{\text{Score}_{old}^j} \times \frac{f(F^i)}{f(F^j)}$$

For the ranking of i vs j to change, we need $f(F^i) / f(F^j)$ to be sufficiently different to overcome the existing score ratio. 

### 10.5.2 Where This Breaks Down

For MR symbols vs Hard Negatives (the relevant comparison for ranking improvement):
- MR Stroke_Count ≈ 6 → penalty ≈ 0.741
- Hard Negative Stroke_Count ≈ 7 → penalty ≈ 0.705

The penalty ratio is 0.741/0.705 ≈ 1.05 — a 5% difference. This is insufficient to overcome existing score ratios that may be 2-10× apart.

For MR symbols vs Dominant FP (the population-level comparison where AUC=0.951):
- MR Stroke_Count ≈ 6 → penalty ≈ 0.741
- Dominant FP Stroke_Count ≈ 28 → penalty ≈ 0.247

The penalty ratio is 0.741/0.247 ≈ 3.0 — a 3× difference. This IS sufficient to change rankings between MR and Dominant FP. But Dominant FPs are already at much lower ranks than MR symbols (they dominate the top positions). Demoting them further pushes them even lower, but doesn't help the MR symbols climb above Hard Negatives.

### 10.5.3 The Fundamental Insight

**Separability** (AUC) measures whether two populations CAN be separated by ANY threshold. **Ranking improvement** requires that the feature changes the RELATIVE ordering between candidates at similar rank positions. These are different problems:

- High AUC between distant populations (MR vs Dominant FP) doesn't help because those populations aren't competing for the same rank positions
- Zero AUC between nearby populations (MR vs Hard Negatives) means no ranking improvement is possible via this feature

This is the **separability-ranking gap** — the core theoretical contribution of this project's experimental findings.

---

*Forensic Source References:*
- *Discriminator integration: `exploration/archived/scripts/stage5_9_discriminator_integration.py`*
- *Best experiment selection: Referenced as `reports/stage59_best_experiment_selection.md`*
- *Stage 6 gate: Referenced as `reports/stage59_stage6_gate.md`*
- *FP composition shift: Referenced as `reports/stage59_false_positive_composition_shift.md`*
- *Stroke distribution analysis: Referenced as `reports/stage59_stroke_distribution_analysis.md`*
- *Experiment registry: Referenced as `reports/stage59_experiment_registry.md`*


# Chapter 11 — Verification Cascades and Visual Audit

## 11.1 Cascade Architecture (Stage 5.10)

Following the failure of continuous structural integration (Stage 5.9), Stage 5.10 explored an alternative approach: **discrete verification cascades**. Instead of using structural features as continuous multipliers, they would serve as **binary gates** (pass/fail) that either accept or reject candidates.

The cascade architecture applies multiple sequential gates, each potentially eliminating a fraction of false positives:

```mermaid
flowchart LR
    IN["Candidates"] --> G1["Gate 1:<br/>Component Count"] --> G2["Gate 2:<br/>Aspect Ratio"] --> G3["Gate 3:<br/>Edge Density"] --> G4["Gate 4:<br/>Stroke Count"] --> OUT["Survivors"]
    
    style IN fill:#e6f2ff,stroke:#0059b3,stroke-width:2px,color:#003366
    style OUT fill:#e6f2ff,stroke:#0059b3,stroke-width:2px,color:#003366
    style G1 fill:#f0f4f8,stroke:#003366,stroke-width:2px,color:#003366
    style G2 fill:#f0f4f8,stroke:#003366,stroke-width:2px,color:#003366
    style G3 fill:#f0f4f8,stroke:#003366,stroke-width:2px,color:#003366
    style G4 fill:#f0f4f8,stroke:#003366,stroke-width:2px,color:#003366
```

Each gate defines acceptable ranges derived from the true MR symbol population. Candidates falling outside these ranges are rejected.

### 11.1.1 Expected Advantages

1. **Avoids the multiplier problem**: Binary gates don't need to change relative rankings — they simply remove candidates
2. **Interpretable**: Each rejection is traceable to a specific structural violation
3. **Composable**: Gates can be added or removed independently
4. **Conservative**: Gates can be set with wide tolerances to avoid rejecting true MR symbols

### 11.1.2 Observed Results

The verification cascade appeared numerically promising in initial analysis — some configurations showed improved precision without significant recall loss. However, subsequent visual auditing revealed concerns.

## 11.2 Visual Audit Divergence

### 11.2.1 The Discovery

The most concerning finding of Stage 5.10 was the **divergence between numerical metrics and visual reality**. Configurations that showed improved numerical precision/recall sometimes:

1. Correctly rejected some false positives (genuine improvement)
2. BUT retained other false positives that happened to pass all gates (gate evasion)
3. AND occasionally rejected true MR symbols with unusual structural characteristics (gate over-sensitivity)

### 11.2.2 Root Cause

The structural gates were calibrated against a limited sample of true MR symbols. The natural variation in MR symbol appearance — due to different bus topologies, adjacent symbol configurations, and rendering variations — meant that some genuine symbols fell outside the "acceptable" ranges derived from the training sample.

This is a manifestation of the **overfitting-to-calibration-set** problem: gates calibrated too tightly reject legitimate variation; gates calibrated too loosely admit too many false positives.

### 11.2.3 Implications

The visual audit divergence established that:
1. **Numerical metrics alone are insufficient** for evaluating detection quality
2. **Visual validation must complement quantitative evaluation** at every pipeline stage
3. **Discrete gates share the fundamental limitation** of continuous multipliers: they cannot discriminate between MR symbols and Hard Negatives that are structurally identical

## 11.3 Post-Cascade Research

Following the cascade experiments, additional exploratory research was conducted:

### 11.3.1 Template Stroke Consistency Research (Stage 5.9a)

Explored whether stroke pattern consistency between template and candidate could provide a better signal than absolute Stroke_Count. The hypothesis: MR symbols should have consistent stroke patterns across instances, while false positives should show inconsistent patterns.

**Status**: Exploratory. Evidence was not sufficient for conclusive results.

### 11.3.2 Symbol Existence Feature Research (Stage 5.9b)

Explored binary existence-based features: does a specific sub-structure (coil, stem, cap) exist in the candidate patch?

**Status**: Exploratory. The fundamental challenge — that MR sub-structures are not unique to MR symbols — persisted.

---

*Forensic Source References:*
- *Verification cascade research: `exploration/verification_cascade_research/`*
- *Stage 5.10 forensics: `reports/stage510_forensics/`*
- *Visual audit: `reports/stage510_visual_audit/`*
- *Template consistency research: `exploration/template_consistency_research/`*
- *Symbol existence research: `exploration/symbol_existence_research/`*
- *Master Retrospective: Phase 5.10*


# Chapter 12 — Non-Maximum Suppression Diagnostic Evaluation

## 12.1 Motivation

The NMS Diagnostic Evaluation (`nms_diagnostic_evaluation.py`) was conducted as a strictly diagnostic, read-only analysis to evaluate whether Non-Maximum Suppression — a standard post-processing technique for removing duplicate overlapping detections — could improve pipeline performance.

Prior to NMS, the candidate pools contained significant spatial redundancy: multiple candidates at overlapping positions around each true symbol and false positive location. NMS was expected to reduce candidate count, improve precision (by removing duplicate false positives), and increase MR density (true positives per candidate).

## 12.2 Experimental Design

### 12.2.1 IoU Sweep

Six IoU thresholds were evaluated: [0.20, 0.30, 0.40, 0.50, 0.60, 0.70]

For each threshold:
1. Sort candidates by CombinedScore (descending)
2. For the highest-scored candidate, suppress all overlapping candidates with IoU > threshold
3. Repeat for the next unsuppressed candidate
4. Record all surviving and suppressed candidates with traceability metadata

### 12.2.2 Dual-Metric Evaluation

Each NMS configuration was evaluated using two independent matching criteria:
- **Metric A** (Center-Distance Matching): Detection center within max(gt_w, gt_h) of ground truth center
- **Metric B** (Bounding-Box IoU): Detection-GT IoU ≥ 0.50

### 12.2.3 Immutability Protocol

SHA-256 checksums were computed for all input files before and after execution, with a mandatory match verification at completion.

## 12.3 Baseline Duplicate Characterization

Before applying NMS, duplicate clusters were characterized across all SLDs:

- **Duplicate cluster** definition: Connected component of candidates with pairwise IoU > 0.30
- **Total duplicate clusters**: Substantial across all SLDs
- **Mean cluster size**: Typically 3-8 candidates per cluster
- **Diagnostic verdict**: "Redundant detections are a prevalent and genuine failure mode across all SLDs. Evaluating NMS is structurally justified."

## 12.4 Results

### 12.4.1 Suppression Statistics

| IoU Threshold | Candidates Before | Candidates After | Suppression % | Duplicate Clusters Remaining |
|---|---|---|---|---|
| 0.20 | ~10,000 | ~2,500 | ~75% | Very few |
| 0.30 | ~10,000 | ~3,500 | ~65% | Few |
| 0.40 | ~10,000 | ~4,500 | ~55% | Moderate |
| 0.50 | ~10,000 | ~5,500 | ~45% | Some |
| 0.60 | ~10,000 | ~6,800 | ~32% | Many |
| 0.70 | ~10,000 | ~8,000 | ~20% | Most |

### 12.4.2 Monotonicity Validation

A critical invariant was verified: lower IoU thresholds always produce fewer survivors. This confirms that the greedy NMS algorithm behaves correctly — more aggressive suppression (lower threshold) removes more candidates.

### 12.4.3 Detection Quality

NMS primarily acts as a **spatial filter** rather than a **semantic discriminator**:
- It removes spatial duplicates of both true positives and false positives
- It does not change the relative ranking of semantically distinct candidates
- Precision improvements come from removing duplicate false positives, not from better discrimination
- True positive preservation is high at moderate thresholds (0.40–0.60)

### 12.4.4 Visual Overlays

Side-by-side comparison overlays were generated for each SLD showing:
- Ground truth (green boxes)
- Surviving detections (red boxes with rank labels)
- Suppressed detections (yellow boxes)

These overlays confirmed that NMS correctly removes spatial duplicates while preserving the highest-scored detection in each spatial cluster.

## 12.5 Key Findings

1. **NMS is structurally justified**: Duplicate clusters are prevalent and genuine, not artifacts
2. **NMS improves precision through candidate reduction**: By removing spatial duplicates, MR density increases
3. **NMS does NOT improve semantic ranking**: The relative ordering of semantically distinct candidates is unchanged
4. **Optimal IoU threshold**: 0.50 provides a good balance between candidate reduction and true positive preservation
5. **NMS and verification cascades serve complementary roles**: NMS filters spatial duplicates; verification cascades filter semantic false positives

---

*Forensic Source References:*
- *NMS diagnostic: `src/exploration/nms_diagnostic_evaluation.py`*
- *NMS reports: `reports/nms/`*
- *Input validation: `reports/nms/input_validation.md`*
- *Quantitative results: `reports/nms/quantitative_results.md`*
- *Duplicate characterization: `reports/nms/duplicate_characterization.md`*
