# MR Symbol Localization in Single Line Diagrams â€” Technical PRD

## Part 1: Executive Summary, Problem Definition, and Dataset Analysis

---

# SECTION 1 â€” EXECUTIVE SUMMARY

## 1.1 Problem Statement

This project addresses the localization of a specific Current Transformer (CT/MR) symbol across ten industrial Single Line Diagrams (SLDs) from the power systems engineering domain. Given exactly **one query symbol image** (`MR_Symbol.png`) and **ten target SLD images**, the system must automatically locate and return bounding boxes around every occurrence of the query symbol in every diagram.

## 1.2 Core Constraints

| Constraint | Value |
|---|---|
| Query templates available | 1 |
| Target diagrams | 10 |
| Labeled training data | None |
| Annotated bounding boxes | None |
| Training epochs possible | N/A â€” no training set |

## 1.3 Why Conventional Object Detection Is Not Ideal

Modern supervised object detectors (YOLO, Faster R-CNN, DETR, Mask R-CNN, Vision Transformers) require thousands of annotated examples to learn class-discriminative features. This project has:

- **Zero annotations.** No bounding box labels exist for any SLD.
- **One template.** A single reference image defines the target class.
- **Ten images total.** The entire corpus is ten diagrams â€” not ten thousand.
- **No negative mining.** Without labeled negatives, contrastive learning is infeasible.
- **Determinism required.** The system must produce identical results across runs â€” stochastic training is architecturally inappropriate.

Even few-shot detectors (e.g., Siamese networks, prototypical networks) require meta-learning episodes across many support/query pairs from multiple classes. With one class, one template, and zero annotations, these approaches collapse into template matching with unnecessary neural overhead.

## 1.4 Why This Project Is Fundamentally Different

This is **not** a conventional computer vision project. It is:

1. **A symbol spotting problem** â€” locating a known geometric pattern within structured technical drawings.
2. **A one-shot localization problem** â€” the entire "training set" is a single reference image.
3. **A document image analysis problem** â€” the inputs are engineering drawings with known conventions, not natural images.
4. **A geometric matching problem** â€” the symbol is defined by its shape, not its texture, color, or semantic context.

The dominant challenge is **not** image quality (the SLDs are clean, high-contrast, binary line drawings). The dominant challenge is **discriminating the target symbol from visually similar neighboring symbols** that share geometric sub-primitives (semicircular lobes, vertical stems, horizontal conductors).

---

# SECTION 2 â€” PROBLEM DEFINITION

## 2.1 Input Specification

| Input | Description | Format |
|---|---|---|
| Query Symbol | `MR_Symbol.png` â€” 161Ã—103 pixels, RGBA, grayscale content on fully opaque white background | PNG |
| Target SLDs | `SLD1.png` through `SLD12.png` (10 files; SLD5, SLD6 absent) | PNG |

## 2.2 Output Specification

For each SLD, produce a list of bounding boxes `(x, y, w, h)` where:
- `(x, y)` = top-left corner of the detected symbol occurrence
- `(w, h)` = width and height of the bounding box
- Each bounding box encloses one instance of the MR symbol

Additionally, produce annotated visualization images showing all detected bounding boxes overlaid on the original SLD.

## 2.3 Success Criteria

| Metric | Target | Justification |
|---|---|---|
| Recall | â‰¥ 0.90 | Missing a real symbol is operationally dangerous |
| Precision | â‰¥ 0.85 | False positives waste engineering review time |
| F1-Score | â‰¥ 0.87 | Balanced performance requirement |
| IoU (per detection) | â‰¥ 0.50 | Standard PASCAL VOC localization threshold |
| Determinism | 100% | Identical inputs must produce identical outputs |
| Explainability | Full pipeline transparency | Every detection must be traceable to a geometric score |

## 2.4 Failure Criteria

- Recall < 0.70 on any individual SLD
- Precision < 0.50 (excessive false positives)
- System requires manual parameter tuning per SLD
- System requires GPU or deep learning inference
- Non-deterministic behavior across runs

## 2.5 Assumptions

1. All SLDs originate from the same engineering domain (power systems substation design).
2. The MR symbol represents a Current Transformer (CT) with a consistent geometric structure across all diagrams.
3. Symbol geometry is the primary discriminator â€” text labels are NOT part of the symbol definition.
4. SLDs are digitally generated (not scanned), resulting in clean line work.
5. The symbol appears connected to horizontal conductors (bus bars) in all diagrams.

## 2.6 Non-Assumptions (Requires Empirical Verification)

- **Exact symbol count per SLD:** Not assumed â€” must be determined empirically.
- **Rotation range:** Observed to be primarily 0Â° (horizontal orientation) but vertical orientation (90Â°) is present in SLD11. Full rotation range requires verification.
- **Scale range:** Symbol size relative to diagram varies. Exact scale factor distribution requires measurement.
- **Symbol isolation:** Symbols are NOT isolated connected components â€” they are topologically embedded in the bus structure (empirically verified in prior work).

## 2.7 Edge Cases

| Edge Case | Description | Expected Handling |
|---|---|---|
| Overlapping text | Text labels ("MR", "2000/5", "Z2") directly adjacent to or overlapping the symbol | Text must not influence detection; purely geometric matching |
| Dense symbol chains | Multiple MR symbols in sequence with <1 symbol-width spacing | NMS must distinguish individual instances |
| Visually similar symbols | Symbols sharing the dual-semicircle lobe structure but with different stems/caps | PCA or structural verification must discriminate |
| Partial visibility | Symbols at diagram edges potentially cropped | Graceful degradation; report only fully visible instances |
| Scale variation | Different SLDs may render the symbol at different pixel sizes | Multi-scale matching required |
| Orientation variation | Most symbols are horizontal; SLD11 shows vertical arrangement | Multi-orientation matching required |

---

# SECTION 3 â€” DATASET ANALYSIS

## 3.1 Forensic Analysis: Target Symbol (MR_Symbol.png)

### 3.1.1 Technical Properties

| Property | Value |
|---|---|
| Dimensions | 161 Ã— 103 pixels (W Ã— H) |
| Aspect Ratio | 1.563 (wider than tall) |
| Color Mode | RGBA (all pixels fully opaque, Î±=255) |
| Effective Color | Grayscale â€” mean RGB = (231, 231, 231) |
| Unique Colors | 200 (anti-aliased grayscale rendering) |
| File Size | 2,406 bytes |

### 3.1.2 Geometric Structure (Observed from Image)

The MR symbol consists of the following geometric primitives, from top to bottom:

```
â”Œâ”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”
â”‚  Horizontal conductor (top bar)       â”‚  â† Connects to bus; NOT part of symbol
â”‚         â”‚              â”¼              â”‚  â† Vertical stem + Cross/cap structure
â”‚         â”‚                             â”‚
â”‚  â”Œâ”€â”€â”€â”€â”€â”€â”´â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”              â”‚  â† Thick horizontal base bar
â”‚  â”‚    âŒ’âŒ’       âŒ’âŒ’     â”‚              â”‚  â† Two adjacent downward semicircular lobes
â”‚  â””â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”˜              â”‚
â””â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”˜
```

**Observed primitives:**

1. **Horizontal conductor** (top): A horizontal line extending across the full width. This is the bus/conductor and is contextual â€” NOT part of the symbol's intrinsic geometry.
2. **Vertical stem**: A short vertical line descending from the conductor to the symbol body.
3. **Cross/cap structure**: A small cross or T-cap near the top of the stem (right side). This is a distinguishing feature.
4. **Horizontal base bar**: A thick horizontal line forming the base of the symbol body.
5. **Two semicircular lobes**: Two adjacent, downward-facing semicircles hanging from the base bar. These are the most visually distinctive feature.

### 3.1.3 Shape Characteristics

| Characteristic | Assessment |
|---|---|
| Contour complexity | Low-to-medium â€” composed of straight lines and semicircular arcs |
| Symmetry | Approximate bilateral symmetry along vertical axis |
| Rotational symmetry | None â€” the symbol has a clear "up" direction (stem up, lobes down) |
| Connected component structure | Single connected component when attached to conductor; the cross-cap may form a separate small component when isolated |
| Shape uniqueness | Medium â€” the dual-semicircle motif is distinctive, but individual semicircles appear in other symbols |
| Distinguishing features | (1) The dual-lobe structure, (2) the cross/cap, (3) the specific aspect ratio of lobes to stem |
| Potential confusion sources | Other symbols with semicircular elements, zigzag resistor symbols that share some edge structure, transformer symbols with curved elements |

### 3.1.4 Candidate Descriptors

Based on the observed geometry, the following descriptors are well-suited:

| Descriptor | Suitability | Reason |
|---|---|---|
| Edge map (Canny) | High | Clean line drawing produces strong, unambiguous edges |
| Distance Transform | High | Enables efficient Chamfer matching against diagram edges |
| Shape Context | Medium | Captures spatial distribution of edge points, but sensitive to scale |
| Contour chain codes | Medium | The semicircular lobes produce distinctive contour sequences |
| HOG | Medium | Captures gradient orientation distribution of the lobe structure |
| Hu Moments | Low | Too global â€” cannot discriminate between symbols with similar mass distribution |
| SIFT/ORB keypoints | Low | Very few keypoints on simple line drawings |

## 3.2 Forensic Analysis: Individual SLD Characteristics

### 3.2.1 Image Metadata Summary

| SLD | Dimensions (WÃ—H) | Aspect Ratio | File Size | Dark Pixel Ratio | Total Pixels |
|---|---|---|---|---|---|
| SLD1 | 1544 Ã— 382 | 4.04 | 59,966 B | 0.0292 | 589,808 |
| SLD2 | 1024 Ã— 678 | 1.51 | 92,423 B | 0.0287 | 694,272 |
| SLD3 | 1789 Ã— 368 | 4.86 | 81,585 B | 0.0354 | 658,352 |
| SLD4 | 806 Ã— 255 | 3.16 | 35,186 B | 0.0402 | 205,530 |
| SLD7 | 1778 Ã— 819 | 2.17 | 169,448 B | 0.0294 | 1,456,182 |
| SLD8 | 901 Ã— 537 | 1.68 | 58,386 B | 0.0258 | 483,837 |
| SLD9 | 1700 Ã— 549 | 3.10 | 43,051 B | 0.0135 | 933,300 |
| SLD10 | 1581 Ã— 915 | 1.73 | 136,435 B | 0.0235 | 1,446,615 |
| SLD11 | 769 Ã— 698 | 1.10 | 56,541 B | 0.0287 | 536,762 |
| SLD12 | 871 Ã— 112 | 7.78 | 11,503 B | 0.0373 | 97,552 |

**Key observations:**
- All images are RGBA mode with grayscale content on white backgrounds.
- Dark pixel ratios are uniformly low (1.35%â€“4.02%), confirming sparse engineering drawings.
- Resolution varies significantly: from 97K pixels (SLD12) to 1.45M pixels (SLD7).
- Aspect ratios range from 1.10 (nearly square, SLD11) to 7.78 (extremely wide, SLD12).

### 3.2.2 Per-SLD Detailed Observations

#### SLD1 â€” 1544 Ã— 382

**Observed from image inspection:**
- **Layout**: Single horizontal conductor line running left-to-right
- **Complexity**: Low â€” sparse layout with large whitespace
- **Symbol density**: Low â€” symbols are well-separated along the conductor
- **MR symbol occurrences**: Approximately 5 visible MR-labeled CT symbols along the main bus, plus 1 on a vertical branch below
- **Text labels**: "MR Y1 1200/5", "MR X1 1200/5", "MR X2 3000/5", "MR Y2 3000/5", "3000/5 X0 MR" â€” confirms multiple CT instances
- **Visually similar symbols**: Zigzag patterns (resistors/impedances), triangle symbols, surge arresters (SA)
- **Noise**: None â€” clean digital rendering
- **Scan artifacts**: None
- **Skew/rotation**: No skew. All MR symbols appear in standard horizontal orientation
- **Potential FP sources**: The zigzag transformer symbols share some edge structure with the MR lobes
- **Potential FN sources**: The vertically-oriented CT on the branch below may have different scale

**Estimated MR count**: ~6 (requires empirical verification)

#### SLD2 â€” 1024 Ã— 678

**Observed from image inspection:**
- **Layout**: Two horizontal bus bays (BAY#1 and BAY#2) with vertical interconnections
- **Complexity**: Medium-high â€” dense symbol population
- **Symbol density**: High â€” symbols tightly packed along both bus bays
- **MR symbol occurrences**: Numerous â€” each bay contains approximately 12 MR-labeled CTs. Labels visible: "MR 2000/5 Z2", "MR 2000/5 Y2", "MR 2000/5 X2", "MR 2000/5 X1", "MR 2000/5 Y1", "MR 2000/5 Z1" per section (712, 711, 722, 721 sections)
- **Text labels**: Dense text with colored labels (blue "MR" labels visible)
- **Text density**: High â€” labels for every symbol
- **Visually similar symbols**: Circuit breaker (G/B) boxes, motor (M) circles, disconnect switches, line traps
- **Noise**: None
- **Skew**: None. Includes rotated text labels (vertical text for cable specs)
- **Engineering topology**: Two parallel bus bays connected through breakers and VT sections
- **Potential FP sources**: G/B breaker rectangles, motor circles, disconnect switch elements
- **Potential FN sources**: Very dense packing may cause overlapping score basins in sliding window approaches

**Estimated MR count**: ~24 (requires empirical verification)

#### SLD3 â€” 1789 Ã— 368

**Observed from image inspection:**
- **Layout**: Single wide horizontal bus with sections 712, 711
- **Complexity**: Medium â€” this appears to be a zoomed/cropped view of one bay from SLD2
- **Symbol density**: Medium â€” symbols evenly distributed along the bus
- **MR symbol occurrences**: Approximately 12 MR-labeled CTs visible along the main conductor
- **Text**: "MR 2000/5" labels with position identifiers (Z2, Y2, X2, X1, Y1, Z1) for sections 712 and 711
- **Visually similar symbols**: G/B boxes, motor circles, VT section in center
- **Noise**: None
- **Vertical structures**: VT section (7T01VT) descends from center with branching topology
- **Potential FP sources**: The central VT section contains transformer symbols that may share edge structure with MR lobes
- **Potential FN sources**: Tightly packed CTs may merge in sliding window score maps

**Estimated MR count**: ~12 (requires empirical verification)

#### SLD4 â€” 806 Ã— 255

**Observed from image inspection:**
- **Layout**: Single horizontal conductor with section 722
- **Complexity**: Low â€” clean, isolated bus section
- **Symbol density**: Medium â€” symbols clearly separated
- **MR symbol occurrences**: ~6 visible MR-labeled CTs: "MR 2000/5 Z2", "Y2", "X2", "X1", "Y1", "Z1"
- **Text**: Clear labels, well-separated from symbols
- **Visually similar symbols**: G/B box, motor circles (M) at bus ends
- **Noise**: None
- **Important**: Clean validation target â€” all MR symbols clearly visible and well-separated
- **Potential FP sources**: Minimal â€” clean isolation
- **Potential FN sources**: Minimal â€” clear separation

**Estimated MR count**: ~6 (requires empirical verification)

#### SLD7 â€” 1778 Ã— 819

**Observed from image inspection:**
- **Layout**: Largest and most complex SLD â€” multi-section structure with 4+ bus sections (713, 712, 711, 723, 722, 721)
- **Complexity**: High â€” multiple bus bays, vertical interconnections, VT sections
- **Symbol density**: Very high â€” densely packed symbols across all sections
- **MR symbol occurrences**: Numerous â€” each section contains ~6 MR CTs, across 6 sections = ~36 total
- **Text**: Dense text labels throughout
- **Engineering topology**: Two major horizontal bus bars (7B02 and 7B01) connected via VT sections and breakers
- **Visually similar symbols**: G/B boxes, motor circles, disconnect switches, surge arresters, VT transformer symbols
- **Noise**: None
- **Potential FP sources**: High â€” complex topology creates many edge-dense regions
- **Potential FN sources**: Scale variation between sections possible

**Estimated MR count**: ~36 (requires empirical verification)

#### SLD8 â€” 901 Ã— 537

**Observed from image inspection:**
- **Layout**: Single bus section (713) with vertical VT branch
- **Complexity**: Medium â€” one bus section plus VT/SA branch
- **Symbol density**: Medium â€” symbols along one main conductor
- **MR symbol occurrences**: ~6 MR-labeled CTs on the main bus: "MR 2000/5 Z2", "Y2", "X2", "X1", "Y1", "Z1"
- **Text**: Clear labels
- **Visually similar symbols**: G/B box, motor circles, VT section with transformer, SA surge arrester
- **Noise**: None
- **VT branch**: Contains transformer symbols (zigzag), switch symbols â€” potential FP source
- **Potential FP sources**: Transformer/VT zigzag patterns
- **Potential FN sources**: Minimal â€” clean separation

**Estimated MR count**: ~6 (requires empirical verification)

#### SLD9 â€” 1700 Ã— 549

**Observed from image inspection:**
- **Layout**: Wide diagram with multiple vertical structures â€” breaker arrangements
- **Complexity**: Medium-high â€” different topology from other SLDs
- **Symbol density**: Medium â€” symbols distributed along a wider horizontal span
- **MR symbol occurrences**: Multiple CT-like symbols visible but with different geometric presentation â€” symbols appear smaller and the dual-lobe structure appears more as a downward "Ï‰" shape
- **Text**: Minimal visible MR labels; section numbers 732, 731
- **Visually similar symbols**: Switch/breaker assemblies, motor circles, ground symbols, VT elements
- **Noise**: None
- **Important**: This SLD has a visually different rendering style â€” the CT symbols appear to have a different scale and aspect ratio relative to the bus structure
- **Potential FP sources**: Switch assemblies with curved elements
- **Potential FN sources**: Different scale may cause template mismatch

**Estimated MR count**: ~12â€“18 (requires empirical verification â€” significant uncertainty due to different rendering style)

#### SLD10 â€” 1581 Ã— 915

**Observed from image inspection:**
- **Layout**: Two-bay structure similar to SLD2 â€” BAY#1 and BAY#2 with central VT section
- **Complexity**: Medium-high â€” structurally similar to SLD2
- **Symbol density**: High â€” dense symbol population on both bays
- **MR symbol occurrences**: Very similar to SLD2 â€” each bay contains ~12 MR CTs
- **Text**: Dense labels, blue-colored MR text
- **Visually similar symbols**: G/B boxes, motor circles, disconnect switches
- **Noise**: None
- **Note**: This appears to be a slightly different rendering of the same substation topology as SLD2

**Estimated MR count**: ~24 (requires empirical verification)

#### SLD11 â€” 769 Ã— 698

**Observed from image inspection:**
- **Layout**: VERTICAL arrangement â€” two parallel vertical buses (601, 602) with branching structure
- **Complexity**: Medium â€” fewer symbols but different orientation paradigm
- **Symbol density**: Medium â€” symbols distributed vertically
- **MR symbol occurrences**: ~4 visible MR-labeled CTs: "MR CT1 3000/5" and "MR CT2 3000/5" for both sections 601 and 602
- **Text**: Clear labels with "MR CT1" and "MR CT2" designations
- **CRITICAL**: The symbols in this SLD are oriented **vertically** â€” the horizontal base bar of the MR symbol is now vertical, and the lobes extend horizontally. This is a ~90Â° rotation from the standard orientation.
- **Visually similar symbols**: V/B boxes, motor circles (M), NC/NO switches, VT elements (601VT, 602VT)
- **Noise**: None
- **Potential FP sources**: V/B boxes share rectangular geometry
- **Potential FN sources**: 90Â° rotation means the template must be rotated to match

**Estimated MR count**: ~4 (requires empirical verification)

#### SLD12 â€” 871 Ã— 112

**Observed from image inspection:**
- **Layout**: Single narrow horizontal strip â€” one bus conductor
- **Complexity**: Very low â€” simplest SLD in the dataset
- **Symbol density**: Low-to-medium â€” symbols along a single line
- **MR symbol occurrences**: Multiple CT-like symbols visible â€” the dual-semicircle lobe pattern is clearly identifiable
- **Text**: Minimal â€” section label "733"
- **Visually similar symbols**: G/B box, motor circles, ground/switch elements
- **Noise**: None
- **Important**: Small image (871Ã—112 = 97K pixels) â€” symbols are proportionally small
- **Potential FP sources**: Minimal
- **Potential FN sources**: Small image size may cause scale issues

**Estimated MR count**: ~6 (requires empirical verification)

## 3.3 Dataset-Wide Analysis

### 3.3.1 Dataset Statistics

| Statistic | Value |
|---|---|
| Total SLDs | 10 |
| Total pixel area | ~7.1 million pixels |
| Mean dark pixel ratio | 0.0282 |
| Resolution range | 97Kâ€“1.46M pixels |
| Aspect ratio range | 1.10â€“7.78 |
| Image mode | All RGBA |
| Estimated total MR occurrences | ~138 (significant uncertainty; requires ground truth) |

### 3.3.2 Rotation Distribution

| Orientation | SLDs | Percentage |
|---|---|---|
| 0Â° (standard horizontal) | SLD1, SLD2, SLD3, SLD4, SLD7, SLD8, SLD9, SLD10, SLD12 | 90% |
| ~90Â° (vertical) | SLD11 | 10% |
| Other angles | None observed | 0% |

**Conclusion**: The rotation distribution is bimodal â€” overwhelmingly 0Â° with one SLD showing 90Â° rotation. The system must handle at minimum 0Â° and 90Â° orientations. Continuous rotation is NOT observed and should not be the primary design target.

### 3.3.3 Scale Distribution

The MR symbol template is 161Ã—103 pixels. The actual symbol size in diagrams varies:

- In dense SLDs (SLD2, SLD3, SLD7, SLD10): symbols appear approximately **25â€“40 pixels wide** â€” roughly 4â€“6Ã— smaller than the template.
- In sparse SLDs (SLD1, SLD4): symbols appear approximately **30â€“50 pixels wide** â€” roughly 3â€“5Ã— smaller than the template.
- In SLD9: symbols appear at a potentially different scale due to the different rendering style.
- In SLD12: symbols appear approximately **15â€“25 pixels wide** due to the very compact image.

**Conclusion**: Scale variation is moderate (estimated 0.15â€“0.35Ã— of template). Multi-scale matching is required with approximately 3â€“5 scale levels. Requires empirical calibration.

### 3.3.4 Symbol Occurrence Distribution

| Estimated Count | SLDs |
|---|---|
| ~4â€“6 | SLD4, SLD8, SLD11, SLD12 |
| ~6 | SLD1 |
| ~12 | SLD3, SLD9 |
| ~24 | SLD2, SLD10 |
| ~36 | SLD7 |

**Note**: All occurrence counts are estimates from visual inspection. Ground truth annotation is required for precise evaluation.

### 3.3.5 Dataset Strengths

1. **Extremely clean images** â€” no noise, no scan artifacts, no compression artifacts. Dark pixel ratio < 5% across all SLDs.
2. **High inter-document consistency** â€” same engineering domain, same symbol family, same drawing conventions.
3. **Binary-like contrast** â€” near-perfect foreground/background separation simplifies binarization.
4. **Structured layouts** â€” symbols follow engineering grid patterns, reducing random spatial variation.
5. **Consistent symbol identity** â€” the MR symbol has a unique dual-semicircle lobe structure that is geometrically distinctive.

### 3.3.6 Dataset Weaknesses

1. **No ground truth** â€” zero labeled bounding boxes exist. Evaluation requires manual annotation.
2. **Scale variation** â€” the template is significantly larger than the actual symbols in diagrams.
3. **Topological embedding** â€” MR symbols are connected to bus conductors, preventing connected-component isolation (empirically proven in prior work).
4. **Dense packing** â€” in SLD2, SLD7, SLD10, symbols are very close together, creating overlapping score basins.
5. **Orientation variation** â€” SLD11 introduces 90Â° rotated symbols.
6. **Rendering inconsistency** â€” SLD9 appears to have a different rendering style/scale.

### 3.3.7 Dataset Risks

1. **False positive hotspots**: G/B breaker boxes, VT transformer zigzags, and surge arrester symbols share geometric sub-primitives with the MR symbol.
2. **Score basin merging**: In dense SLDs, adjacent MR symbols may produce merged score basins, causing under-counting.
3. **Scale miscalibration**: The 4â€“6Ã— scale difference between template and diagram symbols means scale estimation errors directly impact recall.
4. **SLD9 anomaly**: The visually different rendering style of SLD9 may require special handling or a wider scale search range.

### 3.3.8 Expected Matching Challenges

| Challenge | Severity | Affected SLDs |
|---|---|---|
| Discriminating MR from G/B boxes | High | SLD2, SLD3, SLD4, SLD7, SLD8, SLD10 |
| Discriminating MR from VT zigzags | Medium | SLD1, SLD3, SLD7, SLD8 |
| Dense NMS in packed bus sections | High | SLD2, SLD7, SLD10 |
| 90Â° rotation handling | Medium | SLD11 |
| Scale estimation for small symbols | Medium | SLD12 |
| Different rendering style | Medium-High | SLD9 |

### 3.3.9 Expected Failure Modes

1. **False positives on G/B breaker symbols**: These rectangular boxes with internal structure share some edge density with MR symbols at certain scales.
2. **Missed detections at extreme scales**: If the scale search range is too narrow, symbols in SLD12 (very small) or SLD1 (potentially larger) may be missed.
3. **Duplicate detections in dense sections**: Adjacent MR symbols in SLD7 may not be properly separated by NMS.
4. **Rotation failure on SLD11**: If only 0Â° orientation is searched, all SLD11 symbols will be missed.
5. **Template-to-diagram scale mismatch**: The 161Ã—103 template rendered at the wrong scale will produce poor Chamfer scores everywhere.

## 3.4 Mandatory Research Question: "What Problem Is This ACTUALLY?"

### Analysis

Based on the forensic dataset inspection, this problem is:

**Primarily: One-Shot Symbol Spotting via Geometric Template Matching**

**Evidence:**
1. **One-shot**: Only one reference symbol is available. There is no training set, no validation set, no meta-learning support.
2. **Symbol spotting**: The task is to locate instances of a known geometric pattern in structured technical documents. This is the textbook definition of symbol spotting in Document Image Analysis (DIA).
3. **Geometric template matching**: The symbol is defined entirely by its geometric shape â€” straight lines and semicircular arcs. There is no texture, no color, no semantic context beyond geometry.

**Secondarily: A Hybrid Problem combining:**
- **Multi-scale template matching** (to handle the 4â€“6Ã— scale difference)
- **Chamfer distance matching** (to handle minor geometric deformations and anti-aliasing)
- **Spatial non-maximum suppression** (to consolidate dense overlapping detections)
- **Semantic verification** (PCA subspace or structural verification to discriminate from visually similar symbols)

**NOT primarily:**
- âŒ Object detection (no training data)
- âŒ Image retrieval (we know what we're looking for)
- âŒ Graph matching (overkill for this geometric complexity)
- âŒ Few-shot learning (requires meta-learning episodes we don't have)
- âŒ Document understanding (we don't need to understand the diagram semantics)

**This is a classical computer vision problem that should be solved with classical computer vision methods**, augmented by principled verification stages to suppress structured false positives.


---

# SECTION 4 â€” LITERATURE AND METHOD SURVEY

This section analyzes every potentially relevant technique for MR symbol localization. Each technique is evaluated against the **specific characteristics** of this dataset: clean binary line drawings, one-shot template, 4â€“6Ã— scale mismatch, topologically embedded symbols, and a primary discrimination challenge against visually similar symbols.

---

## 4.1 Template Matching (Normalized Cross-Correlation)

**How it works**: Slides a template image across the target image, computing the normalized cross-correlation (NCC) at each position:

$$NCC(x,y) = \frac{\sum_{i,j} [T(i,j) - \bar{T}][I(x+i, y+j) - \bar{I}_{x,y}]}{\sqrt{\sum_{i,j}[T(i,j)-\bar{T}]^2 \cdot \sum_{i,j}[I(x+i,y+j)-\bar{I}_{x,y}]^2}}$$

**Advantages**: Simple, fast (FFT-accelerated), deterministic, well-understood.

**Disadvantages**: Fundamentally pixel-to-pixel â€” assumes exact scale, rotation, and appearance match. No invariance to geometric deformation.

**Expected performance on THIS dataset**: **Poor.** The template is 161Ã—103 pixels while diagram symbols are ~25â€“40 pixels. The 4â€“6Ã— scale mismatch makes direct NCC fail entirely. Even with rescaling, NCC is sensitive to the topological context (connected bus conductors alter the local pixel pattern).

**Implementation complexity**: Very low.

**Suitability score**: 2/10 â€” Fundamental scale and context mismatch.

---

## 4.2 Multi-Scale Template Matching

**How it works**: Applies NCC at multiple scale levels by resizing the template to a pyramid of scales and running NCC at each level. Best match across scales is retained.

**Advantages**: Addresses scale variation. Still simple and deterministic.

**Disadvantages**: Computational cost scales linearly with number of scale levels. Still pixel-domain â€” sensitive to anti-aliasing, line thickness variation, and topological context. No rotation handling without explicit rotation pyramid.

**Expected performance on THIS dataset**: **Moderate.** Would correctly localize symbols at the right scale level but will produce false positives on G/B boxes and VT elements that happen to have similar pixel density at certain scales. Cannot disambiguate geometric structure.

**Implementation complexity**: Low.

**Suitability score**: 4/10 â€” Better than single-scale NCC but lacks geometric discrimination.

---

## 4.3 Chamfer Matching (Distance Transform Matching)

**How it works**: Operates in the **edge domain**. Computes the Distance Transform (DT) of the diagram's edge map, then overlays the template's edge pixels onto the DT. The Chamfer distance is the mean DT value sampled at template edge pixel locations:

$$D_{chamfer}(T, I) = \frac{1}{|E_T|} \sum_{p \in E_T} DT_I(p + t)$$

where $E_T$ is the set of template edge pixels and $t$ is the translation offset. Low Chamfer distance indicates good geometric alignment.

**Mathematical intuition**: Rather than comparing raw pixels, Chamfer matching asks: "How far are the template's edges from the nearest diagram edges at this location?" This is fundamentally a **geometric proximity measure** rather than a pixel correlation measure.

**Advantages**:
- **Edge-domain operation** â€” invariant to fill patterns, textures, and background.
- **Robust to minor deformation** â€” the DT provides a smooth scoring landscape.
- **Fast computation** â€” DT is O(n) via the Felzenszwalb algorithm; scoring is O(|E_T|) per position.
- **Naturally handles anti-aliasing** â€” soft edge variations produce smooth DT gradients rather than hard mismatches.
- **Proven in engineering drawing analysis** â€” this is the classic approach for symbol spotting in CAD/technical drawings.

**Disadvantages**:
- **No inherent scale invariance** â€” requires multi-scale search.
- **Sensitive to edge clutter** â€” dense diagram regions with many edges produce false low-distance basins.
- **Asymmetric** â€” measures template-to-diagram distance but not diagram-to-template. A simple diagram edge can produce low scores if it happens to be near all template edges.

**Expected performance on THIS dataset**: **Very good.** Empirically validated in prior work on similar MR symbols: Chamfer matching successfully identified 3/5 MR symbols on a single SLD with a mean distance of 1.0 pixel and 87% edge coverage ratio. The edge-domain approach is perfectly suited to these clean binary line drawings.

**Implementation complexity**: Medium.

**Suitability score**: 9/10 â€” Primary candidate. Proven on this exact domain.

---

## 4.4 Bidirectional Chamfer Matching

**How it works**: Extends standard Chamfer by computing BOTH forward (templateâ†’diagram) and reverse (diagramâ†’template) distances:

$$D_{bidir} = \alpha \cdot D_{forward}(T \to I) + (1-\alpha) \cdot D_{reverse}(I \to T)$$

**Advantages**: Addresses the asymmetry problem. The reverse distance penalizes "empty" matches where a simple edge happens to align with the template but has no additional structure.

**Disadvantages**: Reverse distance computation requires extracting the local diagram edge patch at each candidate position, adding computational cost.

**Expected performance on THIS dataset**: **Excellent.** The bidirectional score would help discriminate MR symbols from isolated edges or simple geometric structures that produce low forward-only Chamfer scores.

**Implementation complexity**: Medium.

**Suitability score**: 8/10 â€” Strong enhancement to standard Chamfer.

---

## 4.5 Hausdorff Distance

**How it works**: Measures the maximum minimum distance between two point sets:

$$H(A,B) = \max(\max_{a \in A} \min_{b \in B} d(a,b), \max_{b \in B} \min_{a \in A} d(a,b))$$

The partial Hausdorff distance uses a percentile instead of max, making it robust to outliers.

**Advantages**: Theoretically elegant shape distance. Robust to partial occlusion when using the partial variant.

**Disadvantages**: Extremely sensitive to outlier edge pixels. Computationally expensive for dense point sets. The max operation makes it unstable for practical use with noisy edges.

**Expected performance on THIS dataset**: **Moderate.** The clean edges reduce outlier sensitivity, but the connected bus conductor introduces many "foreign" edge points in the matching window that would inflate the Hausdorff distance even for true matches.

**Implementation complexity**: Medium.

**Suitability score**: 5/10 â€” Theoretically sound but practically inferior to Chamfer for this application.

---

## 4.6 Shape Context Descriptors

**How it works**: For each point on a contour, computes a log-polar histogram of the relative positions of all other contour points. Matching is performed by finding the minimum-cost correspondence between two sets of shape context descriptors using the Hungarian algorithm.

**Advantages**: Rich shape representation. Invariant to translation and scale (with normalization). Captures both local and global shape structure.

**Disadvantages**: Computationally expensive â€” O(nÂ³) for the Hungarian algorithm on n contour points. Sensitive to the number and distribution of sample points. Requires clean, isolated contours â€” which are NOT available in this dataset because symbols are topologically embedded in the bus structure.

**Expected performance on THIS dataset**: **Poor-to-moderate.** The fundamental requirement for isolated contours is not met. Extracting contours from a bus-connected region would include bus conductor edges, corrupting the shape context descriptor. Could work on post-proposal candidate patches if the symbol can be approximately isolated.

**Implementation complexity**: High.

**Suitability score**: 4/10 â€” Contour isolation problem is a fundamental blocker for primary use.

---

## 4.7 Contour Matching (Fourier Descriptors)

**How it works**: Represents closed contours as sequences of complex numbers, computes the DFT, and uses the magnitudes of the low-frequency coefficients as rotation/scale-invariant shape descriptors.

**Advantages**: Compact representation. Inherent invariance to rotation, scale, and starting point.

**Disadvantages**: Requires closed, isolated contours. Sensitive to contour extraction quality. Cannot handle partial shapes or connected structures.

**Expected performance on THIS dataset**: **Poor.** Same contour isolation problem as Shape Context. The MR symbol's contour includes the bus conductor when embedded in the diagram.

**Implementation complexity**: Medium.

**Suitability score**: 3/10 â€” Contour isolation failure.

---

## 4.8 Connected Component Analysis

**How it works**: Labels connected regions in a binary image, then filters by geometric properties (area, aspect ratio, solidity, etc.).

**Advantages**: Very fast. Provides natural region proposals. Simple to implement.

**Disadvantages**: Fundamentally assumes symbols are **isolated connected components**. This was empirically tested and **proven to fail** in prior work on this exact domain â€” MR symbols are topologically connected to the bus conductor and do NOT emerge as standalone components even after wire suppression and morphological repair.

**Expected performance on THIS dataset**: **Failed â€” empirically verified.** In Stage 2/2.5/2.75 of the prior pipeline, connected-component analysis was systematically tested with wire suppression, morphological closing experiments, and relaxed filtering thresholds. The MR symbol never emerged as an isolated connected component.

**Implementation complexity**: Very low.

**Suitability score**: 1/10 â€” Empirically invalidated.

---

## 4.9 Morphological Analysis (Erosion, Dilation, Opening, Closing)

**How it works**: Applies structuring element operations to binary images to modify topology â€” closing gaps, removing noise, separating touching structures.

**Advantages**: Can recover broken contours, separate weakly connected components. Fast.

**Disadvantages**: Structuring element choice is critical and problem-specific. Aggressive operations reconnect suppressed bus conductors, creating giant merged components.

**Expected performance on THIS dataset**: **Useful as preprocessing, not as detection.** Empirically validated in Stage 2.75: controlled morphological closing with small kernels (3Ã—3, 5Ã—3) successfully recovered fragmented MR coil geometry but did NOT enable connected-component isolation.

**Implementation complexity**: Low.

**Suitability score**: 5/10 as preprocessing support â€” 1/10 as primary detection.

---

## 4.10 Skeleton Matching

**How it works**: Computes the morphological skeleton (medial axis) of binary shapes, then compares skeletons using graph-based or structural matching.

**Advantages**: Topology-preserving dimensionality reduction. Captures the essential structure of shapes without fill information.

**Disadvantages**: Sensitive to noise and boundary irregularities. The skeleton of a bus-connected MR symbol includes the bus conductor skeleton, making isolated comparison impossible without prior segmentation.

**Expected performance on THIS dataset**: **Moderate as a verification step.** Could be useful for comparing the skeleton structure of candidate patches against the template skeleton, but cannot serve as the primary localization mechanism.

**Implementation complexity**: Medium.

**Suitability score**: 4/10 â€” Useful only for post-detection verification.

---

## 4.11 Graph-Based Matching (Graph Edit Distance)

**How it works**: Represents symbols as attributed graphs (nodes = junction points, edges = connecting strokes) and computes the graph edit distance (GED) â€” the minimum cost sequence of edit operations to transform one graph into another.

**Advantages**: Theoretically the most structurally precise matching method. Captures topology, not just geometry.

**Disadvantages**: NP-hard â€” GED computation is computationally intractable for large graphs. Requires prior graph extraction from pixel images, which is itself a hard problem. Overkill for geometrically simple symbols.

**Expected performance on THIS dataset**: **Unnecessarily complex.** The MR symbol has low structural complexity (a few lines and semicircles). Graph matching would work but provides no advantage over simpler geometric methods while incurring exponential computational cost.

**Implementation complexity**: Very high.

**Suitability score**: 2/10 â€” Overkill and computationally impractical.

---

## 4.12 PCA-Based Verification

**How it works**: Builds a PCA subspace from augmented versions of the template (rotations, scales, morphological variants). Projects candidate patches into this subspace and measures reconstruction error. Low reconstruction error indicates the candidate lies on the "symbol manifold."

**Mathematical intuition**: PCA learns the principal modes of appearance variation for the symbol class. True symbols project well onto these modes; non-symbols (G/B boxes, zigzags) project poorly, producing high reconstruction error.

**Advantages**: Provides semantic verification orthogonal to geometric matching. One-shot augmentation-driven training requires no external data. Computationally cheap at inference (matrix multiplication).

**Disadvantages**: Requires careful centroid alignment to prevent PCA from learning alignment variance rather than structural variance. The augmentation strategy must be carefully designed. Sensitive to PCA dimensionality.

**Expected performance on THIS dataset**: **Empirically validated as a powerful disambiguation tool.** In Stage 4 of prior work, PCA subspace refinement successfully discriminated true MR symbols from G/B false positives when combined with proper score calibration (exponential normalization, Î±=2.0, 0.7/0.3 fusion weights).

**Implementation complexity**: Medium.

**Suitability score**: 8/10 â€” Proven second-stage verification.

---

## 4.13 SIFT (Scale-Invariant Feature Transform)

**How it works**: Detects scale-space extrema in the Difference-of-Gaussians (DoG) pyramid, computes 128-dimensional gradient histogram descriptors at stable keypoint locations. Matching is performed via nearest-neighbor descriptor distance with Lowe's ratio test.

**Advantages**: Invariant to scale, rotation, and affine distortion. Highly discriminative descriptors.

**Disadvantages**: Designed for natural images with rich texture. Line drawings produce very few stable keypoints because DoG extrema require local gradient contrast that simple lines don't provide.

**Expected performance on THIS dataset**: **Very poor.** The MR symbol is composed of thin lines and arcs â€” the DoG pyramid produces almost no stable extrema. Empirically, line drawings typically yield 0â€“5 keypoints per symbol, which is insufficient for reliable matching.

**Implementation complexity**: Low (OpenCV provides full implementation).

**Suitability score**: 1/10 â€” Fundamentally unsuited to line drawings.

---

## 4.14 SURF (Speeded-Up Robust Features)

**How it works**: Similar to SIFT but uses Hessian-based detector and integral image approximations for speed.

**Advantages**: Faster than SIFT. Same invariance properties.

**Disadvantages**: Same fundamental problem as SIFT â€” requires texture-rich images.

**Expected performance on THIS dataset**: **Very poor.** Same limitations as SIFT on line drawings.

**Suitability score**: 1/10.

---

## 4.15 ORB (Oriented FAST and Rotated BRIEF)

**How it works**: Uses FAST corner detector with Harris corner measure for keypoint detection, BRIEF binary descriptors with learned rotation compensation.

**Advantages**: Very fast (binary descriptors). Free from patent issues.

**Disadvantages**: FAST corners require local intensity contrast. Binary descriptors have limited discriminative power for subtle shape differences.

**Expected performance on THIS dataset**: **Poor.** Line drawings produce sparse corners primarily at junction points (intersections with bus conductors). These junctions are shared across many symbol types, providing no discrimination.

**Suitability score**: 2/10.

---

## 4.16 AKAZE (Accelerated-KAZE)

**How it works**: Uses nonlinear scale space (Perona-Malik diffusion) for keypoint detection, Modified-Local Difference Binary (M-LDB) descriptors.

**Advantages**: Nonlinear scale space preserves boundaries better than Gaussian blurring. Better suited to structured images than SIFT/SURF.

**Disadvantages**: Still assumes sufficient local texture/gradient contrast for keypoint detection.

**Expected performance on THIS dataset**: **Moderate.** AKAZE's nonlinear diffusion preserves edges better, potentially producing more stable keypoints on line drawings. However, the fundamental sparsity problem remains â€” there are very few distinctive keypoint locations in the MR symbol.

**Suitability score**: 3/10 â€” Slightly better than SIFT/ORB but still insufficient for primary matching.

---

## 4.17 HOG (Histogram of Oriented Gradients)

**How it works**: Divides the image into cells, computes gradient orientation histograms per cell, normalizes across blocks. The resulting descriptor captures local edge/gradient structure.

**Advantages**: Captures the distribution of edge orientations â€” directly relevant for the MR symbol's mix of horizontal lines, vertical lines, and curved arcs. Translation-invariant within cells.

**Disadvantages**: Fixed-size descriptor â€” requires candidate patches to be extracted first (not a localizer). Sensitive to cell/block size parameters. No inherent scale or rotation invariance.

**Expected performance on THIS dataset**: **Moderate as a verification feature.** HOG descriptors of the MR symbol's dual-semicircle lobes would have a distinctive gradient orientation distribution (strong vertical gradients from the lobes, strong horizontal from the base bar). Could serve as a secondary verification feature but cannot localize symbols.

**Implementation complexity**: Low.

**Suitability score**: 5/10 â€” Useful for post-detection verification, not localization.

---

## 4.18 Siamese Networks (One-Shot Learning)

**How it works**: Trains a twin neural network that maps pairs of images into an embedding space where similar images are close and dissimilar images are far apart. Uses contrastive loss or triplet loss.

**Advantages**: Explicitly designed for one-shot/few-shot scenarios. Learns discriminative features from pairs.

**Disadvantages**: Requires training data â€” specifically, positive and negative pairs. With one template and zero annotations, there are no positive pairs and no principled way to construct negative pairs. Transfer learning from natural image domains (ImageNet) is unlikely to help because line drawings have fundamentally different statistics.

**Expected performance on THIS dataset**: **Poor without external data.** A Siamese network cannot be meaningfully trained on a single template image. Even with augmentation, the network would learn template-specific artifacts rather than general symbol recognition. Could potentially work if pre-trained on a large corpus of engineering drawing symbols, but no such corpus is available.

**Implementation complexity**: High (requires deep learning framework, GPU, training loop).

**Suitability score**: 2/10 â€” Data requirements not met.

---

## 4.19 Few-Shot Learning (Prototypical Networks, Matching Networks)

**How it works**: Meta-learns an embedding space and a distance function across many episodes of support/query tasks.

**Advantages**: Designed for limited data scenarios.

**Disadvantages**: Meta-learning requires **many classes** and **many episodes** â€” not just few examples per class. With one class and one template, there is no meta-learning structure to exploit.

**Expected performance on THIS dataset**: **Not applicable.** The meta-learning paradigm requires a distribution of tasks, which does not exist here.

**Suitability score**: 1/10 â€” Paradigm mismatch.

---

## 4.20 YOLO / Faster R-CNN / DETR / Mask R-CNN

**How it works**: Supervised object detection architectures that learn to predict bounding boxes and class labels from thousands of annotated training images.

**Analysis and rejection**:

| Requirement | Available |
|---|---|
| Training images needed | 1,000â€“10,000+ |
| Training images available | 0 (template is not a training image) |
| Annotated bounding boxes needed | 5,000â€“50,000+ |
| Annotated bounding boxes available | 0 |
| Class diversity needed | Multiple classes for discriminative learning |
| Classes available | 1 (MR symbol only) |

**Verdict**: **Rejected.** These architectures are fundamentally unsuitable for this problem. No amount of augmentation on a single template can substitute for the thousands of annotated scene-level training examples these detectors require. Transfer learning from COCO/ImageNet would transfer natural image statistics that are irrelevant to engineering line drawings.

**Suitability score**: 0/10 â€” Hard reject due to data requirements.

---

## 4.21 Vision Transformers (ViT, DINOv2)

**How it works**: Self-supervised or supervised transformers that learn patch-level representations through attention mechanisms.

**Analysis**: DINOv2 self-supervised features could theoretically provide good representations without labeled data. However, the features are learned from natural images (ImageNet-scale), and engineering line drawings lie far outside this distribution. Fine-tuning requires labeled data we don't have.

**Suitability score**: 1/10 â€” Domain gap is too large for zero-shot transfer.

---

## 4.22 Classical Feature Matching (Template Histogram Comparison)

**How it works**: Compares histograms of image properties (intensity, gradient magnitude, gradient direction) between template and candidate regions.

**Advantages**: Fast, simple.

**Disadvantages**: Discards all spatial structure â€” two regions with the same histogram but different spatial arrangements would score identically.

**Expected performance on THIS dataset**: **Poor.** Many symbols share similar edge density and gradient distributions. Spatial structure is the key discriminator.

**Suitability score**: 2/10.

---

## 4.23 Hybrid Pipeline: Chamfer Localization + PCA Verification

**How it works**: Uses multi-scale Chamfer matching as the primary localization mechanism, followed by spatial NMS for consolidation, and PCA subspace refinement for semantic verification.

**Advantages**: Combines the strengths of geometric edge matching (localization) with appearance manifold verification (discrimination). Each stage addresses a specific failure mode:
- Chamfer â†’ spatial localization
- Multi-scale search â†’ scale invariance
- Multi-orientation search â†’ rotation handling
- NMS â†’ duplicate consolidation
- PCA â†’ semantic disambiguation from structured false positives

**Disadvantages**: Multi-stage pipeline requires careful parameter calibration. Computational cost of dense sliding-window Chamfer scales with image size and number of scale/orientation levels.

**Expected performance on THIS dataset**: **Excellent â€” empirically validated.** This exact architecture was implemented and tested in prior work (Stages 1â€“4.5), achieving:
- Correct localization of true MR symbols
- Successful suppression of G/B false positives via PCA refinement
- Stable NMS consolidation of overlapping score basins
- Recall improvement via multi-template ensemble search

**Implementation complexity**: Medium-high.

**Suitability score**: 10/10 â€” Proven architecture with empirical validation on this domain.


---

# SECTION 5 â€” ARCHITECTURE TRADE STUDY

## 5.1 Evaluation Criteria

Each candidate architecture is evaluated against seven criteria derived from the dataset analysis:

| Criterion | Weight | Rationale |
|---|---|---|
| **One-shot capability** | Critical | Only one template exists |
| **Scale handling** | High | 4â€“6Ã— scale mismatch between template and diagram symbols |
| **Edge-domain suitability** | High | Binary line drawings are most naturally represented as edge maps |
| **Discrimination power** | High | Must distinguish MR from G/B boxes, VT zigzags, and other visually similar symbols |
| **Computational feasibility** | Medium | Must run on CPU without GPU requirements |
| **Determinism** | Critical | Must produce identical results across runs |
| **Empirical validation** | Critical | Preference for methods empirically tested on this domain |

## 5.2 Comparison Matrix

| Architecture | One-Shot | Scale | Edge-Domain | Discrimination | CPU-Only | Deterministic | Empirical | **Overall** |
|---|---|---|---|---|---|---|---|---|
| NCC Template Matching | âœ… | âŒ | âŒ | âŒ | âœ… | âœ… | âŒ | 2/10 |
| Multi-Scale NCC | âœ… | âœ… | âŒ | âŒ | âœ… | âœ… | âŒ | 4/10 |
| **Chamfer Matching** | **âœ…** | **âœ…*** | **âœ…** | **âœ…** | **âœ…** | **âœ…** | **âœ…** | **9/10** |
| Bidirectional Chamfer | âœ… | âœ…* | âœ… | âœ…âœ… | âœ… | âœ… | âŒ | 8/10 |
| Hausdorff Distance | âœ… | âœ…* | âœ… | âš ï¸ | âœ… | âœ… | âŒ | 5/10 |
| Shape Context | âœ… | âœ… | âœ… | âœ… | âš ï¸ | âœ… | âŒ | 4/10 |
| Contour Matching | âœ… | âœ… | âœ… | âš ï¸ | âœ… | âœ… | âŒ | 3/10 |
| CC Analysis | âœ… | âœ… | âŒ | âŒ | âœ… | âœ… | âŒ Failed | 1/10 |
| Skeleton Matching | âœ… | âš ï¸ | âœ… | âš ï¸ | âœ… | âœ… | âŒ | 4/10 |
| Graph Edit Distance | âœ… | âœ… | âœ… | âœ…âœ… | âŒ NP-hard | âœ… | âŒ | 2/10 |
| **PCA Verification** | **âœ…** | **âœ…** | **âš ï¸** | **âœ…âœ…** | **âœ…** | **âœ…** | **âœ…** | **8/10** |
| SIFT/SURF | âœ… | âœ… | âŒ | âŒ | âœ… | âœ… | âŒ | 1/10 |
| ORB | âœ… | âš ï¸ | âŒ | âŒ | âœ… | âœ… | âŒ | 2/10 |
| AKAZE | âœ… | âœ… | âš ï¸ | âš ï¸ | âœ… | âœ… | âŒ | 3/10 |
| HOG | âœ… | âŒ | âš ï¸ | âš ï¸ | âœ… | âœ… | âŒ | 5/10 |
| Siamese Networks | âš ï¸ | âœ… | âŒ | âš ï¸ | âŒ | âŒ | âŒ | 2/10 |
| Few-Shot Learning | âŒ | âœ… | âŒ | âš ï¸ | âŒ | âŒ | âŒ | 1/10 |
| YOLO/RCNN/DETR | âŒ | âœ… | âŒ | âœ… | âŒ | âŒ | âŒ | 0/10 |
| Vision Transformers | âŒ | âœ… | âŒ | âš ï¸ | âŒ | âŒ | âŒ | 1/10 |
| **Chamfer + PCA Hybrid** | **âœ…** | **âœ…** | **âœ…** | **âœ…âœ…** | **âœ…** | **âœ…** | **âœ…** | **10/10** |

*âœ…\* = requires multi-scale search wrapper, which is a standard extension.*

## 5.3 Detailed Rejection Justifications

### 5.3.1 YOLO / Faster R-CNN / DETR / Mask R-CNN â€” REJECTED

**Rejection reason**: Data requirements fundamentally unmet.

These supervised detectors require 1,000â€“50,000+ annotated training images. This project has:
- 0 annotated bounding boxes
- 1 template image (not a training image)
- 10 target images (not a training set)

Even with aggressive augmentation of the single template, supervised detectors cannot learn:
- Background context statistics (what is NOT the symbol)
- Hard negative examples (G/B boxes that look similar but are not MR symbols)
- Scale/aspect ratio distributions from real scene-level examples

Data augmentation of a single isolated template produces artificial training examples that do not reflect the actual in-context appearance of the symbol embedded within bus structures.

**Strength of rejection**: Definitive. No mitigation possible without external annotated data.

### 5.3.2 Siamese / Few-Shot Networks â€” REJECTED

**Rejection reason**: Meta-learning paradigm mismatch.

Few-shot learning requires:
- A meta-training distribution of tasks (many classes, many episodes)
- Support/query pairs from multiple categories
- A learned metric/embedding space

This project has one class, one template, and zero labeled scene-level examples. There is no meta-learning structure to exploit. Pre-training on natural image pairs (Omniglot, miniImageNet) would not transfer to engineering line drawings.

**Strength of rejection**: Strong. Could be revisited if a large corpus of engineering drawing symbol annotations becomes available.

### 5.3.3 SIFT / SURF / ORB â€” REJECTED

**Rejection reason**: Feature detection failure on line drawings.

These feature detectors are designed for natural images with rich texture gradients. Engineering line drawings consist of thin lines and arcs that produce:
- Very few stable keypoints (0â€“5 per symbol)
- High positional instability in the scale-space pyramid
- Non-distinctive descriptors at junction points (shared across symbol types)

**Strength of rejection**: Strong. Fundamental domain mismatch between textured natural images and binary line drawings.

### 5.3.4 Connected Component Analysis â€” REJECTED

**Rejection reason**: Empirically invalidated.

Tested in Stages 2, 2.5, and 2.75 of prior work. The MR symbol does NOT emerge as an isolated connected component because:
- It is topologically connected to the bus conductor
- Wire suppression removes horizontal conductors but does not sever the vertical stem connection
- Morphological closing experiments recovered coil continuity but did not enable component isolation

Even with relaxed filtering thresholds (allowing 4Ã— the template area), zero additional MR candidates were recovered.

**Strength of rejection**: Definitive. Empirically proven to fail on this exact dataset.

### 5.3.5 Graph Edit Distance â€” REJECTED

**Rejection reason**: Computational intractability and over-engineering.

GED is NP-hard. For practical graph sizes (10â€“50 nodes), approximate algorithms exist but are still O(nâ´) or worse. The MR symbol has low structural complexity that does not justify graph-theoretic reasoning. Chamfer matching captures the necessary geometric discrimination at a fraction of the computational cost.

**Strength of rejection**: Strong. Correct in theory but impractical and unnecessary for this symbol complexity.

### 5.3.6 Shape Context â€” REJECTED as primary method

**Rejection reason**: Contour isolation requirement not met.

Shape Context requires sampling points from isolated contours. The MR symbol is topologically embedded in the bus structure â€” there is no clean, isolated contour to sample from. Attempting to extract a local contour from a candidate patch would include bus conductor edges, corrupting the descriptor.

**Strength of rejection**: Strong for primary localization. Could potentially be used as a verification step on extracted candidate patches with manual contour cleaning.

### 5.3.7 NCC Template Matching â€” REJECTED as primary method

**Rejection reason**: Pixel-domain sensitivity to context.

NCC compares raw pixel values, which are influenced by:
- The connected bus conductor passing through the matching window
- Adjacent text labels
- Neighboring symbols within the matching window
- Anti-aliasing variations

In engineering drawings, the local pixel context around a symbol is highly variable (different neighboring symbols, different text labels, different bus orientations), making pixel-domain correlation unreliable.

**Strength of rejection**: Moderate. Multi-scale NCC could serve as a crude initial filter but should not be the primary architecture.

---

# SECTION 6 â€” FINAL ARCHITECTURE DECISION

## 6.1 Selected Architecture

**Multi-Scale Multi-Orientation Chamfer Matching with PCA Subspace Verification**

This is a **hybrid classical computer vision pipeline** consisting of four major stages:

```
â”Œâ”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”
â”‚                    PREPROCESSING                             â”‚
â”‚  Binarization â†’ Edge Extraction â†’ Wire Suppression          â”‚
â”‚  (Both template and diagram)                                 â”‚
â””â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”¬â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”˜
                       â”‚
â”Œâ”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â–¼â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”
â”‚              MULTI-SCALE CHAMFER LOCALIZATION                â”‚
â”‚  Template scale pyramid â†’ Distance Transform of diagram     â”‚
â”‚  Dense sliding window â†’ Chamfer score map per scale         â”‚
â”‚  Multi-orientation search (0Â°, 90Â°, 180Â°, 270Â°)            â”‚
â”‚  Coverage ratio filtering                                    â”‚
â””â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”¬â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”˜
                       â”‚
â”Œâ”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â–¼â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”
â”‚              SPATIAL NON-MAXIMUM SUPPRESSION                 â”‚
â”‚  Local minima extraction â†’ Greedy NMS                       â”‚
â”‚  Distance-based suppression radius                          â”‚
â”‚  Ranked candidate list                                      â”‚
â””â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”¬â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”˜
                       â”‚
â”Œâ”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â–¼â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”
â”‚              PCA SUBSPACE VERIFICATION                       â”‚
â”‚  One-shot augmentation â†’ PCA manifold construction          â”‚
â”‚  Candidate patch extraction â†’ Centroid alignment            â”‚
â”‚  Reconstruction error computation                           â”‚
â”‚  Chamfer-PCA score fusion â†’ Final ranked detections         â”‚
â””â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”˜
```

## 6.2 Justification for Every Stage

### Stage 1: Preprocessing

**Why it exists**: Raw SLD images contain RGBA channels, anti-aliased edges, and embedded text. The pipeline operates in the edge domain, requiring clean binary edge maps.

**Why alternatives were rejected**:
- Direct pixel-domain matching: Sensitive to background, text, anti-aliasing
- No preprocessing: Chamfer matching requires binary edge inputs
- OCR-based text removal: Adds unnecessary complexity; Chamfer matching is naturally robust to text because text edges have different geometric structure than symbol edges

### Stage 2: Multi-Scale Chamfer Localization

**Why it exists**: This is the PRIMARY localization mechanism. Chamfer matching operates in the edge domain, computing geometric proximity between template edges and diagram edges. It is:
- Naturally suited to binary line drawings
- Robust to minor geometric deformation and anti-aliasing
- Computationally efficient via Distance Transform precomputation
- Empirically proven on this exact domain

**Why Chamfer over NCC**: NCC operates in the pixel domain, making it sensitive to contextual variations (bus conductors, adjacent text, neighboring symbols). Chamfer operates in the edge domain, where only the geometric structure matters.

**Why Chamfer over Hausdorff**: Chamfer uses mean distance (robust to outlier edges from bus conductors). Hausdorff uses max distance (sensitive to any single distant edge pixel).

**Why multi-scale**: The template is 161Ã—103 pixels; diagram symbols are ~25â€“40 pixels. Without multi-scale search, the scale mismatch guarantees failure.

**Why multi-orientation**: SLD11 contains 90Â° rotated symbols. Without at least 0Â° and 90Â° orientation search, these symbols will be missed entirely.

### Stage 3: Spatial Non-Maximum Suppression

**Why it exists**: Dense sliding-window Chamfer matching produces **overlapping score basins** where many neighboring windows around a true symbol all produce low Chamfer scores. Without NMS, the top-K results would be dominated by multiple windows from the same symbol.

**Why greedy NMS over clustering**: Greedy NMS (sort by score, suppress within radius) is simpler, faster, and more deterministic than clustering-based approaches (DBSCAN, mean-shift). The suppression radius is naturally set to the template size.

### Stage 4: PCA Subspace Verification

**Why it exists**: Chamfer matching alone cannot discriminate the MR symbol from other symbols that share geometric sub-primitives. The G/B breaker box, for example, has sufficient edge density to produce competitive Chamfer scores. PCA provides an **orthogonal semantic verification signal** that captures appearance manifold membership.

**Why PCA over a neural classifier**: PCA requires no labeled data â€” it constructs a symbol manifold from augmented versions of the single template. A neural classifier would require labeled positive and negative examples.

**Why PCA over HOG**: HOG provides a single descriptor vector without a notion of "manifold membership." PCA provides reconstruction error, which naturally measures how well a candidate fits the learned appearance space.

**Why the exponential normalization and 0.7/0.3 fusion**: Empirically calibrated in Stage 4 of prior work across 35 experimental configurations. Exponential normalization (Î±=2.0) with 0.7 Chamfer / 0.3 PCA weighting produced the optimal ranking separation between true MR symbols and structured false positives.

## 6.3 Why This Architecture Is Optimal for This Dataset

1. **Data-driven**: Every design decision emerged from analyzing the actual images, not from following trends.
2. **One-shot compatible**: No training data required beyond the single template.
3. **Edge-domain native**: Operates in the natural representation space of binary line drawings.
4. **Empirically validated**: The core Chamfer + NMS + PCA pipeline has been implemented and tested on similar MR symbols in prior work.
5. **Deterministic**: No stochastic components. Identical inputs always produce identical outputs.
6. **Explainable**: Every detection is traceable to a Chamfer score, a coverage ratio, a PCA reconstruction error, and a fused score.
7. **CPU-efficient**: No GPU required. Distance Transform and sliding-window operations are well-optimized in OpenCV.
8. **Modular**: Each stage can be independently tuned, validated, and debugged.


---

# SECTION 7 â€” DETAILED PIPELINE DESIGN

## 7.1 Pipeline Overview

```
Input: MR_Symbol.png + SLD{1,2,3,4,7,8,9,10,11,12}.png
                     â”‚
    â”Œâ”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â–¼â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”
    â”‚  STAGE 1: PREPROCESSING          â”‚
    â”‚  1a. Template Preprocessing      â”‚
    â”‚  1b. Diagram Preprocessing       â”‚
    â”‚  1c. Wire Suppression            â”‚
    â””â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”¬â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”˜
                     â”‚
    â”Œâ”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â–¼â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”
    â”‚  STAGE 2: SCALE ESTIMATION       â”‚
    â”‚  2a. Template Scale Pyramid      â”‚
    â”‚  2b. Orientation Variants        â”‚
    â””â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”¬â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”˜
                     â”‚
    â”Œâ”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â–¼â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”
    â”‚  STAGE 3: CHAMFER LOCALIZATION   â”‚
    â”‚  3a. Distance Transform          â”‚
    â”‚  3b. Dense Sliding Window        â”‚
    â”‚  3c. Score Map Generation        â”‚
    â”‚  3d. Coverage Ratio Filtering    â”‚
    â””â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”¬â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”˜
                     â”‚
    â”Œâ”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â–¼â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”
    â”‚  STAGE 4: SPATIAL NMS            â”‚
    â”‚  4a. Local Minima Extraction     â”‚
    â”‚  4b. Greedy Suppression          â”‚
    â”‚  4c. Ranked Detection List       â”‚
    â””â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”¬â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”˜
                     â”‚
    â”Œâ”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â–¼â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”
    â”‚  STAGE 5: PCA VERIFICATION       â”‚
    â”‚  5a. Template Augmentation       â”‚
    â”‚  5b. PCA Manifold Construction   â”‚
    â”‚  5c. Candidate Patch Extraction  â”‚
    â”‚  5d. Score Fusion & Re-ranking   â”‚
    â””â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”¬â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”˜
                     â”‚
    â”Œâ”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â–¼â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”
    â”‚  STAGE 6: OUTPUT GENERATION      â”‚
    â”‚  6a. Bounding Box Extraction     â”‚
    â”‚  6b. Visualization Overlays      â”‚
    â”‚  6c. Detection Metadata (JSON)   â”‚
    â””â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”€â”˜

Output: Bounding boxes + Annotated SLDs + Detection metadata
```

---

## 7.2 Stage 1: Preprocessing

### 7.2.1 Template Preprocessing (Stage 1a)

**Purpose**: Convert the raw template image into clean binary and edge representations suitable for Chamfer matching.

**Input**: `MR_Symbol.png` (161Ã—103, RGBA, grayscale content)

**Output**:
- `template_gray` â€” grayscale image (uint8)
- `template_binary` â€” binarized template (0/255)
- `template_edges` â€” Canny edge map (0/255)
- `preprocessing_stats.json` â€” quantitative metadata

**Algorithm**:
1. Load RGBA image, convert to grayscale: `gray = 0.299R + 0.587G + 0.114B`
2. Apply median filter (kernel=3) for anti-aliasing smoothing
3. Adaptive thresholding (Sauvola recommended, block_size=21, k=0.2) to produce binary mask
4. Invert if necessary so foreground (symbol) = 255, background = 0
5. Canny edge detection (low=50, high=150) on the binary or grayscale image
6. Save statistics: dimensions, foreground pixel count, foreground ratio, edge pixel count

**Complexity**: O(WÃ—H) â€” single-pass per operation

**Failure Modes**:
- Incorrect binarization threshold â†’ fragmented symbol edges
- Over-smoothing â†’ loss of fine detail in the cross/cap structure

**Mitigation**: Parameterize all constants. Use adaptive thresholding to handle the anti-aliased grayscale edges.

### 7.2.2 Diagram Preprocessing (Stage 1b)

**Purpose**: Convert each SLD into clean binary and edge representations.

**Input**: `SLD{N}.png` (variable size, RGBA)

**Output**:
- `diagram_gray` â€” grayscale
- `diagram_binary` â€” binarized diagram
- `diagram_edges` â€” Canny edge map

**Algorithm**: Same pipeline as template preprocessing, applied per-SLD.

**Key parameter**: The adaptive threshold parameters may need to be consistent across all SLDs to ensure uniform binarization behavior. Since all SLDs have similar dark pixel ratios (1.4%â€“4.0%), a single parameter set should generalize.

### 7.2.3 Wire Suppression (Stage 1c)

**Purpose**: Suppress long horizontal conductor lines to reduce edge clutter and improve Chamfer matching precision.

**Input**: `diagram_binary`

**Output**: `diagram_binary_no_wire` â€” binary image with horizontal conductors suppressed

**Algorithm**:
1. Create a horizontal structuring element: `kernel = np.ones((1, W_wire), dtype=np.uint8)` where `W_wire â‰ˆ 50â€“100` pixels
2. Apply morphological opening: `wire_mask = cv2.morphologyEx(binary, MORPH_OPEN, kernel)`
3. Subtract wire mask: `no_wire = binary - wire_mask`
4. Re-extract edges from `no_wire`: `edges_no_wire = cv2.Canny(no_wire, low, high)`

**Mathematical justification**: Morphological opening with a wide horizontal kernel preserves only structures that are at least `W_wire` pixels wide horizontally â€” i.e., bus conductors. Subtracting this mask removes the conductor while preserving symbols, which are narrower than `W_wire`.

**Complexity**: O(WÃ—H) per morphological operation

**Failure Modes**:
- `W_wire` too small â†’ incomplete conductor suppression
- `W_wire` too large â†’ vertical text or symbol fragments suppressed
- Wire suppression severs the MR symbol's connection point, fragmenting it

**Mitigation**: Tune `W_wire` per-SLD or use the diagram-wide line length distribution to set it adaptively. Wire suppression is applied to the diagram ONLY â€” the template is processed without it.

---

## 7.3 Stage 2: Scale and Orientation Pyramid

### 7.3.1 Template Scale Pyramid (Stage 2a)

**Purpose**: Generate multiple scaled versions of the template edge map to handle the 4â€“6Ã— scale mismatch.

**Input**: `template_edges` (161Ã—103)

**Output**: List of `(scale_factor, scaled_edge_map)` tuples

**Algorithm**:
1. Define scale range: `scales = np.linspace(s_min, s_max, N_scales)`
   - Recommended: `s_min=0.15, s_max=0.40, N_scales=10`
   - This produces templates from ~24Ã—15 to ~64Ã—41 pixels
2. For each scale factor `s`:
   - Resize template: `scaled = cv2.resize(template_edges, (0,0), fx=s, fy=s, interpolation=INTER_AREA)`
   - Re-threshold to ensure binary: `_, scaled = cv2.threshold(scaled, 127, 255, THRESH_BINARY)`
   - Extract edge coordinates: `edge_coords = np.argwhere(scaled > 0)`

**Mathematical justification**: The scale range [0.15, 0.40] covers the observed 3â€“6Ã— size ratio between template and diagram symbols. Ten scale levels provide sufficient resolution to find a good match without excessive computational cost.

**Complexity**: O(N_scales Ã— W_template Ã— H_template)

### 7.3.2 Orientation Variants (Stage 2b)

**Purpose**: Generate rotated versions of each scaled template to handle orientation variation.

**Input**: Each scaled template edge map

**Output**: For each scale, a set of orientation variants

**Algorithm**:
1. Define orientations: `[0Â°, 90Â°, 180Â°, 270Â°]`
   - 0Â°: Standard horizontal (covers majority of SLDs)
   - 90Â°: Vertical orientation (covers SLD11)
   - 180Â°: Inverted horizontal (may exist for some symbols)
   - 270Â°: Inverted vertical
2. For each orientation:
   - Rotate template: `cv2.getRotationMatrix2D(center, angle, 1.0)` + `cv2.warpAffine`
   - Re-extract edge coordinates

**Total template variants**: `N_scales Ã— N_orientations = 10 Ã— 4 = 40`

---

## 7.4 Stage 3: Dense Chamfer Localization

### 7.4.1 Distance Transform (Stage 3a)

**Purpose**: Precompute the Distance Transform of the diagram edge map, enabling O(1) distance lookup per edge pixel.

**Input**: `diagram_edges_no_wire` (binary edge map)

**Output**: `DT` â€” float32 distance transform image

**Algorithm**:
1. Invert edges: `inv_edges = 255 - diagram_edges_no_wire`
2. Compute Distance Transform: `DT = cv2.distanceTransform(inv_edges, cv2.DIST_L2, 5)`

**Mathematical definition**: `DT(x,y) = min_{(x',y') âˆˆ E} ||( x,y) - (x',y')||â‚‚` where `E` is the set of diagram edge pixels.

**Complexity**: O(WÃ—H) via the Felzenszwalbâ€“Huttenlocher exact Euclidean DT algorithm

**Key property**: DT(x,y) = 0 at edge pixels and increases smoothly away from edges. This creates a smooth scoring landscape for Chamfer matching.

### 7.4.2 Dense Sliding Window Search (Stage 3b)

**Purpose**: Exhaustively evaluate the Chamfer distance at every valid translation position.

**Input**: `DT` (diagram distance transform), template edge coordinates for each (scale, orientation) variant

**Output**: `score_map` â€” 2D array of Chamfer scores per position; one per (scale, orientation)

**Algorithm**:
For each template variant `(s, Î¸)`:
```
For each valid position (tx, ty):
    chamfer_score = 0
    for each template edge pixel (ex, ey):
        diagram_x = tx + ex
        diagram_y = ty + ey
        chamfer_score += DT[diagram_y, diagram_x]
    chamfer_score /= |E_template|    # Mean distance
    
    # Coverage ratio: fraction of template edges within distance Ï„
    coverage = count(DT[ty+ey, tx+ex] < Ï„ for (ex,ey) in E_template) / |E_template|
    
    score_map[ty, tx] = chamfer_score
    coverage_map[ty, tx] = coverage
```

**Coverage ratio threshold**: `Ï„ = 2.0` pixels â€” a template edge pixel is "covered" if the nearest diagram edge is within 2 pixels.

**Optimization opportunities**:
1. Vectorize using NumPy: Extract all DT values at template edge locations simultaneously
2. Step size > 1: Reduce computation by stepping 2â€“3 pixels (at the cost of localization precision)
3. Early termination: Skip positions where the first few edge pixels already have high DT values
4. Multi-scale coarse-to-fine: Run coarse search at lower resolution, refine at full resolution

**Complexity**: O(N_scales Ã— N_orientations Ã— W_diagram Ã— H_diagram Ã— |E_template|)

For a typical SLD (1500Ã—800) with 40 template variants and ~100 edge pixels per template:
- ~1500 Ã— 800 Ã— 40 Ã— 100 = 4.8 billion operations
- With step=2: ~1.2 billion operations
- Feasible on modern CPU in minutes; parallelizable across scales

### 7.4.3 Score Map Aggregation (Stage 3c)

**Purpose**: Combine score maps across all (scale, orientation) variants to produce a single best-match map.

**Input**: All score maps and coverage maps from Stage 3b

**Output**:
- `best_score_map` â€” minimum Chamfer score at each position across all variants
- `best_scale_map` â€” scale that produced the best score at each position
- `best_orientation_map` â€” orientation that produced the best score
- `best_coverage_map` â€” coverage ratio at the best-scoring variant

**Algorithm**: For each position, retain the variant with the **minimum mean Chamfer distance**, subject to coverage ratio threshold:
```
For each (x, y):
    best_score = inf
    for each variant v:
        if coverage_map_v[y, x] >= MIN_COVERAGE and score_map_v[y, x] < best_score:
            best_score = score_map_v[y, x]
            best_scale = v.scale
            best_orientation = v.orientation
```

**MIN_COVERAGE threshold**: 0.65 â€” reject positions where fewer than 65% of template edges are within 2 pixels of a diagram edge. This prevents spurious low-distance matches in regions with only a few coincidental edge alignments.

### 7.4.4 Coverage Ratio Filtering (Stage 3d)

**Purpose**: Eliminate candidate positions with insufficient geometric evidence.

**Input**: `best_score_map`, `best_coverage_map`

**Output**: Filtered candidate list sorted by Chamfer distance

**Algorithm**: Retain only positions where:
1. `coverage_ratio >= 0.65`
2. `mean_chamfer_distance < MAX_DISTANCE` (e.g., 3.0 pixels)

---

## 7.5 Stage 4: Spatial Non-Maximum Suppression

### 7.5.1 Local Minima Extraction (Stage 4a)

**Purpose**: Identify spatially distinct score basins â€” positions that are local minima in the Chamfer score map.

**Input**: `best_score_map`

**Output**: List of candidate positions that are local minima

**Algorithm**:
1. Apply minimum filter with window size `W_nms` (e.g., 15Ã—15):
   `local_min = scipy.ndimage.minimum_filter(score_map, size=W_nms)`
2. Local minima are positions where `score_map[y,x] == local_min[y,x]`
3. Filter by coverage threshold

### 7.5.2 Greedy NMS (Stage 4b)

**Purpose**: Suppress duplicate detections from overlapping score basins.

**Input**: List of local minima with scores and coverage ratios

**Output**: Final detection list with duplicates removed

**Algorithm**:
```
Sort candidates by (mean_distance ASC, coverage_ratio DESC)
detections = []
for candidate in sorted_candidates:
    is_suppressed = False
    for existing in detections:
        dist = euclidean(candidate.position, existing.position)
        if dist < SUPPRESSION_RADIUS:
            is_suppressed = True
            break
    if not is_suppressed:
        detections.append(candidate)
```

**SUPPRESSION_RADIUS**: Set to `max(template_width, template_height) * best_scale` â€” approximately the size of the detected symbol. This ensures that two detections of the same symbol are merged, while adjacent symbols remain separate.

### 7.5.3 Ranked Detection List (Stage 4c)

Each detection contains:
- Position `(x, y)` â€” top-left corner of the bounding box
- Bounding box `(x, y, w, h)` â€” derived from template size at the best-matching scale
- Mean Chamfer distance
- Coverage ratio
- Best matching scale
- Best matching orientation
- Rank (1 = best match)

---

## 7.6 Stage 5: PCA Subspace Verification

### 7.6.1 Template Augmentation (Stage 5a)

**Purpose**: Generate a diverse set of augmented template views to construct a representative appearance manifold from a single reference.

**Input**: `template_binary` (161Ã—103)

**Output**: List of ~300â€“400 augmented binary template patches, all normalized to `PCA_TEMPLATE_SIZE` (e.g., 64Ã—64)

**Augmentation strategy**:
1. **Scale variations**: [0.90, 0.95, 1.00, 1.05, 1.10] â€” 5 levels
2. **Rotation variations**: [-5Â°, -3Â°, -1Â°, 0Â°, +1Â°, +3Â°, +5Â°] â€” 7 levels
3. **Morphological variations**: [erode_1, original, dilate_1] â€” 3 levels (simulates line thickness variation)
4. **Flip variations**: [original, horizontal_flip] â€” 2 levels
5. **Total**: 5 Ã— 7 Ã— 3 Ã— 2 = **210 base variants**
6. Each variant undergoes **centroid alignment** before inclusion

**Centroid alignment procedure**:
```
def center_foreground_centroid(binary_img, target_size=(64,64)):
    coords = np.argwhere(binary_img > 0)
    cy, cx = coords.mean(axis=0)
    # Translate so centroid is at image center
    ty = target_size[0]//2 - cy
    tx = target_size[1]//2 - cx
    M = np.float32([[1,0,tx],[0,1,ty]])
    aligned = cv2.warpAffine(binary_img, M, target_size)
    return aligned
```

**Mathematical justification**: Centroid alignment ensures PCA learns **structural variability** (scale, rotation, thickness) rather than **alignment variability** (translation offsets). This was identified as a critical robustness fix in prior work.

### 7.6.2 PCA Manifold Construction (Stage 5b)

**Purpose**: Build a low-dimensional appearance subspace from the augmented templates.

**Input**: List of augmented template patches (each flattened to a 1D vector of length 64Ã—64 = 4096)

**Output**: Fitted PCA model with `N_components` (e.g., 10â€“20)

**Algorithm**:
1. Stack all augmented patches into a data matrix `X` of shape `(N_augments, 4096)`
2. Center: `X_centered = X - X.mean(axis=0)`
3. Optionally whiten: normalize by singular values
4. Fit PCA: `pca = sklearn.decomposition.PCA(n_components=N_components, whiten=True)`
5. The principal components define the "MR symbol manifold"

**Explained variance diagnostic**: Check that the first 10 components explain â‰¥ 60% of variance. If explained variance is too low, the augmentation may be too aggressive; if too high, it may be insufficient.

### 7.6.3 Candidate Patch Extraction and Scoring (Stage 5c)

**Purpose**: Extract image patches at each NMS-surviving detection location and project them into the PCA subspace.

**Input**: Detection list from Stage 4, original diagram image

**Output**: PCA reconstruction error and similarity score per detection

**Algorithm**:
For each detection `(x, y, w, h, scale, orientation)`:
1. Extract patch from diagram: `patch = diagram_binary[y:y+h, x:x+w]`
2. Resize to `PCA_TEMPLATE_SIZE`: `patch_resized = cv2.resize(patch, (64,64))`
3. Apply centroid alignment: `patch_aligned = center_foreground_centroid(patch_resized)`
4. Flatten: `v = patch_aligned.flatten().astype(float)`
5. Project into PCA space: `z = pca.transform([v])[0]`
6. Reconstruct: `v_hat = pca.inverse_transform([z])[0]`
7. Reconstruction error: `RE = ||v - v_hat||Â²`
8. PCA similarity: `S_pca = exp(-RE / Ï„)` where `Ï„` is a calibration constant

### 7.6.4 Score Fusion and Re-ranking (Stage 5d)

**Purpose**: Combine geometric Chamfer scores with appearance PCA scores for final ranking.

**Input**: Chamfer scores and PCA similarities per detection

**Output**: Fused scores and re-ranked detection list

**Algorithm**:
1. Normalize Chamfer distances using exponential mapping:
   `S_chamfer = exp(-Î± Ã— mean_distance)` where `Î± = 2.0` (empirically calibrated)
2. Compute fused score:
   `S_fused = w_c Ã— S_chamfer + w_p Ã— S_pca`
   where `w_c = 0.7, w_p = 0.3` (empirically calibrated)
3. Re-rank detections by `S_fused` descending
4. Apply final threshold: retain detections with `S_fused > T_final`

**Mathematical justification for exponential normalization**: Linear Chamfer distances have a narrow dynamic range for well-matched candidates (e.g., 1.0 vs 1.5 vs 2.0). Exponential mapping amplifies these small differences, creating sufficient scoring gap for the PCA component to influence ranking.

---

## 7.7 Stage 6: Output Generation

### 7.7.1 Bounding Box Extraction

For each final detection, compute the bounding box:
```
bbox = (x, y, w_template * best_scale, h_template * best_scale)
```

Optionally add padding: `bbox_padded = (x-pad, y-pad, w+2*pad, h+2*pad)`

### 7.7.2 Visualization Overlays

Generate annotated images:
1. **Detection overlay**: Original SLD with green bounding boxes around detections, ranked labels
2. **Chamfer heatmap**: Color-coded score map showing geometric alignment quality
3. **Per-detection crops**: Individual cropped patches around each detection for inspection
4. **PCA comparison grid**: Template vs. candidate vs. reconstruction for each detection

### 7.7.3 Detection Metadata (JSON)

```json
{
  "sld_filename": "SLD1.png",
  "num_detections": 5,
  "detections": [
    {
      "rank": 1,
      "bbox": [331, 174, 83, 53],
      "chamfer_distance": 1.00,
      "coverage_ratio": 0.87,
      "pca_similarity": 0.07,
      "fused_score": 0.72,
      "best_scale": 0.25,
      "best_orientation": 0,
      "confidence": "high"
    }
  ],
  "pipeline_parameters": {
    "scale_range": [0.15, 0.40],
    "n_scales": 10,
    "orientations": [0, 90, 180, 270],
    "min_coverage": 0.65,
    "nms_radius": 40,
    "pca_components": 10,
    "fusion_weights": [0.7, 0.3]
  }
}
```

---

## 7.8 Multi-Template Ensemble Enhancement (Optional Stage)

### Purpose

Enhance recall by generating a small ensemble of template variants (scale, erosion/dilation, small rotations) and running independent Chamfer searches with each. The ensemble's score maps are aggregated via MIN (best score across templates at each position).

### Template Ensemble (7 variants)

1. Baseline (original edges)
2. 0.95Ã— scale
3. 1.05Ã— scale
4. Light erosion (simulates thinner lines)
5. Light dilation (simulates thicker lines)
6. -3Â° rotation
7. +3Â° rotation

### Aggregation

`ensemble_score[y,x] = min(score_v1[y,x], score_v2[y,x], ..., score_v7[y,x])`

### Expected Benefit

Recovers symbols that the baseline template fails to match due to minor geometric differences (line thickness, rendering artifacts, slight scale misalignment). Empirically validated to improve recall from 3/5 to 4â€“5/5 in prior work on a single SLD.

### Computational Cost

7Ã— the cost of single-template search. Feasible for 10 SLDs on modern CPU (estimated total: 10â€“30 minutes).


---

# SECTION 8 â€” IMPLEMENTATION PLAN

## 8.1 Repository Structure

```
Symbol Segmentor/
â”‚
â”œâ”€â”€ Data/
â”‚   â”œâ”€â”€ Symbol/
â”‚   â”‚   â””â”€â”€ MR_Symbol.png
â”‚   â””â”€â”€ SLDs/
â”‚       â”œâ”€â”€ SLD1.png
â”‚       â”œâ”€â”€ SLD2.png
â”‚       â”œâ”€â”€ SLD3.png
â”‚       â”œâ”€â”€ SLD4.png
â”‚       â”œâ”€â”€ SLD7.png
â”‚       â”œâ”€â”€ SLD8.png
â”‚       â”œâ”€â”€ SLD9.png
â”‚       â”œâ”€â”€ SLD10.png
â”‚       â”œâ”€â”€ SLD11.png
â”‚       â””â”€â”€ SLD12.png
â”‚
â”œâ”€â”€ src/
â”‚   â”œâ”€â”€ __init__.py
â”‚   â”œâ”€â”€ config.py              # All pipeline parameters (single source of truth)
â”‚   â”œâ”€â”€ preprocessing.py       # Stage 1: binarization, edge extraction, wire suppression
â”‚   â”œâ”€â”€ scale_pyramid.py       # Stage 2: multi-scale and multi-orientation template generation
â”‚   â”œâ”€â”€ chamfer_matching.py    # Stage 3: distance transform, sliding window, score maps
â”‚   â”œâ”€â”€ nms.py                 # Stage 4: local minima extraction, greedy NMS
â”‚   â”œâ”€â”€ pca_verification.py    # Stage 5: augmentation, PCA manifold, score fusion
â”‚   â”œâ”€â”€ ensemble.py            # Stage 5b (optional): multi-template ensemble
â”‚   â”œâ”€â”€ visualization.py       # All debug/output visualizations
â”‚   â””â”€â”€ utils.py               # I/O, logging, JSON serialization, image loading
â”‚
â”œâ”€â”€ evaluation/
â”‚   â”œâ”€â”€ __init__.py
â”‚   â”œâ”€â”€ ground_truth/          # Manual annotations (PASCAL VOC or COCO format)
â”‚   â”‚   â”œâ”€â”€ SLD1.xml
â”‚   â”‚   â”œâ”€â”€ SLD2.xml
â”‚   â”‚   â””â”€â”€ ...
â”‚   â”œâ”€â”€ metrics.py             # Precision, Recall, F1, IoU computation
â”‚   â”œâ”€â”€ evaluate.py            # Main evaluation script
â”‚   â””â”€â”€ ablation.py            # Ablation study runner
â”‚
â”œâ”€â”€ outputs/
â”‚   â”œâ”€â”€ template/              # Preprocessed template outputs
â”‚   â”œâ”€â”€ diagrams/              # Per-SLD detection outputs
â”‚   â”‚   â”œâ”€â”€ SLD1/
â”‚   â”‚   â”‚   â”œâ”€â”€ preprocessing/
â”‚   â”‚   â”‚   â”œâ”€â”€ chamfer_heatmaps/
â”‚   â”‚   â”‚   â”œâ”€â”€ nms_results/
â”‚   â”‚   â”‚   â”œâ”€â”€ pca_analysis/
â”‚   â”‚   â”‚   â”œâ”€â”€ detections/
â”‚   â”‚   â”‚   â””â”€â”€ detection_results.json
â”‚   â”‚   â””â”€â”€ ...
â”‚   â””â”€â”€ summary/               # Cross-SLD aggregate results
â”‚
â”œâ”€â”€ main.py                    # Main entry point â€” runs full pipeline on all SLDs
â”œâ”€â”€ requirements.txt           # Python dependencies
â”œâ”€â”€ config.yaml                # User-facing configuration file
â””â”€â”€ README.md                  # Project documentation
```

## 8.2 Module Breakdown

### 8.2.1 `src/config.py` â€” Configuration Constants

```python
# === PREPROCESSING ===
MEDIAN_KERNEL_SIZE = 3
ADAPTIVE_BLOCK_SIZE = 21
ADAPTIVE_C = 10
CANNY_LOW = 50
CANNY_HIGH = 150
WIRE_KERNEL_WIDTH = 50

# === SCALE PYRAMID ===
SCALE_MIN = 0.15
SCALE_MAX = 0.40
N_SCALES = 10
ORIENTATIONS = [0, 90, 180, 270]

# === CHAMFER MATCHING ===
COVERAGE_THRESHOLD_TAU = 2.0       # pixels
MIN_COVERAGE_RATIO = 0.65
MAX_CHAMFER_DISTANCE = 3.0
SLIDING_WINDOW_STEP = 2            # pixels

# === NMS ===
NMS_WINDOW_SIZE = 15
NMS_SUPPRESSION_RADIUS_FACTOR = 1.0  # Ã— template size

# === PCA VERIFICATION ===
PCA_TEMPLATE_SIZE = (64, 64)
PCA_N_COMPONENTS = 10
PCA_WHITEN = True
PCA_TAU = 2000.0
CHAMFER_ALPHA = 2.0
FUSION_WEIGHT_CHAMFER = 0.7
FUSION_WEIGHT_PCA = 0.3
FUSED_SCORE_THRESHOLD = 0.10

# === ENSEMBLE ===
ENSEMBLE_ENABLED = True
ENSEMBLE_SCALES = [0.95, 1.00, 1.05]
ENSEMBLE_ROTATIONS = [-3, 0, 3]
ENSEMBLE_MORPHOLOGIES = ['erode', 'original', 'dilate']
```

### 8.2.2 `src/preprocessing.py`

**Functions:**

| Function | Input | Output | Purpose |
|---|---|---|---|
| `load_image(path)` | File path | RGBA ndarray | Safe image loading with validation |
| `to_grayscale(img)` | RGBA/RGB ndarray | Grayscale ndarray | Channel conversion |
| `denoise(gray)` | Grayscale | Denoised grayscale | Median filtering |
| `binarize(gray)` | Grayscale | Binary (0/255) | Adaptive thresholding |
| `extract_edges(binary)` | Binary | Edge map (0/255) | Canny edge detection |
| `suppress_wires(binary)` | Binary | Binary (wires removed) | Morphological wire suppression |
| `preprocess_template(path)` | File path | Dict of all outputs | Full template pipeline |
| `preprocess_diagram(path)` | File path | Dict of all outputs | Full diagram pipeline |

### 8.2.3 `src/scale_pyramid.py`

**Functions:**

| Function | Input | Output | Purpose |
|---|---|---|---|
| `build_scale_pyramid(edges, scales)` | Edge map, scale list | List of (scale, scaled_edges) | Generate scale levels |
| `build_orientation_variants(edges)` | Edge map | List of (angle, rotated_edges) | Generate rotation variants |
| `build_full_pyramid(edges)` | Edge map | List of (scale, angle, edges, edge_coords) | Full scaleÃ—orientation pyramid |
| `extract_edge_coordinates(edges)` | Binary edge map | Nx2 ndarray of (row, col) | Edge pixel extraction |

### 8.2.4 `src/chamfer_matching.py`

**Functions:**

| Function | Input | Output | Purpose |
|---|---|---|---|
| `compute_distance_transform(edges)` | Edge map | Float32 DT image | DT computation |
| `chamfer_score_at_position(dt, edge_coords, tx, ty)` | DT, coords, position | (mean_dist, coverage) | Single-position score |
| `dense_chamfer_search(dt, edge_coords, step)` | DT, coords, step size | score_map, coverage_map | Full sliding window |
| `aggregate_multi_scale(score_maps)` | List of score maps | best_score, best_scale, best_orient | Cross-variant min |
| `filter_by_coverage(score_map, coverage_map)` | Maps, threshold | Filtered candidate list | Coverage filtering |

### 8.2.5 `src/nms.py`

**Functions:**

| Function | Input | Output | Purpose |
|---|---|---|---|
| `extract_local_minima(score_map, window)` | Score map, window size | Candidate list | Local minima detection |
| `greedy_nms(candidates, radius)` | Candidate list, radius | Filtered detections | Spatial suppression |
| `compute_bounding_boxes(detections, template_size, scales)` | Detections, size info | Bbox list | Bbox computation |

### 8.2.6 `src/pca_verification.py`

**Functions:**

| Function | Input | Output | Purpose |
|---|---|---|---|
| `center_foreground_centroid(binary, size)` | Binary patch, target size | Aligned patch | Centroid normalization |
| `generate_augmented_templates(template)` | Template binary | List of aligned patches | Augmentation pipeline |
| `build_pca_subspace(templates)` | List of patches | Fitted PCA model | PCA fitting |
| `extract_candidate_patches(diagram, detections)` | Diagram, detections | List of patches | Patch extraction |
| `compute_pca_scores(pca, patches)` | PCA model, patches | List of (recon_error, similarity) | PCA scoring |
| `fuse_and_rerank(detections)` | Detections with both scores | Re-ranked detections | Score fusion |

### 8.2.7 `src/visualization.py`

**Functions:**

| Function | Purpose |
|---|---|
| `save_preprocessing_overview(output_dir, results)` | Side-by-side preprocessing stages |
| `save_distance_transform_vis(output_dir, dt)` | Color-coded DT visualization |
| `save_chamfer_heatmap(output_dir, score_map)` | Chamfer score heatmap |
| `save_detection_overlay(output_dir, image, detections)` | Bounding boxes on original image |
| `save_detection_crops(output_dir, image, detections)` | Individual cropped patches |
| `save_pca_grid(output_dir, templates)` | Augmented template gallery |
| `save_pca_reconstruction(output_dir, original, reconstructed)` | PCA reconstruction comparison |
| `save_nms_overlay(output_dir, image, before, after)` | Pre/post NMS comparison |

## 8.3 Data Flow

```
main.py
  â”‚
  â”œâ”€ preprocess_template("Data/Symbol/MR_Symbol.png")
  â”‚   â””â”€ returns: template_results {gray, binary, edges, stats}
  â”‚
  â”œâ”€ build_full_pyramid(template_results.edges)
  â”‚   â””â”€ returns: pyramid [(scale, angle, edges, coords), ...]
  â”‚
  â”œâ”€ generate_augmented_templates(template_results.binary)
  â”‚   â””â”€ returns: augmented_patches [aligned_64x64, ...]
  â”‚
  â”œâ”€ build_pca_subspace(augmented_patches)
  â”‚   â””â”€ returns: pca_model (sklearn PCA)
  â”‚
  â””â”€ FOR EACH SLD in Data/SLDs/:
      â”‚
      â”œâ”€ preprocess_diagram(sld_path)
      â”‚   â””â”€ returns: diagram_results {gray, binary, edges, edges_no_wire, stats}
      â”‚
      â”œâ”€ compute_distance_transform(diagram_results.edges_no_wire)
      â”‚   â””â”€ returns: DT (float32 image)
      â”‚
      â”œâ”€ FOR EACH (scale, angle, template_edges, template_coords) in pyramid:
      â”‚   â””â”€ dense_chamfer_search(DT, template_coords, step=2)
      â”‚       â””â”€ returns: score_map, coverage_map
      â”‚
      â”œâ”€ aggregate_multi_scale(all_score_maps)
      â”‚   â””â”€ returns: best_score_map, best_scale_map, best_orient_map
      â”‚
      â”œâ”€ extract_local_minima(best_score_map, window=15)
      â”‚   â””â”€ returns: raw_candidates
      â”‚
      â”œâ”€ greedy_nms(raw_candidates, radius=template_size*scale)
      â”‚   â””â”€ returns: nms_detections
      â”‚
      â”œâ”€ extract_candidate_patches(diagram_binary, nms_detections)
      â”‚   â””â”€ returns: candidate_patches
      â”‚
      â”œâ”€ compute_pca_scores(pca_model, candidate_patches)
      â”‚   â””â”€ returns: pca_scores
      â”‚
      â”œâ”€ fuse_and_rerank(nms_detections, pca_scores)
      â”‚   â””â”€ returns: final_detections
      â”‚
      â””â”€ save_all_outputs(output_dir, final_detections, visualizations)
```

## 8.4 Configuration File (`config.yaml`)

```yaml
data:
  symbol_path: "Data/Symbol/MR_Symbol.png"
  sld_directory: "Data/SLDs/"
  output_directory: "outputs/"

preprocessing:
  median_kernel: 3
  adaptive_blocksize: 21
  adaptive_c: 10
  canny_low: 50
  canny_high: 150
  wire_kernel_width: 50

matching:
  scale_min: 0.15
  scale_max: 0.40
  n_scales: 10
  orientations: [0, 90, 180, 270]
  coverage_tau: 2.0
  min_coverage: 0.65
  max_distance: 3.0
  step_size: 2

nms:
  window_size: 15
  suppression_radius_factor: 1.0

pca:
  template_size: [64, 64]
  n_components: 10
  whiten: true
  tau: 2000.0
  chamfer_alpha: 2.0
  weight_chamfer: 0.7
  weight_pca: 0.3
  score_threshold: 0.10

ensemble:
  enabled: true
  n_templates: 7

visualization:
  save_heatmaps: true
  save_crops: true
  save_overlays: true
  save_pca_diagnostics: true
```

## 8.5 Dependencies (`requirements.txt`)

```
opencv-python>=4.8.0
numpy>=1.24.0
scipy>=1.10.0
scikit-learn>=1.3.0
scikit-image>=0.21.0
matplotlib>=3.7.0
pyyaml>=6.0
```

---

# SECTION 9 â€” EVALUATION STRATEGY

## 9.1 Ground Truth Creation Protocol

### 9.1.1 Annotation Format

Use **PASCAL VOC XML format** for bounding box annotations. Each SLD gets one XML file:

```xml
<annotation>
  <filename>SLD1.png</filename>
  <size>
    <width>1544</width>
    <height>382</height>
  </size>
  <object>
    <name>MR_Symbol</name>
    <bndbox>
      <xmin>325</xmin>
      <ymin>168</ymin>
      <xmax>370</xmax>
      <ymax>200</ymax>
    </bndbox>
  </object>
  <!-- ... more objects ... -->
</annotation>
```

### 9.1.2 Annotation Procedure

1. **Annotator**: Domain expert with power systems engineering knowledge
2. **Tool**: LabelImg or CVAT (open-source annotation tools)
3. **Bounding box definition**: Tight bounding box around the MR symbol body (semicircular lobes + base bar + stem + cap). Excludes connected bus conductor. Excludes text labels.
4. **Labeling rule**: Annotate EVERY visible MR/CT symbol, including partially visible ones at edges (marked with `difficult=1`)
5. **Quality check**: Two independent annotations, resolve disagreements by consensus

### 9.1.3 Expected Annotation Effort

| Item | Estimate |
|---|---|
| SLDs to annotate | 10 |
| Estimated total symbols | ~138 |
| Time per symbol | ~10 seconds |
| Total annotation time | ~25 minutes |
| Quality review | ~15 minutes |
| **Total effort** | **~40 minutes** |

## 9.2 Metrics

### 9.2.1 Detection Metrics (per-SLD and aggregate)

| Metric | Formula | Threshold |
|---|---|---|
| **True Positive (TP)** | Detection with IoU â‰¥ 0.50 against any GT box | IoU â‰¥ 0.50 |
| **False Positive (FP)** | Detection with no GT box having IoU â‰¥ 0.50 | â€” |
| **False Negative (FN)** | GT box with no detection having IoU â‰¥ 0.50 | â€” |
| **Precision** | TP / (TP + FP) | â€” |
| **Recall** | TP / (TP + FN) | â€” |
| **F1-Score** | 2 Ã— (P Ã— R) / (P + R) | â€” |

### 9.2.2 Localization Metrics

| Metric | Formula | Description |
|---|---|---|
| **IoU** | area(det âˆ© gt) / area(det âˆª gt) | Per-detection localization quality |
| **Mean IoU** | average IoU across all TPs | Overall localization precision |
| **Centroid Error** | â€–center(det) - center(gt)â€–â‚‚ | Pixel-level position accuracy |
| **Mean Centroid Error** | average centroid error across TPs | Overall positioning accuracy |

### 9.2.3 Score Distribution Metrics

| Metric | Description |
|---|---|
| **Score gap** | Difference between lowest TP score and highest FP score |
| **Score separability** | AUC of TP vs FP score distributions |
| **Threshold stability** | Range of thresholds that maintain F1 â‰¥ 0.85 |

## 9.3 False Positive Analysis

For every FP detection, record:
1. **Position** in the SLD
2. **What structure was detected** (G/B box, VT element, text, conductor junction, etc.)
3. **Chamfer score** â€” how geometrically similar was it?
4. **PCA score** â€” did PCA correctly assign low similarity?
5. **Failure stage** â€” where in the pipeline should this FP have been rejected?

Classify FPs into categories:
- **Geometric FP**: Structurally similar symbol (G/B, VT) â€” requires stronger PCA discrimination
- **Clutter FP**: Random edge alignment â€” requires stricter coverage threshold
- **Scale FP**: Wrong-scale match â€” requires tighter scale bounds
- **NMS failure**: Duplicate of a TP â€” requires NMS radius tuning

## 9.4 False Negative Analysis

For every FN, record:
1. **Position** in the SLD
2. **Why was it missed?**
   - Scale out of search range
   - Orientation not searched
   - Chamfer score too high (poor edge alignment)
   - Coverage ratio too low
   - Suppressed by NMS (merged with a neighboring detection)
   - PCA rejected (reconstruction error too high)
3. **Best-matching score at the GT location** â€” was there a local minimum, just not strong enough?

## 9.5 Ablation Studies

| Experiment | Variable | Expected Insight |
|---|---|---|
| **No wire suppression** | Wire suppression ON vs OFF | Quantify impact of wire removal on Chamfer precision |
| **Single scale vs multi-scale** | 1 scale vs 10 scales | Quantify recall gain from multi-scale search |
| **Single orientation vs multi** | 0Â° only vs {0,90,180,270} | Quantify recall gain on SLD11 |
| **Chamfer only vs Chamfer+PCA** | PCA OFF vs ON | Quantify FP reduction from PCA verification |
| **Fusion weight sweep** | w_c from 0.0 to 1.0 | Find optimal Chamfer/PCA balance |
| **Coverage threshold sweep** | MIN_COVERAGE from 0.5 to 0.9 | Precision/recall trade-off |
| **NMS radius sweep** | Radius from 0.5Ã— to 2.0Ã— template size | Under/over-suppression analysis |
| **Ensemble vs single template** | Ensemble OFF vs ON | Recall improvement from multi-template |
| **PCA components sweep** | N from 5 to 30 | Reconstruction quality vs overfitting |

## 9.6 Benchmark Comparisons

| Baseline | Description | Purpose |
|---|---|---|
| **Multi-scale NCC** | OpenCV `matchTemplate` with TM_CCOEFF_NORMED | Pixel-domain baseline |
| **Single-scale Chamfer** | Chamfer at one fixed scale | Ablation of multi-scale |
| **Chamfer without PCA** | Full pipeline minus Stage 5 | Ablation of PCA |
| **Full pipeline** | All stages enabled | Target performance |
| **Human performance** | Manual annotation agreement | Upper bound |

## 9.7 Evaluation Script Output

The evaluation script (`evaluation/evaluate.py`) produces:

```json
{
  "aggregate": {
    "total_gt": 138,
    "total_detections": 142,
    "true_positives": 130,
    "false_positives": 12,
    "false_negatives": 8,
    "precision": 0.915,
    "recall": 0.942,
    "f1_score": 0.929,
    "mean_iou": 0.72,
    "mean_centroid_error_px": 3.2
  },
  "per_sld": {
    "SLD1": {"gt": 6, "det": 6, "tp": 6, "fp": 0, "fn": 0, "p": 1.0, "r": 1.0},
    "SLD2": {"gt": 24, "det": 25, "tp": 23, "fp": 2, "fn": 1, "p": 0.92, "r": 0.96},
    ...
  },
  "false_positive_analysis": [...],
  "false_negative_analysis": [...]
}
```

> **Note**: The aggregate metrics shown above are **projected estimates**, not measured values. Actual performance requires ground truth annotation and empirical evaluation. These projections are based on prior work achieving 3/5 detection on a single SLD with the baseline Chamfer pipeline, with significant improvement expected from multi-scale, multi-orientation, and PCA refinement.


---

# SECTION 10 â€” RISK ANALYSIS

## 10.1 Technical Risks

| # | Risk | Probability | Impact | Mitigation |
|---|---|---|---|---|
| T1 | **Chamfer score ambiguity**: G/B boxes or VT elements produce Chamfer scores indistinguishable from true MR symbols | Medium | High | PCA verification stage provides orthogonal discrimination signal. Empirically validated to suppress G/B FPs with exponential normalization (Î±=2.0) |
| T2 | **Scale estimation failure**: The 4â€“6Ã— scale ratio is incorrectly estimated, causing the scale pyramid to miss the true symbol size | Low | Critical | Use a wide scale range (0.15â€“0.40) with 10 levels. Validate on SLD4 (cleanest SLD) first to calibrate the range |
| T3 | **NMS over-suppression**: Adjacent MR symbols in dense bus sections (SLD7) are merged into a single detection | Medium | High | Set NMS suppression radius conservatively (1.0Ã— template size at detected scale). Validate on SLD2/SLD7 which have the densest packing |
| T4 | **Computational timeout**: Dense sliding window on large SLDs (SLD7: 1.5M pixels Ã— 40 variants) exceeds acceptable runtime | Medium | Medium | Use step=2, coarse-to-fine search, early termination. Parallelize across scales. Budget ~3 minutes per SLD |
| T5 | **Wire suppression over-aggressiveness**: Horizontal morphological opening removes vertical symbol elements alongside bus conductors | Low | Medium | Wire suppression uses a wide horizontal kernel (50+ pixels). MR symbols are much narrower than this threshold. Verify with preprocessing diagnostics |
| T6 | **Anti-aliasing artifacts**: Grayscale anti-aliasing on symbol edges produces weak/thick Canny edges that differ between template and diagram | Low | Low | Median filtering smooths anti-aliasing. Adaptive thresholding handles gradual intensity transitions. Coverage ratio (Ï„=2.0) provides tolerance |

## 10.2 Dataset Risks

| # | Risk | Probability | Impact | Mitigation |
|---|---|---|---|---|
| D1 | **SLD9 anomaly**: The visually different rendering style of SLD9 causes systematic scale or geometric mismatch | Medium-High | High | Extend scale range if needed. Run SLD9 as a separate diagnostic case. May require additional scale levels or template thickness variants |
| D2 | **SLD11 rotation failure**: 90Â° rotated symbols are missed because the rotation search is insufficient | Low | High | Explicitly include 90Â° (and 270Â°) in the orientation search. SLD11 serves as the validation case for rotation handling |
| D3 | **Ground truth creation bias**: Manual annotations are inconsistent or incomplete, undermining evaluation validity | Medium | High | Use two independent annotators. Define clear annotation rules (tight bbox, exclude text, exclude bus). Resolve disagreements by consensus |
| D4 | **Unknown symbol count**: The estimated ~138 total occurrences may be significantly wrong (could be 80 or 200) | Medium | Medium | Ground truth annotation is the mitigation. Estimates are clearly labeled as such in this PRD |
| D5 | **Missing SLDs**: SLD5 and SLD6 are absent from the dataset. These may contain symbol configurations not represented in the available 10 SLDs | Low | Low | The 10 available SLDs cover diverse topologies (single bus, double bus, vertical, sparse, dense). Missing SLDs are unlikely to introduce fundamentally new challenges |

## 10.3 Algorithmic Risks

| # | Risk | Probability | Impact | Mitigation |
|---|---|---|---|---|
| A1 | **PCA manifold collapse**: Augmented templates are too similar, causing PCA to capture insufficient variance (explained variance < 50%) | Low | Medium | Monitor explained variance diagnostic. If collapse occurs, increase augmentation diversity (add noise, wider rotation range, more morphological variants) |
| A2 | **Chamfer-PCA fusion instability**: The 0.7/0.3 fusion weights calibrated on prior work may not generalize to all 10 SLDs | Medium | Medium | Run the fusion weight sweep ablation on all 10 SLDs. If weights need per-SLD tuning, this violates the "no manual tuning" constraint â†’ investigate adaptive weighting |
| A3 | **Coverage ratio threshold sensitivity**: MIN_COVERAGE=0.65 may be too strict (missing true symbols) or too lenient (admitting false positives) | Medium | Medium | Run coverage threshold sweep ablation. Plot precision/recall curve as a function of coverage threshold |
| A4 | **Multi-template ensemble introduces new FPs**: Ensemble variants (eroded/dilated templates) match non-MR symbols better than the baseline | Low | Medium | Track per-template attribution: if a template variant produces new detections, verify they are TPs. Disable pathological variants |

## 10.4 Scalability Risks

| # | Risk | Probability | Impact | Mitigation |
|---|---|---|---|---|
| S1 | **Larger SLD corpus**: Scaling from 10 to 100+ SLDs increases computational cost proportionally | High (if project succeeds) | Medium | Computational cost is linear in the number of SLDs. No architectural redesign needed. Parallelize across SLDs using multiprocessing |
| S2 | **Higher resolution SLDs**: Future SLDs at 4000Ã—2000+ pixels quadruple the per-SLD search cost | Medium | High | Implement coarse-to-fine search: run at 0.5Ã— resolution first, refine around candidate regions at full resolution |
| S3 | **Multiple symbol types**: Extension to detect 5â€“10 different symbol types simultaneously | High (logical next step) | High | Current architecture handles one symbol type. Multi-symbol detection requires running the pipeline per-symbol or redesigning for multi-class matching. Consider shared preprocessing, per-class templates |

## 10.5 Maintenance Risks

| # | Risk | Probability | Impact | Mitigation |
|---|---|---|---|---|
| M1 | **Parameter drift**: New SLD batches from different drawing conventions require parameter re-tuning | Medium | Medium | Externalize all parameters to config.yaml. Document which parameters are drawing-convention-dependent vs universal |
| M2 | **Dependency updates**: OpenCV, scikit-learn, or NumPy API changes break the pipeline | Low | Medium | Pin dependency versions in requirements.txt. Use only stable, well-documented APIs |
| M3 | **Knowledge loss**: The pipeline's design rationale is lost when the original developer moves on | Medium | High | This PRD serves as the primary knowledge document. All design decisions are justified. Code must include inline comments linking to PRD sections |

---

# SECTION 11 â€” FUTURE ROADMAP

## Phase 1: MVP (Weeks 1â€“2)

**Objective**: End-to-end pipeline producing bounding boxes on all 10 SLDs.

**Deliverables**:
- Preprocessing module (template + diagram)
- Single-scale Chamfer matching at one estimated scale
- Basic NMS
- Detection overlays for visual inspection
- Per-SLD detection JSON files

**Success criteria**: Pipeline runs end-to-end without crashes. Visual inspection shows detections near true MR symbols on at least 5/10 SLDs.

## Phase 2: Multi-Scale Matching (Weeks 3â€“4)

**Objective**: Scale-invariant detection across all SLDs.

**Deliverables**:
- Scale pyramid generation (10 levels)
- Multi-orientation search (0Â°, 90Â°, 180Â°, 270Â°)
- Scale-aware NMS with adaptive suppression radius
- Coverage ratio filtering
- Chamfer heatmap visualizations

**Success criteria**: Detections on 8/10 SLDs including SLD11 (rotated). Recall > 0.70.

## Phase 3: PCA Verification (Weeks 5â€“6)

**Objective**: Suppress structured false positives using appearance manifold verification.

**Deliverables**:
- One-shot template augmentation pipeline
- PCA manifold construction with centroid alignment
- Score fusion with exponential normalization
- Re-ranking and final thresholding
- PCA diagnostics (variance spectrum, reconstruction examples)

**Success criteria**: Precision improves from ~0.70 to ~0.85+ while maintaining recall. G/B false positives suppressed.

## Phase 4: Multi-Template Ensemble (Weeks 7â€“8)

**Objective**: Improve recall by expanding geometric coverage with template variants.

**Deliverables**:
- 7-template ensemble generation
- MIN-aggregated score maps
- Per-template attribution diagnostics
- New minima emergence tracking

**Success criteria**: Recall improves to > 0.85. New true detections emerge from template variants that the baseline misses.

## Phase 5: Ground Truth and Rigorous Evaluation (Weeks 9â€“10)

**Objective**: Create ground truth annotations and perform rigorous quantitative evaluation.

**Deliverables**:
- PASCAL VOC annotations for all 10 SLDs
- Automated evaluation script (precision, recall, F1, IoU)
- False positive/negative analysis reports
- Ablation study results (wire suppression, scale, orientation, PCA, ensemble)
- Benchmark comparison table

**Success criteria**: F1 â‰¥ 0.87 with mean IoU â‰¥ 0.50. All failure modes documented.

## Phase 6: Pseudo-Label Generation and Active Refinement (Weeks 11â€“14)

**Objective**: Use high-confidence detections as pseudo-labels to refine the pipeline.

**Deliverables**:
- Confidence calibration: classify detections as high/medium/low confidence
- Pseudo-label export for potential supervised fine-tuning
- Hard negative mining: systematically collect FP examples for analysis
- Adaptive threshold selection per-SLD based on score distribution

**Success criteria**: Self-consistent pipeline where high-confidence detections can bootstrap evaluation without manual annotation.

## Phase 7: Deep Learning Transition (If Justified) (Months 4â€“6)

**Objective**: Evaluate whether deep learning can improve upon the classical pipeline.

**Prerequisites**: This phase should ONLY be pursued if:
1. Ground truth annotations exist for all 10 SLDs (~138+ labeled bounding boxes)
2. The classical pipeline has reached its performance ceiling (documented ablation studies)
3. Additional SLDs can be obtained to increase the training set

**Potential approaches**:
- **Siamese matching network**: Train on pseudo-labeled crops from the classical pipeline
- **Fine-tuned object detector**: Use the 10 annotated SLDs with aggressive augmentation for a small-data regime YOLO/EfficientDet
- **Self-supervised pretraining**: Pre-train on engineering drawing patches, then fine-tune for symbol detection

**Critical constraint**: The deep learning system must demonstrably outperform the classical pipeline on the same evaluation metrics. If it does not, the classical pipeline remains the production system.

---

# SECTION 12 â€” FINAL RECOMMENDATION

## 12.1 Recommended Architecture

**Multi-Scale Multi-Orientation Chamfer Matching with PCA Subspace Verification**

A 6-stage classical computer vision pipeline:

```
Preprocessing â†’ Scale/Orientation Pyramid â†’ Dense Chamfer Localization
     â†’ Spatial NMS â†’ PCA Verification â†’ Output Generation
```

## 12.2 Why It Is Optimal

1. **Data-appropriate**: Designed for the actual constraints (1 template, 10 diagrams, 0 annotations).
2. **Edge-domain native**: Operates in the natural representation space of binary engineering drawings.
3. **Empirically grounded**: Core components (Chamfer matching, PCA verification, NMS) have been implemented and tested on similar MR symbols in prior work.
4. **Deterministic**: No stochastic components. Bit-for-bit reproducible.
5. **Explainable**: Every detection has a traceable geometric score, coverage ratio, PCA similarity, and fused confidence.
6. **CPU-efficient**: Runs on standard hardware without GPU requirements.
7. **Incrementally improvable**: Each stage can be independently tuned and verified.

## 12.3 Expected Strengths

| Strength | Evidence |
|---|---|
| High recall on standard-orientation SLDs | Chamfer matching + multi-scale search covers the dominant 0Â° orientation across 9/10 SLDs |
| Effective FP suppression | PCA verification empirically suppresses G/B breaker false positives |
| Scale robustness | 10-level scale pyramid covers the observed 3â€“6Ã— scale range |
| Rotation handling | 4-orientation search covers both horizontal and vertical symbol placements |
| Dense symbol discrimination | Coverage ratio filtering + NMS handles packed bus sections |

## 12.4 Expected Weaknesses

| Weakness | Severity | Mitigation Path |
|---|---|---|
| SLD9 rendering anomaly may require extra calibration | Medium | Extend scale range; add morphological template variants |
| Computational cost for large SLDs (~3 min/SLD) | Low | Coarse-to-fine search; parallelization |
| Parameter sensitivity (coverage threshold, NMS radius) | Medium | Ablation studies to find robust operating point |
| No automatic threshold selection | Medium | Score distribution analysis; Otsu-like auto-thresholding on fused scores |
| Requires manual ground truth for rigorous evaluation | Medium | One-time ~40 minute annotation effort |

## 12.5 Expected Detection Performance

> **Disclaimer**: The following are informed projections, NOT measured results. Actual performance requires ground truth annotation and empirical evaluation.

| Metric | Projected Range | Basis |
|---|---|---|
| **Precision** | 0.82 â€“ 0.92 | PCA verification suppresses most structured FPs; residual FPs from dense regions |
| **Recall** | 0.85 â€“ 0.95 | Multi-scale + multi-orientation + ensemble covers most symbol configurations; potential misses on SLD9 |
| **F1-Score** | 0.84 â€“ 0.93 | Balanced by multi-stage pipeline |
| **Mean IoU** | 0.60 â€“ 0.75 | Scale estimation accuracy limits IoU; bounding boxes may be slightly larger or smaller than GT |
| **Per-SLD worst case** | Recall â‰¥ 0.70 | Anticipated on SLD9 (rendering anomaly) or SLD7 (extreme density) |

## 12.6 Research Value

This project demonstrates several principles of significant research value:

1. **Classical methods remain competitive**: For structured document analysis with clean inputs and low data availability, principled classical CV outperforms data-hungry deep learning.
2. **One-shot symbol spotting**: The entire pipeline bootstraps from a single reference image, proving that one-shot geometric matching is viable for industrial applications.
3. **Hybrid architecture validation**: The Chamfer (geometric) + PCA (appearance) combination demonstrates how orthogonal verification signals can be combined for robust detection.
4. **Empirical methodology**: The staged development approach (preprocessing â†’ proposal â†’ matching â†’ verification â†’ calibration â†’ ensemble) provides a rigorous template for future CV research projects.
5. **Anti-hallucination engineering**: Every design decision is grounded in observed data characteristics, not assumed performance.

## 12.7 Industrial Value

| Dimension | Value |
|---|---|
| **Automation potential** | Reduces manual symbol counting from hours to minutes |
| **Accuracy** | Projected to match or exceed human counting accuracy on clean SLDs |
| **Consistency** | Deterministic â€” eliminates inter-operator variability |
| **Scalability** | Linear cost in number of SLDs; parallelizable |
| **Explainability** | Every detection is auditable â€” critical for engineering compliance |
| **Deployment simplicity** | Python-only, CPU-only, no GPU infrastructure required |
| **Extensibility** | Architecture supports additional symbol types via per-symbol templates |
| **Integration readiness** | JSON output format compatible with downstream engineering databases |

## 12.8 Closing Statement

This PRD was created after a comprehensive forensic analysis of every image in the dataset. Every architectural decision â€” from the selection of Chamfer matching over NCC, to the rejection of YOLO and Siamese networks, to the specific PCA fusion calibration â€” is grounded in observed dataset characteristics and, where available, empirical validation from prior work on the same engineering domain.

The recommended pipeline is not the most modern approach. It is not the most exciting approach. It is the **correct** approach for this specific problem, this specific dataset, and these specific constraints.

The dominant challenge is not image quality â€” these are clean, high-contrast engineering drawings. The dominant challenge is **geometric discrimination** â€” distinguishing the MR symbol from other symbols that share geometric sub-primitives. The recommended architecture directly addresses this challenge through a principled hierarchy of geometric matching (Chamfer), spatial consolidation (NMS), and semantic verification (PCA).

Implementation can begin immediately using this document as the architectural specification.

