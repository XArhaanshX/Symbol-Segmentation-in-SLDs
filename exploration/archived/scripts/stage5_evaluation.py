import os
import csv
import json
import math
import numpy as np
from datetime import datetime

BASE_DIR = r"c:\Users\arhaa\OneDrive\Symbol Segmentor"
REPORTS_DIR = os.path.join(BASE_DIR, "reports")
CANDIDATES_DIR = os.path.join(BASE_DIR, "outputs", "candidates")

TIMESTAMP = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
TEMPLATE_BANK_VERSION = "Stage2_D3_v1"
CANDIDATE_DATASET_SOURCE = "ranked_by_coverage_area.csv"
MANIFEST_VERSION = "outputs/template_bank/template_bank_manifest.csv"
EVALUATION_DATASET_SOURCE = "reports/ground_truth_symbols.json"

def get_traceability_header():
    return f"""<!-- Traceability Header -->
- **Generation Timestamp**: {TIMESTAMP}
- **Template Bank Version**: {TEMPLATE_BANK_VERSION}
- **Stage 4 Candidate Source**: {CANDIDATE_DATASET_SOURCE}
- **Manifest Version**: {MANIFEST_VERSION}
- **Evaluation Dataset Source**: {EVALUATION_DATASET_SOURCE}
- **Investigation Type**: Structural Evaluation Analysis
<!-- End Traceability Header -->

"""

def get_best_rank_for_gt(gt_symbol, candidates_list):
    gt_cx = gt_symbol["x"] + gt_symbol["w"] / 2.0
    gt_cy = gt_symbol["y"] + gt_symbol["h"] / 2.0
    
    for rank, c in enumerate(candidates_list, start=1):
        c_w = float(c.get("template_width", c.get("width", 24)))
        c_h = float(c.get("template_height", c.get("height", 15)))
        c_cx = float(c["x"]) + c_w / 2.0
        c_cy = float(c["y"]) + c_h / 2.0
        
        dist = math.sqrt((gt_cx - c_cx)**2 + (gt_cy - c_cy)**2)
        if dist <= 25.0:
            return rank, c
    return None, None

def load_csv(path):
    if not os.path.exists(path):
        print(f"FATAL: Missing ranking file {path}")
        import sys
        sys.exit(1)
    with open(path, "r", encoding="utf-8") as f:
        return list(csv.DictReader(f))

def split_by_sld(cands):
    res = {}
    for c in cands:
        res.setdefault(c["sld_name"], []).append(c)
    return res

def compute_hit_rates(ranks):
    rates = {}
    for n in [10, 50, 100, 500, 1000]:
        hits = sum(1 for r in ranks if r is not None and r <= n)
        rates[n] = hits / len(ranks) if ranks else 0.0
    return rates

def main():
    print("Stage 5 Rank Analysis...")
    gt_path = os.path.join(REPORTS_DIR, "ground_truth_symbols.json")
    with open(gt_path, "r") as f:
        ground_truth = json.load(f)
        
    stg3_cands = load_csv(os.path.join(CANDIDATES_DIR, "ranked_candidates.csv"))
    stg4_cands = load_csv(os.path.join(CANDIDATES_DIR, "ranked_by_coverage_area.csv"))
    stg5_cands = load_csv(os.path.join(CANDIDATES_DIR, "ranked_by_combined_score.csv"))
    
    stg3_by_sld = split_by_sld(stg3_cands)
    stg4_by_sld = split_by_sld(stg4_cands)
    stg5_by_sld = split_by_sld(stg5_cands)
    
    stg3_ranks = []
    stg4_ranks = []
    stg5_ranks = []
    improvements = []
    
    analysis_lines = []
    analysis_lines.append("| SLD | GT Index | Orig Stage3 Rank | Stage4 Rank | Stage5 Rank | Stage5 Improv |")
    analysis_lines.append("| :--- | :---: | :---: | :---: | :---: | :---: |")
    
    for sld, gts in ground_truth.items():
        for i, gt in enumerate(gts):
            r3, _ = get_best_rank_for_gt(gt, stg3_by_sld.get(sld, []))
            r4, _ = get_best_rank_for_gt(gt, stg4_by_sld.get(sld, []))
            r5, _ = get_best_rank_for_gt(gt, stg5_by_sld.get(sld, []))
            
            stg3_ranks.append(r3)
            stg4_ranks.append(r4)
            stg5_ranks.append(r5)
            
            imp = (r4 - r5) if r4 and r5 else 0
            if r4 and r5: improvements.append(imp)
            
            str3 = str(r3) if r3 else "Miss"
            str4 = str(r4) if r4 else "Miss"
            str5 = str(r5) if r5 else "Miss"
            
            analysis_lines.append(f"| {sld} | {i} | {str3} | {str4} | {str5} | {imp:+} |")
            
    def agg(ranks, improvements):
        valid_r = [r for r in ranks if r is not None]
        valid_i = [i for i in improvements if i != 0]
        return {
            "median_rank": np.median(valid_r) if valid_r else 0,
            "mean_rank": np.mean(valid_r) if valid_r else 0,
            "mean_imp": np.mean(valid_i) if valid_i else 0,
            "median_imp": np.median(valid_i) if valid_i else 0,
            "best_imp": np.max(valid_i) if valid_i else 0,
            "worst_imp": np.min(valid_i) if valid_i else 0,
            "hit_rates": compute_hit_rates(ranks)
        }
        
    s3_agg = agg(stg3_ranks, [0]*len(stg3_ranks))
    s4_agg = agg(stg4_ranks, [0]*len(stg4_ranks))
    s5_agg = agg(stg5_ranks, improvements)
    
    header = get_traceability_header()
    
    with open(os.path.join(REPORTS_DIR, "stage5_rank_improvement_analysis.md"), "w", encoding="utf-8") as f:
        f.write(f"# Stage 5 Rank Improvement Analysis\n\n{header}\n\n")
        f.write("## 1. Objective\nDetermine if True MR Symbols move upward in the candidate ranking after combined structural verification.\n\n")
        f.write("## 2. Granular SLD Ranking Shifts\n")
        f.write("\n".join(analysis_lines) + "\n")
        
    with open(os.path.join(REPORTS_DIR, "stage5_effectiveness_assessment.md"), "w", encoding="utf-8") as f:
        f.write(f"# Stage 5 Effectiveness Assessment\n\n{header}\n\n")
        f.write("## 1. Evaluation Results\n\n")
        
        f.write(f"- **Mean Rank Improvement (Stage 4 to 5)**: {s5_agg['mean_imp']:+.0f}\n")
        f.write(f"- **Median Rank Improvement**: {s5_agg['median_imp']:+.0f}\n")
        f.write(f"- **Best Rank Improvement**: {s5_agg['best_imp']:+.0f}\n\n")
        
        f.write("## 2. Hit Rates (True Symbol Penetration)\n")
        f.write("| Threshold | Stage 3 (Orig) | Stage 4 (Cov x Area) | Stage 5 (Combined) |\n")
        f.write("| :--- | :---: | :---: | :---: |\n")
        for n in [10, 50, 100, 500, 1000]:
            o = s3_agg['hit_rates'][n]*100
            s4 = s4_agg['hit_rates'][n]*100
            s5 = s5_agg['hit_rates'][n]*100
            f.write(f"| Top {n} | {o:.1f}% | {s4:.1f}% | {s5:.1f}% |\n")

if __name__ == "__main__":
    main()
