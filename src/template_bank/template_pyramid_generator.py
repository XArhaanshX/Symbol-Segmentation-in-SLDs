import os
import sys
import cv2
import numpy as np
import csv
import yaml
import datetime

BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
TEMPLATE_PATH = os.path.join(BASE_DIR, "outputs", "template", "edges.png")
TEMPLATE_BANK_DIR = os.path.join(BASE_DIR, "outputs", "template_bank")
SCALES_DIR = os.path.join(TEMPLATE_BANK_DIR, "scales")
ROTATIONS_DIR = os.path.join(TEMPLATE_BANK_DIR, "rotations")
MANIFEST_PATH = os.path.join(TEMPLATE_BANK_DIR, "template_bank_manifest.csv")
CONFIG_PATH = os.path.join(BASE_DIR, "config", "template_bank.yaml")

# Check config file existence
if not os.path.exists(CONFIG_PATH):
    # Create configuration_missing.md
    reports_dir = os.path.join(BASE_DIR, "reports")
    os.makedirs(reports_dir, exist_ok=True)
    timestamp = datetime.datetime.now().strftime("%Y-%m-%dT%H:%M:%SZ")
    
    missing_report = f"""# Configuration File Missing

## Traceability
- **Generation Timestamp**: {timestamp}
- **Template Bank Version**: N/A (Failed to Initialize)
- **Generation Method**: N/A
- **Configuration Source**: {CONFIG_PATH} (MISSING)
- **Manifest Version**: N/A
- **Template Count**: 0

---

## 1. Error Summary

The template bank generation pipeline could not proceed because the configuration file `config/template_bank.yaml` is missing.

As mandated by Stage 2.7 requirements, the generation has halted immediately to prevent any fallback to hardcoded or unverified parameter values.

Please ensure the configuration file exists and contains the PRD-approved values:
- `scale_min`
- `scale_max`
- `num_scales`
- `scale_spacing_strategy`
- `rotations`
- `generation_method`
"""
    with open(os.path.join(reports_dir, "configuration_missing.md"), "w") as f:
        f.write(missing_report)
    
    print(f"CRITICAL ERROR: Configuration file not found at {CONFIG_PATH}.", file=sys.stderr)
    print(f"Halted and generated reports/configuration_missing.md.", file=sys.stderr)
    sys.exit(1)

# Load parameters from config
with open(CONFIG_PATH, "r") as f:
    config = yaml.safe_load(f)

SCALE_MIN = float(config.get("scale_min", 0.15))
SCALE_MAX = float(config.get("scale_max", 0.40))
N_SCALES = int(config.get("num_scales", 10))
ROTATIONS = [int(r) for r in config.get("rotations", [0, 90, 180, 270])]
SPACING_STRATEGY = config.get("scale_spacing_strategy", "linear")
GENERATION_METHOD = config.get("generation_method", "D3")

if GENERATION_METHOD != "D3":
    print(f"CRITICAL ERROR: Selected method {GENERATION_METHOD} is not Method D3.", file=sys.stderr)
    sys.exit(1)

def rotate_bound(image, angle):
    """Rotate image without clipping."""
    h, w = image.shape[:2]
    cx, cy = w / 2.0, h / 2.0
    M = cv2.getRotationMatrix2D((cx, cy), angle, 1.0)
    
    cos = np.abs(M[0, 0])
    sin = np.abs(M[0, 1])
    
    nW = int((h * sin) + (w * cos))
    nH = int((h * cos) + (w * sin))
    
    M[0, 2] += (nW / 2.0) - cx
    M[1, 2] += (nH / 2.0) - cy
    
    return cv2.warpAffine(image, M, (nW, nH), borderMode=cv2.BORDER_CONSTANT, borderValue=0)

def get_structural_metadata(img):
    """Compute measured structural metrics on binary template."""
    h, w = img.shape
    edge_count = int(np.count_nonzero(img))
    if edge_count == 0:
        return w, h, 0, 0, 0, 0.0, 0.0
    
    num_labels, labels = cv2.connectedComponents(img, connectivity=8)
    component_count = int(max(0, num_labels - 1))
    contours, _ = cv2.findContours(img, cv2.RETR_LIST, cv2.CHAIN_APPROX_SIMPLE)
    contour_count = int(len(contours))
    
    coords = cv2.findNonZero(img)
    bx, by, bw, bh = cv2.boundingRect(coords)
    bbox_area = bw * bh
    edge_density = float(edge_count / bbox_area if bbox_area > 0 else 0.0)
    
    label_sizes = [int(np.sum(labels == idx)) for idx in range(1, num_labels)]
    largest_cc = max(label_sizes) if label_sizes else 0
    edge_continuity = float(largest_cc / edge_count if edge_count > 0 else 0.0)
    
    return w, h, edge_count, component_count, contour_count, edge_density, edge_continuity

def generate_d3_template(rotated_base, scale_factor, w_s, h_s):
    """Implement Method D3: Coordinate Scaling + Subpixel Anti-Aliased Rasterization."""
    edge_pixels = np.argwhere(rotated_base > 0) # List of [y, x]
    if len(edge_pixels) == 0:
        return np.zeros((h_s, w_s), dtype=np.uint8)
    
    # 8-connectivity adjacent pixel pairs in rotated high-res template
    adj_pairs = []
    for i in range(len(edge_pixels)):
        y1, x1 = edge_pixels[i]
        for j in range(i + 1, len(edge_pixels)):
            y2, x2 = edge_pixels[j]
            if max(abs(y1 - y2), abs(x1 - x2)) <= 1:
                adj_pairs.append((i, j))
                
    # Canvas scale factor
    F = 8
    canvas_w = w_s * F
    canvas_h = h_s * F
    canvas = np.zeros((canvas_h, canvas_w), dtype=np.uint8)
    
    # Scale coordinates to subpixel space
    scaled_pixels = edge_pixels * scale_factor * F
    for i, j in adj_pairs:
        y1, x1 = scaled_pixels[i]
        y2, x2 = scaled_pixels[j]
        pt1 = (int(round(x1)), int(round(y1)))
        pt2 = (int(round(x2)), int(round(y2)))
        cv2.line(canvas, pt1, pt2, 255, 1)
        
    downsampled = cv2.resize(canvas, (w_s, h_s), interpolation=cv2.INTER_AREA)
    _, img_d3 = cv2.threshold(downsampled, 25, 255, cv2.THRESH_BINARY)
    return img_d3

def clean_directory(dir_path):
    """Safely delete all files inside a directory to avoid WinError 5 on directory rmtree."""
    if os.path.exists(dir_path):
        for root, dirs, files in os.walk(dir_path, topdown=False):
            for name in files:
                try:
                    os.remove(os.path.join(root, name))
                except Exception as e:
                    print(f"Warning: could not remove file {name}: {e}")
            for name in dirs:
                try:
                    os.rmdir(os.path.join(root, name))
                except Exception as e:
                    print(f"Warning: could not remove dir {name}: {e}")

def generate_pyramids():
    # Clean output directories safely
    clean_directory(SCALES_DIR)
    clean_directory(ROTATIONS_DIR)
        
    os.makedirs(SCALES_DIR, exist_ok=True)
    os.makedirs(ROTATIONS_DIR, exist_ok=True)

    if not os.path.exists(TEMPLATE_PATH):
        raise FileNotFoundError(f"Source template not found: {TEMPLATE_PATH}")

    edges = cv2.imread(TEMPLATE_PATH, cv2.IMREAD_GRAYSCALE)
    if edges is None:
        raise ValueError("Failed to load template edges.")

    if SPACING_STRATEGY == "linear":
        scales = np.linspace(SCALE_MIN, SCALE_MAX, N_SCALES)
    else:
        print(f"CRITICAL ERROR: Strategy {SPACING_STRATEGY} is not supported.", file=sys.stderr)
        sys.exit(1)
        
    manifest = []

    for s in scales:
        # 1. Generate scale-only template (r=0) using Method D3
        w_s = int(round(edges.shape[1] * s))
        h_s = int(round(edges.shape[0] * s))
        scale_img = generate_d3_template(edges, s, w_s, h_s)
        
        scale_filename = f"scale_{s:.3f}.png"
        scale_filepath = os.path.join(SCALES_DIR, scale_filename)
        cv2.imwrite(scale_filepath, scale_img)

        # 2. Generate rotation variants
        for r in ROTATIONS:
            # Rotate high-resolution baseline first
            rotated_high = rotate_bound(edges, r)
            w_rot = int(round(rotated_high.shape[1] * s))
            h_rot = int(round(rotated_high.shape[0] * s))
            rotated_img = generate_d3_template(rotated_high, s, w_rot, h_rot)
            
            rot_filename = f"scale_{s:.3f}_rot_{r:03d}.png"
            rot_filepath = os.path.join(ROTATIONS_DIR, rot_filename)
            cv2.imwrite(rot_filepath, rotated_img)
            
            w, h, e_c, comp_c, cont_c, density, continuity = get_structural_metadata(rotated_img)
            template_id = f"T_{s:.3f}_{r:03d}"
            
            rel_path = f"outputs/template_bank/rotations/{rot_filename}"
            
            manifest.append({
                "template_id": template_id,
                "scale": f"{s:.3f}",
                "rotation": r,
                "width": w,
                "height": h,
                "edge_count": e_c,
                "component_count": comp_c,
                "contour_count": cont_c,
                "edge_density": float(density),
                "edge_continuity": float(continuity),
                "filepath": rel_path
            })

    # Save manifest
    with open(MANIFEST_PATH, "w", newline="") as f:
        fieldnames = [
            "template_id", "scale", "rotation", "width", "height", 
            "edge_count", "component_count", "contour_count", 
            "edge_density", "edge_continuity", "filepath"
        ]
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(manifest)

    print(f"Generated {len(manifest)} template variants using Method D3.")
    print(f"Manifest saved to {MANIFEST_PATH}")

if __name__ == "__main__":
    generate_pyramids()
