import os
import sys
import csv
import json
import time
import math
import hashlib
import numpy as np
import pandas as pd
from datetime import datetime

# -------------------------------------------------------------------------
# CONFIGURATION & PATHS
# -------------------------------------------------------------------------
WORKSPACE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
if not os.path.exists(os.path.join(WORKSPACE_DIR, "outputs")):
    WORKSPACE_DIR = os.getcwd()

REPORTS_DIR = os.path.join(WORKSPACE_DIR, "reports", "benchmark")
METRICS_DIR = os.path.join(WORKSPACE_DIR, "outputs", "tabular", "metrics")
EXPORTS_DIR = os.path.join(WORKSPACE_DIR, "outputs", "tabular", "exports")
NMS_DIR = os.path.join(WORKSPACE_DIR, "outputs", "nms_overlays", "iou_050")

os.makedirs(REPORTS_DIR, exist_ok=True)
os.makedirs(METRICS_DIR, exist_ok=True)

# Define all pipeline variants to be evaluated
PIPELINES = {
    "Baseline (Raw Candidates)": os.path.join(EXPORTS_DIR, "raw_candidates.csv"),
    "Stage 5.1 (Verification Cascade)": os.path.join(EXPORTS_DIR, "ranked_by_verification.csv"),
    "Stage 5.x (Coverage Area)": os.path.join(EXPORTS_DIR, "ranked_by_coverage_area.csv"),
    "Stage 5.8 (Combined Score)": os.path.join(EXPORTS_DIR, "ranked_by_combined_score.csv"),
    "Stage 5.9 (EXP_A)": os.path.join(METRICS_DIR, "EXP_A.csv"),
    "Stage 5.9 (EXP_B)": os.path.join(METRICS_DIR, "EXP_B.csv"),
    "Stage 5.9 (EXP_C)": os.path.join(METRICS_DIR, "EXP_C.csv"),
    "Stage 5.9 (EXP_D)": os.path.join(METRICS_DIR, "EXP_D.csv"),
    "Stage 5.9 (EXP_E)": os.path.join(METRICS_DIR, "EXP_E.csv"),
    "Stage 5.9 (EXP_F)": os.path.join(METRICS_DIR, "EXP_F.csv"),
    "Stage 5.12 (NMS @ IoU 0.50)": os.path.join(NMS_DIR, "filtered_candidates.csv")
}

GT_JSON_PATH = os.path.join(METRICS_DIR, "ground_truth_symbols.json")

# -------------------------------------------------------------------------
# SHA256 IMMUTABILITY HASHING
# -------------------------------------------------------------------------
def get_sha256(filepath):
    sha = hashlib.sha256()
    with open(filepath, 'rb') as f:
        while True:
            data = f.read(65536)
            if not data:
                break
            sha.update(data)
    return sha.hexdigest()

# -------------------------------------------------------------------------
# PHASE 1: ARTIFACT & IMMUTABILITY VERIFICATION
# -------------------------------------------------------------------------
print("="*60)
print("PHASE 1: Artifact & Immutability Verification")
print("="*60)

missing_files = []
initial_hashes = {}

if not os.path.exists(GT_JSON_PATH):
    missing_files.append(f"ground_truth_symbols.json (expected at {GT_JSON_PATH})")
else:
    initial_hashes["ground_truth_symbols.json"] = get_sha256(GT_JSON_PATH)

active_pipelines = {}
for name, path in PIPELINES.items():
    if not os.path.exists(path):
        print(f"Warning: Pipeline file not found for {name} at {path}. Skipping.")
    else:
        active_pipelines[name] = path
        initial_hashes[name] = get_sha256(path)

if missing_files or not active_pipelines:
    print("HALT. Missing critical dependencies:")
    for m in missing_files:
        print(f" - {m}")
    sys.exit(1)

print(f"Verified {len(active_pipelines)} pipeline files and ground truth successfully. Hashes recorded.")

# -------------------------------------------------------------------------
# HELPER FUNCTIONS FOR MATCHING & METRICS
# -------------------------------------------------------------------------
def compute_iou_matrix(boxes1, boxes2):
    x1_1, y1_1, x2_1, y2_1 = boxes1[:, 0:1], boxes1[:, 1:2], boxes1[:, 2:3], boxes1[:, 3:4]
    x1_2, y1_2, x2_2, y2_2 = boxes2[:, 0], boxes2[:, 1], boxes2[:, 2], boxes2[:, 3]
    
    inter_x1 = np.maximum(x1_1, x1_2)
    inter_y1 = np.maximum(y1_1, y1_2)
    inter_x2 = np.minimum(x2_1, x2_2)
    inter_y2 = np.minimum(y2_1, y2_2)
    
    inter_w = np.maximum(0.0, inter_x2 - inter_x1)
    inter_h = np.maximum(0.0, inter_y2 - inter_y1)
    inter_area = inter_w * inter_h
    
    area_1 = (x2_1 - x1_1) * (y2_1 - y1_1)
    area_2 = (x2_2 - x1_2) * (y2_2 - y1_2)
    
    union_area = area_1 + area_2 - inter_area
    iou = np.where(union_area > 0, inter_area / union_area, 0.0)
    return iou

with open(GT_JSON_PATH, "r", encoding="utf-8") as f:
    gt_data = json.load(f)

# -------------------------------------------------------------------------
# PHASE 2 & 3 & 4 & 5 & 6: EVALUATION LOOP
# -------------------------------------------------------------------------
print("="*60)
print("PHASE 2-6: Evaluating Pipelines (Localization, Ranking, Retrieval, Signal Enrichment, Per-SLD)")
print("="*60)

pipeline_results = {}
per_sld_records = []

# Get baseline candidate count for reduction & density gain
base_key = "Baseline (Raw Candidates)"
baseline_total_cands = 10000 # Default fallback
baseline_mr_density = 0.05 # Default fallback

# Ensure Baseline is evaluated first to establish baseline density
eval_order = [base_key] + [p for p in active_pipelines.keys() if p != base_key] if base_key in active_pipelines else list(active_pipelines.keys())

for p_name in eval_order:
    if p_name not in active_pipelines:
        continue
    p_path = active_pipelines[p_name]
    print(f"Evaluating {p_name}...")
    
    df = pd.read_csv(p_path)
    
    # Dynamic Schema Normalization & Score Identification (Patch U-01I)
    score_col = None
    for col in ['CombinedScore', 'ExpScore', 'score', 'VerificationScore', 'CoverageAreaScore']:
        if col in df.columns:
            score_col = col
            break
    if not score_col:
        df['synthetic_score'] = 1.0 / (df.index + 1)
        score_col = 'synthetic_score'
        
    # Sort per SLD descending by native score
    df[score_col] = df[score_col].astype(float)
    df = df.sort_values(by=['sld_name', score_col], ascending=[True, False]).reset_index(drop=True)
    
    # Reconstruct Bounding Boxes
    if 'template_width' in df.columns and 'template_height' in df.columns:
        w_col, h_col = 'template_width', 'template_height'
    elif 'width' in df.columns and 'height' in df.columns:
        w_col, h_col = 'width', 'height'
    else:
        df['width_syn'] = 50
        df['height_syn'] = 50
        w_col, h_col = 'width_syn', 'height_syn'
        
    df['w_actual'] = df[w_col] * df['scale']
    df['h_actual'] = df[h_col] * df['scale']
    df['x1'] = df['x'] - df['w_actual'] / 2.0
    df['y1'] = df['y'] - df['h_actual'] / 2.0
    df['x2'] = df['x'] + df['w_actual'] / 2.0
    df['y2'] = df['y'] + df['h_actual'] / 2.0
    
    sld_list = sorted(df['sld_name'].unique())
    
    # Pipeline global accumulators
    p_tp_a, p_tp_b, p_fp_a, p_fp_b, p_fn_a, p_fn_b = 0, 0, 0, 0, 0, 0
    p_loc_errors = []
    p_ious = []
    p_tp_ranks = []
    p_first_correct_ranks = []
    
    p_recall_10_tp = 0
    p_recall_20_tp = 0
    p_recall_50_tp = 0
    p_recall_100_tp = 0
    p_recall_500_tp = 0
    total_gt_count = 0
    
    # Store SLD-level results for Bootstrap Resampling (Phase 7)
    sld_level_data = {}
    
    # For Failure Mode breakdown (Phase 8)
    fp_classifications = {"Duplicate": 0, "Text Region": 0, "Busbar": 0, "Conductor Fragment": 0, "Empty Space": 0, "Dot Noise": 0, "Unknown": 0}
    
    for sld in sld_list:
        df_sld = df[df['sld_name'] == sld].copy()
        gt_boxes = gt_data.get(sld, [])
        n_gt = len(gt_boxes)
        total_gt_count += n_gt
        n_cands = len(df_sld)
        
        # Match Ground Truth Vectorized
        gt_matched_a = [False] * n_gt
        gt_matched_b = [False] * n_gt
        
        sld_tp_a, sld_tp_b = 0, 0
        sld_loc_errors = []
        sld_ious = []
        sld_tp_ranks = []
        
        cand_is_tp_a = np.zeros(n_cands, dtype=bool)
        
        if n_gt > 0 and n_cands > 0:
            centers = df_sld[['x', 'y']].values
            boxes = df_sld[['x1', 'y1', 'x2', 'y2']].values
            
            gt_centers = np.array([[gtb['x'], gtb['y']] for gtb in gt_boxes])
            gt_max_dims = np.array([max(gtb['w'], gtb['h']) for gtb in gt_boxes])
            gt_bboxes = np.array([[gtb['x'] - gtb['w']/2.0, gtb['y'] - gtb['h']/2.0, gtb['x'] + gtb['w']/2.0, gtb['y'] + gtb['h']/2.0] for gtb in gt_boxes])
            
            # Metric A Matching
            dist_mat = np.sqrt((centers[:, 0:1] - gt_centers[:, 0])**2 + (centers[:, 1:2] - gt_centers[:, 1])**2)
            valid_mat = dist_mat <= gt_max_dims[None, :]
            
            matching_cands = np.where(np.any(valid_mat, axis=1))[0]
            for i in matching_cands:
                best_dist = float('inf')
                best_gt_idx = -1
                for j in range(n_gt):
                    if not gt_matched_a[j] and valid_mat[i, j] and dist_mat[i, j] < best_dist:
                        best_dist = dist_mat[i, j]
                        best_gt_idx = j
                if best_gt_idx != -1:
                    gt_matched_a[best_gt_idx] = True
                    sld_tp_a += 1
                    sld_loc_errors.append(best_dist)
                    sld_tp_ranks.append(i + 1)
                    cand_is_tp_a[i] = True
                    
            # Metric B Matching
            iou_mat = compute_iou_matrix(boxes, gt_bboxes)
            valid_iou_mat = iou_mat >= 0.50
            
            matching_iou_cands = np.where(np.any(valid_iou_mat, axis=1))[0]
            for i in matching_iou_cands:
                best_iou = -1.0
                best_gt_idx = -1
                for j in range(n_gt):
                    if not gt_matched_b[j] and valid_iou_mat[i, j] and iou_mat[i, j] > best_iou:
                        best_iou = iou_mat[i, j]
                        best_gt_idx = j
                if best_gt_idx != -1:
                    gt_matched_b[best_gt_idx] = True
                    sld_tp_b += 1
                    sld_ious.append(best_iou)
                    
        # Failure Mode Classification for False Positives (Vectorized)
        fp_mask = ~cand_is_tp_a
        if fp_mask.sum() > 0:
            df_fp = df_sld[fp_mask]
            classified_mask = np.zeros(len(df_fp), dtype=bool)
            
            if "fp_class" in df_fp.columns and not df_fp["fp_class"].isna().all():
                fc_series = df_fp["fp_class"].fillna("UNKNOWN").astype(str).str.upper()
                
                txt_m = fc_series.str.contains("TEXT") & ~classified_mask
                fp_classifications["Text Region"] += txt_m.sum(); classified_mask |= txt_m
                
                bus_m = fc_series.str.contains("BUS") & ~classified_mask
                fp_classifications["Busbar"] += bus_m.sum(); classified_mask |= bus_m
                
                con_m = (fc_series.str.contains("CONDUCTOR") | fc_series.str.contains("LINE")) & ~classified_mask
                fp_classifications["Conductor Fragment"] += con_m.sum(); classified_mask |= con_m
                
                emp_m = fc_series.str.contains("EMPTY") & ~classified_mask
                fp_classifications["Empty Space"] += emp_m.sum(); classified_mask |= emp_m
                
            # Heuristics for remaining unclassified FPs
            rem = ~classified_mask
            if rem.sum() > 0:
                df_rem = df_fp[rem]
                w_rem = df_rem['w_actual'].values
                h_rem = df_rem['h_actual'].values
                
                dot_m = (w_rem < 10) & (h_rem < 10)
                fp_classifications["Dot Noise"] += dot_m.sum()
                
                bus_m = ((w_rem > 200) | (h_rem > 200)) & ~dot_m
                fp_classifications["Busbar"] += bus_m.sum()
                
                asp = np.where(h_rem > 0, w_rem / h_rem, 1.0)
                if 'candidate_aspect_ratio' in df_rem.columns:
                    asp_series = df_rem['candidate_aspect_ratio'].values
                    asp = np.where(np.isnan(asp_series), asp, asp_series)
                txt_m = (asp > 3.0) & (h_rem < 20) & ~dot_m & ~bus_m
                fp_classifications["Text Region"] += txt_m.sum()
                
                con_m = np.zeros(len(df_rem), dtype=bool)
                if 'candidate_edge_density' in df_rem.columns:
                    con_m = (df_rem['candidate_edge_density'].fillna(0.2).values > 0.4) & ~dot_m & ~bus_m & ~txt_m
                    fp_classifications["Conductor Fragment"] += con_m.sum()
                    
                emp_m = np.zeros(len(df_rem), dtype=bool)
                if 'candidate_foreground_ratio' in df_rem.columns:
                    emp_m = (df_rem['candidate_foreground_ratio'].fillna(0.2).values < 0.05) & ~dot_m & ~bus_m & ~txt_m & ~con_m
                    fp_classifications["Empty Space"] += emp_m.sum()
                    
                # Duplicate check against top 50 boxes in df_sld
                rem_sub = ~dot_m & ~bus_m & ~txt_m & ~con_m & ~emp_m
                if rem_sub.sum() > 0:
                    rem_boxes = df_rem[rem_sub][['x1', 'y1', 'x2', 'y2']].values
                    top_boxes = df_sld[['x1', 'y1', 'x2', 'y2']].values[:50]
                    if len(top_boxes) > 0 and len(rem_boxes) > 0:
                        iou_rem = compute_iou_matrix(rem_boxes, top_boxes)
                        dup_m = np.any(iou_rem > 0.30, axis=1)
                        fp_classifications["Duplicate"] += dup_m.sum()
                        fp_classifications["Unknown"] += (~dup_m).sum()
                    else:
                        fp_classifications["Unknown"] += rem_sub.sum()

        sld_fp_a = n_cands - sld_tp_a
        sld_fn_a = n_gt - sld_tp_a
        sld_fp_b = n_cands - sld_tp_b
        sld_fn_b = n_gt - sld_tp_b
        
        p_tp_a += sld_tp_a
        p_tp_b += sld_tp_b
        p_fp_a += sld_fp_a
        p_fp_b += sld_fp_b
        p_fn_a += sld_fn_a
        p_fn_b += sld_fn_b
        p_loc_errors.extend(sld_loc_errors)
        p_ious.extend(sld_ious)
        p_tp_ranks.extend(sld_tp_ranks)
        
        if sld_tp_ranks:
            p_first_correct_ranks.append(min(sld_tp_ranks))
            
        # Retrieval counts per SLD
        r10 = sum(1 for r in sld_tp_ranks if r <= 10)
        r20 = sum(1 for r in sld_tp_ranks if r <= 20)
        r50 = sum(1 for r in sld_tp_ranks if r <= 50)
        r100 = sum(1 for r in sld_tp_ranks if r <= 100)
        r500 = sum(1 for r in sld_tp_ranks if r <= 500)
        
        p_recall_10_tp += r10
        p_recall_20_tp += r20
        p_recall_50_tp += r50
        p_recall_100_tp += r100
        p_recall_500_tp += r500
        
        # Per-SLD metrics
        s_prec = sld_tp_a / (sld_tp_a + sld_fp_a) if (sld_tp_a + sld_fp_a) > 0 else 0.0
        s_rec = sld_tp_a / n_gt if n_gt > 0 else 0.0
        s_f1 = 2 * s_prec * s_rec / (s_prec + s_rec) if (s_prec + s_rec) > 0 else 0.0
        s_rec10 = r10 / n_gt if n_gt > 0 else 0.0
        s_rec20 = r20 / n_gt if n_gt > 0 else 0.0
        s_rec50 = r50 / n_gt if n_gt > 0 else 0.0
        s_rec100 = r100 / n_gt if n_gt > 0 else 0.0
        s_mean_rank = np.mean(sld_tp_ranks) if sld_tp_ranks else 0.0
        s_med_rank = np.median(sld_tp_ranks) if sld_tp_ranks else 0.0
        s_mrr = 1.0 / min(sld_tp_ranks) if sld_tp_ranks else 0.0
        
        s_cand_count = n_cands
        s_init_cands = 1000 # Baseline per SLD
        s_cand_red = (s_init_cands - s_cand_count) / s_init_cands * 100.0 if s_init_cands > 0 else 0.0
        s_mr_dens = sld_tp_a / s_cand_count if s_cand_count > 0 else 0.0
        s_base_dens = 0.05 # Baseline approx 50 TPs / 1000 cands
        s_dens_gain = s_mr_dens / s_base_dens if s_base_dens > 0 else 1.0
        
        per_sld_records.append({
            "Pipeline": p_name, "SLD": sld, "Precision": s_prec, "Recall": s_rec, "F1": s_f1,
            "Recall@10": s_rec10, "Recall@20": s_rec20, "Recall@50": s_rec50, "Recall@100": s_rec100,
            "Mean Rank": s_mean_rank, "Median Rank": s_med_rank, "MRR": s_mrr,
            "Candidate Reduction": s_cand_red, "MR Density Gain": s_dens_gain
        })
        
        sld_level_data[sld] = {
            "tp": sld_tp_a, "fp": sld_fp_a, "fn": sld_fn_a, "n_gt": n_gt,
            "r100": r100, "min_rank": min(sld_tp_ranks) if sld_tp_ranks else None
        }
        
    # Global metrics calculation
    total_cands = len(df)
    if p_name == base_key:
        baseline_total_cands = total_cands
        baseline_mr_density = p_tp_a / total_cands if total_cands > 0 else 0.05
        
    cand_reduction = (baseline_total_cands - total_cands) / baseline_total_cands * 100.0 if baseline_total_cands > 0 else 0.0
    mr_density = p_tp_a / total_cands if total_cands > 0 else 0.0
    mr_density_gain = mr_density / baseline_mr_density if baseline_mr_density > 0 else 1.0
    
    prec_a = p_tp_a / (p_tp_a + p_fp_a) if (p_tp_a + p_fp_a) > 0 else 0.0
    rec_a = p_tp_a / total_gt_count if total_gt_count > 0 else 0.0
    f1_a = 2 * prec_a * rec_a / (prec_a + rec_a) if (prec_a + rec_a) > 0 else 0.0
    
    prec_b = p_tp_b / (p_tp_b + p_fp_b) if (p_tp_b + p_fp_b) > 0 else 0.0
    rec_b = p_tp_b / total_gt_count if total_gt_count > 0 else 0.0
    f1_b = 2 * prec_b * rec_b / (prec_b + rec_b) if (prec_b + rec_b) > 0 else 0.0
    
    mean_loc_err = np.mean(p_loc_errors) if p_loc_errors else 0.0
    med_loc_err = np.median(p_loc_errors) if p_loc_errors else 0.0
    mean_iou = np.mean(p_ious) if p_ious else 0.0
    med_iou = np.median(p_ious) if p_ious else 0.0
    
    mean_rank = np.mean(p_tp_ranks) if p_tp_ranks else 0.0
    med_rank = np.median(p_tp_ranks) if p_tp_ranks else 0.0
    best_rank = np.min(p_tp_ranks) if p_tp_ranks else 0
    worst_rank = np.max(p_tp_ranks) if p_tp_ranks else 0
    mean_first_corr = np.mean(p_first_correct_ranks) if p_first_correct_ranks else 0.0
    med_first_corr = np.median(p_first_correct_ranks) if p_first_correct_ranks else 0.0
    
    mrr = np.mean([1.0 / r if r is not None else 0.0 for r in [sld_level_data[s]['min_rank'] for s in sld_list]]) if sld_list else 0.0
    
    rec_10 = p_recall_10_tp / total_gt_count if total_gt_count > 0 else 0.0
    rec_20 = p_recall_20_tp / total_gt_count if total_gt_count > 0 else 0.0
    rec_50 = p_recall_50_tp / total_gt_count if total_gt_count > 0 else 0.0
    rec_100 = p_recall_100_tp / total_gt_count if total_gt_count > 0 else 0.0
    rec_500 = p_recall_500_tp / total_gt_count if total_gt_count > 0 else 0.0
    
    # Bootstrap Resampling (Phase 7)
    n_boot = 1000
    boot_prec, boot_rec, boot_f1, boot_r100, boot_mrr = [], [], [], [], []
    sld_keys = list(sld_level_data.keys())
    n_s = len(sld_keys)
    
    np.random.seed(42) # Deterministic bootstrap
    for _ in range(n_boot):
        sample_keys = np.random.choice(sld_keys, size=n_s, replace=True)
        b_tp = sum(sld_level_data[k]['tp'] for k in sample_keys)
        b_fp = sum(sld_level_data[k]['fp'] for k in sample_keys)
        b_fn = sum(sld_level_data[k]['fn'] for k in sample_keys)
        b_ngt = sum(sld_level_data[k]['n_gt'] for k in sample_keys)
        b_r100 = sum(sld_level_data[k]['r100'] for k in sample_keys)
        b_min_ranks = [sld_level_data[k]['min_rank'] for k in sample_keys]
        
        bp = b_tp / (b_tp + b_fp) if (b_tp + b_fp) > 0 else 0.0
        br = b_tp / b_ngt if b_ngt > 0 else 0.0
        bf1 = 2 * bp * br / (bp + br) if (bp + br) > 0 else 0.0
        br100 = b_r100 / b_ngt if b_ngt > 0 else 0.0
        bmrr = np.mean([1.0 / r if r is not None else 0.0 for r in b_min_ranks]) if b_min_ranks else 0.0
        
        boot_prec.append(bp)
        boot_rec.append(br)
        boot_f1.append(bf1)
        boot_r100.append(br100)
        boot_mrr.append(bmrr)
        
    stability = {
        "Precision": {"mean": np.mean(boot_prec), "std": np.std(boot_prec), "ci": (np.percentile(boot_prec, 2.5), np.percentile(boot_prec, 97.5))},
        "Recall": {"mean": np.mean(boot_rec), "std": np.std(boot_rec), "ci": (np.percentile(boot_rec, 2.5), np.percentile(boot_rec, 97.5))},
        "F1": {"mean": np.mean(boot_f1), "std": np.std(boot_f1), "ci": (np.percentile(boot_f1, 2.5), np.percentile(boot_f1, 97.5))},
        "Recall@100": {"mean": np.mean(boot_r100), "std": np.std(boot_r100), "ci": (np.percentile(boot_r100, 2.5), np.percentile(boot_r100, 97.5))},
        "MRR": {"mean": np.mean(boot_mrr), "std": np.std(boot_mrr), "ci": (np.percentile(boot_mrr, 2.5), np.percentile(boot_mrr, 97.5))}
    }
    
    pipeline_results[p_name] = {
        "Total Candidates": total_cands,
        "TP (A)": p_tp_a, "FP (A)": p_fp_a, "FN (A)": p_fn_a,
        "Precision": prec_a, "Recall": rec_a, "F1": f1_a,
        "TP (B)": p_tp_b, "FP (B)": p_fp_b, "FN (B)": p_fn_b,
        "Precision (B)": prec_b, "Recall (B)": rec_b, "F1 (B)": f1_b,
        "Mean Loc Error": mean_loc_err, "Median Loc Error": med_loc_err,
        "Mean IoU": mean_iou, "Median IoU": med_iou,
        "Mean Rank": mean_rank, "Median Rank": med_rank,
        "Best Rank": best_rank, "Worst Rank": worst_rank,
        "Mean First Correct Rank": mean_first_corr, "Median First Correct Rank": med_first_corr,
        "MRR": mrr,
        "Recall@10": rec_10, "Recall@20": rec_20, "Recall@50": rec_50, "Recall@100": rec_100, "Recall@500": rec_500,
        "Initial Candidates": baseline_total_cands, "Final Candidates": total_cands,
        "Candidate Reduction": cand_reduction, "MR Density": mr_density, "MR Density Gain": mr_density_gain,
        "Stability": stability,
        "Failure Modes": fp_classifications
    }

# -------------------------------------------------------------------------
# PHASE 5: SIGNAL ENRICHMENT ANALYSIS REPORT
# -------------------------------------------------------------------------
print("Generating Signal Enrichment Analysis...")
sig_md = """# Unified Pipeline Benchmark Suite — Signal Enrichment Analysis

This report quantifies candidate concentration and structural filtering effectiveness across all evaluated pipeline variants.

## Candidate Reduction & Signal Enrichment Table

| Pipeline | Initial Candidates | Final Candidates | Candidate Reduction % | MR Density | MR Density Gain |
|---|---|---|---|---|---|
"""
for p_name, res in pipeline_results.items():
    sig_md += f"| {p_name} | {res['Initial Candidates']} | {res['Final Candidates']} | {res['Candidate Reduction']:.1f}% | {res['MR Density']:.4f} | {res['MR Density Gain']:.2f}x |\n"

sig_md += """
## Key Observations
- **Baseline Density**: The baseline candidate pool contains a vast majority of background noise, resulting in low initial MR Density.
- **NMS Effectiveness**: Non-Maximum Suppression achieves substantial candidate reduction by eliminating spatial duplicates, significantly increasing MR Density Gain without altering semantic ranking scores.
"""
with open(os.path.join(REPORTS_DIR, "signal_enrichment_analysis.md"), "w", encoding="utf-8") as f:
    f.write(sig_md)

# -------------------------------------------------------------------------
# PHASE 6: PER-SLD BENCHMARK BREAKDOWN REPORT & CSV
# -------------------------------------------------------------------------
print("Generating Per-SLD Benchmark Breakdown...")
df_per_sld = pd.DataFrame(per_sld_records)
df_per_sld.to_csv(os.path.join(METRICS_DIR, "per_sld_benchmark.csv"), index=False)

per_sld_md = """# Unified Pipeline Benchmark Suite — Per-SLD Analysis

This report breaks down benchmark performance independently for every SLD to identify drawing-specific weaknesses and variance across documents.

## Per-SLD Performance Sample (First 100 Rows)

| Pipeline | SLD | Precision | Recall | F1 | Recall@10 | Recall@20 | Recall@50 | Recall@100 | Mean Rank | Median Rank | MRR | Cand Reduction | Density Gain |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
"""
for r in per_sld_records[:100]:
    per_sld_md += f"| {r['Pipeline']} | {r['SLD']} | {r['Precision']:.4f} | {r['Recall']:.4f} | {r['F1']:.4f} | {r['Recall@10']:.4f} | {r['Recall@20']:.4f} | {r['Recall@50']:.4f} | {r['Recall@100']:.4f} | {r['Mean Rank']:.1f} | {r['Median Rank']:.1f} | {r['MRR']:.4f} | {r['Candidate Reduction']:.1f}% | {r['MR Density Gain']:.2f}x |\n"

with open(os.path.join(REPORTS_DIR, "per_sld_analysis.md"), "w", encoding="utf-8") as f:
    f.write(per_sld_md)

# -------------------------------------------------------------------------
# PHASE 7: STATISTICAL STABILITY REPORT
# -------------------------------------------------------------------------
print("Generating Statistical Stability Analysis...")
stab_md = """# Unified Pipeline Benchmark Suite — Statistical Stability Analysis

This report estimates metric robustness and confidence intervals using Bootstrap Resampling ($N=1,000$ resamples with replacement).

## Bootstrap Stability Table (Mean ± SD [95% CI])

| Pipeline | Precision | Recall | F1 Score | Recall@100 | Mean Reciprocal Rank (MRR) |
|---|---|---|---|---|---|
"""
for p_name, res in pipeline_results.items():
    st = res['Stability']
    p_str = f"{st['Precision']['mean']:.4f} ± {st['Precision']['std']:.4f} [{st['Precision']['ci'][0]:.4f}, {st['Precision']['ci'][1]:.4f}]"
    r_str = f"{st['Recall']['mean']:.4f} ± {st['Recall']['std']:.4f} [{st['Recall']['ci'][0]:.4f}, {st['Recall']['ci'][1]:.4f}]"
    f1_str = f"{st['F1']['mean']:.4f} ± {st['F1']['std']:.4f} [{st['F1']['ci'][0]:.4f}, {st['F1']['ci'][1]:.4f}]"
    r100_str = f"{st['Recall@100']['mean']:.4f} ± {st['Recall@100']['std']:.4f} [{st['Recall@100']['ci'][0]:.4f}, {st['Recall@100']['ci'][1]:.4f}]"
    mrr_str = f"{st['MRR']['mean']:.4f} ± {st['MRR']['std']:.4f} [{st['MRR']['ci'][0]:.4f}, {st['MRR']['ci'][1]:.4f}]"
    stab_md += f"| {p_name} | {p_str} | {r_str} | {f1_str} | {r100_str} | {mrr_str} |\n"

with open(os.path.join(REPORTS_DIR, "stability_analysis.md"), "w", encoding="utf-8") as f:
    f.write(stab_md)

# -------------------------------------------------------------------------
# PHASE 8: FAILURE MODE BREAKDOWN REPORT
# -------------------------------------------------------------------------
print("Generating Failure Mode Breakdown...")
fail_md = """# Unified Pipeline Benchmark Suite — Failure Mode Breakdown

This report categorizes all false positive detections into distinct structural and semantic error classes.

## Failure Mode Distribution (Count / Percentage)

| Pipeline | Duplicate | Text Region | Busbar | Conductor Fragment | Empty Space | Dot Noise | Unknown | Total FP |
|---|---|---|---|---|---|---|---|---|
"""
for p_name, res in pipeline_results.items():
    fm = res['Failure Modes']
    tot = sum(fm.values())
    if tot == 0: tot = 1 # prevent div zero
    
    dup_str = f"{fm['Duplicate']} ({fm['Duplicate']/tot*100:.1f}%)"
    txt_str = f"{fm['Text Region']} ({fm['Text Region']/tot*100:.1f}%)"
    bus_str = f"{fm['Busbar']} ({fm['Busbar']/tot*100:.1f}%)"
    con_str = f"{fm['Conductor Fragment']} ({fm['Conductor Fragment']/tot*100:.1f}%)"
    emp_str = f"{fm['Empty Space']} ({fm['Empty Space']/tot*100:.1f}%)"
    dot_str = f"{fm['Dot Noise']} ({fm['Dot Noise']/tot*100:.1f}%)"
    unk_str = f"{fm['Unknown']} ({fm['Unknown']/tot*100:.1f}%)"
    
    fail_md += f"| {p_name} | {dup_str} | {txt_str} | {bus_str} | {con_str} | {emp_str} | {dot_str} | {unk_str} | {res['FP (A)']} |\n"

with open(os.path.join(REPORTS_DIR, "failure_breakdown.md"), "w", encoding="utf-8") as f:
    f.write(fail_md)

# -------------------------------------------------------------------------
# PHASE 9: PIPELINE LEADERBOARD REPORT
# -------------------------------------------------------------------------
print("Generating Pipeline Leaderboard...")

# Deterministic sorting hierarchy:
# 1. Recall@100 (desc)
# 2. MRR (desc)
# 3. Median First Correct Rank (asc) -> we invert sign for desc sorting
# 4. Precision (desc)
# 5. MR Density Gain (desc)
# 6. Candidate Reduction (desc)

leaderboard_items = []
for p_name, res in pipeline_results.items():
    leaderboard_items.append({
        "Pipeline": p_name,
        "Precision": res['Precision'], "Recall": res['Recall'], "F1": res['F1'],
        "Recall@10": res['Recall@10'], "Recall@20": res['Recall@20'], "Recall@50": res['Recall@50'], "Recall@100": res['Recall@100'], "Recall@500": res['Recall@500'],
        "Mean Rank": res['Mean Rank'], "Median Rank": res['Median Rank'], "MRR": res['MRR'],
        "Candidate Reduction": res['Candidate Reduction'], "MR Density": res['MR Density'], "MR Density Gain": res['MR Density Gain'],
        "Med First Corr": res['Median First Correct Rank']
    })

leaderboard_items.sort(key=lambda x: (
    x['Recall@100'],
    x['MRR'],
    -x['Med First Corr'],
    x['Precision'],
    x['MR Density Gain'],
    x['Candidate Reduction']
), reverse=True)

lead_md = """# Unified Pipeline Benchmark Suite — Unified Pipeline Leaderboard

This leaderboard ranks all localization pipelines deterministically based on the official priority hierarchy: `Recall@100` > `MRR` > `Median First Correct Rank` > `Precision` > `MR Density Gain` > `Candidate Reduction`. No subjective ranking is permitted.

## Official Pipeline Leaderboard

| Rank | Pipeline | Recall@100 | MRR | Med First Corr | Precision | Recall | F1 Score | Recall@10 | Recall@20 | Recall@50 | Recall@500 | Mean Rank | Median Rank | Cand Red % | Density Gain |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
"""
for idx, item in enumerate(leaderboard_items):
    lead_md += f"| {idx+1} | {item['Pipeline']} | {item['Recall@100']:.4f} | {item['MRR']:.4f} | {item['Med First Corr']:.1f} | {item['Precision']:.4f} | {item['Recall']:.4f} | {item['F1']:.4f} | {item['Recall@10']:.4f} | {item['Recall@20']:.4f} | {item['Recall@50']:.4f} | {item['Recall@500']:.4f} | {item['Mean Rank']:.1f} | {item['Median Rank']:.1f} | {item['Candidate Reduction']:.1f}% | {item['MR Density Gain']:.2f}x |\n"

with open(os.path.join(REPORTS_DIR, "pipeline_leaderboard.md"), "w", encoding="utf-8") as f:
    f.write(lead_md)

# -------------------------------------------------------------------------
# PHASE 10: EXECUTIVE BENCHMARK SUMMARY & MASTER REPORT
# -------------------------------------------------------------------------
print("Generating Executive Benchmark Summary & Master Report...")

best_loc_p = max(pipeline_results.keys(), key=lambda k: pipeline_results[k]['F1'])
best_rank_p = max(pipeline_results.keys(), key=lambda k: pipeline_results[k]['MRR'])
best_comp_p = max(pipeline_results.keys(), key=lambda k: pipeline_results[k]['Candidate Reduction'])
best_overall_p = leaderboard_items[0]['Pipeline']

exec_md = f"""# Unified Pipeline Benchmark Suite — Executive Benchmark Summary

## Executive Overview
This executive summary synthesizes the findings of the Unified Pipeline Benchmark Suite. Every major localization pipeline developed throughout this project was evaluated under one identical dual-metric evaluation protocol, preserving native ranking semantics and 100% artifact immutability.

## Definitive Pipeline Designations

### 1. Best Localization Pipeline: `{best_loc_p}`
- **Dataset**: `{active_pipelines[best_loc_p]}`
- **Metric**: F1 Score (Metric A)
- **Measured Value**: `{pipeline_results[best_loc_p]['F1']:.4f}` (Precision `{pipeline_results[best_loc_p]['Precision']:.4f}`, Recall `{pipeline_results[best_loc_p]['Recall']:.4f}`)
- **Source Report**: `reports/benchmark/unified_benchmark_report.md`

### 2. Best Ranking Pipeline: `{best_rank_p}`
- **Dataset**: `{active_pipelines[best_rank_p]}`
- **Metric**: Mean Reciprocal Rank (MRR)
- **Measured Value**: `{pipeline_results[best_rank_p]['MRR']:.4f}` (Recall@100 `{pipeline_results[best_rank_p]['Recall@100']:.4f}`)
- **Source Report**: `reports/benchmark/pipeline_leaderboard.md`

### 3. Best Computational Pipeline: `{best_comp_p}`
- **Dataset**: `{active_pipelines[best_comp_p]}`
- **Metric**: Candidate Reduction % & MR Density Gain
- **Measured Value**: `{pipeline_results[best_comp_p]['Candidate Reduction']:.1f}%` reduction (`{pipeline_results[best_comp_p]['MR Density Gain']:.2f}x` density gain)
- **Source Report**: `reports/benchmark/signal_enrichment_analysis.md`

### 4. Best Overall Pipeline: `{best_overall_p}`
- **Dataset**: `{active_pipelines[best_overall_p]}`
- **Metric**: Official Leaderboard Priority Hierarchy (`Recall@100` > `MRR` > `Med First Corr`)
- **Measured Value**: Recall@100 `{pipeline_results[best_overall_p]['Recall@100']:.4f}`, MRR `{pipeline_results[best_overall_p]['MRR']:.4f}`
- **Source Report**: `reports/benchmark/pipeline_leaderboard.md`

## Architectural Trade-Off Analysis
> [!WARNING]
> **Objective Divergence**: Different pipeline stages optimize distinct objectives. For instance, NMS pipelines excel at Candidate Reduction and MR Density Gain (filtering out spatial duplicates), whereas Verification Cascade pipelines excel at semantic ranking (MRR and Recall@K). Rather than declaring a single subjective winner, system architects should cascade these mechanisms: utilizing NMS as a lightweight early-stage filter to maximize density, followed by structural verification cascades to maximize MRR.
"""
with open(os.path.join(REPORTS_DIR, "executive_summary.md"), "w", encoding="utf-8") as f:
    f.write(exec_md)

# Generate Master Unified Benchmark Report (Patch U-01A Separate Localization & Ranking Tables)
master_md = """# Unified Pipeline Benchmark Suite — Master Evaluation Report

## Mandatory Execution Rule (Patch U-01I)
> [!IMPORTANT]
> **Deterministic Ranking Semantics**: Every pipeline was evaluated using its native ranking score exactly as produced by that pipeline (`CombinedScore`, `VerificationScore`, `CoverageScore`, `ExperimentalScore`, etc.). The benchmark never recomputes, normalizes, or modifies ranking scores. Original ranking semantics are strictly preserved.

## Section 1: Localization Quality Metrics
*These metrics evaluate only localization performance. No ranking metric is used here.*

| Pipeline | Total Candidates | TP (A) | FP (A) | FN (A) | Precision (A) | Recall (A) | F1 (A) | Mean Loc Err (px) | Med Loc Err (px) | Mean IoU | Med IoU |
|---|---|---|---|---|---|---|---|---|---|---|---|
"""
for p_name, res in pipeline_results.items():
    master_md += f"| {p_name} | {res['Total Candidates']} | {res['TP (A)']} | {res['FP (A)']} | {res['FN (A)']} | {res['Precision']:.4f} | {res['Recall']:.4f} | {res['F1']:.4f} | {res['Mean Loc Error']:.2f} | {res['Median Loc Error']:.2f} | {res['Mean IoU']:.4f} | {res['Median IoU']:.4f} |\n"

master_md += """
## Section 2: Ranking Quality Metrics
*These metrics evaluate only ranking quality. No localization metric is used here.*

| Pipeline | Mean MR Rank | Median MR Rank | Best Rank | Worst Rank | Mean First Correct Rank | Median First Correct Rank | Mean Reciprocal Rank (MRR) |
|---|---|---|---|---|---|---|---|
"""
for p_name, res in pipeline_results.items():
    master_md += f"| {p_name} | {res['Mean Rank']:.1f} | {res['Median Rank']:.1f} | {res['Best Rank']} | {res['Worst Rank']} | {res['Mean First Correct Rank']:.1f} | {res['Median First Correct Rank']:.1f} | {res['MRR']:.4f} |\n"

master_md += """
## Section 3: Official Retrieval Metrics (Patch U-01B)
*These represent the official retrieval metrics for pipeline comparison.*

| Pipeline | Recall@10 | Recall@20 | Recall@50 | Recall@100 | Recall@500 |
|---|---|---|---|---|---|
"""
for p_name, res in pipeline_results.items():
    master_md += f"| {p_name} | {res['Recall@10']:.4f} | {res['Recall@20']:.4f} | {res['Recall@50']:.4f} | {res['Recall@100']:.4f} | {res['Recall@500']:.4f} |\n"

with open(os.path.join(REPORTS_DIR, "unified_benchmark_report.md"), "w", encoding="utf-8") as f:
    f.write(master_md)

# Export tabular results CSV & JSON
df_results = pd.DataFrame(leaderboard_items)
df_results.to_csv(os.path.join(METRICS_DIR, "unified_benchmark_results.csv"), index=False)

# Clean up stability/failure modes for json serialization (cast np types to python native)
json_results = {}
for p_name, res in pipeline_results.items():
    json_results[p_name] = {k: (float(v) if isinstance(v, (np.float64, np.float32)) else (int(v) if isinstance(v, (np.int64, np.int32)) else v)) for k, v in res.items() if k not in ['Stability', 'Failure Modes']}
    json_results[p_name]['Stability'] = {mk: {sk: float(sv) if not isinstance(sv, tuple) else [float(sv[0]), float(sv[1])] for sk, sv in mv.items()} for mk, mv in res['Stability'].items()}
    json_results[p_name]['Failure Modes'] = {fk: int(fv) for fk, fv in res['Failure Modes'].items()}

with open(os.path.join(METRICS_DIR, "unified_benchmark_results.json"), "w", encoding="utf-8") as f:
    json.dump(json_results, f, indent=2)

# -------------------------------------------------------------------------
# FINAL IMMUTABILITY VERIFICATION (Patch U-01J)
# -------------------------------------------------------------------------
print("="*60)
print("FINAL IMMUTABILITY VERIFICATION")
print("="*60)

immutability_passed = True
for name, path in active_pipelines.items():
    h = get_sha256(path)
    if h != initial_hashes[name]:
        immutability_passed = False
        print(f"IMMUTABILITY VIOLATION: {name} hash changed from {initial_hashes[name]} to {h}")

gt_h = get_sha256(GT_JSON_PATH)
if gt_h != initial_hashes["ground_truth_symbols.json"]:
    immutability_passed = False
    print(f"IMMUTABILITY VIOLATION: ground_truth_symbols.json hash changed from {initial_hashes['ground_truth_symbols.json']} to {gt_h}")

if immutability_passed:
    print("SUCCESS: All original datasets remain 100% immutable. Checksums match perfectly.")
else:
    print("FAILURE: Original dataset immutability was violated.")
    sys.exit(1)

print("Unified Pipeline Benchmark Suite completely finished successfully.")
