import os
import sys
import csv
import json
import math
import numpy as np
import cv2
from datetime import datetime
from collections import defaultdict

BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
REPORTS_DIR = os.path.join(BASE_DIR, "reports")
OUTPUTS_DIR = os.path.join(BASE_DIR, "outputs")
CANDIDATES_DIR = os.path.join(OUTPUTS_DIR, "candidates")
DT_DIR = os.path.join(OUTPUTS_DIR, "distance_transforms")
DIAGRAMS_DIR = os.path.join(OUTPUTS_DIR, "diagrams")
TEMPLATE_BANK_DIR = os.path.join(OUTPUTS_DIR, "template_bank")
VISUALS_DIR = os.path.join(OUTPUTS_DIR, "stage4_visualizations")

TIMESTAMP = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
TEMPLATE_BANK_VERSION = "Stage2_D3_v1"
CANDIDATE_DATASET_SOURCE = "outputs/candidates/ranked_candidates.csv"
COVERAGE_METHOD_SOURCE = "Stage 3.5"
NORMALIZATION_METHOD_SOURCE = "Stage 3.6"
MANIFEST_VERSION = "outputs/template_bank/template_bank_manifest.csv"

def get_traceability_header(count_before, count_after, sld_count):
    return f"""<!-- Traceability Header -->
- **Generation Timestamp**: {TIMESTAMP}
- **Template Bank Version**: {TEMPLATE_BANK_VERSION}
- **Stage 3 Candidate Source**: {CANDIDATE_DATASET_SOURCE}
- **Coverage Method Source**: {COVERAGE_METHOD_SOURCE}
- **Normalization Method Source**: {NORMALIZATION_METHOD_SOURCE}
- **Manifest Version**: {MANIFEST_VERSION}
- **Candidate Count Before Rescoring**: {count_before}
- **Candidate Count After Rescoring**: {count_after}
- **SLD Count**: {sld_count}
- **Investigation Type**: Operational Rescoring
<!-- End Traceability Header -->

"""

def phase_4a_input_validation():
    required = [
        os.path.join(CANDIDATES_DIR, "ranked_candidates.csv"),
        DT_DIR,
        os.path.join(TEMPLATE_BANK_DIR, "template_bank_manifest.csv"),
        os.path.join(REPORTS_DIR, "coverage_metrics_dataset.csv"),
        os.path.join(REPORTS_DIR, "stage4_feasibility_assessment.md")
    ]
    missing = []
    for req in required:
        if not os.path.exists(req):
            missing.append(req)
            
    if missing:
        content = f"""# Precondition Check Failure: Missing Dependencies

> [!CAUTION]
> Stage 4 has been terminated due to missing required input artifacts.

- **Generation Time**: {TIMESTAMP}
- **Missing File(s)**:
"""
        for m in missing:
            content += f"- `{m}`\n"
        with open(os.path.join(REPORTS_DIR, "stage4_missing_dependencies.md"), "w", encoding="utf-8") as f:
            f.write(content)
        print("Missing dependencies. Halted.")
        sys.exit(1)
        
def check_score_c_validated():
    # Only compute Score C if it was validated in Stage 3.6
    val_path = os.path.join(REPORTS_DIR, "coverage_normalization_experiments.md")
    if os.path.exists(val_path):
        with open(val_path, "r", encoding="utf-8") as f:
            content = f.read()
            if "Coverage x Scale x Density" in content or "Coverage × Scale × Density" in content:
                return True
    return False

def load_template_cache():
    manifest_path = os.path.join(TEMPLATE_BANK_DIR, "template_bank_manifest.csv")
    cache = {}
    with open(manifest_path, "r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for r in reader:
            t_id = r["template_id"]
            img_path = os.path.join(BASE_DIR, r["filepath"])
            img = cv2.imread(img_path, cv2.IMREAD_GRAYSCALE)
            if img is not None:
                ys, xs = np.where(img > 0)
            else:
                ys, xs = np.array([]), np.array([])
                
            w, h = int(r["width"]), int(r["height"])
            cache[t_id] = {
                "edge_ys": ys,
                "edge_xs": xs,
                "edge_count": int(r["edge_count"]),
                "area": w * h,
                "density": float(r["edge_density"]),
                "width": w,
                "height": h
            }
    return cache

def main():
    print("Stage 4: Input Validation...")
    phase_4a_input_validation()
    
    compute_score_c = check_score_c_validated()
    
    print("Loading Templates...")
    templates = load_template_cache()
    
    # Load Candidates
    print("Loading Candidates...")
    candidates = []
    candidates_by_sld = defaultdict(list)
    ranked_path = os.path.join(CANDIDATES_DIR, "ranked_candidates.csv")
    
    with open(ranked_path, "r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            candidates.append(row)
            candidates_by_sld[row["sld_name"]].append(row)
            
    count_before = len(candidates)
    
    print("Phase 4B & 4C: Recomputing Coverage and Rescoring...")
    rescored_candidates = []
    
    for sld, sld_candidates in candidates_by_sld.items():
        dt_path = os.path.join(DT_DIR, f"{sld}_dt.tiff")
        if not os.path.exists(dt_path):
            print(f"Warning: DT missing for {sld}")
            continue
            
        dt_img = cv2.imread(dt_path, cv2.IMREAD_UNCHANGED)
        if dt_img is None:
            continue
            
        h_d, w_d = dt_img.shape
        
        for row in sld_candidates:
            c = dict(row)
            t_id = c["template_id"]
            x, y = int(c["x"]), int(c["y"])
            scale = float(c["scale"])
            
            t_info = templates.get(t_id)
            if t_info is None:
                c["coverage_r0"] = c["coverage_r1"] = c["coverage_r2"] = c["coverage_r3"] = 0.0
                c["normalized_score_a"] = c["normalized_score_b"] = 0.0
                if compute_score_c:
                    c["normalized_score_c"] = 0.0
                c["template_width"] = c["template_height"] = c["template_area"] = c["edge_count"] = 0
                rescored_candidates.append(c)
                continue
                
            xs = x + t_info["edge_xs"]
            ys = y + t_info["edge_ys"]
            
            valid = (xs >= 0) & (xs < w_d) & (ys >= 0) & (ys < h_d)
            valid_xs = xs[valid]
            valid_ys = ys[valid]
            
            dists = dt_img[valid_ys, valid_xs]
            
            cov_r0_cnt = np.sum(dists <= 0.05)
            cov_r1_cnt = np.sum(dists <= 1.05)
            cov_r2_cnt = np.sum(dists <= 2.05)
            cov_r3_cnt = np.sum(dists <= 3.05)
            
            edge_count = t_info["edge_count"]
            cov_r0 = cov_r0_cnt / edge_count if edge_count > 0 else 0.0
            cov_r1 = cov_r1_cnt / edge_count if edge_count > 0 else 0.0
            cov_r2 = cov_r2_cnt / edge_count if edge_count > 0 else 0.0
            cov_r3 = cov_r3_cnt / edge_count if edge_count > 0 else 0.0
            
            # Save metrics
            c["coverage_r0"] = cov_r0
            c["coverage_r1"] = cov_r1
            c["coverage_r2"] = cov_r2
            c["coverage_r3"] = cov_r3
            
            # Phase 4C: Normalized Rescoring
            c["normalized_score_a"] = cov_r1 * scale
            c["normalized_score_b"] = cov_r1 * t_info["area"]
            
            if compute_score_c:
                c["normalized_score_c"] = cov_r1 * scale * t_info["density"]
                
            c["template_width"] = t_info["width"]
            c["template_height"] = t_info["height"]
            c["template_area"] = t_info["area"]
            c["edge_count"] = edge_count
            
            rescored_candidates.append(c)
            
    count_after = len(rescored_candidates)
    
    # Candidate Survival Audit Check
    if count_after != count_before:
        print(f"FATAL: Candidate survival mismatch! Before: {count_before}, After: {count_after}")
        sys.exit(1)
        
    print("Phase 4D & 4E: Generating Ranked Datasets...")
    
    # 1. rescored_candidates.csv
    resc_path = os.path.join(CANDIDATES_DIR, "rescored_candidates.csv")
    fieldnames = [
        "candidate_id", "sld_name", "template_id", "scale", "rotation", "x", "y", "score",
        "coverage_r0", "coverage_r1", "coverage_r2", "coverage_r3",
        "normalized_score_a", "normalized_score_b"
    ]
    if compute_score_c:
        fieldnames.append("normalized_score_c")
    fieldnames.extend(["template_width", "template_height", "template_area", "edge_count"])
    
    # Map score to chamfer_score to match standard naming if needed, but original csv has 'score'.
    # We will rename 'score' to 'chamfer_score' to match PRD
    for c in rescored_candidates:
        if "score" in c and "chamfer_score" not in c:
            c["chamfer_score"] = c["score"]
            
    fieldnames = [f if f != "score" else "chamfer_score" for f in fieldnames]
    
    with open(resc_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames, extrasaction='ignore')
        writer.writeheader()
        writer.writerows(rescored_candidates)
        
    # 2. ranked_by_coverage_scale.csv
    rescored_candidates.sort(key=lambda x: float(x["normalized_score_a"]), reverse=True)
    with open(os.path.join(CANDIDATES_DIR, "ranked_by_coverage_scale.csv"), "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames, extrasaction='ignore')
        writer.writeheader()
        writer.writerows(rescored_candidates)
        
    # 3. ranked_by_coverage_area.csv
    rescored_candidates.sort(key=lambda x: float(x["normalized_score_b"]), reverse=True)
    with open(os.path.join(CANDIDATES_DIR, "ranked_by_coverage_area.csv"), "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames, extrasaction='ignore')
        writer.writeheader()
        writer.writerows(rescored_candidates)
        
    # 4. ranked_by_combined.csv (If Score C)
    if compute_score_c:
        rescored_candidates.sort(key=lambda x: float(x["normalized_score_c"]), reverse=True)
        with open(os.path.join(CANDIDATES_DIR, "ranked_by_combined.csv"), "w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames, extrasaction='ignore')
            writer.writeheader()
            writer.writerows(rescored_candidates)
            
    print("Phase 4G: Generating Visual Validation...")
    os.makedirs(VISUALS_DIR, exist_ok=True)
    
    # Load rankings grouped by SLD for visualization
    def load_ranked_sld(path):
        data = defaultdict(list)
        with open(path, "r", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            for r in reader:
                data[r["sld_name"]].append(r)
        return data
        
    orig_grouped = load_ranked_sld(ranked_path)
    scale_grouped = load_ranked_sld(os.path.join(CANDIDATES_DIR, "ranked_by_coverage_scale.csv"))
    area_grouped = load_ranked_sld(os.path.join(CANDIDATES_DIR, "ranked_by_coverage_area.csv"))
    
    for sld in ["SLD1", "SLD4", "SLD11"]:
        diag_path = os.path.join(DIAGRAMS_DIR, sld, "edges.png")
        if not os.path.exists(diag_path):
            continue
            
        def draw_top(groups, sld_name, n, color, thickness=2):
            img = cv2.imread(diag_path, cv2.IMREAD_COLOR)
            cands = groups.get(sld_name, [])[:n]
            for c in cands:
                x, y = int(c["x"]), int(c["y"])
                w, h = int(c.get("template_width", c.get("width", 24))), int(c.get("template_height", c.get("height", 15)))
                cv2.rectangle(img, (x, y), (x + w, y + h), color, thickness)
            return img

        # Red=Original, Green=Scale, Blue=Area
        for n in [10, 25, 50]:
            img_orig = draw_top(orig_grouped, sld, n, (0, 0, 255))
            img_scale = draw_top(scale_grouped, sld, n, (0, 255, 0))
            img_area = draw_top(area_grouped, sld, n, (255, 0, 0))
            
            cv2.imwrite(os.path.join(VISUALS_DIR, f"{sld}_top{n}_original.png"), img_orig)
            cv2.imwrite(os.path.join(VISUALS_DIR, f"{sld}_top{n}_scale.png"), img_scale)
            cv2.imwrite(os.path.join(VISUALS_DIR, f"{sld}_top{n}_area.png"), img_area)
            
    print("Writing Operational Reports...")
    header = get_traceability_header(count_before, count_after, len(candidates_by_sld))
    
    with open(os.path.join(REPORTS_DIR, "stage4_candidate_survival_audit.md"), "w", encoding="utf-8") as f:
        f.write(f"""# Candidate Survival Audit

{header}

## 1. Objective
Ensure that Stage 4 functions purely as a rescoring layer without accidentally implementing filtering, suppression, or deletion algorithms.

## 2. Audit Results
- **Candidates In**: {count_before}
- **Candidates Out**: {count_after}
- **Loss Factor**: 0%
- **Status**: PASSED. No candidates were removed, suppressed, or merged.
""")

    with open(os.path.join(REPORTS_DIR, "stage4_rescoring_methodology.md"), "w", encoding="utf-8") as f:
        f.write(rf"""# Stage 4 Rescoring Methodology

{header}

## 1. Methodology
For every candidate across all SLDs, Stage 4 recomputed coverage against the distance transform using exact Stage 3.5 methodology:
$Coverage\_R = \frac{{\text{{edge pixels within }} R}}{{\text{{total template edges}}}}$

Following recomputation, diagnostic models from Stage 3.6 were applied to synthesize operationally normalized scores:
- `NormalizedScore_A` = $Coverage\_R1 \\times Scale$
- `NormalizedScore_B` = $Coverage\_R1 \\times TemplateArea$
{'- `NormalizedScore_C` = Coverage_R1 \\times Scale \\times EdgeDensity' if compute_score_c else ''}

## 2. Pipeline Integrity
The ground truth evaluation and rank analysis are completely separated from this operational engine. All ranked CSVs are preserved in `outputs/candidates/`.
""")

if __name__ == "__main__":
    main()
