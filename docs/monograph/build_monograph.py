"""
Monograph Concatenation Script
Combines all individual chapter files into a single master document.
"""

import os

MONOGRAPH_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)))
OUTPUT_FILE = os.path.join(MONOGRAPH_DIR, "MASTER_MONOGRAPH.md")

# Ordered list of chapter files
CHAPTERS = [
    "chapter_01_introduction.md",
    "chapter_02_literature_review.md",
    "chapter_03_architecture_selection.md",
    "chapter_04_pipeline_design.md",
    "chapter_05_implementation.md",
    "chapter_06_template_bank.md",
    "chapter_07_08_chamfer_and_coverage.md",
    "chapter_09_structural_verification.md",
    "chapter_10_11_12_integration_cascades_nms.md",
    "chapter_13_14_15_benchmark_failures_conclusions.md",
]

TITLE_PAGE = """---

# Circuit Symbol Localization in Industrial Single Line Diagrams:
# A Multi-Scale Chamfer Matching and PCA Verification Pipeline

## Technical Research Monograph

---

**Author**: Arhaansh Jhingan  
**Company**: Larsen and Toubro  
**Date**: June 2026  
**Document Type**: Industrial R&D Technical Research Monograph  
**Pipeline Status**: Stage 5.10 (Verification Cascades) — Stage 6 NOT REACHED  

---

## Abstract

This monograph documents the complete research study for the localization of Current Transformer (MR) symbols across 10 industrial Single Line Diagrams (SLDs) using a one-shot, deterministic, classical computer vision pipeline. The pipeline architecture — Multi-Scale Chamfer Matching with PCA Subspace Verification — was selected through a systematic trade study evaluating 23 candidate detection methodologies against the constraints of one-shot operation, binary line-drawing domains, CPU-only computation, and full determinism.

The research produced several significant contributions: (1) **Method D3** (Coordinate Scaling + Anti-Aliased Rasterization), which resolves the catastrophic template degradation problem at small scales where naive downsampling produces empty images; (2) the **separability-ranking paradox**, documenting that a structural feature achieving AUC=0.951 for population-level discrimination produces zero ranking improvement when integrated as a continuous score modifier; (3) empirical proof that **coverage ratio is mathematically redundant** with Chamfer score (r ≈ −0.90) and exhibits an inverted distribution relative to expectations; and (4) a comprehensive **architecture trade study** providing explicit rejection rationale for deep learning methods (YOLO, Faster R-CNN, DETR, Siamese networks) in the one-shot line-drawing regime.

The pipeline successfully localizes true MR symbols in the candidate pool (detection recall > 95% at full depth) but fails to rank them above structurally similar false positives (median MR rank = 573, Top-100 hit rate = 5.8%). The project terminated at Stage 5.10, having never passed the Stage 6 readiness gate after two consecutive gate evaluations. Five architectural dead ends (connected-component isolation, Method A template generation, coverage independence, continuous structural integration, ranking remediation experiments) and three persistent blockers (small-symbol detection, ranking inversion, hard negative irreducibility) are forensically documented with complete traceability to repository artifacts.

**Keywords**: Symbol localization, Chamfer matching, template matching, one-shot detection, single line diagrams, edge-domain analysis, distance transforms, structural verification, engineering drawing analysis

---

## Table of Contents

1. [Introduction](#chapter-1--introduction)
2. [Literature Review](#chapter-2--literature-review)
3. [Architecture Selection](#chapter-3--architecture-selection)
4. [Pipeline Design](#chapter-4--pipeline-design)
5. [Implementation](#chapter-5--implementation)
6. [Template Bank Investigation](#chapter-6--template-bank-investigation)
7. [Chamfer Matching and Candidate Generation](#chapter-7--chamfer-matching-and-candidate-generation)
8. [Coverage Rescoring](#chapter-8--coverage-rescoring)
9. [Structural Verification and Discriminator Discovery](#chapter-9--structural-verification-and-discriminator-discovery)
10. [Discriminator Integration Experiments](#chapter-10--discriminator-integration-experiments)
11. [Verification Cascades and Visual Audit](#chapter-11--verification-cascades-and-visual-audit)
12. [Non-Maximum Suppression Diagnostic Evaluation](#chapter-12--non-maximum-suppression-diagnostic-evaluation)
13. [Unified Pipeline Benchmark](#chapter-13--unified-pipeline-benchmark)
14. [Failure Analysis and Lessons Learned](#chapter-14--failure-analysis-and-lessons-learned)
15. [Conclusions, Open Problems, and Future Directions](#chapter-15--conclusions-open-problems-and-future-directions)

---

"""

def concatenate():
    """Concatenate all chapter files into the master document."""
    
    # Verify all chapters exist
    missing = []
    for ch in CHAPTERS:
        path = os.path.join(MONOGRAPH_DIR, ch)
        if not os.path.exists(path):
            missing.append(ch)
    
    if missing:
        print("ERROR: Missing chapter files:")
        for m in missing:
            print(f"  - {m}")
        return False
    
    # Build master document
    with open(OUTPUT_FILE, "w", encoding="utf-8") as out:
        # Write title page
        out.write(TITLE_PAGE)
        
        # Write each chapter
        for i, ch in enumerate(CHAPTERS):
            path = os.path.join(MONOGRAPH_DIR, ch)
            with open(path, "r", encoding="utf-8") as f:
                content = f.read()
            
            out.write(content)
            out.write("\n\n---\n\n")  # Chapter separator
            
            print(f"  [{i+1}/{len(CHAPTERS)}] Included: {ch}")
    
    # Report
    file_size = os.path.getsize(OUTPUT_FILE)
    with open(OUTPUT_FILE, "r", encoding="utf-8") as f:
        line_count = sum(1 for _ in f)
    
    print(f"\n{'='*60}")
    print(f"MASTER MONOGRAPH GENERATED SUCCESSFULLY")
    print(f"{'='*60}")
    print(f"  Output: {OUTPUT_FILE}")
    print(f"  Chapters: {len(CHAPTERS)}")
    print(f"  Total Lines: {line_count:,}")
    print(f"  File Size: {file_size:,} bytes ({file_size/1024:.1f} KB)")
    print(f"  Estimated Pages: {line_count // 45}")
    
    return True

if __name__ == "__main__":
    concatenate()
