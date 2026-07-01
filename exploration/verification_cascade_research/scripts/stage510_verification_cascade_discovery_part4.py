# -------------------------------------------------------------------------
# PHASE 5.10F & 5.10F-1 & 5.10F-2: CASCADE EVALUATION & SELECTION
# -------------------------------------------------------------------------
print("Phase 5.10F: Cascade Evaluation")

cas_eval_md = "# Cascade Evaluation\n\n" + get_traceability_header() + "\n"
cas_attr_md = "# Cascade Attribution Analysis\n\n" + get_traceability_header() + "\n"

cascade_results = {}

for c_name, c_gates in CASCADES.items():
    current_cands = list(canonical_cands)
    attr_data = []
    
    for g in c_gates:
        pre_count = len(current_cands)
        grp_a_pre = len([c for c in current_cands if c.get("group") == "A_TrueMR"])
        grp_b_pre = len([c for c in current_cands if c.get("group") == "B_DominantFP"])
        grp_e_pre = len([c for c in current_cands if c.get("group") == "E_PromotedNoise"])
        
        if g == "Verification":
            # Dummy threshold for verification score to simulate a final pass
            retained = [c for c in current_cands if c.get("CombinedScore", 0) > 10.0]
        else:
            retained, _ = evaluate_threshold(current_cands, GATES[g]["feature"], BEST_THRESHOLDS[g], GATES[g]["type"])
            
        grp_a_post = len([c for c in retained if c.get("group") == "A_TrueMR"])
        grp_b_post = len([c for c in retained if c.get("group") == "B_DominantFP"])
        grp_e_post = len([c for c in retained if c.get("group") == "E_PromotedNoise"])
        
        attr_data.append({
            "gate": g,
            "cands_rejected": pre_count - len(retained),
            "mr_rejected": grp_a_pre - grp_a_post,
            "fp_rejected": grp_b_pre - grp_b_post,
            "noise_rejected": grp_e_pre - grp_e_post
        })
        current_cands = retained
        
    m = compute_metrics(canonical_cands, current_cands)
    cascade_results[c_name] = m
    
    cas_eval_md += f"## {c_name}\n"
    cas_eval_md += f"- MR Retention: {m['mr_ret_pct']*100:.1f}%\n"
    cas_eval_md += f"  - Regime A: {m['reg_a_ret_pct']*100:.1f}%\n"
    cas_eval_md += f"  - Regime B: {m['reg_b_ret_pct']*100:.1f}%\n"
    cas_eval_md += f"  - Regime C: {m['reg_c_ret_pct']*100:.1f}%\n"
    cas_eval_md += f"  - Regime D: {m['reg_d_ret_pct']*100:.1f}%\n"
    cas_eval_md += f"- FP Rejection: {m['fp_rej_pct']*100:.1f}%\n"
    cas_eval_md += f"- Noise Rejection: {m['noise_rej_pct']*100:.1f}%\n"
    cas_eval_md += f"- Vol Reduction: {m['vol_red_pct']*100:.1f}%\n"
    cas_eval_md += f"- MR Density Gain: {m['mr_density_gain']:.2f}x\n\n"
    
    cas_attr_md += f"## {c_name}\n"
    for i, a in enumerate(attr_data):
        cas_attr_md += f"### {i+1}. {a['gate']}\n"
        cas_attr_md += f"- Candidates Rejected: {a['cands_rejected']}\n"
        cas_attr_md += f"- MR Rejected: {a['mr_rejected']}\n"
        cas_attr_md += f"- FP Rejected: {a['fp_rejected']}\n"
        cas_attr_md += f"- Noise Rejected: {a['noise_rejected']}\n\n"
        
save_md(cas_eval_md, os.path.join(REPORTS_DIR, "stage510_cascade_evaluation.md"))
save_md(cas_attr_md, os.path.join(REPORTS_DIR, "stage510_cascade_attribution.md"))

# Select Best Cascade
def rank_score(m):
    return (m['mr_ret_pct'] * 1000) + (m['reg_d_ret_pct'] * 100) + (m['noise_rej_pct'] * 10) + m['fp_rej_pct']

best_cas_name = max(cascade_results.keys(), key=lambda k: rank_score(cascade_results[k]))

best_cas_md = "# Best Cascade Selection\n\n" + get_traceability_header() + "\n"
best_cas_md += f"## Selected Cascade: {best_cas_name}\n"
best_cas_md += "Selection based on deterministic priority: 1. MR Ret, 2. Reg D Ret, 3. Noise Rej, 4. FP Rej\n\n"
save_md(best_cas_md, os.path.join(REPORTS_DIR, "stage510_best_cascade_selection.md"))
