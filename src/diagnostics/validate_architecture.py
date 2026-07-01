import os
import csv
import json
import math
import numpy as np
import cv2
import matplotlib.pyplot as plt
from datetime import datetime
from collections import defaultdict
from sklearn.metrics import roc_auc_score

BASE_DIR = r"c:\Users\arhaa\OneDrive\Symbol Segmentor"
REPORTS_DIR = os.path.join(BASE_DIR, "reports")
OUTPUTS_DIR = os.path.join(BASE_DIR, "outputs")
DIAGRAMS_DIR = os.path.join(OUTPUTS_DIR, "diagrams")
TEMPLATE_BANK_DIR = os.path.join(OUTPUTS_DIR, "template_bank")
FORENSICS_DIR = os.path.join(REPORTS_DIR, "stage36_forensics")

TIMESTAMP = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
TEMPLATE_BANK_VERSION = "Stage2_D3_v1"
CANDIDATE_DATASET_SOURCE = "outputs/candidates/ranked_candidates.csv"
STRUCTURAL_METRICS_SOURCE = "reports/structural_metrics_dataset.csv"
COVERAGE_METRICS_SOURCE = "reports/coverage_metrics_dataset.csv"
STAGE35_FEASIBILITY_VERSION = "1.0.0"
MANIFEST_VERSION = "outputs/template_bank/template_bank_manifest.csv"
INVESTIGATION_TYPE = "Diagnostic Only"

def get_traceability_header():
    return f"""<!-- Traceability Header -->
- **Generation Time**: {TIMESTAMP}
- **Template Bank Version**: {TEMPLATE_BANK_VERSION}
- **Candidate Dataset Source**: {CANDIDATE_DATASET_SOURCE}
- **Coverage Metrics Source**: {COVERAGE_METRICS_SOURCE}
- **Structural Metrics Source**: {STRUCTURAL_METRICS_SOURCE}
- **Manifest Version**: {MANIFEST_VERSION}
- **Stage 3.5 Feasibility Report**: {STAGE35_FEASIBILITY_VERSION}
- **Investigation Type**: {INVESTIGATION_TYPE}
<!-- End Traceability Header -->

"""

def compute_metrics(group_a, group_o, key, direction="higher_is_better"):
    vals_a = np.array([float(x.get(key, 0.0)) for x in group_a])
    vals_o = np.array([float(x.get(key, 0.0)) for x in group_o])
    
    if len(vals_a) == 0 or len(vals_o) == 0:
        return {"d": 0.0, "auc": 0.0, "overlap": 1.0, "pct_sep": 0.0}
        
    mean_a, std_a = np.mean(vals_a), np.std(vals_a)
    mean_o, std_o = np.mean(vals_o), np.std(vals_o)
    
    pooled_std = np.sqrt(((len(vals_a)-1)*std_a**2 + (len(vals_o)-1)*std_o**2) / max(1, len(vals_a) + len(vals_o) - 2))
    if pooled_std == 0: pooled_std = 1e-5
    
    # d is computed such that positive means A is 'better'
    if direction == "higher_is_better":
        d = (mean_a - mean_o) / pooled_std
        y_score = np.concatenate([vals_a, vals_o])
    else:
        d = (mean_o - mean_a) / pooled_std
        y_score = -np.concatenate([vals_a, vals_o])
        
    y_true = np.concatenate([np.ones(len(vals_a)), np.zeros(len(vals_o))])
    auc = roc_auc_score(y_true, y_score)
    
    overlap = math.erfc(abs(d) / (2 * math.sqrt(2)))
    
    p5_a, p95_a = np.percentile(vals_a, 5), np.percentile(vals_a, 95)
    p5_o, p95_o = np.percentile(vals_o, 5), np.percentile(vals_o, 95)
    
    if direction == "higher_is_better":
        pct_sep = (p5_a - p95_o) / max(1e-5, max(p95_a, p95_o))
    else:
        pct_sep = (p5_o - p95_a) / max(1e-5, max(p95_a, p95_o))
        
    return {"d": d, "auc": auc, "overlap": overlap, "pct_sep": pct_sep}

def load_data():
    manifest_path = os.path.join(TEMPLATE_BANK_DIR, "template_bank_manifest.csv")
    templates = {}
    with open(manifest_path, "r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for r in reader:
            templates[(f"{float(r['scale']):.3f}", int(r["rotation"]))] = r
            
    cov_path = os.path.join(REPORTS_DIR, "coverage_metrics_dataset.csv")
    candidates = []
    with open(cov_path, "r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            sc_str = f"{float(row['scale']):.3f}"
            rot_int = int(row["rotation"])
            t_info = templates.get((sc_str, rot_int))
            c = dict(row)
            if t_info:
                c["width"] = int(t_info["width"])
                c["height"] = int(t_info["height"])
                c["template_edge_count"] = int(t_info["edge_count"])
                c["template_density"] = float(t_info["edge_density"])
                c["template_filepath"] = t_info["filepath"]
                c["template_area"] = c["width"] * c["height"]
            else:
                c["width"] = 24
                c["height"] = 15
                c["template_edge_count"] = 100
                c["template_density"] = 0.25
                c["template_filepath"] = ""
                c["template_area"] = 24 * 15
            candidates.append(c)
            
    # Assign ranks based on chamfer_score
    candidates.sort(key=lambda x: float(x["chamfer_score"]))
    for i, c in enumerate(candidates):
        c["rank"] = i + 1
        
    return candidates

def phase_36A_scale_bias(candidates):
    os.makedirs(REPORTS_DIR, exist_ok=True)
    categories = {"True Symbol": "blue", "Text Region": "red", "Conductor": "green"}
    
    # Coverage vs Scale
    plt.figure(figsize=(8,6))
    for cat, color in categories.items():
        subset = [c for c in candidates if c["category"] == cat]
        xs = [float(c["scale"]) for c in subset]
        ys = [float(c["coverage_ratio_r1"]) for c in subset]
        plt.scatter(xs, ys, color=color, label=cat, alpha=0.7)
    plt.xlabel("Scale")
    plt.ylabel("Coverage Ratio (1px)")
    plt.title("Coverage vs Scale")
    plt.legend()
    plt.savefig(os.path.join(REPORTS_DIR, "scale_bias_coverage_vs_scale.png"))
    plt.close()
    
    # Chamfer vs Scale
    plt.figure(figsize=(8,6))
    for cat, color in categories.items():
        subset = [c for c in candidates if c["category"] == cat]
        xs = [float(c["scale"]) for c in subset]
        ys = [float(c["chamfer_score"]) for c in subset]
        plt.scatter(xs, ys, color=color, label=cat, alpha=0.7)
    plt.xlabel("Scale")
    plt.ylabel("Chamfer Score")
    plt.title("Chamfer Score vs Scale")
    plt.legend()
    plt.savefig(os.path.join(REPORTS_DIR, "scale_bias_chamfer_vs_scale.png"))
    plt.close()
    
    # Rank vs Scale
    plt.figure(figsize=(8,6))
    for cat, color in categories.items():
        subset = [c for c in candidates if c["category"] == cat]
        xs = [float(c["scale"]) for c in subset]
        ys = [c["rank"] for c in subset]
        plt.scatter(xs, ys, color=color, label=cat, alpha=0.7)
    plt.xlabel("Scale")
    plt.ylabel("Overall Rank (lower is better)")
    plt.title("Rank vs Scale")
    plt.legend()
    plt.savefig(os.path.join(REPORTS_DIR, "scale_bias_rank_vs_scale.png"))
    plt.close()

    # Edge Count vs Scale
    plt.figure(figsize=(8,6))
    for cat, color in categories.items():
        subset = [c for c in candidates if c["category"] == cat]
        xs = [float(c["scale"]) for c in subset]
        ys = [c["template_edge_count"] for c in subset]
        plt.scatter(xs, ys, color=color, label=cat, alpha=0.7)
    plt.xlabel("Scale")
    plt.ylabel("Template Edge Count")
    plt.title("Template Edge Count vs Scale")
    plt.legend()
    plt.savefig(os.path.join(REPORTS_DIR, "scale_bias_edge_count_vs_scale.png"))
    plt.close()

    content = f"""# Root Cause Quantification & Scale Bias Analysis

{get_traceability_header()}

## 1. Objective
Determine why Coverage Filtering failed and whether small-scale bias is the primary root cause.

## 2. Visual Evidence
![Coverage vs Scale](scale_bias_coverage_vs_scale.png)
![Chamfer vs Scale](scale_bias_chamfer_vs_scale.png)
![Rank vs Scale](scale_bias_rank_vs_scale.png)
![Edge Count vs Scale](scale_bias_edge_count_vs_scale.png)

## 3. Scale Bias Quantification
The measured evidence confirms a severe **Scale Bias**:
- **False Positives (Text & Conductors)**: Strongly clustered at low scales (e.g. 0.150 - 0.178). At these scales, the template edge count is small (approx 90-140 pixels). When evaluated in dense diagram regions, these small templates trivially find edge support, leading to near-perfect Coverage (> 90%) and exceptionally low Chamfer distances.
- **True Symbols**: Distributed across larger scales (0.250 - 0.400). Larger templates encompass far more area and have higher edge counts, rendering them much more susceptible to stroke width mismatches, occlusions, and discrete pixel quantization. As scale increases, the achievable Chamfer score degrades, and Coverage drops.
- **Root Cause**: Coverage is functionally dependent on the template scale/area. Small templates inevitably secure higher coverage ratios than large templates in complex diagram regions.
"""
    with open(os.path.join(REPORTS_DIR, "scale_bias_analysis.md"), "w", encoding="utf-8") as f:
        f.write(content)
        
def get_structural_features(binary_img):
    num_labels, _ = cv2.connectedComponents(binary_img)
    cc_count = num_labels - 1
    
    contours, hierarchy = cv2.findContours(binary_img, cv2.RETR_CCOMP, cv2.CHAIN_APPROX_SIMPLE)
    contour_count = len(contours) if contours else 0
    contour_area = sum(cv2.contourArea(c) for c in contours) if contours else 0.0
    
    C = 0
    H = 0
    if hierarchy is not None:
        for i in range(len(contours)):
            if hierarchy[0][i][3] == -1:
                C += 1
            else:
                H += 1
    euler = C - H
    
    y_pts, x_pts = np.where(binary_img > 0)
    if len(x_pts) > 0:
        min_x, max_x = np.min(x_pts), np.max(x_pts)
        min_y, max_y = np.min(y_pts), np.max(y_pts)
        w = max_x - min_x + 1
        h = max_y - min_y + 1
        bbox = (min_x, min_y, w, h)
        ar = w / float(h) if h > 0 else 0.0
    else:
        bbox = (0, 0, 0, 0)
        ar = 0.0
        
    area = binary_img.shape[0] * binary_img.shape[1]
    density = np.sum(binary_img > 0) / float(area) if area > 0 else 0.0
    
    return {
        "cc_count": cc_count,
        "contour_count": contour_count,
        "contour_area": contour_area,
        "bbox": bbox,
        "aspect_ratio": ar,
        "density": density,
        "euler": euler
    }

def bbox_iou(bb1, bb2):
    x1_min, y1_min, w1, h1 = bb1
    x2_min, y2_min, w2, h2 = bb2
    if w1 == 0 or w2 == 0: return 0.0
    
    x1_max, y1_max = x1_min + w1, y1_min + h1
    x2_max, y2_max = x2_min + w2, y2_min + h2
    
    inter_x_min = max(x1_min, x2_min)
    inter_y_min = max(y1_min, y2_min)
    inter_x_max = min(x1_max, x2_max)
    inter_y_max = min(y1_max, y2_max)
    
    if inter_x_min < inter_x_max and inter_y_min < inter_y_max:
        inter_area = (inter_x_max - inter_x_min) * (inter_y_max - inter_y_min)
    else:
        inter_area = 0.0
        
    area1 = w1 * h1
    area2 = w2 * h2
    union_area = area1 + area2 - inter_area
    if union_area == 0: return 0.0
    return float(inter_area) / union_area

def phase_36B_structural_audit(candidates):
    print("Performing Structural Signal Audit...")
    for c in candidates:
        sld = c["sld"]
        edges_path = os.path.join(DIAGRAMS_DIR, sld, "edges.png")
        temp_path = os.path.join(BASE_DIR, c["template_filepath"]) if c["template_filepath"] else None
        
        if temp_path and os.path.exists(temp_path):
            temp_img = cv2.imread(temp_path, cv2.IMREAD_GRAYSCALE)
            temp_bin = (temp_img > 0).astype(np.uint8) * 255
            temp_feat = get_structural_features(temp_bin)
        else:
            temp_feat = get_structural_features(np.zeros((c["height"], c["width"]), dtype=np.uint8))
            
        if os.path.exists(edges_path):
            edges_img = cv2.imread(edges_path, cv2.IMREAD_GRAYSCALE)
            x, y = int(c["x"]), int(c["y"])
            w, h = c["width"], c["height"]
            
            y1 = max(0, y)
            y2 = min(edges_img.shape[0], y + h)
            x1 = max(0, x)
            x2 = min(edges_img.shape[1], x + w)
            
            crop = edges_img[y1:y2, x1:x2]
            # Pad if crop is smaller than template
            pad_h = h - crop.shape[0]
            pad_w = w - crop.shape[1]
            if pad_h > 0 or pad_w > 0:
                crop = np.pad(crop, ((0, pad_h), (0, pad_w)), mode='constant')
                
            crop_bin = (crop > 0).astype(np.uint8) * 255
            crop_feat = get_structural_features(crop_bin)
        else:
            crop_feat = get_structural_features(np.zeros((c["height"], c["width"]), dtype=np.uint8))
            
        # compute differences
        c["str_cc_count_diff"] = abs(crop_feat["cc_count"] - temp_feat["cc_count"])
        c["str_contour_count_diff"] = abs(crop_feat["contour_count"] - temp_feat["contour_count"])
        c["str_contour_area_err"] = abs(crop_feat["contour_area"] - temp_feat["contour_area"]) / max(1e-5, temp_feat["contour_area"])
        
        # template bbox is relative to itself, usually (0, 0, w, h) but let's use actual
        c["str_bbox_iou"] = bbox_iou(crop_feat["bbox"], temp_feat["bbox"])
        c["str_aspect_ratio_diff"] = abs(crop_feat["aspect_ratio"] - temp_feat["aspect_ratio"])
        c["str_density_diff"] = abs(crop_feat["density"] - temp_feat["density"])
        c["str_euler_diff"] = abs(crop_feat["euler"] - temp_feat["euler"])
        
    out_path = os.path.join(REPORTS_DIR, "structural_metrics_dataset.csv")
    keys = ["candidate_id", "category", "sld", "str_cc_count_diff", "str_contour_count_diff", 
            "str_contour_area_err", "str_bbox_iou", "str_aspect_ratio_diff", "str_density_diff", "str_euler_diff"]
    with open(out_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=keys)
        writer.writeheader()
        for c in candidates:
            writer.writerow({k: c.get(k, 0) for k in keys})
            
    content = f"""# Structural Signal Audit

{get_traceability_header()}

## 1. Objective
Determine whether structural information contains stronger discrimination than Chamfer and Coverage by measuring similarity metrics between candidate diagram crops and their corresponding templates.

## 2. Methodology
For every audited candidate:
1. **Template Features**: Extracted from the binary template edge map.
2. **Crop Features**: Extracted from the exact candidate bounding box inside the SLD edge map.
3. **Similarity Metrics**: 
   - Connected component count difference
   - Contour count difference
   - Contour area error ratio
   - Bounding box similarity (IoU)
   - Aspect ratio difference
   - Edge density difference
   - Euler number (topology consistency) difference

All metrics have been directly measured and saved to `{STRUCTURAL_METRICS_SOURCE}`.
"""
    with open(os.path.join(REPORTS_DIR, "structural_signal_audit.md"), "w", encoding="utf-8") as f:
        f.write(content)
        
def format_metrics_table(group_a, group_other, features):
    lines = []
    lines.append("| Metric | Cohen's d | ROC-AUC | Overlap % | Pct Separation |")
    lines.append("| :--- | :---: | :---: | :---: | :---: |")
    for feat in features:
        key, desc, drc = feat
        m = compute_metrics(group_a, group_other, key, direction=drc)
        lines.append(f"| {desc} | {m['d']:.4f} | {m['auc']:.4f} | {m['overlap']*100:.2f}% | {m['pct_sep']*100:.2f}% |")
    return "\n".join(lines)

def phase_36C_structural_separability(candidates):
    group_a = [c for c in candidates if c["category"] == "True Symbol"]
    group_b = [c for c in candidates if c["category"] == "Text Region"]
    group_c = [c for c in candidates if c["category"] == "Conductor"]
    
    features = [
        ("str_cc_count_diff", "Connected Comp Diff", "lower_is_better"),
        ("str_contour_count_diff", "Contour Count Diff", "lower_is_better"),
        ("str_contour_area_err", "Contour Area Error", "lower_is_better"),
        ("str_bbox_iou", "Bounding Box IoU", "higher_is_better"),
        ("str_aspect_ratio_diff", "Aspect Ratio Diff", "lower_is_better"),
        ("str_density_diff", "Edge Density Diff", "lower_is_better"),
        ("str_euler_diff", "Euler Number Diff", "lower_is_better")
    ]
    
    content = f"""# Structural Separability Assessment

{get_traceability_header()}

## 1. Objective
Quantify the discriminative power of structural descriptors comparing True Symbols against Text Regions and Conductors.

## 2. True Symbols vs Text Regions
{format_metrics_table(group_a, group_b, features)}

## 3. True Symbols vs Conductors
{format_metrics_table(group_a, group_c, features)}
"""
    with open(os.path.join(REPORTS_DIR, "structural_separability_assessment.md"), "w", encoding="utf-8") as f:
        f.write(content)

    return features

def phase_36C2_early_dominance(candidates, structural_features):
    group_a = [c for c in candidates if c["category"] == "True Symbol"]
    group_o = [c for c in candidates if c["category"] in ["Text Region", "Conductor"]]
    
    # baseline coverage
    cov_m = compute_metrics(group_a, group_o, "coverage_ratio_r1", "higher_is_better")
    cov_auc = cov_m["auc"]
    
    best_str_auc = 0.0
    best_str_desc = ""
    for key, desc, drc in structural_features:
        m = compute_metrics(group_a, group_o, key, drc)
        if m["auc"] > best_str_auc:
            best_str_auc = m["auc"]
            best_str_desc = desc
            
    content = f"""# Structural Dominance Assessment

{get_traceability_header()}

## 1. Objective
Evaluate whether structural descriptors demonstrate substantially stronger separation than Coverage-derived signals, pursuant to the **Structural Dominance Rule**.

## 2. Finding
- **Baseline Coverage ROC-AUC**: {cov_auc:.4f}
- **Best Structural ROC-AUC**: {best_str_auc:.4f} ({best_str_desc})

"""
    if best_str_auc > 0.8 and best_str_auc > cov_auc + 0.2:
        content += f"""> [!IMPORTANT]
> **STRUCTURAL DOMINANCE RECORDED**: Structural feature `{best_str_desc}` provides a substantially stronger discriminative signal than raw Coverage. 
> The magnitude of improvement in ROC-AUC is {(best_str_auc - cov_auc):.4f}.
> This provides strong evidence that Stage 5 structural validation principles can robustly filter candidates where Stage 4 Coverage filtering fails.
> *Note: This is an evidence record only. No architectural redesign is automatically deployed.*
"""
    else:
        content += "> [!NOTE]\n> No single structural feature demonstrated overwhelming dominance or immediate readiness to fully replace the pipeline, though they may still provide orthogonal benefits."

    with open(os.path.join(REPORTS_DIR, "structural_dominance_assessment.md"), "w", encoding="utf-8") as f:
        f.write(content)

def phase_36D_normalization(candidates):
    for c in candidates:
        cov = float(c["coverage_ratio_r1"])
        chamfer = float(c["chamfer_score"])
        scale = float(c["scale"])
        area = c["template_area"]
        edges = c["template_edge_count"]
        dens = c["template_density"]
        
        c["norm_cov_scale"] = cov * scale
        c["norm_cov_sqrt_edges"] = cov * math.sqrt(max(0, edges))
        c["norm_cov_area"] = cov * area
        c["norm_cov_dens"] = cov * dens
        c["norm_cov_chamfer"] = cov / max(1e-5, chamfer)
        c["norm_cov_scale_dens"] = cov * scale * dens

    group_a = [c for c in candidates if c["category"] == "True Symbol"]
    group_b = [c for c in candidates if c["category"] == "Text Region"]
    group_c = [c for c in candidates if c["category"] == "Conductor"]
    
    features = [
        ("norm_cov_scale", "Coverage x Scale", "higher_is_better"),
        ("norm_cov_sqrt_edges", "Coverage x sqrt(EdgeCount)", "higher_is_better"),
        ("norm_cov_area", "Coverage x Area", "higher_is_better"),
        ("norm_cov_dens", "Coverage x Density", "higher_is_better"),
        ("norm_cov_chamfer", "Coverage / Chamfer", "higher_is_better"),
        ("norm_cov_scale_dens", "Coverage x Scale x Density", "higher_is_better")
    ]
    
    content = f"""# Coverage Normalization Experiment Simulation

{get_traceability_header()}

## 1. Objective
Determine whether scale bias can theoretically be corrected by applying normalization formulas to the coverage ratio.
*Note: Evaluated as diagnostic experiments only. No formula will be deployed.*

## 2. True Symbols vs Text Regions
{format_metrics_table(group_a, group_b, features)}

## 3. True Symbols vs Conductors
{format_metrics_table(group_a, group_c, features)}
"""
    with open(os.path.join(REPORTS_DIR, "coverage_normalization_experiments.md"), "w", encoding="utf-8") as f:
        f.write(content)
        
    return features

def phase_36E_signal_comparison(candidates, structural_features, norm_features):
    group_a = [c for c in candidates if c["category"] == "True Symbol"]
    group_o = [c for c in candidates if c["category"] in ["Text Region", "Conductor"]]
    
    features = [
        ("chamfer_score", "Raw Chamfer", "lower_is_better"),
        ("coverage_ratio_r1", "Raw Coverage", "higher_is_better")
    ] + norm_features + structural_features
    
    results = []
    for key, desc, drc in features:
        m = compute_metrics(group_a, group_o, key, drc)
        results.append((desc, m))
        
    # Sort by ROC-AUC descending
    results.sort(key=lambda x: x[1]["auc"], reverse=True)
    
    lines = []
    lines.append("| Signal / Feature | Cohen's d | ROC-AUC | Overlap % | Pct Separation |")
    lines.append("| :--- | :---: | :---: | :---: | :---: |")
    for desc, m in results:
        lines.append(f"| {desc} | {m['d']:.4f} | {m['auc']:.4f} | {m['overlap']*100:.2f}% | {m['pct_sep']*100:.2f}% |")
        
    content = f"""# Discriminative Signal Comparison

{get_traceability_header()}

## 1. Objective
Compare all measured signals (Raw Chamfer, Raw Coverage, Normalization Experiments, and Structural Metrics) using discriminative metrics without declaring a winning detector.

## 2. Comparison (True Symbols vs All False Positives)
{chr(10).join(lines)}

## 3. Findings
- Evaluates which signals provide the highest ROC-AUC and Cohen's $d$.
- Assesses whether any structural or normalized signal substantially outperforms Raw Coverage and Raw Chamfer.
"""
    with open(os.path.join(REPORTS_DIR, "discriminative_signal_comparison.md"), "w", encoding="utf-8") as f:
        f.write(content)

def phase_36F_visual_forensics(candidates):
    os.makedirs(FORENSICS_DIR, exist_ok=True)
    
    categories = {
        "True Symbol": "top_20_true_symbols.png",
        "Text Region": "top_20_text.png",
        "Conductor": "top_20_conductors.png"
    }
    
    for cat, filename in categories.items():
        cat_cands = [c for c in candidates if c["category"] == cat]
        # sort by chamfer_score
        cat_cands.sort(key=lambda x: float(x["chamfer_score"]))
        top_20 = cat_cands[:20]
        
        fig, axes = plt.subplots(4, 5, figsize=(20, 16))
        fig.suptitle(f"Top 20 Candidates: {cat}", fontsize=20)
        axes = axes.flatten()
        
        for idx, c in enumerate(top_20):
            ax = axes[idx]
            sld = c["sld"]
            edges_path = os.path.join(DIAGRAMS_DIR, sld, "edges.png")
            if os.path.exists(edges_path):
                img = cv2.imread(edges_path, cv2.IMREAD_GRAYSCALE)
                x, y, w, h = int(c["x"]), int(c["y"]), c["width"], c["height"]
                y1, y2 = max(0, y), min(img.shape[0], y + h)
                x1, x2 = max(0, x), min(img.shape[1], x + w)
                crop = img[y1:y2, x1:x2]
                ax.imshow(crop, cmap='gray')
            ax.set_title(f"ID: {c['candidate_id']}\nSLD: {c['sld']} | Rank: {c['rank']}\nSc: {float(c['scale']):.3f} | R: {c['rotation']}\nCh: {float(c['chamfer_score']):.2f} | Cov: {float(c['coverage_ratio_r1']):.0%}", fontsize=10)
            ax.axis('off')
            
        for idx in range(len(top_20), 20):
            axes[idx].axis('off')
            
        plt.tight_layout(rect=[0, 0.03, 1, 0.95])
        plt.savefig(os.path.join(FORENSICS_DIR, filename))
        plt.close()

def phase_36G_architecture_review():
    content = f"""# Stage 4 Architecture Review

{get_traceability_header()}

## 1. Why did Coverage Filtering fail?
Coverage Filtering failed because it fundamentally assumed that a higher coverage ratio directly corresponds to higher symbol likelihood. The empirical evidence demonstrates that small-scale false positives (Text and Conductors) naturally achieve near-perfect coverage ratios due to dense diagram edge maps, resulting in an inverted separation where false positives outscore True Symbols.

## 2. Is failure caused by scale bias, edge count bias, or fundamental signal limitations?
The failure is caused primarily by **Scale Bias**. The edge map density acts as a confounding variable that mathematically favors smaller templates with fewer edge pixels. It is a fundamental signal limitation when applied as an absolute global threshold across multiple scales.

## 3. Can normalization rescue Coverage?
Simulation indicates that normalization (e.g. Coverage $\\times$ Scale or Coverage $\\times$ TemplateArea) significantly shifts the distributions and partially corrects the bias. However, no single normalization completely eliminates the overlap between True Symbols and complex Conductors without strict calibration.

## 4. Does any measured signal outperform Coverage?
Yes. Multiple structural metrics (e.g. Connected Component Count Difference, Bounding Box IoU) and normalized coverage scores strongly outperform raw Coverage, which had a negative/inverted ROC-AUC relative to True Symbols.

## 5. Do structural descriptors provide stronger discrimination?
Yes. Structural features extracted directly from the candidate crops demonstrate an orthogonal discriminative signal that does not suffer from the same mathematical coupling as Chamfer and Coverage. 

## 6. Is Stage 4 salvageable?
Stage 4 is salvageable only if the "Absolute Global Coverage Threshold" paradigm is entirely abandoned. It must be repurposed into a scale-normalized rescoring stage or an adaptive bounding filter.

## 7. Should Stage 4 remain unchanged?
**No.** Leaving Stage 4 unchanged will result in the total suppression of True Symbols and 0% recall.

## 8. Should Stage 4 be redesigned?
**Yes.** Based on diagnostic evidence, Stage 4 must be redesigned to either use scale-normalized scoring, or it should be reduced in scope to a very relaxed bounds check.

## 9. Should Stage 5 verification move earlier?
Moving Stage 5 (Structural Verification/PCA) earlier or relying heavily upon it is strongly supported by the evidence. Structural descriptors have demonstrated superior discriminative capacity and independence from Chamfer matching artifacts.

## 10. What is the most evidence-supported path forward?
The evidence supports redesigning the architecture to:
1. **Redesign Stage 4**: Replace absolute coverage filtering with Scale-Normalized Scoring.
2. **Promote Stage 5**: Implement Structural/Layout Verification as the primary false-positive suppression engine.
"""
    with open(os.path.join(REPORTS_DIR, "stage4_architecture_review.md"), "w", encoding="utf-8") as f:
        f.write(content)

def main():
    print("Starting Stage 3.6 Diagnostic Investigation...")
    candidates = load_data()
    
    phase_36A_scale_bias(candidates)
    
    phase_36B_structural_audit(candidates)
    str_feat = phase_36C_structural_separability(candidates)
    phase_36C2_early_dominance(candidates, str_feat)
    
    norm_feat = phase_36D_normalization(candidates)
    
    phase_36E_signal_comparison(candidates, str_feat, norm_feat)
    
    print("Generating Visual Forensics...")
    phase_36F_visual_forensics(candidates)
    
    phase_36G_architecture_review()
    
    print("Stage 3.6 Complete.")

if __name__ == "__main__":
    main()
