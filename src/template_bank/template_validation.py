import os
import cv2
import numpy as np
import csv
import matplotlib.pyplot as plt
from datetime import datetime

BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
TEMPLATE_PATH = os.path.join(BASE_DIR, "outputs", "template", "edges.png")
MANIFEST_PATH = os.path.join(BASE_DIR, "outputs", "template_bank", "template_bank_manifest.csv")
REPORTS_DIR = os.path.join(BASE_DIR, "reports")
VISUAL_DIR = os.path.join(REPORTS_DIR, "template_bank_visual_validation")

def load_manifest():
    templates = []
    with open(MANIFEST_PATH, "r") as f:
        reader = csv.DictReader(f)
        for row in reader:
            templates.append(row)
    return templates

def get_structural_metadata(img):
    h, w = img.shape
    edge_count = np.count_nonzero(img)
    num_labels, _ = cv2.connectedComponents(img, connectivity=8)
    component_count = max(0, num_labels - 1)
    contours, _ = cv2.findContours(img, cv2.RETR_LIST, cv2.CHAIN_APPROX_SIMPLE)
    contour_count = len(contours)
    return w, h, edge_count, component_count, contour_count

def validate_bank():
    os.makedirs(VISUAL_DIR, exist_ok=True)
    timestamp = datetime.utcnow().strftime('%Y-%m-%dT%H:%M:%SZ')
    
    # 1. Baseline stats
    baseline_img = cv2.imread(TEMPLATE_PATH, cv2.IMREAD_GRAYSCALE)
    bw, bh, bedge, bcomp, bcont = get_structural_metadata(baseline_img)
    
    manifest = load_manifest()
    
    warnings = []
    errors = []
    
    manifest_errors = []
    stats = {
        "widths": [],
        "heights": [],
        "edge_counts": [],
        "comp_counts": [],
        "cont_counts": [],
        "rotations": {0: 0, 90: 0, 180: 0, 270: 0},
        "scales": []
    }
    
    # Validation Loop
    for t in manifest:
        tid = t["template_id"]
        filepath = os.path.join(BASE_DIR, t["filepath"].replace("/", os.sep))
        scale = float(t["scale"])
        rotation = int(t["rotation"])
        
        # Manifest checks
        if not os.path.exists(filepath):
            manifest_errors.append(f"Missing file for {tid}: {filepath}")
            continue
            
        img = cv2.imread(filepath, cv2.IMREAD_GRAYSCALE)
        if img is None:
            errors.append(f"{tid}: File corrupted or unreadable.")
            continue
            
        w, h, edge, comp, cont = get_structural_metadata(img)
        
        # Record stats
        stats["widths"].append(w)
        stats["heights"].append(h)
        stats["edge_counts"].append(edge)
        stats["comp_counts"].append(comp)
        stats["cont_counts"].append(cont)
        stats["rotations"][rotation] += 1
        if scale not in stats["scales"]:
            stats["scales"].append(scale)
            
        # Programmatic checks
        if edge == 0:
            errors.append(f"{tid}: Template is empty (0 edge pixels).")
        
        # Geometry Preservation
        if comp != bcomp:
            warnings.append(f"{tid}: Component count changed ({bcomp} -> {comp}). Indicates merged/split structures.")
            
        # A simple aspect ratio check on 0 and 180 rotations
        if rotation in [0, 180]:
            ar_base = bw / bh if bh > 0 else 0
            ar_t = w / h if h > 0 else 0
            if abs(ar_base - ar_t) > 0.1:
                warnings.append(f"{tid}: Aspect ratio significantly distorted ({ar_base:.2f} -> {ar_t:.2f}).")
        
        # Verify manifest matches actual file contents
        if int(t["width"]) != w or int(t["height"]) != h or int(t["edge_count"]) != edge:
            manifest_errors.append(f"{tid}: Manifest metadata mismatch.")

    # Generate Reports
    
    # 1. Manifest Validation Report
    with open(os.path.join(REPORTS_DIR, "template_manifest_validation.md"), "w", encoding="utf-8") as f:
        f.write("# Template Manifest Validation Report\n\n")
        f.write("## Traceability\n")
        f.write(f"- **Source Template**: `outputs/template/edges.png`\n")
        f.write(f"- **Generation Timestamp**: {timestamp}\n")
        f.write(f"- **Template Count**: {len(manifest)}\n")
        f.write(f"- **PRD Version Used**: PRD_Symbol_Localization.md (Current)\n\n")
        f.write("## Results\n")
        if not manifest_errors:
            f.write("✅ **PASSED**: All manifest entries map to existing files, and metadata strictly matches file contents.\n")
        else:
            f.write("❌ **FAILED**: Manifest errors detected:\n")
            for e in manifest_errors:
                f.write(f"- {e}\n")
                
    # 2. Geometry Validation Report
    with open(os.path.join(REPORTS_DIR, "template_bank_validation.md"), "w", encoding="utf-8") as f:
        f.write("# Geometry Preservation Validation Report\n\n")
        f.write("## Traceability\n")
        f.write(f"- **Source Template**: `outputs/template/edges.png`\n")
        f.write(f"- **Generation Timestamp**: {timestamp}\n")
        f.write(f"- **Template Count**: {len(manifest)}\n")
        f.write(f"- **PRD Version Used**: PRD_Symbol_Localization.md (Current)\n\n")
        
        f.write("## Error Summary (Critical Failures)\n")
        if not errors:
            f.write("No critical errors detected. No empty or corrupted templates.\n\n")
        else:
            for e in errors:
                f.write(f"- ❌ {e}\n")
            f.write("\n")
            
        f.write("## Warning Summary (Geometry Alterations)\n")
        if not warnings:
            f.write("No geometry warnings. Component structures perfectly preserved across all scales and rotations.\n")
        else:
            for w_msg in warnings:
                f.write(f"- ⚠️ {w_msg}\n")
                
    # 3. Statistics Report
    with open(os.path.join(REPORTS_DIR, "template_bank_statistics.md"), "w", encoding="utf-8") as f:
        f.write("# Template Bank Statistics\n\n")
        f.write("## Traceability\n")
        f.write(f"- **Source Template**: `outputs/template/edges.png`\n")
        f.write(f"- **Generation Timestamp**: {timestamp}\n")
        f.write(f"- **Template Count**: {len(manifest)}\n")
        f.write(f"- **PRD Version Used**: PRD_Symbol_Localization.md (Current)\n\n")
        
        f.write("## Summary Metrics\n")
        f.write(f"- **Total Templates Generated**: {len(manifest)}\n")
        f.write(f"- **Scale Distribution**: {min(stats['scales']):.3f} to {max(stats['scales']):.3f} ({len(stats['scales'])} levels)\n")
        f.write(f"- **Rotation Distribution**: 0° ({stats['rotations'][0]}), 90° ({stats['rotations'][90]}), 180° ({stats['rotations'][180]}), 270° ({stats['rotations'][270]})\n")
        
        f.write("\n## Dimensional Statistics\n")
        f.write(f"- **Smallest Template**: {min(stats['widths'])} x {min(stats['heights'])} px\n")
        f.write(f"- **Largest Template**: {max(stats['widths'])} x {max(stats['heights'])} px\n")
        f.write(f"- **Mean Dimensions**: {np.mean(stats['widths']):.1f} x {np.mean(stats['heights']):.1f} px\n")
        f.write(f"- **Median Dimensions**: {np.median(stats['widths']):.1f} x {np.median(stats['heights']):.1f} px\n")
        
        f.write("\n## Structural Statistics\n")
        f.write(f"- **Mean Edge Pixels**: {np.mean(stats['edge_counts']):.1f}\n")
        f.write(f"- **Mean Connected Components**: {np.mean(stats['comp_counts']):.1f} (Baseline: {bcomp})\n")
        f.write(f"- **Mean Contours**: {np.mean(stats['cont_counts']):.1f} (Baseline: {bcont})\n")
        f.write("\n**Conclusion**: This report is the canonical reference for Stage 3 debugging and Chamfer analysis.\n")
        
    # 4. Visual Validation
    # Pick min scale, mid scale, max scale
    sorted_scales = sorted(stats["scales"])
    min_s, mid_s, max_s = sorted_scales[0], sorted_scales[len(sorted_scales)//2], sorted_scales[-1]
    scales_to_plot = [min_s, mid_s, max_s]
    
    for s in scales_to_plot:
        fig, axes = plt.subplots(1, 5, figsize=(15, 3))
        fig.suptitle(f"Visual Validation: Scale {s:.3f}")
        
        axes[0].imshow(baseline_img, cmap='gray')
        axes[0].set_title("Original")
        axes[0].axis('off')
        
        for i, r in enumerate([0, 90, 180, 270]):
            tid = f"T_{s:.3f}_{r:03d}"
            entry = next((item for item in manifest if item["template_id"] == tid), None)
            if entry:
                p = os.path.join(BASE_DIR, entry["filepath"].replace("/", os.sep))
                img = cv2.imread(p, cv2.IMREAD_GRAYSCALE)
                axes[i+1].imshow(img, cmap='gray')
                axes[i+1].set_title(f"Rot {r}°")
                axes[i+1].axis('off')
                
        plt.tight_layout()
        plt.savefig(os.path.join(VISUAL_DIR, f"visual_scale_{s:.3f}.png"), dpi=150)
        plt.close()

    print(f"Validation completed. Reports saved to {REPORTS_DIR}")

if __name__ == "__main__":
    validate_bank()
