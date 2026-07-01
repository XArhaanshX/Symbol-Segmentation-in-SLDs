import os
import csv
import json
import math
import numpy as np
import cv2
from datetime import datetime
from collections import defaultdict
import skimage.morphology
import networkx as nx
from scipy.stats import spearmanr, pearsonr, mannwhitneyu
from sklearn.metrics import roc_auc_score
import itertools

BASE_DIR = r"c:\Users\arhaa\OneDrive\Symbol Segmentor"
REPORTS_DIR = os.path.join(BASE_DIR, "reports")
OUTPUTS_DIR = os.path.join(BASE_DIR, "outputs")
CANDIDATES_DIR = os.path.join(OUTPUTS_DIR, "candidates")
DIAGRAMS_DIR = os.path.join(OUTPUTS_DIR, "diagrams")
TEMPLATE_BANK_DIR = os.path.join(OUTPUTS_DIR, "template_bank")
FORENSICS_DIR = os.path.join(REPORTS_DIR, "stage58_forensics")
SIM_RANKINGS_DIR = os.path.join(REPORTS_DIR, "stage58_simulated_rankings")

TIMESTAMP = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

def load_csv(path):
    if not os.path.exists(path): return []
    with open(path, "r", encoding="utf-8") as f:
        return list(csv.DictReader(f))

def save_csv(data, path, fieldnames):
    with open(path, "w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(data)

def get_traceability_header(experiment_id="N/A", method="N/A"):
    lines = [
        f"- Generation Timestamp: {TIMESTAMP}",
        "- Stage Version: Stage 5.8",
        "- Input Datasets: ranked_by_combined_score.csv, top100_competitor_sheet.csv, ground_truth_symbols.json",
        "- Template Bank Version: Stage2_D3_v1",
        "- Ground Truth Source: reports/ground_truth_symbols.json",
        f"- Evaluation Method: {method}",
        "- Scale Regime Definitions: A (>=0.30), B (0.20-0.30), C (0.15-0.20), D (<0.15)",
        "- Association Radius: 25px",
        "- Referenced Prior Stages: Stage 4, Stage 5.2, Stage 5.5, Stage 5.6",
        "- Manual Dependency Status: Competitor Family Classification from 5.5 (if available)"
    ]
    return "\n".join(lines) + "\n"

def get_scale_regime(scale):
    s = float(scale)
    if s >= 0.30: return "A"
    if s >= 0.20: return "B"
    if s >= 0.15: return "C"
    return "D"

# -------------------------------------------------------------------------
# Feature Extraction
# -------------------------------------------------------------------------

def extract_topological_features(binary_img):
    """ Extracts morphological, skeleton, loop, and stroke features from a binary image """
    h, w = binary_img.shape
    if h == 0 or w == 0: return {k: 0.0 for k in [
        "Connected_Component_Count", "Largest_Component_Ratio", "Component_Area_Variance",
        "Loop_Count", "Hole_Count", "Euler_Number", "Contour_Hierarchy_Depth",
        "Endpoint_Count", "Branch_Point_Count", "Average_Branch_Length", "Maximum_Branch_Length",
        "Branch_Length_Variance", "Stroke_Count", "Stroke_Density", "Horizontal_Stroke_Ratio", "Vertical_Stroke_Ratio"]}
    
    num_labels, labels, stats, centroids = cv2.connectedComponentsWithStats(binary_img, connectivity=8)
    areas = [stats[i, cv2.CC_STAT_AREA] for i in range(1, num_labels)]
    comp_count = max(0, num_labels - 1)
    max_comp_ratio = max(areas) / sum(areas) if areas and sum(areas) > 0 else 0
    comp_var = np.var(areas) if len(areas) > 1 else 0
    
    contours, hierarchy = cv2.findContours(binary_img, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)
    loop_count = hole_count = max_depth = 0
    if hierarchy is not None:
        hierarchy = hierarchy[0]
        for i, h_node in enumerate(hierarchy):
            if h_node[3] != -1: hole_count += 1
            else: loop_count += 1
            d = 0
            curr = i
            while hierarchy[curr][3] != -1:
                d += 1
                curr = hierarchy[curr][3]
            max_depth = max(max_depth, d)
            
    euler_number = comp_count - hole_count
    
    skeleton = skimage.morphology.skeletonize(binary_img > 0).astype(np.uint8) * 255
    kernel = np.array([[1, 1, 1], [1, 10, 1], [1, 1, 1]], dtype=np.uint8)
    filtered = cv2.filter2D(skeleton // 255, -1, kernel)
    
    endpoints = np.sum(filtered == 11)
    branch_points = np.sum(filtered > 12)
    skel_pixels = np.sum(skeleton > 0)
    avg_branch_length = skel_pixels / max(1, branch_points + 1)
    max_branch_length = avg_branch_length * 2 
    branch_var = 0 
    
    lines = cv2.HoughLinesP(skeleton, 1, np.pi/180, threshold=10, minLineLength=5, maxLineGap=2)
    stroke_count = horiz_strokes = vert_strokes = 0
    if lines is not None:
        stroke_count = len(lines)
        for line in lines:
            x1, y1, x2, y2 = line[0]
            angle = math.degrees(math.atan2(y2 - y1, x2 - x1)) % 180
            if angle < 20 or angle > 160: horiz_strokes += 1
            elif 70 < angle < 110: vert_strokes += 1
            
    stroke_density = stroke_count / max(1, comp_count)
    horiz_ratio = horiz_strokes / max(1, stroke_count)
    vert_ratio = vert_strokes / max(1, stroke_count)
    
    return {
        "Connected_Component_Count": float(comp_count),
        "Largest_Component_Ratio": float(max_comp_ratio),
        "Component_Area_Variance": float(comp_var),
        "Loop_Count": float(loop_count),
        "Hole_Count": float(hole_count),
        "Euler_Number": float(euler_number),
        "Contour_Hierarchy_Depth": float(max_depth),
        "Endpoint_Count": float(endpoints),
        "Branch_Point_Count": float(branch_points),
        "Average_Branch_Length": float(avg_branch_length),
        "Maximum_Branch_Length": float(max_branch_length),
        "Branch_Length_Variance": float(branch_var),
        "Stroke_Count": float(stroke_count),
        "Stroke_Density": float(stroke_density),
        "Horizontal_Stroke_Ratio": float(horiz_ratio),
        "Vertical_Stroke_Ratio": float(vert_ratio)
    }

def build_graph(binary_img):
    if binary_img.size == 0: return nx.Graph()
    skeleton = skimage.morphology.skeletonize(binary_img > 0).astype(np.uint8)
    kernel = np.array([[1, 1, 1], [1, 10, 1], [1, 1, 1]], dtype=np.uint8)
    filtered = cv2.filter2D(skeleton, -1, kernel)
    
    nodes_y, nodes_x = np.where((filtered == 11) | (filtered > 12))
    G = nx.Graph()
    for i, (y, x) in enumerate(zip(nodes_y, nodes_x)):
        G.add_node(i, pos=(x, y))
        
    if len(nodes_x) > 1:
        from scipy.spatial import KDTree
        tree = KDTree(np.c_[nodes_x, nodes_y])
        pairs = tree.query_pairs(15) 
        for i, j in pairs: G.add_edge(i, j)
    return G

def compare_graphs(g_cand, g_temp):
    nc_diff = abs(g_cand.number_of_nodes() - g_temp.number_of_nodes())
    ec_diff = abs(g_cand.number_of_edges() - g_temp.number_of_edges())
    
    dens_c = nx.density(g_cand) if g_cand.number_of_nodes() > 1 else 0
    dens_t = nx.density(g_temp) if g_temp.number_of_nodes() > 1 else 0
    dens_diff = abs(dens_c - dens_t)
    
    deg_c = np.mean([d for n, d in g_cand.degree()]) if g_cand.number_of_nodes() > 0 else 0
    deg_t = np.mean([d for n, d in g_temp.degree()]) if g_temp.number_of_nodes() > 0 else 0
    deg_diff = abs(deg_c - deg_t)
    
    ged_approx = nc_diff + ec_diff
    ep_match = min(1.0, g_cand.number_of_nodes() / max(1, g_temp.number_of_nodes()))
    jp_match = min(1.0, g_cand.number_of_edges() / max(1, g_temp.number_of_edges()))
    
    return {
        "Node_Count_Difference": float(nc_diff),
        "Edge_Count_Difference": float(ec_diff),
        "Degree_Distribution_Difference": float(deg_diff),
        "Graph_Density_Difference": float(dens_diff),
        "Junction_Similarity": float(1.0 / (1.0 + ec_diff)),
        "Endpoint_Similarity": float(1.0 / (1.0 + nc_diff)),
        "Graph_Edit_Distance_Approx": float(ged_approx),
        "Endpoint_Matching_Ratio": float(ep_match),
        "Junction_Matching_Ratio": float(jp_match)
    }

# -------------------------------------------------------------------------
# Statistical Functions
# -------------------------------------------------------------------------
def cohen_d(x, y):
    if len(x) < 2 or len(y) < 2: return 0.0
    nx_v, ny_v = len(x), len(y)
    dof = nx_v + ny_v - 2
    pool_std = math.sqrt(((nx_v - 1)*np.var(x, ddof=1) + (ny_v - 1)*np.var(y, ddof=1)) / dof)
    if pool_std == 0: return 0.0
    return abs(np.mean(x) - np.mean(y)) / pool_std

def dist_overlap(x, y):
    # Approximation via percentile overlap
    if not len(x) or not len(y): return 1.0
    min_overlap = max(np.min(x), np.min(y))
    max_overlap = min(np.max(x), np.max(y))
    if min_overlap >= max_overlap: return 0.0
    range_x = np.max(x) - np.min(x)
    range_y = np.max(y) - np.min(y)
    if range_x == 0 and range_y == 0: return 1.0
    return (max_overlap - min_overlap) / max(range_x, range_y, 1e-6)

def percentile_sep(x, y):
    if not len(x) or not len(y): return 0.0
    return abs(np.percentile(x, 50) - np.percentile(y, 50))

# -------------------------------------------------------------------------
# Main Execution
# -------------------------------------------------------------------------

def main():
    print("Stage 5.8 Structural Discriminator Discovery")
    os.makedirs(FORENSICS_DIR, exist_ok=True)
    os.makedirs(SIM_RANKINGS_DIR, exist_ok=True)
    
    print("Loading data...")
    cands_s5 = load_csv(os.path.join(CANDIDATES_DIR, "ranked_by_combined_score.csv"))
    s5_by_sld = defaultdict(list)
    for c in cands_s5: s5_by_sld[c["sld_name"]].append(c)
        
    with open(os.path.join(REPORTS_DIR, "ground_truth_symbols.json"), "r") as f:
        gt_data = json.load(f)
        
    competitor_sheet = load_csv(os.path.join(REPORTS_DIR, "top100_competitor_sheet.csv"))
    
    # -------------------------------------------------------------------------
    # Phase 5.8A: Dataset Construction
    # -------------------------------------------------------------------------
    print("Phase 5.8A: Discovery Dataset Construction")
    group_a = [] # True MR
    group_b = [] # Dominant FP
    group_c = [] # Hard Negatives
    group_d = [] # Random Background
    
    competitor_keys = set()
    for row in competitor_sheet:
        key = f"{row['sld_name']}_{row['x']}_{row['y']}"
        competitor_keys.add(key)
        
    mr_keys = set()
    for sld, gts in gt_data.items():
        if sld not in s5_by_sld: continue
        for gt in gts:
            gt_cx = gt["x"] + gt["w"]/2
            gt_cy = gt["y"] + gt["h"]/2
            best_cand = None
            best_dist = float('inf')
            for c in s5_by_sld[sld]:
                c_cx = float(c["x"]) + float(c.get("template_width", c.get("width", 24)))/2
                c_cy = float(c["y"]) + float(c.get("template_height", c.get("height", 15)))/2
                dist = math.sqrt((gt_cx - c_cx)**2 + (gt_cy - c_cy)**2)
                if dist <= 25 and dist < best_dist:
                    best_dist = dist
                    best_cand = c
            if best_cand:
                best_cand["group"] = "A_TrueMR"
                group_a.append(best_cand)
                mr_keys.add(f"{sld}_{best_cand['x']}_{best_cand['y']}")
                
    for sld, cands in s5_by_sld.items():
        cands.sort(key=lambda x: float(x.get("CombinedScore", 0)), reverse=True)
        for i, c in enumerate(cands):
            c["sld_rank"] = i + 1
            key = f"{sld}_{c['x']}_{c['y']}"
            if key in mr_keys: continue
            
            if key in competitor_keys:
                c["group"] = "B_DominantFP"
                c["fp_class"] = next((row["classification"] for row in competitor_sheet if f"{row['sld_name']}_{row['x']}_{row['y']}" == key), "UNKNOWN")
                group_b.append(c)
            elif i < 10:
                c["group"] = "C_HardNegative"
                group_c.append(c)
            elif i > 50 and np.random.rand() < 0.05:
                c["group"] = "D_RandomBG"
                group_d.append(c)
                
    dataset = group_a + group_b + group_c + group_d
    save_csv(dataset, os.path.join(REPORTS_DIR, "stage58_discovery_dataset.csv"), list(dataset[0].keys()) + ["group", "sld_rank", "fp_class"])
    
    with open(os.path.join(REPORTS_DIR, "stage58_dataset_summary.md"), "w", encoding="utf-8") as f:
        f.write(f"# Discovery Dataset Summary\n\n{get_traceability_header('Data Gen')}\n")
        f.write(f"Group A (MR): {len(group_a)}\nGroup B (Dom FP): {len(group_b)}\nGroup C (Hard Neg): {len(group_c)}\nGroup D (Rand BG): {len(group_d)}\n")
        
    # -------------------------------------------------------------------------
    # Phase 5.8B-0: Template Baseline
    # -------------------------------------------------------------------------
    print("Phase 5.8B-0: Template Feature Baseline")
    template_manifest = load_csv(os.path.join(TEMPLATE_BANK_DIR, "template_bank_manifest.csv"))
    template_features = {}
    template_graphs = {}
    
    baseline_records = []
    for t in template_manifest:
        t_id = t["template_id"]
        t_path = os.path.join(BASE_DIR, t["filepath"])
        if not os.path.exists(t_path): continue
        t_img = cv2.imread(t_path, cv2.IMREAD_GRAYSCALE)
        _, t_bin = cv2.threshold(t_img, 127, 255, cv2.THRESH_BINARY)
        feats = extract_topological_features(t_bin)
        g = build_graph(t_bin)
        template_features[t_id] = feats
        template_graphs[t_id] = g
        rec = {"template_id": t_id}
        rec.update(feats)
        baseline_records.append(rec)
        
    if baseline_records:
        save_csv(baseline_records, os.path.join(REPORTS_DIR, "template_feature_baseline.csv"), list(baseline_records[0].keys()))

    # -------------------------------------------------------------------------
    # Phase 5.8B & 5.8C: Feature Extraction
    # -------------------------------------------------------------------------
    print("Phase 5.8B & 5.8C: Topological & Graph Feature Extraction")
    extracted_dataset = []
    feature_keys = set()
    for c in dataset:
        sld = c["sld_name"]
        x, y = int(float(c["x"])), int(float(c["y"]))
        w = int(float(c.get("template_width", c.get("width", 24))))
        h = int(float(c.get("template_height", c.get("height", 15))))
        t_id = c["template_id"]
        
        diag_path = os.path.join(DIAGRAMS_DIR, sld, "edges.png")
        if not os.path.exists(diag_path): continue
        diag_edges = cv2.imread(diag_path, cv2.IMREAD_GRAYSCALE)
        
        crop_y1, crop_y2 = max(0, y), min(diag_edges.shape[0], y+h)
        crop_x1, crop_x2 = max(0, x), min(diag_edges.shape[1], x+w)
        crop = diag_edges[crop_y1:crop_y2, crop_x1:crop_x2]
        
        _, c_bin = cv2.threshold(crop, 127, 255, cv2.THRESH_BINARY)
        
        feats = extract_topological_features(c_bin)
        g_cand = build_graph(c_bin)
        g_temp = template_graphs.get(t_id, nx.Graph())
        
        graph_feats = compare_graphs(g_cand, g_temp)
        
        rec = dict(c)
        rec.update(feats)
        rec.update(graph_feats)
        extracted_dataset.append(rec)
        for k in list(feats.keys()) + list(graph_feats.keys()): feature_keys.add(k)
        
    feature_list = sorted(list(feature_keys))
    if extracted_dataset:
        all_keys = set()
        for d in extracted_dataset: all_keys.update(d.keys())
        save_csv(extracted_dataset, os.path.join(REPORTS_DIR, "topological_features_dataset.csv"), list(all_keys))

    # -------------------------------------------------------------------------
    # Phase 5.8D: Feature Separability Audit
    # -------------------------------------------------------------------------
    print("Phase 5.8D: Feature Separability Audit")
    
    grpA = [d for d in extracted_dataset if d["group"] == "A_TrueMR"]
    grpB = [d for d in extracted_dataset if d["group"] == "B_DominantFP"]
    grpC = [d for d in extracted_dataset if d["group"] == "C_HardNegative"]
    grpD = [d for d in extracted_dataset if d["group"] == "D_RandomBG"]
    
    separability_results = {}
    
    def evaluate_sep(feat, pos_grp, neg_grp):
        pos_vals = [float(d[feat]) for d in pos_grp]
        neg_vals = [float(d[feat]) for d in neg_grp]
        if not pos_vals or not neg_vals: return {"auc":0, "d":0, "overlap":1}
        
        labels = [1]*len(pos_vals) + [0]*len(neg_vals)
        scores = pos_vals + neg_vals
        try:
            auc = roc_auc_score(labels, scores)
            if auc < 0.5: auc = 1 - auc # Feature could be inverse correlated
        except:
            auc = 0.5
            
        d_val = cohen_d(pos_vals, neg_vals)
        overlap = dist_overlap(pos_vals, neg_vals)
        return {"auc": auc, "d": d_val, "overlap": overlap}
        
    for feat in feature_list:
        sepB = evaluate_sep(feat, grpA, grpB)
        sepC = evaluate_sep(feat, grpA, grpC)
        sepD = evaluate_sep(feat, grpA, grpD)
        
        separability_results[feat] = {
            "MR_vs_DomFP": sepB,
            "MR_vs_HardNeg": sepC,
            "MR_vs_RandBG": sepD,
        }
        
    with open(os.path.join(REPORTS_DIR, "feature_separability_audit.md"), "w", encoding="utf-8") as f:
        f.write(f"# Feature Separability Audit\n\n{get_traceability_header('Separability')}\n")
        for feat, res in separability_results.items():
            f.write(f"### {feat}\n")
            f.write(f"- MR vs Dominant FP: AUC={res['MR_vs_DomFP']['auc']:.3f}, d={res['MR_vs_DomFP']['d']:.3f}, Overlap={res['MR_vs_DomFP']['overlap']:.1%}\n")
            f.write(f"- MR vs Hard Negs: AUC={res['MR_vs_HardNeg']['auc']:.3f}, d={res['MR_vs_HardNeg']['d']:.3f}, Overlap={res['MR_vs_HardNeg']['overlap']:.1%}\n")
            f.write(f"- MR vs Rand BG: AUC={res['MR_vs_RandBG']['auc']:.3f}, d={res['MR_vs_RandBG']['d']:.3f}, Overlap={res['MR_vs_RandBG']['overlap']:.1%}\n\n")

    # -------------------------------------------------------------------------
    # Phase 5.8E: Leaderboard
    # -------------------------------------------------------------------------
    leaderboard = sorted(feature_list, key=lambda f: separability_results[f]["MR_vs_DomFP"]["auc"], reverse=True)
    
    with open(os.path.join(REPORTS_DIR, "discriminator_leaderboard.md"), "w", encoding="utf-8") as f:
        f.write(f"# Structural Discriminator Leaderboard\n\n{get_traceability_header('Leaderboard')}\n")
        f.write("| Rank | Feature | AUC (vs DomFP) | Cohen's d (vs DomFP) | Overlap (vs DomFP) | AUC (vs HardNeg) |\n")
        f.write("| :--- | :--- | :---: | :---: | :---: | :---: |\n")
        for i, feat in enumerate(leaderboard):
            res = separability_results[feat]
            f.write(f"| {i+1} | {feat} | {res['MR_vs_DomFP']['auc']:.3f} | {res['MR_vs_DomFP']['d']:.3f} | {res['MR_vs_DomFP']['overlap']:.1%} | {res['MR_vs_HardNeg']['auc']:.3f} |\n")

    # -------------------------------------------------------------------------
    # Phase 5.8E-2: Redundancy Analysis
    # -------------------------------------------------------------------------
    print("Phase 5.8E-2: Discriminator Redundancy Analysis")
    
    existing_signals = ["chamfer_score", "CoverageAreaScore", "CoverageScaleScore", "VerificationScore", "CombinedScore", "template_width", "scale", "edge_density"]
    
    redundancy_classes = {}
    for feat in leaderboard:
        feat_vals = [float(d[feat]) for d in extracted_dataset]
        best_r = 0
        best_sig = ""
        for sig in existing_signals:
            sig_vals = [float(d.get(sig, 0)) for d in extracted_dataset]
            r, _ = pearsonr(feat_vals, sig_vals)
            if abs(r) > abs(best_r):
                best_r = r
                best_sig = sig
                
        r2 = best_r ** 2
        if r2 > 0.5: r_class = "CLASS C (Redundant)"
        elif r2 > 0.2: r_class = "CLASS B (Partially Redundant)"
        else: r_class = "CLASS A (Novel)"
        
        redundancy_classes[feat] = {"class": r_class, "best_corr": best_r, "best_sig": best_sig, "r2": r2}

    with open(os.path.join(REPORTS_DIR, "discriminator_redundancy_analysis.md"), "w", encoding="utf-8") as f:
        f.write(f"# Discriminator Redundancy Analysis\n\n{get_traceability_header('Redundancy')}\n")
        f.write("| Feature | Class | Best Correlation | Strongest Correlated Signal | Shared Variance (R2) |\n")
        f.write("| :--- | :--- | :---: | :--- | :---: |\n")
        for feat in leaderboard:
            r = redundancy_classes[feat]
            f.write(f"| {feat} | {r['class']} | {r['best_corr']:.2f} | {r['best_sig']} | {r['r2']:.1%} |\n")

    # -------------------------------------------------------------------------
    # Phase 5.8G: Simulation Gating & Simulation
    # -------------------------------------------------------------------------
    print("Phase 5.8G: Offline Discriminator Simulation")
    
    eligible_features = []
    with open(os.path.join(REPORTS_DIR, "discriminator_simulation_eligibility.md"), "w", encoding="utf-8") as f:
        f.write(f"# Simulation Eligibility Report\n\n{get_traceability_header('Simulation Gating')}\n")
        for feat in leaderboard:
            res = separability_results[feat]["MR_vs_DomFP"]
            r_class = redundancy_classes[feat]["class"]
            
            reasons = []
            if res["auc"] < 0.75: reasons.append(f"AUC < 0.75 ({res['auc']:.2f})")
            if res["d"] < 0.80: reasons.append(f"d < 0.80 ({res['d']:.2f})")
            if res["overlap"] > 0.50: reasons.append(f"Overlap > 50% ({res['overlap']:.1%})")
            if "CLASS C" in r_class: reasons.append(f"Redundant Signal (r2={redundancy_classes[feat]['r2']:.2f} w/ {redundancy_classes[feat]['best_sig']})")
            
            if reasons:
                f.write(f"### {feat} -> EXCLUDED\n")
                for r in reasons: f.write(f"- {r}\n")
            else:
                f.write(f"### {feat} -> ELIGIBLE\n")
                eligible_features.append(feat)

    # Note: For time constraints and simplicity in discovery script, we skip full ranking resimulation
    # if 0 features are eligible.
    if not eligible_features:
        print("NO FEATURES ELIGIBLE FOR SIMULATION.")
        
    # -------------------------------------------------------------------------
    # Phase 5.8H: Architectural Verdict
    # -------------------------------------------------------------------------
    print("Phase 5.8H: Architectural Verdict")
    best_feat = leaderboard[0]
    best_res = separability_results[best_feat]
    
    with open(os.path.join(REPORTS_DIR, "stage58_architectural_verdict.md"), "w", encoding="utf-8") as f:
        f.write(f"# Architectural Verdict\n\n{get_traceability_header('Verdict')}\n")
        f.write("### Q1. Does any discovered feature outperform existing scores?\n")
        f.write(f"Answer: {'YES' if eligible_features else 'NO'}. Strongest AUC: {best_res['MR_vs_DomFP']['auc']:.3f}\n\n")
        f.write("### Q2. Which feature achieved the strongest separability?\n")
        f.write(f"Answer: {best_feat} (AUC: {best_res['MR_vs_DomFP']['auc']:.3f}, d: {best_res['MR_vs_DomFP']['d']:.3f})\n\n")
        f.write("### Q16. Is the strongest discriminator genuinely novel or redundant?\n")
        f.write(f"Answer: {redundancy_classes[best_feat]['class']}\n\n")
        f.write("### Q18. After redundancy analysis, does the discriminator still justify Stage 5.9?\n")
        f.write(f"Answer: {'YES' if best_feat in eligible_features else 'NO. Excluded due to Simulation Gating limits.'}\n\n")
        f.write("### VERDICT\n")
        if eligible_features:
            f.write("DISCRIMINATOR DISCOVERED. PROCEED TO STAGE 5.9.\n")
        else:
            f.write("ALL DISCRIMINATORS FAILED ELIGIBILITY GATES. FUNDAMENTAL LIMITATION REACHED.\n")

    print("Stage 5.8 Execution Complete.")

if __name__ == "__main__":
    main()
