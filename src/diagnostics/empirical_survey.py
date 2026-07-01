import os
import cv2
import numpy as np
import matplotlib.pyplot as plt

BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
SLD_DIR = os.path.join(BASE_DIR, "Data", "SLDs")
TEMPLATE_PATH = os.path.join(BASE_DIR, "Data", "Symbol", "MR_Symbol.png")
REPORTS_DIR = os.path.join(BASE_DIR, "reports")
EVIDENCE_DIR = os.path.join(REPORTS_DIR, "measurement_evidence")

SLD_FILES = ["SLD1.png", "SLD2.png", "SLD3.png", "SLD4.png", "SLD7.png", "SLD8.png", "SLD9.png", "SLD10.png", "SLD11.png", "SLD12.png"]

def measure_reference():
    img = cv2.imread(TEMPLATE_PATH, cv2.IMREAD_GRAYSCALE)
    if img is None:
        raise ValueError(f"Could not load {TEMPLATE_PATH}")
    
    # Invert if necessary (assume black on white for raw symbol, but let's check)
    if img[0,0] > 127:
        img = cv2.bitwise_not(img)
    
    _, bin_img = cv2.threshold(img, 127, 255, cv2.THRESH_BINARY)
    coords = cv2.findNonZero(bin_img)
    if coords is not None:
        x, y, w, h = cv2.boundingRect(coords)
    else:
        h, w = img.shape
        x, y = 0, 0
    
    with open(os.path.join(REPORTS_DIR, "reference_template_dimensions.md"), "w", encoding="utf-8") as f:
        f.write("# Reference Template Measurement\n\n")
        f.write(f"- **File**: `Data/Symbol/MR_Symbol.png`\n")
        f.write(f"- **Image Width**: {img.shape[1]}\n")
        f.write(f"- **Image Height**: {img.shape[0]}\n")
        f.write(f"- **Bounding Box Width**: {w}\n")
        f.write(f"- **Bounding Box Height**: {h}\n")
        f.write(f"- **Aspect Ratio**: {w/h:.2f}\n")
        
    return w, h

def find_representative_symbols(ref_w, ref_h):
    os.makedirs(EVIDENCE_DIR, exist_ok=True)
    
    # We will use simple template matching just to extract some crops.
    # We use outputs/template/edges.png because MR_Symbol is raw.
    processed_template_path = os.path.join(BASE_DIR, "outputs", "template", "edges.png")
    template_edges = cv2.imread(processed_template_path, cv2.IMREAD_GRAYSCALE)
    
    # We'll search across a few scales to find the best match just to act as our "temporary measurement utility".
    # This is NOT localization, just a tool to extract empirical crops for measurement.
    search_scales = [0.25, 0.35, 0.45] 
    
    measurements = []
    
    for sld_name in SLD_FILES:
        sld_path = os.path.join(SLD_DIR, sld_name)
        if not os.path.exists(sld_path):
            print(f"Skipping {sld_name}, not found.")
            continue
            
        sld_img = cv2.imread(sld_path, cv2.IMREAD_GRAYSCALE)
        # Apply standard Canny to SLD
        sld_edges = cv2.Canny(sld_img, 50, 150)
        
        best_val = -1
        best_loc = None
        best_scale = None
        best_tw, best_th = 0, 0
        
        for s in search_scales:
            tw = int(template_edges.shape[1] * s)
            th = int(template_edges.shape[0] * s)
            t_resized = cv2.resize(template_edges, (tw, th), interpolation=cv2.INTER_AREA)
            
            res = cv2.matchTemplate(sld_edges, t_resized, cv2.TM_CCOEFF_NORMED)
            _, max_val, _, max_loc = cv2.minMaxLoc(res)
            
            if max_val > best_val:
                best_val = max_val
                best_loc = max_loc
                best_scale = s
                best_tw, best_th = tw, th
                
        # If we found a reasonable match
        if best_val > 0.3:
            x, y = best_loc
            # Expand crop to ensure we get the whole symbol for empirical measurement
            pad = 20
            crop_x1 = max(0, x - pad)
            crop_y1 = max(0, y - pad)
            crop_x2 = min(sld_img.shape[1], x + best_tw + pad)
            crop_y2 = min(sld_img.shape[0], y + best_th + pad)
            
            crop = sld_img[crop_y1:crop_y2, crop_x1:crop_x2]
            # Invert crop to measure bounding box (black on white)
            crop_inv = cv2.bitwise_not(crop)
            _, crop_bin = cv2.threshold(crop_inv, 127, 255, cv2.THRESH_BINARY)
            
            # Find the largest connected component (ignoring lines crossing it) is hard.
            # Instead, let's just find the bounding box of non-zero pixels near the center.
            # Or use findContours.
            contours, _ = cv2.findContours(crop_bin, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
            
            # Find contour closest to center
            cx, cy = crop_bin.shape[1]//2, crop_bin.shape[0]//2
            best_contour = None
            min_dist = float('inf')
            best_rect = None
            
            for cnt in contours:
                rx, ry, rw, rh = cv2.boundingRect(cnt)
                rcx, rcy = rx + rw/2, ry + rh/2
                dist = (rcx - cx)**2 + (rcy - cy)**2
                if dist < min_dist and rw > 10 and rh > 10:
                    min_dist = dist
                    best_contour = cnt
                    best_rect = (rx, ry, rw, rh)
                    
            if best_rect:
                rx, ry, rw, rh = best_rect
                occ_id = f"{sld_name.split('.')[0]}_symbol_01"
                evidence_filename = f"{occ_id}.png"
                
                # Draw on color crop
                crop_color = cv2.cvtColor(crop, cv2.COLOR_GRAY2BGR)
                cv2.rectangle(crop_color, (rx, ry), (rx+rw, ry+rh), (0, 0, 255), 2)
                cv2.putText(crop_color, f"{rw}x{rh}", (rx, ry-5), cv2.FONT_HERSHEY_SIMPLEX, 0.4, (0,0,255), 1)
                
                cv2.imwrite(os.path.join(EVIDENCE_DIR, evidence_filename), crop_color)
                
                scale_w = rw / ref_w
                scale_h = rh / ref_h
                eff_scale = (scale_w + scale_h) / 2
                
                measurements.append({
                    "sld": sld_name,
                    "id": occ_id,
                    "evidence": evidence_filename,
                    "w": rw,
                    "h": rh,
                    "scale_w": scale_w,
                    "scale_h": scale_h,
                    "eff_scale": eff_scale
                })
                print(f"Measured {occ_id}: {rw}x{rh} -> Eff Scale: {eff_scale:.3f}")

    return measurements

def generate_reports(measurements):
    # Scale Distribution
    with open(os.path.join(REPORTS_DIR, "observed_scale_distribution.md"), "w", encoding="utf-8") as f:
        f.write("# Observed Scale Distribution\n\n")
        f.write("| SLD File | Occurrence ID | Evidence File | Width | Height | Scale W | Scale H | Effective Scale |\n")
        f.write("|---|---|---|---|---|---|---|---|\n")
        scales = []
        for m in measurements:
            scales.append(m["eff_scale"])
            f.write(f"| {m['sld']} | {m['id']} | `{m['evidence']}` | {m['w']} | {m['h']} | {m['scale_w']:.3f} | {m['scale_h']:.3f} | {m['eff_scale']:.3f} |\n")
            
        if scales:
            f.write("\n## Summary Statistics\n")
            f.write(f"- **Minimum Observed Scale**: {min(scales):.3f}\n")
            f.write(f"- **Maximum Observed Scale**: {max(scales):.3f}\n")
            f.write(f"- **Mean Scale**: {np.mean(scales):.3f}\n")
            f.write(f"- **Median Scale**: {np.median(scales):.3f}\n")
            f.write(f"- **Standard Deviation**: {np.std(scales):.3f}\n")
    
    # PRD Validation
    min_scale = min(scales) if scales else 0
    max_scale = max(scales) if scales else 0
    below_0289 = sum(1 for s in scales if s < 0.289) > 0
    below_0233 = sum(1 for s in scales if s < 0.233) > 0
    below_0206 = sum(1 for s in scales if s < 0.206) > 0
    below_0150 = sum(1 for s in scales if s < 0.150) > 0
    
    with open(os.path.join(REPORTS_DIR, "prd_scale_range_validation.md"), "w", encoding="utf-8") as f:
        f.write("# PRD Scale Range Validation\n\n")
        f.write(f"1. **What is the smallest observed scale?** {min_scale:.3f}\n")
        f.write(f"2. **What is the largest observed scale?** {max_scale:.3f}\n")
        f.write(f"3. **Does the dataset contain symbols below 0.289?** {'Yes' if below_0289 else 'No'}\n")
        f.write(f"4. **Does the dataset contain symbols below 0.233?** {'Yes' if below_0233 else 'No'}\n")
        f.write(f"5. **Does the dataset contain symbols below 0.206?** {'Yes' if below_0206 else 'No'}\n")
        f.write(f"6. **Does the dataset contain symbols below 0.150?** {'Yes' if below_0150 else 'No'}\n\n")
        
        status = "PRD RANGE NOT SUPPORTED"
        if not below_0289:
            status = "PRD RANGE SUPPORTED (Lower bounds are unnecessary/unused)"
        elif below_0289 and not below_0150:
            status = "PRD RANGE PARTIALLY SUPPORTED (Symbols exist below threshold, but not down to 0.150)"
            
        f.write(f"## Classification\n**{status}**\n")

    # Decision Support
    with open(os.path.join(REPORTS_DIR, "stage2_decision_support.md"), "w", encoding="utf-8") as f:
        f.write("# Stage 2 Decision Support\n\n")
        f.write("## Evidence Conclusion\n")
        if below_0289:
            f.write("**Scenario A**: Observed symbols exist below topology threshold.\n\n")
            f.write(f"Empirical evidence demonstrates that real MR symbols appear in the SLDs at scales as low as {min_scale:.3f}, which is below the topological preservation threshold of 0.289.\n")
        else:
            f.write("**Scenario B**: Observed symbols do NOT exist below topology threshold.\n\n")
            f.write(f"Empirical evidence demonstrates that the smallest real MR symbol observed has a scale of {min_scale:.3f}. The dataset does NOT naturally require the problematic `[0.15, 0.28]` range.\n")

if __name__ == "__main__":
    w, h = measure_reference()
    print(f"Reference dimensions: {w}x{h}")
    measurements = find_representative_symbols(w, h)
    generate_reports(measurements)
