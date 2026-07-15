import os
import numpy as np
import json
import datetime
import yaml

BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
SCORE_MAPS_DIR = os.path.join(BASE_DIR, "outputs", "score_maps")
CONFIG_PATH = os.path.join(BASE_DIR, "config", "chamfer.yaml")
REPORT_PATH = os.path.join(BASE_DIR, "reports", "chamfer_score_map_validation.md")

# Traceability info
TIMESTAMP = datetime.datetime.now().strftime("%Y-%m-%dT%H:%M:%SZ")
VERSION = "Stage2_D3_v1"
MANIFEST_VER = "1.0"

def main():
    print("Running Chamfer Score Map Validation...")
    
    # Load config
    with open(CONFIG_PATH, "r", encoding="utf-8") as f:
        config = yaml.safe_load(f)
        
    meta_path = os.path.join(SCORE_MAPS_DIR, "generation_metadata.json")
    if not os.path.exists(meta_path):
        print("Metadata file generation_metadata.json not found! Run chamfer_matching.py first.")
        return
        
    with open(meta_path, "r", encoding="utf-8") as f:
        meta_dict = json.load(f)
        
    score_maps = sorted([f for f in os.listdir(SCORE_MAPS_DIR) if f.endswith(".npy")])
    
    rows = []
    all_valid = True
    
    total_size_bytes = 0
    total_time = 0.0
    total_minima = 0
    
    for filename in score_maps:
        # Parse name e.g., SLD1_T_0.150_000.npy
        parts = filename.replace(".npy", "").split("_")
        sld_name = parts[0]
        scale = float(parts[2])
        rotation = int(parts[3])
        temp_id = f"T_{scale:.3f}_{rotation:03d}"
        
        filepath = os.path.join(SCORE_MAPS_DIR, filename)
        score_map = np.load(filepath)
        
        # Load metadata
        key = f"{sld_name}_{temp_id}"
        meta = meta_dict.get(key, {})
        
        h, w = score_map.shape
        min_score = np.min(score_map)
        max_score = np.max(score_map)
        mean_score = np.mean(score_map)
        median_score = np.median(score_map)
        
        nan_present = np.isnan(score_map).any()
        inf_present = np.isinf(score_map).any()
        
        status = "VALID"
        if nan_present or inf_present:
            status = "FAILED (NaN/Inf)"
            all_valid = False
            
        gen_time = meta.get("generation_time", 0.0)
        mem_cons = meta.get("memory_consumption", 0)
        file_size = meta.get("file_size", 0)
        minima_count = meta.get("local_minima_count", 0)
        
        total_size_bytes += file_size
        total_time += gen_time
        total_minima += minima_count
        
        rows.append({
            "sld": sld_name,
            "template": temp_id,
            "scale": scale,
            "rotation": rotation,
            "dims": f"{w}x{h}",
            "min": float(min_score),
            "max": float(max_score),
            "mean": float(mean_score),
            "median": float(median_score),
            "nan": bool(nan_present),
            "inf": bool(inf_present),
            "status": status,
            "size_kb": file_size / 1024.0,
            "time_ms": gen_time * 1000.0,
            "mem_kb": mem_cons / 1024.0,
            "minima": minima_count
        })
        
    # Generate report
    report_content = f"""# Chamfer Score Map Validation Report

## Traceability
* **Timestamp**: {TIMESTAMP}
* **Version**: {VERSION}
* **Manifest Version**: {MANIFEST_VER}
* **Configuration**: `config/chamfer.yaml`
* **Local Minima Kernel Size**: {config.get('local_minima_kernel_size')}
* **Score Map Storage Format**: {config.get('score_map_storage_format')}

---

## Executive Summary
This report validates the Chamfer score maps computed for all combinations of diagrams and template variants.
Each score map is a float32 matrix representing the average Chamfer distance at each translation offset.

* **Total Score Maps Validated**: {len(rows)}
* **Validation Status**: {"PASS" if all_valid and len(rows) == 400 else "FAIL"}
* **Total Storage Size**: {total_size_bytes / (1024 * 1024):.2f} MB
* **Total Sweep & Extraction Time**: {total_time:.2f} seconds
* **Total Local Minima Proposals**: {total_minima}

---

## Detailed Measurements

| SLD | Template ID | Scale | Rotation | Dimensions | Min Score | Max Score | Mean Score | Median Score | NaN? | Inf? | Status | Size (KB) | Time (ms) | Memory (KB) | Minima Count |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
"""
    
    for r in rows:
        report_content += f"| {r['sld']} | {r['template']} | {r['scale']:.3f} | {r['rotation']} | {r['dims']} | {r['min']:.4f} | {r['max']:.4f} | {r['mean']:.4f} | {r['median']:.4f} | {r['nan']} | {r['inf']} | {r['status']} | {r['size_kb']:.1f} | {r['time_ms']:.1f} | {r['mem_kb']:.1f} | {r['minima']} |\n"
        
    with open(REPORT_PATH, "w", encoding="utf-8") as f:
        f.write(report_content)
        
    print(f"Chamfer Score Map Validation complete. Report generated at: {REPORT_PATH}")

if __name__ == "__main__":
    main()
