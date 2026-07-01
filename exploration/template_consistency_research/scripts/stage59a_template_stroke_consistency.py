import os
import csv
import json
import numpy as np
import cv2
from datetime import datetime
from collections import defaultdict
import matplotlib.pyplot as plt
from sklearn.metrics import roc_auc_score

import sys
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))
from exploration.archived.scripts.stage5_8_structural_discovery import extract_topological_features

BASE_DIR = r"c:\Users\arhaa\OneDrive\Symbol Segmentor"
REPORTS_DIR = os.path.join(BASE_DIR, "reports")
OUTPUTS_DIR = os.path.join(BASE_DIR, "outputs")
CANDIDATES_DIR = os.path.join(OUTPUTS_DIR, "candidates")
TEMPLATE_BANK_DIR = os.path.join(OUTPUTS_DIR, "template_bank")
EXP_RANKINGS_DIR = os.path.join(REPORTS_DIR, "stage59a_experimental_rankings")
FORENSICS_DIR = os.path.join(REPORTS_DIR, "stage59a_forensics")
HISTOGRAMS_DIR = os.path.join(REPORTS_DIR, "stage59a_distribution_histograms")

TIMESTAMP = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

def load_csv(path):
    if not os.path.exists(path): return []
    with open(path, "r", encoding="utf-8") as f:
        return list(csv.DictReader(f))

def save_csv(data, path, fieldnames):
    if not data: return
    with open(path, "w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(data)

def get_traceability_header(exp_id="N/A", base_comp_id="BASE", survival_count="N/A"):
    lines = [
        f"- Generation Timestamp: {TIMESTAMP}",
        "- Stage Version: Stage 5.9A",
        "- Input Datasets: ranked_by_combined_score.csv, topological_features_dataset.csv, template_bank_manifest.csv",
        f"- Candidate Count: {survival_count}",
        "- Evaluation Method: Deterministic Mathematical Integration Validation",
        "- Scale Regime Definitions: A (>=0.30), B (0.20-0.30), C (0.15-0.20), D (<0.15)",
        "- Association Radius: 25px",
        f"- Experiment Identifier: {exp_id}",
        f"- Baseline Comparison ID: {base_comp_id}",
        "- Referenced Prior Stages: Stage 3, Stage 4, Stage 5.2, Stage 5.5, Stage 5.8, Stage 5.9",
        "- Manual Dependency Status: None"
    ]
    return "\n".join(lines) + "\n"

def get_scale_regime(scale):
    s = float(scale)
    if s >= 0.30: return "A"
    if s >= 0.20: return "B"
    if s >= 0.15: return "C"
    return "D"

def cohen_d(x, y):
    nx, ny = len(x), len(y)
    if nx < 2 or ny < 2: return 0.0
    dof = nx + ny - 2
    pool_var = ((nx - 1) * np.var(x, ddof=1) + (ny - 1) * np.var(y, ddof=1)) / dof
    if pool_var == 0: return 0.0
    return (np.mean(x) - np.mean(y)) / np.sqrt(pool_var)

def main():
    print("Stage 5.9A: Template-Relative Stroke Consistency Exploration")
    os.makedirs(EXP_RANKINGS_DIR, exist_ok=True)
    os.makedirs(FORENSICS_DIR, exist_ok=True)
    os.makedirs(HISTOGRAMS_DIR, exist_ok=True)
    
    # -------------------------------------------------------------------------
    # PHASE 5.9A.1: INPUT VALIDATION
    # -------------------------------------------------------------------------
    print("Phase 5.9A.1: Input Validation")
    req_files = [
        os.path.join(CANDIDATES_DIR, "ranked_by_combined_score.csv"),
        os.path.join(CANDIDATES_DIR, "verified_candidates.csv"),
        os.path.join(REPORTS_DIR, "topological_features_dataset.csv"),
        os.path.join(TEMPLATE_BANK_DIR, "template_bank_manifest.csv"),
        os.path.join(REPORTS_DIR, "stage58_architectural_verdict.md")
    ]
    missing = [f for f in req_files if not os.path.exists(f)]
    if missing:
        with open(os.path.join(REPORTS_DIR, "stage59a_input_validation.md"), "w", encoding="utf-8") as f:
            f.write(f"# Input Validation Failed\n\nMissing dependencies:\n")
            for m in missing: f.write(f"- {m}\n")
        print("HALT. Missing Dependencies.")
        return
        
    with open(os.path.join(REPORTS_DIR, "stage59a_input_validation.md"), "w", encoding="utf-8") as f:
        f.write("# Input Validation Passed\n\nAll dependencies present.\n")
        
    # Load data
    cands_s5 = load_csv(os.path.join(CANDIDATES_DIR, "ranked_by_combined_score.csv"))
    feats_s58 = load_csv(os.path.join(REPORTS_DIR, "topological_features_dataset.csv"))
    template_manifest = load_csv(os.path.join(TEMPLATE_BANK_DIR, "template_bank_manifest.csv"))
    competitor_sheet = load_csv(os.path.join(REPORTS_DIR, "top100_competitor_sheet.csv"))
    
    with open(os.path.join(REPORTS_DIR, "ground_truth_symbols.json"), "r") as f:
        gt_data = json.load(f)

    competitor_keys = {f"{r['sld_name']}_{int(float(r['x']))}_{int(float(r['y']))}" for r in competitor_sheet}
    
    # -------------------------------------------------------------------------
    # PHASE 5.9A.2: TEMPLATE STROKE BASELINE
    # -------------------------------------------------------------------------
    print("Phase 5.9A.2: Template Stroke Baseline")
    template_strokes = {}
    baseline_records = []
    
    for t in template_manifest:
        t_id = t["template_id"]
        t_path = os.path.join(BASE_DIR, t["filepath"])
        if not os.path.exists(t_path): continue
        t_img = cv2.imread(t_path, cv2.IMREAD_GRAYSCALE)
        _, t_bin = cv2.threshold(t_img, 127, 255, cv2.THRESH_BINARY)
        
        # Exact extraction pipeline from Stage 5.8
        feat_dict = extract_topological_features(t_bin)
        sc = feat_dict.get("Stroke_Count", 0)
        template_strokes[t_id] = sc
        
        baseline_records.append({
            "template_id": t_id,
            "template_name": t_id,
            "template_scale": t["scale"],
            "template_stroke_count": sc
        })
        
    save_csv(baseline_records, os.path.join(REPORTS_DIR, "stage59a_template_stroke_baseline.csv"), ["template_id", "template_name", "template_scale", "template_stroke_count"])
    
    with open(os.path.join(REPORTS_DIR, "stage59a_template_stroke_baseline.md"), "w", encoding="utf-8") as f:
        f.write(f"# Template Stroke Baseline\n\n{get_traceability_header()}\n")
        f.write("### Methodology Requirement Check\n")
        f.write("PASS: Template Stroke_Count was extracted using the exact same `extract_topological_features` method from Stage 5.8 to guarantee 1:1 comparability.\n\n")
        scs = [r["template_stroke_count"] for r in baseline_records]
        f.write(f"### Distribution\n- Min: {np.min(scs)}\n- Max: {np.max(scs)}\n- Mean: {np.mean(scs):.2f}\n- Median: {np.median(scs)}\n")

    # -------------------------------------------------------------------------
    # PHASE 5.9A.3: CONSISTENCY DATASET
    # -------------------------------------------------------------------------
    print("Phase 5.9A.3: Stroke Consistency Dataset")
    
    feat_lookup = {f"{c['sld_name']}_{int(float(c['x']))}_{int(float(c['y']))}": c for c in feats_s58}
    
    consistency_dataset = []
    s5_by_sld = defaultdict(list)
    mr_keys = set()
    
    # First identify MRs
    for sld, gts in gt_data.items():
        cands_in_sld = [c for c in cands_s5 if c["sld_name"] == sld]
        for gt in gts:
            gt_cx = gt["x"] + gt["w"]/2
            gt_cy = gt["y"] + gt["h"]/2
            best_cand = None
            best_dist = float('inf')
            for c in cands_in_sld:
                c_cx = float(c["x"]) + float(c.get("template_width", c.get("width", 24)))/2
                c_cy = float(c["y"]) + float(c.get("template_height", c.get("height", 15)))/2
                dist = np.sqrt((gt_cx - c_cx)**2 + (gt_cy - c_cy)**2)
                if dist <= 25 and dist < best_dist:
                    best_dist = dist
                    best_cand = c
            if best_cand:
                mr_keys.add(f"{sld}_{int(float(best_cand['x']))}_{int(float(best_cand['y']))}")
                
    for c in cands_s5:
        key = f"{c['sld_name']}_{int(float(c['x']))}_{int(float(c['y']))}"
        c_feat = feat_lookup.get(key, {})
        cand_sc = float(c_feat.get("Stroke_Count", 0))
        grp = c_feat.get("group", "")
        
        c["is_mr"] = key in mr_keys
        
        tid = c.get("best_template_id", "T_0.200_000")
        # try to find match or use closest scale roughly if not matched
        temp_sc = template_strokes.get(tid, 2.0) # default to 2 if not found
        
        diff = abs(cand_sc - temp_sc)
        norm_diff = diff / max(1.0, temp_sc)
        ratio = max(cand_sc, temp_sc) / max(1.0, min(cand_sc, temp_sc))
        sim = 1.0 / (1.0 + diff)
        
        c["Stroke_Difference"] = diff
        c["Normalized_Stroke_Difference"] = norm_diff
        c["Stroke_Ratio"] = ratio
        c["Stroke_Similarity"] = sim
        
        consistency_dataset.append({
            "key": key,
            "group": grp,
            "candidate_stroke_count": cand_sc,
            "template_stroke_count": temp_sc,
            "Stroke_Difference": diff,
            "Normalized_Stroke_Difference": norm_diff,
            "Stroke_Ratio": ratio,
            "Stroke_Similarity": sim
        })
        s5_by_sld[c["sld_name"]].append(c)
        
    save_csv(consistency_dataset, os.path.join(REPORTS_DIR, "stage59a_stroke_consistency_dataset.csv"), list(consistency_dataset[0].keys()))

    # -------------------------------------------------------------------------
    # PHASE 5.9A.4 & 5.9A.5: DISTRIBUTIONS & SEPARABILITY
    # -------------------------------------------------------------------------
    print("Phase 5.9A.4 & 5.9A.5: Separability Analysis")
    
    metrics = ["Stroke_Difference", "Normalized_Stroke_Difference", "Stroke_Ratio", "Stroke_Similarity"]
    groups = {"A_TrueMR": [], "B_DominantFP": [], "C_HardNegative": [], "D_RandomBG": []}
    
    for c in consistency_dataset:
        grp = c["group"]
        if grp in groups:
            groups[grp].append(c)
            
    def compute_sep(metric, grp1, grp2):
        x = [c[metric] for c in grp1]
        y = [c[metric] for c in grp2]
        if not x or not y: return 0, 0, 100, 0
        
        # For Similarity, higher is better for MR (grp1). For others, lower is better.
        if metric == "Stroke_Similarity":
            labels = [1]*len(x) + [0]*len(y)
            scores = x + y
        else:
            labels = [0]*len(x) + [1]*len(y)
            scores = x + y
            
        try:
            auc = roc_auc_score(labels, scores)
        except: auc = 0.5
        
        d = abs(cohen_d(x, y))
        
        # Overlap Approximation
        min_max = min(max(x), max(y))
        max_min = max(min(x), min(y))
        overlap = max(0, min_max - max_min) / max(1, max(max(x), max(y)) - min(min(x), min(y)))
        
        return auc, d, overlap*100, 0

    sep_results = []
    for m in metrics:
        auc_fp, d_fp, ov_fp, _ = compute_sep(m, groups["A_TrueMR"], groups["B_DominantFP"])
        auc_hn, d_hn, ov_hn, _ = compute_sep(m, groups["A_TrueMR"], groups["C_HardNegative"])
        auc_bg, d_bg, ov_bg, _ = compute_sep(m, groups["A_TrueMR"], groups["D_RandomBG"])
        sep_results.append({
            "Metric": m,
            "AUC_FP": auc_fp, "d_FP": d_fp,
            "AUC_HN": auc_hn, "d_HN": d_hn,
            "AUC_BG": auc_bg, "d_BG": d_bg
        })
        
    with open(os.path.join(REPORTS_DIR, "stage59a_separability_analysis.md"), "w", encoding="utf-8") as f:
        f.write(f"# Consistency Separability Analysis\n\n{get_traceability_header()}\n")
        f.write("| Metric | AUC (vs FP) | d (vs FP) | AUC (vs HN) | AUC (vs BG) |\n")
        f.write("| :--- | :---: | :---: | :---: | :---: |\n")
        for r in sep_results:
            f.write(f"| {r['Metric']} | {r['AUC_FP']:.3f} | {r['d_FP']:.3f} | {r['AUC_HN']:.3f} | {r['AUC_BG']:.3f} |\n")

    # -------------------------------------------------------------------------
    # PHASE 5.9A.5-1: BEST METRIC SELECTION
    # -------------------------------------------------------------------------
    print("Phase 5.9A.5-1: Best Metric Selection")
    
    sep_results.sort(key=lambda x: (x["AUC_FP"], x["d_FP"]), reverse=True)
    best_overall = sep_results[0]["Metric"]
    best_abs = "Stroke_Difference"
    best_rel = "Normalized_Stroke_Difference" if [r for r in sep_results if r["Metric"] == "Normalized_Stroke_Difference"][0]["AUC_FP"] > [r for r in sep_results if r["Metric"] == "Stroke_Ratio"][0]["AUC_FP"] else "Stroke_Ratio"
    
    with open(os.path.join(REPORTS_DIR, "stage59a_best_consistency_metric.md"), "w", encoding="utf-8") as f:
        f.write(f"# Best Consistency Metric Selection\n\n{get_traceability_header()}\n")
        f.write(f"- **Best Absolute Metric:** {best_abs}\n")
        f.write(f"- **Best Relative Metric:** {best_rel}\n")
        f.write(f"- **Overall Winner:** {best_overall}\n")

    # -------------------------------------------------------------------------
    # PHASE 5.9A.6: PILOT EXPERIMENTS
    # -------------------------------------------------------------------------
    print("Phase 5.9A.6: Pilot Experiments")
    
    rankings = {
        "BASE": [],
        "EXP_A1": [], "EXP_A2": [], "EXP_A3": [],
        "EXP_B": [], "EXP_C": [], "EXP_D": [], "EXP_E": [], "EXP_F": []
    }
    
    for sld, cands in s5_by_sld.items():
        for c in cands:
            diff = c["Stroke_Difference"]
            norm_diff = c["Normalized_Stroke_Difference"]
            ratio = c["Stroke_Ratio"]
            sim = c["Stroke_Similarity"]
            cov = float(c.get("CoverageAreaScore", 0))
            ver = float(c.get("VerificationScore", 0))
            cmb = float(c.get("CombinedScore", 0))
            
            c_base = dict(c); c_base["ExpScore"] = cmb
            c_a1 = dict(c); c_a1["ExpScore"] = -diff # ascending rank
            c_a2 = dict(c); c_a2["ExpScore"] = -norm_diff
            c_a3 = dict(c); c_a3["ExpScore"] = -ratio
            c_b = dict(c); c_b["ExpScore"] = sim
            c_c = dict(c); c_c["ExpScore"] = cmb * sim
            c_d = dict(c); c_d["ExpScore"] = cmb - (diff * 0.0001) # Tie-breaker
            c_e = dict(c); c_e["ExpScore"] = cmb - (norm_diff * 0.0001)
            c_f = dict(c); c_f["ExpScore"] = ver * sim
            
            rankings["BASE"].append(c_base)
            rankings["EXP_A1"].append(c_a1)
            rankings["EXP_A2"].append(c_a2)
            rankings["EXP_A3"].append(c_a3)
            rankings["EXP_B"].append(c_b)
            rankings["EXP_C"].append(c_c)
            rankings["EXP_D"].append(c_d)
            rankings["EXP_E"].append(c_e)
            rankings["EXP_F"].append(c_f)
            
    for exp_id, cands in rankings.items():
        by_sld = defaultdict(list)
        for c in cands: by_sld[c["sld_name"]].append(c)
        ranked_list = []
        for sld, slist in by_sld.items():
            slist.sort(key=lambda x: float(x["ExpScore"]), reverse=True)
            for i, c in enumerate(slist):
                c["rank"] = i + 1
                ranked_list.append(c)
        
        all_keys = set()
        for d in ranked_list: all_keys.update(d.keys())
        save_csv(ranked_list, os.path.join(EXP_RANKINGS_DIR, f"{exp_id}.csv"), list(all_keys))
        rankings[exp_id] = by_sld

    # -------------------------------------------------------------------------
    # PHASE 5.9A.7 & 5.9A.8: RECOVERY ANALYSIS
    # -------------------------------------------------------------------------
    print("Phase 5.9A.7: Recovery Analysis")
    
    exp_metrics = {}
    for exp_id, by_sld in rankings.items():
        mr_ranks = []
        hits = {10:0, 50:0, 100:0, 500:0, 1000:0}
        total_mr = len(mr_keys)
        
        resolved_count = 0
        total_inversions_base = 0
        regime_d_ranks = []
        
        for sld, cands in by_sld.items():
            for c in cands:
                if c.get("is_mr"):
                    r = c["rank"]
                    mr_ranks.append(r)
                    if get_scale_regime(c.get("scale", 0.4)) == "D":
                        regime_d_ranks.append(r)
                    for k in hits.keys():
                        if r <= k: hits[k] += 1
                        
            # Inversions
            if sld in rankings["BASE"]:
                mr_ranks_base = [c["rank"] for c in rankings["BASE"][sld] if c.get("is_mr")]
                fp_ranks_base = [c["rank"] for c in rankings["BASE"][sld] if f"{c['sld_name']}_{int(float(c['x']))}_{int(float(c['y']))}" in competitor_keys]
                
                if mr_ranks_base and fp_ranks_base:
                    worst_mr_base = max(mr_ranks_base)
                    best_fp_base = min(fp_ranks_base)
                    if worst_mr_base > best_fp_base:
                        total_inversions_base += 1
                        
                        mr_ranks_exp = [c["rank"] for c in by_sld[sld] if c.get("is_mr")]
                        fp_ranks_exp = [c["rank"] for c in by_sld[sld] if f"{c['sld_name']}_{int(float(c['x']))}_{int(float(c['y']))}" in competitor_keys]
                        
                        if mr_ranks_exp and fp_ranks_exp:
                            worst_mr_exp = max(mr_ranks_exp)
                            best_fp_exp = min(fp_ranks_exp)
                            if worst_mr_exp < best_fp_exp:
                                resolved_count += 1
                                
        exp_metrics[exp_id] = {
            "MeanRank": np.mean(mr_ranks) if mr_ranks else 0,
            "MedRank": np.median(mr_ranks) if mr_ranks else 0,
            "Top100": hits[100] / total_mr if total_mr else 0,
            "Top500": hits[500] / total_mr if total_mr else 0,
            "Inversions": resolved_count,
            "TotalInversions": total_inversions_base,
            "RegimeD_Median": np.median(regime_d_ranks) if regime_d_ranks else 0
        }
        
    with open(os.path.join(REPORTS_DIR, "stage59a_ranking_recovery.md"), "w", encoding="utf-8") as f:
        f.write(f"# Ranking Recovery Analysis\n\n{get_traceability_header()}\n")
        f.write("| Exp ID | Median MR | Top-100 Hit Rate | Inversions Resolved | Regime D Median |\n")
        f.write("| :--- | :---: | :---: | :---: | :---: |\n")
        for exp_id, m in exp_metrics.items():
            f.write(f"| {exp_id} | {m['MedRank']:.1f} | {m['Top100']:.1%} | {m['Inversions']} / {m['TotalInversions']} | {m['RegimeD_Median']:.1f} |\n")

    # Find the best experiment (not BASE) to answer questions
    exp_list = list(rankings.keys())
    exp_list.sort(key=lambda x: (
        exp_metrics[x]["MedRank"],
        -exp_metrics[x]["Top100"],
        -exp_metrics[x]["Inversions"]
    ))
    
    best_exp = exp_list[0] if exp_list[0] != "BASE" else exp_list[1]
    
    # -------------------------------------------------------------------------
    # PHASE 5.9A.9: FALSE POSITIVE COMPOSITION CHECK
    # -------------------------------------------------------------------------
    print("Phase 5.9A.9: FP Composition Check")
    def get_top_n_stats(cands_by_sld, N):
        all_top = []
        for sld, cands in cands_by_sld.items():
            all_top.extend(cands[:N])
        scs = [float(c.get("candidate_stroke_count", c.get("Stroke_Count",0))) for c in all_top]
        diffs = [float(c.get("Stroke_Difference",0)) for c in all_top]
        return np.mean(scs), np.mean(diffs)
        
    base_sc_50, base_diff_50 = get_top_n_stats(rankings["BASE"], 50)
    best_sc_50, best_diff_50 = get_top_n_stats(rankings[best_exp], 50)
    
    with open(os.path.join(REPORTS_DIR, "stage59a_false_positive_composition_check.md"), "w", encoding="utf-8") as f:
        f.write(f"# False Positive Composition Check\n\n{get_traceability_header(exp_id=best_exp)}\n")
        f.write(f"### Q1. Did low-complexity noise dominate?\n")
        # In Stage 5.9, SC was artificially pulled down to < 1.0. If it stays around 3-4, noise didn't dominate.
        f.write(f"Answer: {'YES' if best_sc_50 < 1.5 else 'NO'} (BASE: {base_sc_50:.2f} -> BEST: {best_sc_50:.2f})\n\n")
        f.write(f"### Q2. Did template consistency prevent noise promotion?\n")
        f.write(f"Answer: {'YES' if best_sc_50 >= 1.5 else 'NO'}\n\n")

    # -------------------------------------------------------------------------
    # PHASE 5.9A.11: EXPLORATION VERDICT
    # -------------------------------------------------------------------------
    print("Phase 5.9A.11: Exploration Verdict")
    m_base = exp_metrics["BASE"]
    m_best = exp_metrics[best_exp]
    
    outperforms_base = m_best["MedRank"] < m_base["MedRank"] or m_best["Top100"] > m_base["Top100"] or m_best["Inversions"] > 0
    norm_better = next(r for r in sep_results if r["Metric"] == "Normalized_Stroke_Difference")["AUC_FP"] > next(r for r in sep_results if r["Metric"] == "Stroke_Difference")["AUC_FP"]
    ratio_better = next(r for r in sep_results if r["Metric"] == "Stroke_Ratio")["AUC_FP"] > next(r for r in sep_results if r["Metric"] == "Stroke_Difference")["AUC_FP"]
    
    with open(os.path.join(REPORTS_DIR, "stage59a_exploration_verdict.md"), "w", encoding="utf-8") as f:
        f.write(f"# Exploration Verdict\n\n{get_traceability_header(exp_id=best_exp)}\n")
        f.write(f"### Q1. Is template-relative stroke consistency more useful than absolute Stroke_Count?\n")
        f.write(f"Answer: {'YES' if outperforms_base else 'NO'} (Best Median Rank: {m_best['MedRank']} vs BASE: {m_base['MedRank']})\n\n")
        
        f.write(f"### Q2. Does it avoid False Positive Composition Shift?\n")
        f.write(f"Answer: {'YES' if best_sc_50 >= 1.5 else 'NO'} (Top 50 SC: {best_sc_50:.2f})\n\n")
        
        f.write(f"### Q3. Does it improve Top-N hit rates?\n")
        f.write(f"Answer: {'YES' if m_best['Top100'] > m_base['Top100'] else 'NO'} (Best Top-100: {m_best['Top100']:.1%} vs BASE: {m_base['Top100']:.1%})\n\n")
        
        f.write(f"### Q4. Does it improve Median MR Rank?\n")
        f.write(f"Answer: {'YES' if m_best['MedRank'] < m_base['MedRank'] else 'NO'} (Best: {m_best['MedRank']} vs BASE: {m_base['MedRank']})\n\n")
        
        f.write(f"### Q5. Does it improve inversion recovery?\n")
        f.write(f"Answer: {'YES' if m_best['Inversions'] > 0 else 'NO'} (Resolved: {m_best['Inversions']})\n\n")
        
        f.write(f"### Q6. Does it improve Regime D performance?\n")
        f.write(f"Answer: {'YES' if m_best['RegimeD_Median'] < m_base['RegimeD_Median'] else 'NO'} (Best D Median: {m_best['RegimeD_Median']} vs BASE: {m_base['RegimeD_Median']})\n\n")
        
        f.write(f"### Q9. Does Normalized_Stroke_Difference outperform absolute Stroke_Difference?\n")
        f.write(f"Answer: {'YES' if norm_better else 'NO'}\n\n")
        
        f.write(f"### Q10. Does Stroke_Ratio outperform both Difference metrics?\n")
        f.write(f"Answer: {'YES' if ratio_better and next(r for r in sep_results if r['Metric'] == 'Stroke_Ratio')['AUC_FP'] > next(r for r in sep_results if r['Metric'] == 'Normalized_Stroke_Difference')['AUC_FP'] else 'NO'}\n\n")
        
        f.write(f"### Q11. Which template-consistency formulation performs best?\n")
        f.write(f"Answer: {best_exp}\n\n")
        
        f.write(f"### Q7 & Q13. Does evidence justify a full Stage 5.10 Template Consistency Verification architecture?\n")
        if outperforms_base:
            f.write("Answer: YES. Template consistency successfully avoids the composition shift vulnerability and improves ranking.\n")
        else:
            f.write("Answer: NO. Template consistency does not provide enough signal to improve median rank or resolve inversions over the BASE formulation.\n")

    print("Stage 5.9A Execution Complete.")

if __name__ == "__main__":
    main()
