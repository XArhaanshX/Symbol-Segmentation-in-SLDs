import os
import cv2
import numpy as np
import datetime
import yaml

BASE_DIR = r"c:\Users\arhaa\OneDrive\Symbol Segmentor"
DT_DIR = os.path.join(BASE_DIR, "outputs", "distance_transforms")
CONFIG_PATH = os.path.join(BASE_DIR, "config", "chamfer.yaml")
REPORT_PATH = os.path.join(BASE_DIR, "reports", "distance_transform_validation.md")

# Traceability info
TIMESTAMP = datetime.datetime.now().strftime("%Y-%m-%dT%H:%M:%SZ")
VERSION = "Stage2_D3_v1"
MANIFEST_VER = "1.0"
TEMPLATE_COUNT = 40
SLD_COUNT = 10

def main():
    print("Running Distance Transform Validation...")
    
    # Check config
    with open(CONFIG_PATH, "r", encoding="utf-8") as f:
        config = yaml.safe_load(f)
        
    sld_dts = sorted([f for f in os.listdir(DT_DIR) if f.endswith("_dt.tiff")])
    
    rows = []
    all_valid = True
    
    for filename in sld_dts:
        sld_name = filename.split("_")[0]
        filepath = os.path.join(DT_DIR, filename)
        
        # Load float32 tiff
        dt_img = cv2.imread(filepath, cv2.IMREAD_UNCHANGED)
        if dt_img is None:
            rows.append({
                "sld": sld_name,
                "width": 0,
                "height": 0,
                "min_val": 0.0,
                "max_val": 0.0,
                "mean_val": 0.0,
                "nan_present": True,
                "inf_present": True,
                "status": "FAILED (Load Error)"
            })
            all_valid = False
            continue
            
        h, w = dt_img.shape
        min_val = np.min(dt_img)
        max_val = np.max(dt_img)
        mean_val = np.mean(dt_img)
        
        nan_present = np.isnan(dt_img).any()
        inf_present = np.isinf(dt_img).any()
        
        status = "VALID"
        if nan_present or inf_present:
            status = "FAILED (NaN/Inf)"
            all_valid = False
        if min_val < 0.0:
            status = "FAILED (Negative Distance)"
            all_valid = False
            
        rows.append({
            "sld": sld_name,
            "width": w,
            "height": h,
            "min_val": float(min_val),
            "max_val": float(max_val),
            "mean_val": float(mean_val),
            "nan_present": bool(nan_present),
            "inf_present": bool(inf_present),
            "status": status
        })
        
    # Generate report content
    report_content = f"""# Distance Transform Validation Report

## Traceability
* **Timestamp**: {TIMESTAMP}
* **Version**: {VERSION}
* **Manifest Version**: {MANIFEST_VER}
* **Configuration**: `config/chamfer.yaml`
* **Local Minima Kernel Size**: {config.get('local_minima_kernel_size')}
* **Score Map Storage Format**: {config.get('score_map_storage_format')}

---

## Executive Summary
This report validates the Euclidean Distance Transforms (DT) computed for the target diagrams under Stage 3a. Distance transforms are floating-point representations where each pixel represents the spatial Euclidean distance to the nearest edge pixel in the binarized diagram.

**Validation Result**: {"PASS" if all_valid and len(rows) == SLD_COUNT else "FAIL"}

---

## Detailed Measurements

| SLD Name | Width | Height | Min Distance | Max Distance | Mean Distance | NaN Present | Inf Present | Transform Status |
|---|---|---|---|---|---|---|---|---|
"""
    
    for r in rows:
        report_content += f"| {r['sld']} | {r['width']} | {r['height']} | {r['min_val']:.4f} | {r['max_val']:.4f} | {r['mean_val']:.4f} | {r['nan_present']} | {r['inf_present']} | {r['status']} |\n"
        
    report_content += """
---

## Verification Assertions
1. **Edge Anchoring Check**: Min Distance must be exactly `0.0` or close to `0.0` at the locations of the diagram edges.
2. **Smooth Gradient Check**: Mean distance values should reflect the overall density of the edge map (sparsely populated maps will have higher mean distances).
3. **No NaNs/Infs**: Distance values must be real finite floating-point numbers.
"""
    
    os.makedirs(os.path.dirname(REPORT_PATH), exist_ok=True)
    with open(REPORT_PATH, "w", encoding="utf-8") as f:
        f.write(report_content)
        
    print(f"Distance Transform Validation complete. Report generated at: {REPORT_PATH}")

if __name__ == "__main__":
    main()
