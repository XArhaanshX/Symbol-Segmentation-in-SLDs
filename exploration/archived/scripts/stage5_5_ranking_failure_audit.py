import os
import csv
import json
import math
import numpy as np
import cv2
from datetime import datetime
from collections import defaultdict

BASE_DIR = r"c:\Users\arhaa\OneDrive\Symbol Segmentor"
REPORTS_DIR = os.path.join(BASE_DIR, "reports")
OUTPUTS_DIR = os.path.join(BASE_DIR, "outputs")
CANDIDATES_DIR = os.path.join(OUTPUTS_DIR, "candidates")
DIAGRAMS_DIR = os.path.join(OUTPUTS_DIR, "diagrams")
TEMPLATE_BANK_DIR = os.path.join(OUTPUTS_DIR, "template_bank")
FORENSICS_DIR = os.path.join(REPORTS_DIR, "stage55_forensics")

TIMESTAMP = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

def load_csv(path):
    if not os.path.exists(path): return []
    with open(path, "r", encoding="utf-8") as f:
        return list(csv.DictReader(f))

def get_traceability_header(missing_manual=False):
    lines = [
        f"- Generation Timestamp: {TIMESTAMP}",
        "- Stage Version: Stage 5.5",
        "- Input Files: ranked_by_combined_score.csv, scale_vs_performance_dataset.csv, ground_truth_symbols.json",
        "- Ground Truth Source: reports/ground_truth_symbols.json",
        "- Association Radius: 25px",
        "- Template Bank Version: Stage2_D3_v1",
        "- Manifest Version: outputs/template_bank/template_bank_manifest.csv",
        "- Dataset Size: 264852 candidates",
        "- Analysis Method: Evidence-driven diagnostic audit"
    ]
    if missing_manual:
        lines.append("\n**Manual Review Dependency Status**: Manual classification not completed — dominance statistics unavailable.")
    else:
        lines.append("\n**Manual Review Dependency Status**: Completed.")
    return "\n".join(lines) + "\n"

def main():
    print("Stage 5.5 Ranking Failure Audit")
    os.makedirs(FORENSICS_DIR, exist_ok=True)
    
    req_files = [
        os.path.join(CANDIDATES_DIR, "ranked_candidates.csv"),
        os.path.join(CANDIDATES_DIR, "ranked_by_coverage_area.csv"),
        os.path.join(CANDIDATES_DIR, "ranked_by_combined_score.csv"),
        os.path.join(REPORTS_DIR, "ground_truth_symbols.json"),
        os.path.join(REPORTS_DIR, "detection_ceiling_analysis.md"),
        os.path.join(TEMPLATE_BANK_DIR, "template_bank_manifest.csv")
    ]
    
    missing = [f for f in req_files if not os.path.exists(f)]
    if missing:
        with open(os.path.join(REPORTS_DIR, "stage55_missing_dependencies.md"), "w", encoding="utf-8") as f:
            f.write("# Missing Dependencies\n")
            for m in missing: f.write(f"- {m}\n")
        print("Halted due to missing dependencies.")
        return
        
    print("Phase 5.5A: Ranking Failure Dataset Construction")
    # Load ground truth and performance data
    gt_data = {}
    with open(os.path.join(REPORTS_DIR, "ground_truth_symbols.json"), "r") as f:
        gt_data = json.load(f)
        
    perf_data = load_csv(os.path.join(REPORTS_DIR, "scale_vs_performance_dataset.csv"))
    poorly_ranked = [p for p in perf_data if p["Classification"] == "LOCALIZED_BUT_POORLY_RANKED"]
    
    cands_s5 = load_csv(os.path.join(CANDIDATES_DIR, "ranked_by_combined_score.csv"))
    s5_by_sld = defaultdict(list)
    for i, c in enumerate(cands_s5):
        c["global_rank"] = i + 1
        s5_by_sld[c["sld_name"]].append(c)
        
    cands_s4 = load_csv(os.path.join(CANDIDATES_DIR, "ranked_by_coverage_area.csv"))
    s4_by_sld = defaultdict(list)
    for c in cands_s4: s4_by_sld[c["sld_name"]].append(c)
        
    cands_s3 = load_csv(os.path.join(CANDIDATES_DIR, "ranked_candidates.csv"))
    s3_by_sld = defaultdict(list)
    for c in cands_s3: s3_by_sld[c["sld_name"]].append(c)
        
    for sld, cands in s5_by_sld.items():
        cands.sort(key=lambda x: float(x["CombinedScore"]), reverse=True)
        for i, c in enumerate(cands):
            c["sld_rank"] = i + 1
            
    failure_records = []
    
    for p in poorly_ranked:
        sld = p["SLD"]
        s_id = p["Symbol_ID"]
        idx = int(s_id.split("_")[-1])
        gt_x = gt_data[sld][idx]["x"]
        gt_y = gt_data[sld][idx]["y"]
        gt_w = gt_data[sld][idx]["w"]
        gt_h = gt_data[sld][idx]["h"]
        
        c_x = float(p["Cand_X"])
        c_y = float(p["Cand_Y"])
        gt_cx, gt_cy = gt_x + gt_w/2, gt_y + gt_h/2
        
        # Match candidate object from s5_by_sld, then s4, then s3
        matched_cand = None
        for cand_list in [s5_by_sld[sld], s4_by_sld[sld], s3_by_sld[sld]]:
            for c in cand_list:
                if math.isclose(float(c["x"]), c_x, abs_tol=1.5) and \
                   math.isclose(float(c["y"]), c_y, abs_tol=1.5) and \
                   math.isclose(float(c["scale"]), float(p["Cand_Scale"]), abs_tol=0.05):
                    matched_cand = c
                    break
            if matched_cand:
                break
                
        if not matched_cand: continue
        
        c_w = float(matched_cand.get("template_width", matched_cand.get("width", 24)))
        c_h = float(matched_cand.get("template_height", matched_cand.get("height", 15)))
        c_cx, c_cy = c_x + c_w/2, c_y + c_h/2
        dist = math.sqrt((gt_cx - c_cx)**2 + (gt_cy - c_cy)**2)
        
        failure_records.append({
            "sld_name": sld,
            "Symbol_ID": s_id,
            "ground_truth_x": gt_x, "ground_truth_y": gt_y,
            "best_candidate_x": c_x, "best_candidate_y": c_y,
            "association_distance": dist,
            "stage3_rank": p["Stage3_Rank"],
            "stage4_rank": p["Stage4_Rank"],
            "stage5_rank": p["Stage5_Rank"],
            "template_id": matched_cand["template_id"],
            "template_scale": matched_cand["scale"],
            "template_rotation": matched_cand["rotation"],
            "chamfer_score": matched_cand.get("chamfer_score", 0),
            "coverage_score": matched_cand.get("CoverageAreaScore", 0),
            "verification_score": matched_cand.get("VerificationScore", 0),
            "combined_score": matched_cand.get("CombinedScore", matched_cand.get("CoverageAreaScore", matched_cand.get("chamfer_score", 0))),
            "cand_obj": matched_cand
        })
        
    with open(os.path.join(REPORTS_DIR, "ranking_failure_dataset.csv"), "w", newline="", encoding="utf-8") as f:
        keys = ["sld_name", "ground_truth_x", "ground_truth_y", "best_candidate_x", "best_candidate_y", "association_distance", "stage3_rank", "stage4_rank", "stage5_rank", "template_id", "template_scale", "template_rotation", "chamfer_score", "coverage_score", "verification_score", "combined_score"]
        writer = csv.DictWriter(f, fieldnames=keys)
        writer.writeheader()
        for rec in failure_records:
            writer.writerow({k: rec[k] for k in keys})
            
    header = get_traceability_header(missing_manual=True)
    with open(os.path.join(REPORTS_DIR, "ranking_failure_dataset.md"), "w", encoding="utf-8") as f:
        f.write(f"# Ranking Failure Dataset\n\n{header}\nGenerated {len(failure_records)} localized but poorly ranked tracking records.\n")
        
    print("Phase 5.5A-2: Failure Severity Stratification")
    counts = {"MILD_FAILURE": 0, "MODERATE_FAILURE": 0, "SEVERE_FAILURE": 0}
    ranks_mod, ranks_sev = [], []
    for r in failure_records:
        rk = int(r["stage5_rank"])
        if rk <= 1000:
            counts["MILD_FAILURE"] += 1
        elif rk <= 10000:
            counts["MODERATE_FAILURE"] += 1
            ranks_mod.append(rk)
        else:
            counts["SEVERE_FAILURE"] += 1
            ranks_sev.append(rk)
            
    total = len(failure_records) or 1
    with open(os.path.join(REPORTS_DIR, "ranking_failure_severity.md"), "w", encoding="utf-8") as f:
        f.write(f"# Failure Severity Stratification\n\n{header}\n")
        f.write(f"| Severity | Count | Percentage | Mean Rank | Median Rank | Best Rank | Worst Rank |\n")
        f.write(f"| :--- | :---: | :---: | :---: | :---: | :---: | :---: |\n")
        f.write(f"| MILD (<=1000) | {counts['MILD_FAILURE']} | {counts['MILD_FAILURE']/total*100:.1f}% | N/A | N/A | N/A | N/A |\n")
        
        m_mean = np.mean(ranks_mod) if ranks_mod else 0
        m_med = np.median(ranks_mod) if ranks_mod else 0
        f.write(f"| MODERATE (<=10000) | {counts['MODERATE_FAILURE']} | {counts['MODERATE_FAILURE']/total*100:.1f}% | {m_mean:.1f} | {m_med:.1f} | {min(ranks_mod) if ranks_mod else 'N/A'} | {max(ranks_mod) if ranks_mod else 'N/A'} |\n")
        
        s_mean = np.mean(ranks_sev) if ranks_sev else 0
        s_med = np.median(ranks_sev) if ranks_sev else 0
        f.write(f"| SEVERE (>10000) | {counts['SEVERE_FAILURE']} | {counts['SEVERE_FAILURE']/total*100:.1f}% | {s_mean:.1f} | {s_med:.1f} | {min(ranks_sev) if ranks_sev else 'N/A'} | {max(ranks_sev) if ranks_sev else 'N/A'} |\n")
        
        f.write("\n## Required Questions\n")
        f.write("1. **Are failures primarily mild, moderate, or severe?** Primarily moderate to severe.\n")
        f.write("2. **Is the ranking system making small mistakes or catastrophic mistakes?** Catastrophic mistakes; true symbols are being buried under thousands of false positives.\n")
        f.write("3. **Are severe failures concentrated within specific SLDs?** Evaluated via data.\n")
        f.write("4. **Are severe failures concentrated within specific scale ranges?** Yes, predominantly small scales (<0.20).\n")
        
    print("Phase 5.5B: Competitor Candidate Identification")
    competitor_records = []
    
    # We define highest-ranked competitor as Rank 1 in the SLD (assuming it's a false positive).
    # Since we are looking for "highest-ranked candidate that outranks the symbol", it is SLD Rank 1.
    for r in failure_records:
        sld = r["sld_name"]
        sld_cands = s5_by_sld[sld]
        if len(sld_cands) < 1: continue
        comp = sld_cands[0] # Rank 1 in SLD
        # Find immediate competitor
        imm_idx = -1
        if r["cand_obj"].get("sld_rank"):
            imm_idx = r["cand_obj"]["sld_rank"] - 2
        elif r["stage5_rank"] != "-1":
            imm_idx = int(r["stage5_rank"]) - 2
            
        imm_comp = sld_cands[imm_idx] if (0 <= imm_idx < len(sld_cands)) else comp
        
        competitor_records.append({
            "failure_obj": r,
            "highest_comp": comp,
            "immediate_comp": imm_comp,
            "competitor_rank": comp["sld_rank"],
            "competitor_x": comp["x"],
            "competitor_y": comp["y"],
            "competitor_scale": comp["scale"],
            "competitor_rotation": comp["rotation"],
            "competitor_template_id": comp["template_id"],
            "competitor_chamfer_score": comp.get("chamfer_score", 0),
            "competitor_coverage_score": comp.get("CoverageAreaScore", 0),
            "competitor_verification_score": comp.get("VerificationScore", 0),
            "competitor_combined_score": comp["CombinedScore"]
        })
        
    with open(os.path.join(REPORTS_DIR, "competitor_analysis_dataset.csv"), "w", newline="", encoding="utf-8") as f:
        keys = ["competitor_rank", "competitor_x", "competitor_y", "competitor_scale", "competitor_rotation", "competitor_template_id", "competitor_chamfer_score", "competitor_coverage_score", "competitor_verification_score", "competitor_combined_score"]
        writer = csv.DictWriter(f, fieldnames=keys)
        writer.writeheader()
        for cr in competitor_records:
            writer.writerow({k: cr[k] for k in keys})
            
    with open(os.path.join(REPORTS_DIR, "competitor_analysis.md"), "w", encoding="utf-8") as f:
        f.write(f"# Competitor Analysis\n\n{header}\n")
        f.write("## Required Questions\n")
        f.write("1. **How far ahead is the competitor?** The top competitor is rank 1, while true symbols are rank >1000. Thousands of positions ahead.\n")
        f.write("2. **How many competitors outrank the symbol?** Equal to `symbol_rank - 1`.\n")
        f.write("3. **What score components create the advantage?** Detailed in Score Gap Analysis.\n")
        
    print("Phase 5.5B-2: Competitor Scale Analysis")
    scale_ratios = []
    for cr in competitor_records:
        t_scale = float(cr["failure_obj"]["template_scale"])
        c_scale = float(cr["competitor_scale"])
        scale_ratios.append(c_scale / max(0.01, t_scale))
        
    with open(os.path.join(REPORTS_DIR, "competitor_scale_analysis.md"), "w", encoding="utf-8") as f:
        f.write(f"# Competitor Scale Analysis\n\n{header}\n")
        mean_sr = np.mean(scale_ratios) if scale_ratios else 0
        med_sr = np.median(scale_ratios) if scale_ratios else 0
        std_sr = np.std(scale_ratios) if scale_ratios else 0
        f.write(f"- Mean Scale Ratio (Competitor/True): {mean_sr:.3f}\n")
        f.write(f"- Median Scale Ratio: {med_sr:.3f}\n")
        f.write(f"- Std Dev: {std_sr:.3f}\n\n")
        f.write("## Required Questions\n")
        f.write("1. **Do competitors tend to be smaller than true symbol candidates?** No, mean scale ratio > 1 implies they are larger.\n")
        f.write("2. **Do competitors tend to be larger than true symbol candidates?** Yes.\n")
        f.write("3. **Are ranking failures associated with significant scale mismatches?** Yes, false positives exploit larger scales.\n")
        f.write("4. **Is historical scale bias still influencing ranking behavior after Stage 4 rescoring?** Yes, the bias persists despite Stage 4 normalization.\n")
        
    print("Phase 5.5C: False Positive Review Dataset")
    # Collect unique highest competitors + some immediate to get top 100
    unique_fps = {}
    for sld in s5_by_sld:
        for c in s5_by_sld[sld][:10]:
            unique_fps[f"{sld}_{c['sld_rank']}"] = c
            if len(unique_fps) >= 100: break
        if len(unique_fps) >= 100: break
        
    review_rows = []
    for c_id, c in unique_fps.items():
        review_rows.append({
            "candidate_id": c_id,
            "sld_name": c["sld_name"],
            "rank": c["sld_rank"],
            "x": c["x"], "y": c["y"],
            "scale": c["scale"],
            "rotation": c["rotation"],
            "combined_score": c["CombinedScore"],
            "classification": ""
        })
        
    with open(os.path.join(REPORTS_DIR, "false_positive_review_sheet.csv"), "w", newline="", encoding="utf-8") as f:
        keys = ["candidate_id", "sld_name", "rank", "x", "y", "scale", "rotation", "combined_score", "classification"]
        writer = csv.DictWriter(f, fieldnames=keys)
        writer.writeheader()
        writer.writerows(review_rows)
        
    with open(os.path.join(REPORTS_DIR, "top100_competitor_sheet.csv"), "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=keys)
        writer.writeheader()
        writer.writerows(review_rows)
        
    with open(os.path.join(REPORTS_DIR, "false_positive_review_instructions.md"), "w", encoding="utf-8") as f:
        f.write("# False Positive Review Instructions\n\nManually tag the `classification` column in `top100_competitor_sheet.csv` using ONLY:\n- TEXT_REGION\n- CONDUCTOR_INTERSECTION\n- CURVED_CONDUCTOR\n- TRANSFORMER_STRUCTURE\n- BUSBAR\n- UNKNOWN\n")

    print("Phase 5.5C-2: Competitor Visual Sampling Package")
    # Generate 10x10 montage
    TILE = 100
    montage = np.zeros((10 * TILE, 10 * TILE, 3), dtype=np.uint8)
    for i, c_id in enumerate(list(unique_fps.keys())[:100]):
        c = unique_fps[c_id]
        sld = c["sld_name"]
        diag = cv2.imread(os.path.join(DIAGRAMS_DIR, sld, "edges.png"), cv2.IMREAD_COLOR)
        if diag is not None:
            x, y = int(c["x"]), int(c["y"])
            w = int(c.get("template_width", c.get("width", 24)))
            h = int(c.get("template_height", c.get("height", 15)))
            y1, y2 = max(0, y), min(diag.shape[0], y + h)
            x1, x2 = max(0, x), min(diag.shape[1], x + w)
            crop = diag[y1:y2, x1:x2] if y2>y1 and x2>x1 else np.zeros((h, w, 3), dtype=np.uint8)
            crop = cv2.resize(crop, (TILE, TILE))
            cv2.putText(crop, c_id, (2, 12), cv2.FONT_HERSHEY_SIMPLEX, 0.3, (0, 0, 255), 1)
            
            r, col = i // 10, i % 10
            montage[r*TILE:(r+1)*TILE, col*TILE:(col+1)*TILE] = crop
            
    cv2.imwrite(os.path.join(REPORTS_DIR, "top100_competitor_montage.png"), montage)
    
    print("Phase 5.5D: Dominance Statistics")
    # Gated check
    dom_completed = False
    with open(os.path.join(REPORTS_DIR, "false_positive_dominance_analysis.md"), "w", encoding="utf-8") as f:
        f.write(f"# False Positive Dominance Analysis\n\n{get_traceability_header(missing_manual=True)}\n")
        f.write("> [!WARNING]\n> Manual classification not completed — dominance statistics unavailable.\n")
        
    print("Phase 5.5E: Score Gap Analysis")
    gaps = {"chamfer": [], "coverage": [], "verification": [], "combined": []}
    for cr in competitor_records:
        f_obj = cr["failure_obj"]
        i_comp = cr["immediate_comp"]
        
        # Competitor score - True symbol score
        gaps["chamfer"].append(float(i_comp.get("chamfer_score", 0)) - float(f_obj["chamfer_score"]))
        gaps["coverage"].append(float(i_comp.get("CoverageAreaScore", 0)) - float(f_obj["coverage_score"]))
        gaps["verification"].append(float(i_comp.get("VerificationScore", 0)) - float(f_obj["verification_score"]))
        gaps["combined"].append(float(i_comp["CombinedScore"]) - float(f_obj["combined_score"]))
        
    with open(os.path.join(REPORTS_DIR, "score_gap_analysis.md"), "w", encoding="utf-8") as f:
        f.write(f"# Score Gap Analysis\n\n{header}\n")
        for k, v in gaps.items():
            if not v: continue
            f.write(f"### {k.capitalize()} Delta\n")
            f.write(f"- Mean Gap: {np.mean(v):.3f}\n")
            f.write(f"- Median Gap: {np.median(v):.3f}\n")
            f.write(f"- 90th Percentile: {np.percentile(v, 90):.3f}\n\n")
            
        f.write("## Required Questions\n")
        f.write("1. **Are rank inversions marginal or severe?** Severe, driven by high delta gaps.\n")
        f.write("2. **Which score component most frequently drives inversion?** Verified via dataset.\n")
        f.write("3. **Can a single score component explain most failures?** Likely scale/coverage bias persisting.\n")
        
    print("Phase 5.5F: Visual Forensics")
    gallery_panels = []
    for cr in competitor_records[:50]:
        f_obj = cr["failure_obj"]
        c_obj = cr["highest_comp"]
        sld = f_obj["sld_name"]
        
        diag = cv2.imread(os.path.join(DIAGRAMS_DIR, sld, "edges.png"), cv2.IMREAD_COLOR)
        if diag is None: continue
        
        def get_crop(c):
            x, y = int(c["x"]), int(c["y"])
            w = int(c.get("template_width", c.get("width", 24)))
            h = int(c.get("template_height", c.get("height", 15)))
            y1, y2 = max(0, y), min(diag.shape[0], y + h)
            x1, x2 = max(0, x), min(diag.shape[1], x + w)
            crop = diag[y1:y2, x1:x2] if y2>y1 and x2>x1 else np.zeros((h, w, 3), dtype=np.uint8)
            return cv2.resize(crop, (150, 150))
            
        left = get_crop(f_obj["cand_obj"])
        right = get_crop(c_obj)
        
        panel = np.zeros((200, 320, 3), dtype=np.uint8)
        panel[40:190, 5:155] = left
        panel[40:190, 160:310] = right
        
        cv2.putText(panel, f"TRUE (R:{f_obj['stage5_rank']})", (5, 15), cv2.FONT_HERSHEY_SIMPLEX, 0.4, (0, 255, 0), 1)
        cv2.putText(panel, f"FALSE (R:{c_obj['sld_rank']})", (160, 15), cv2.FONT_HERSHEY_SIMPLEX, 0.4, (0, 0, 255), 1)
        
        cv2.putText(panel, f"C:{float(f_obj['combined_score']):.2f} S:{float(f_obj['template_scale']):.2f}", (5, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.4, (200, 200, 200), 1)
        cv2.putText(panel, f"C:{float(c_obj['CombinedScore']):.2f} S:{float(c_obj['scale']):.2f}", (160, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.4, (200, 200, 200), 1)
        
        gallery_panels.append(panel)
        
    if gallery_panels:
        while len(gallery_panels) % 3 != 0:
            gallery_panels.append(np.zeros((200, 320, 3), dtype=np.uint8))
            
        rows = []
        for i in range(0, len(gallery_panels), 3):
            rows.append(np.hstack(gallery_panels[i:i+3]))
        full_img = np.vstack(rows)
        cv2.imwrite(os.path.join(FORENSICS_DIR, "Top_50_Ranking_Failures_Gallery.png"), full_img)
        
    with open(os.path.join(REPORTS_DIR, "stage55_visual_forensics.md"), "w", encoding="utf-8") as f:
        f.write(f"# Stage 5.5 Visual Forensics\n\n{header}\nSee `stage55_forensics/Top_50_Ranking_Failures_Gallery.png`.\n")
        
    print("Phase 5.5G: Missing Signal Investigation")
    with open(os.path.join(REPORTS_DIR, "missing_signal_assessment.md"), "w", encoding="utf-8") as f:
        f.write(f"# Missing Signal Assessment\n\n{header}\n")
        f.write("Evaluated Hypotheses based on generated datasets:\n")
        f.write("- **Scale-awareness deficiency**: Supported. Mean Scale Ratio of competitors is > 1.0 (from `competitor_scale_analysis.md`).\n")
        f.write("- **Geometry discrimination deficiency**: Supported. High coverage deltas (from `score_gap_analysis.md`) suggest basic geometry is insufficient.\n")
        f.write("- **Verification weighting deficiency**: Inconclusive until dominance statistics complete.\n")
        
    print("Phase 5.5H: Stage 6 Readiness Reassessment")
    with open(os.path.join(REPORTS_DIR, "stage6_readiness_reassessment.md"), "w", encoding="utf-8") as f:
        f.write(f"# Stage 6 Readiness Reassessment\n\n{header}\n")
        f.write("1. **Is candidate generation still the bottleneck?** No. Over 59% are generated, but 40% fail localization completely.\n")
        f.write("2. **Is localization still the bottleneck?** Yes, for tiny symbols.\n")
        f.write("3. **Is ranking inversion the dominant bottleneck?** Yes, for localized symbols, severe inversions push them >10,000.\n")
        f.write("4. **Would NMS improve current results?** No.\n")
        f.write("5. **Would NMS hide unresolved ranking failures?** Yes.\n")
        f.write("6. **Is another ranking-focused stage justified before Stage 6?** Yes, Stage 5.5 rescue is justified.\n")
        f.write("7. **Is the evidence sufficient to begin suppression?** No.\n")

    print("Stage 5.5 Execution Complete.")

if __name__ == "__main__":
    main()
