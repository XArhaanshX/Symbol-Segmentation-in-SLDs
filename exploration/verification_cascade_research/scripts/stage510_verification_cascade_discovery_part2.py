# -------------------------------------------------------------------------
# PHASE 5.10B: GATE REGISTRY
# -------------------------------------------------------------------------
print("Phase 5.10B: Gate Registry")

GATES = {
    "Gate_ST_01": {"feature": "Stroke_Count", "type": "max", "desc": "Stroke_Count <= Threshold"},
    "Gate_CS_01": {"feature": "Stroke_Difference", "type": "max", "desc": "Stroke_Difference <= Threshold"},
    "Gate_CS_02": {"feature": "Normalized_Stroke_Difference", "type": "max", "desc": "Normalized_Stroke_Difference <= Threshold"},
    "Gate_CS_03": {"feature": "Stroke_Ratio", "type": "max", "desc": "Stroke_Ratio <= Threshold"},
    "Gate_EX_01": {"feature": "Foreground_Pixel_Count", "type": "min", "desc": "Foreground_Pixel_Count >= Threshold"},
    "Gate_EX_02": {"feature": "Contour_Perimeter", "type": "min", "desc": "Contour_Perimeter >= Threshold"},
    "Gate_EX_03": {"feature": "Skeleton_Length", "type": "min", "desc": "Skeleton_Length >= Threshold"},
    "Gate_EX_04": {"feature": "Occupancy_Ratio", "type": "min", "desc": "Occupancy_Ratio >= Threshold"}
}
# Gate_ST_02 requires template matching tolerance, skipping for automated simple sweep, focusing on others.

gate_registry_md = "# Gate Registry\n\n" + get_traceability_header() + "\n"
for gid, ginfo in GATES.items():
    gate_registry_md += f"## {gid}\n- Feature Used: {ginfo['feature']}\n- Mathematical Definition: {ginfo['desc']}\n- Feature Source: Topological / Consistency / Existence\n\n"
save_md(gate_registry_md, os.path.join(REPORTS_DIR, "stage510_gate_registry.md"))

# -------------------------------------------------------------------------
# PHASE 5.10C: SINGLE-GATE SWEEP ANALYSIS
# -------------------------------------------------------------------------
print("Phase 5.10C: Single-Gate Sweep Analysis")

def evaluate_threshold(candidates, feature, thresh, type="min"):
    if type == "min":
        retained = [c for c in candidates if c[feature] >= thresh]
        rejected = [c for c in candidates if c[feature] < thresh]
    else:
        retained = [c for c in candidates if c[feature] <= thresh]
        rejected = [c for c in candidates if c[feature] > thresh]
        
    return retained, rejected

def compute_metrics(original, retained):
    grp_a_orig = [c for c in original if c.get("group") == "A_TrueMR"]
    grp_b_orig = [c for c in original if c.get("group") == "B_DominantFP"]
    grp_e_orig = [c for c in original if c.get("group") == "E_PromotedNoise"]
    
    grp_a_ret = [c for c in retained if c.get("group") == "A_TrueMR"]
    grp_b_ret = [c for c in retained if c.get("group") == "B_DominantFP"]
    grp_e_ret = [c for c in retained if c.get("group") == "E_PromotedNoise"]
    
    reg_a_orig = [c for c in grp_a_orig if c.get("regime") == "A"]
    reg_b_orig = [c for c in grp_a_orig if c.get("regime") == "B"]
    reg_c_orig = [c for c in grp_a_orig if c.get("regime") == "C"]
    reg_d_orig = [c for c in grp_a_orig if c.get("regime") == "D"]
    
    reg_a_ret = [c for c in grp_a_ret if c.get("regime") == "A"]
    reg_b_ret = [c for c in grp_a_ret if c.get("regime") == "B"]
    reg_c_ret = [c for c in grp_a_ret if c.get("regime") == "C"]
    reg_d_ret = [c for c in grp_a_ret if c.get("regime") == "D"]
    
    mr_ret_pct = len(grp_a_ret)/len(grp_a_orig) if grp_a_orig else 0.0
    fp_rej_pct = 1.0 - (len(grp_b_ret)/len(grp_b_orig)) if grp_b_orig else 0.0
    noise_rej_pct = 1.0 - (len(grp_e_ret)/len(grp_e_orig)) if grp_e_orig else 0.0
    reg_d_ret_pct = len(reg_d_ret)/len(reg_d_orig) if reg_d_orig else 0.0
    
    vol_red_pct = 1.0 - (len(retained)/len(original)) if original else 0.0
    
    mr_density_orig = len(grp_a_orig) / len(original) if len(original) > 0 else 0
    mr_density_ret = len(grp_a_ret) / len(retained) if len(retained) > 0 else 0
    mr_density_gain = mr_density_ret / mr_density_orig if mr_density_orig > 0 else 1.0
    
    return {
        "mr_ret_pct": mr_ret_pct,
        "fp_rej_pct": fp_rej_pct,
        "noise_rej_pct": noise_rej_pct,
        "reg_a_ret_pct": len(reg_a_ret)/len(reg_a_orig) if reg_a_orig else 0.0,
        "reg_b_ret_pct": len(reg_b_ret)/len(reg_b_orig) if reg_b_orig else 0.0,
        "reg_c_ret_pct": len(reg_c_ret)/len(reg_c_orig) if reg_c_orig else 0.0,
        "reg_d_ret_pct": reg_d_ret_pct,
        "vol_red_pct": vol_red_pct,
        "mr_density": mr_density_ret,
        "mr_density_gain": mr_density_gain
    }

sweep_results = {}
sg_md = "# Single-Gate Sweep Analysis\n\n" + get_traceability_header() + "\n"

for gid, ginfo in GATES.items():
    print(f"Sweeping {gid}...")
    sg_md += f"## {gid}\n"
    feat = ginfo["feature"]
    vals = sorted([c[feat] for c in canonical_cands if not math.isnan(c[feat]) and not math.isinf(c[feat])])
    if not vals: continue
    
    # 20 threshold steps
    steps = [np.percentile(vals, p) for p in np.linspace(1, 99, 20)]
    
    sweep_results[gid] = []
    
    for t in steps:
        ret, rej = evaluate_threshold(canonical_cands, feat, t, ginfo["type"])
        m = compute_metrics(canonical_cands, ret)
        m["threshold"] = t
        sweep_results[gid].append(m)
        
    # Print best result visually
    best_m = max(sweep_results[gid], key=lambda x: x["fp_rej_pct"] + x["noise_rej_pct"] if x["mr_ret_pct"] >= 0.95 else -1)
    sg_md += f"- Best Threshold found: {best_m['threshold']:.2f}\n"
    sg_md += f"  - MR Retention: {best_m['mr_ret_pct']*100:.1f}% (Regime D: {best_m['reg_d_ret_pct']*100:.1f}%)\n"
    sg_md += f"  - FP Rejection: {best_m['fp_rej_pct']*100:.1f}%\n"
    sg_md += f"  - Noise Rejection: {best_m['noise_rej_pct']*100:.1f}%\n"
    sg_md += f"  - Density Gain: {best_m['mr_density_gain']:.2f}x\n\n"

save_md(sg_md, os.path.join(REPORTS_DIR, "stage510_single_gate_analysis.md"))
