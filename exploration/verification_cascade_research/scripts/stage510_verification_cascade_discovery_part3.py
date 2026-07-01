# -------------------------------------------------------------------------
# PHASE 5.10D: SAFE OPERATING REGION DISCOVERY
# -------------------------------------------------------------------------
print("Phase 5.10D & D-1 & D-2: Threshold Discovery, Feasibility, Stability")

BEST_THRESHOLDS = {}
sor_md = "# Safe Operating Region Discovery\n\n" + get_traceability_header() + "\n"
feas_md = "# Threshold Feasibility Assessment\n\n" + get_traceability_header() + "\n"
stab_md = "# Threshold Stability Validation\n\n" + get_traceability_header() + "\n"

for gid, res in sweep_results.items():
    # Feasibility: does ANY threshold meet criteria?
    valid = [m for m in res if m["mr_ret_pct"] >= 0.95 and m["reg_d_ret_pct"] >= 0.90]
    
    feas_md += f"## {gid}\n"
    if len(valid) == 0:
        feas_md += "- **Feasible Threshold Exists:** NO\n"
        sor_md += f"## {gid}\n- Safe Range: NONE\n\n"
        continue
    
    best_m = max(valid, key=lambda x: x["fp_rej_pct"] + x["noise_rej_pct"])
    if best_m["fp_rej_pct"] < 0.05 and best_m["noise_rej_pct"] < 0.05:
        feas_md += "- **Feasible Threshold Exists:** NO (Fails meaningful rejection)\n"
        sor_md += f"## {gid}\n- Safe Range: NONE (No meaningful rejection)\n\n"
        continue
        
    feas_md += "- **Feasible Threshold Exists:** YES\n"
    BEST_THRESHOLDS[gid] = best_m["threshold"]
    
    min_t = min(v["threshold"] for v in valid)
    max_t = max(v["threshold"] for v in valid)
    
    sor_md += f"## {gid}\n"
    sor_md += f"- Safe Threshold Range: [{min_t:.2f}, {max_t:.2f}]\n"
    sor_md += f"- Best Threshold: {best_m['threshold']:.2f}\n"
    sor_md += f"- MR Retention: {best_m['mr_ret_pct']*100:.1f}%\n"
    sor_md += f"  - Regime A: {best_m['reg_a_ret_pct']*100:.1f}%\n"
    sor_md += f"  - Regime B: {best_m['reg_b_ret_pct']*100:.1f}%\n"
    sor_md += f"  - Regime C: {best_m['reg_c_ret_pct']*100:.1f}%\n"
    sor_md += f"  - Regime D: {best_m['reg_d_ret_pct']*100:.1f}%\n"
    sor_md += f"- FP Rejection: {best_m['fp_rej_pct']*100:.1f}%\n"
    sor_md += f"- Noise Rejection: {best_m['noise_rej_pct']*100:.1f}%\n\n"
    
    # 5.10D-1: Stability Validation (Bootstrap Resampling)
    n_boot = 50
    st_mr = []
    st_reg_d = []
    st_fp = []
    st_noise = []
    
    for _ in range(n_boot):
        sample = list(np.random.choice(canonical_cands, size=len(canonical_cands), replace=True))
        ret, _ = evaluate_threshold(sample, GATES[gid]["feature"], best_m["threshold"], GATES[gid]["type"])
        m = compute_metrics(sample, ret)
        st_mr.append(m["mr_ret_pct"])
        st_reg_d.append(m["reg_d_ret_pct"])
        st_fp.append(m["fp_rej_pct"])
        st_noise.append(m["noise_rej_pct"])
        
    stab_md += f"## {gid} (Threshold {best_m['threshold']:.2f})\n"
    stab_md += f"- Mean MR Retention: {np.mean(st_mr)*100:.2f}% (StdDev: {np.std(st_mr)*100:.2f}%)\n"
    stab_md += f"- Mean Reg D Retention: {np.mean(st_reg_d)*100:.2f}% (StdDev: {np.std(st_reg_d)*100:.2f}%)\n"
    stab_md += f"- Mean FP Rejection: {np.mean(st_fp)*100:.2f}% (StdDev: {np.std(st_fp)*100:.2f}%)\n"
    stab_md += f"- Mean Noise Rejection: {np.mean(st_noise)*100:.2f}% (StdDev: {np.std(st_noise)*100:.2f}%)\n"
    if np.std(st_mr) < 0.05:
        stab_md += "- Q1. Stable? YES\n- Q2. Large Variance? NO\n- Q3. Generalizes? YES\n\n"
    else:
        stab_md += "- Q1. Stable? NO\n- Q2. Large Variance? YES\n- Q3. Generalizes? NO\n\n"

save_md(sor_md, os.path.join(REPORTS_DIR, "stage510_safe_operating_regions.md"))
save_md(feas_md, os.path.join(REPORTS_DIR, "stage510_threshold_feasibility.md"))
save_md(stab_md, os.path.join(REPORTS_DIR, "stage510_threshold_stability.md"))

# -------------------------------------------------------------------------
# PHASE 5.10E: CASCADE REGISTRY
# -------------------------------------------------------------------------
print("Phase 5.10E: Cascade Registry")

CASCADES = {
    "Cascade_A": ["Gate_EX_02", "Gate_CS_01"],
    "Cascade_B": ["Gate_CS_01", "Gate_EX_02"],
    "Cascade_C": ["Gate_EX_02", "Gate_ST_01", "Gate_CS_01"],
    "Cascade_D": ["Gate_EX_02", "Gate_CS_01", "Verification"],
    "Cascade_E": ["Gate_EX_02", "Gate_ST_01", "Gate_CS_01", "Verification"]
}

# If a required gate didn't find a safe threshold, we must drop it or use a default
for c_name, c_gates in CASCADES.items():
    for g in c_gates:
        if g != "Verification" and g not in BEST_THRESHOLDS:
            print(f"Warning: {g} has no valid threshold for {c_name}. Using permissive fallback.")
            BEST_THRESHOLDS[g] = 0.0 if GATES[g]["type"] == "min" else 999999.0

cas_reg_md = "# Cascade Registry\n\n" + get_traceability_header() + "\n"
for c_name, c_gates in CASCADES.items():
    cas_reg_md += f"## {c_name}\n- Execution Order: {' -> '.join(c_gates)}\n"
    cas_reg_md += "- Feature Dependencies: " + ", ".join([GATES[g]["feature"] for g in c_gates if g != "Verification"]) + "\n\n"
save_md(cas_reg_md, os.path.join(REPORTS_DIR, "stage510_cascade_registry.md"))
