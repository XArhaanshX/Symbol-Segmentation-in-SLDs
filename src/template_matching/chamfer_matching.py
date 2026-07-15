import os
import csv
import time
import datetime
import cv2
import numpy as np
import yaml
import matplotlib.pyplot as plt

BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
CONFIG_PATH = os.path.join(BASE_DIR, "config", "chamfer.yaml")
MANIFEST_PATH = os.path.join(BASE_DIR, "outputs", "template_bank", "template_bank_manifest.csv")
DIAGRAMS_DIR = os.path.join(BASE_DIR, "outputs", "diagrams")
DATA_SLDS_DIR = os.path.join(BASE_DIR, "Data", "SLDs")

# Output directories
DT_DIR = os.path.join(BASE_DIR, "outputs", "distance_transforms")
SCORE_MAPS_DIR = os.path.join(BASE_DIR, "outputs", "score_maps")
CANDIDATES_DIR = os.path.join(BASE_DIR, "outputs", "candidates")
CHAMFER_VIS_DIR = os.path.join(BASE_DIR, "outputs", "chamfer_visualizations")
SCORE_VIS_DIR = os.path.join(BASE_DIR, "outputs", "score_map_visualizations")

# Ensure output directories exist
os.makedirs(DT_DIR, exist_ok=True)
os.makedirs(SCORE_MAPS_DIR, exist_ok=True)
os.makedirs(CANDIDATES_DIR, exist_ok=True)
os.makedirs(CHAMFER_VIS_DIR, exist_ok=True)
os.makedirs(SCORE_VIS_DIR, exist_ok=True)

# Load configuration
with open(CONFIG_PATH, "r", encoding="utf-8") as f:
    config = yaml.safe_load(f)

KERNEL_SIZE = int(config.get("local_minima_kernel_size", 15))
EXTRACTION_METHOD = config.get("candidate_extraction_method", "local_minima")
STORAGE_FORMAT = config.get("score_map_storage_format", "npy")

# Traceability info
TIMESTAMP = datetime.datetime.now().strftime("%Y-%m-%dT%H:%M:%SZ")
VERSION = "Stage2_D3_v1"
MANIFEST_VER = "1.0"
TEMPLATE_COUNT = 40
SLD_COUNT = 10

def main():
    print("Starting Stage 3 Chamfer Localization Matching Engine...")
    t_start = time.time()
    
    # 1. Load template manifest
    templates = []
    with open(MANIFEST_PATH, "r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for r in reader:
            templates.append(r)
            
    # Load SLD list
    slds = sorted([d for d in os.listdir(DIAGRAMS_DIR) if os.path.isdir(os.path.join(DIAGRAMS_DIR, d)) and d.startswith("SLD")])
    
    raw_candidates = []
    
    # Track statistics for reports
    total_positions_evaluated = 0
    total_comparisons_made = 0
    
    metadata_dict = {}
    
    # We will compute distance transforms for each SLD
    for sld_name in slds:
        print(f"\nProcessing {sld_name}...")
        
        edges_path = os.path.join(DIAGRAMS_DIR, sld_name, "edges.png")
        if not os.path.exists(edges_path):
            print(f"Edges image not found for {sld_name}, skipping.")
            continue
            
        edges = cv2.imread(edges_path, cv2.IMREAD_GRAYSCALE)
        h_d, w_d = edges.shape
        
        # Phase 3A: Distance Transform
        inv_edges = 255 - edges
        dt = cv2.distanceTransform(inv_edges, cv2.DIST_L2, 5)
        
        # Save distance transform
        dt_path = os.path.join(DT_DIR, f"{sld_name}_dt.tiff")
        cv2.imwrite(dt_path, dt)
        
        # Slide each template over the distance transform
        for temp in templates:
            temp_id = temp["template_id"]
            scale = float(temp["scale"])
            rotation = int(temp["rotation"])
            width = int(temp["width"])
            height = int(temp["height"])
            edge_count = int(temp["edge_count"])
            temp_filepath = os.path.join(BASE_DIR, temp["filepath"].replace("/", os.sep))
            
            temp_img = cv2.imread(temp_filepath, cv2.IMREAD_GRAYSCALE)
            if temp_img is None:
                print(f"Failed to load template image: {temp_filepath}, skipping.")
                continue
                
            # Create template kernel (1.0 for edges, 0.0 otherwise)
            kernel = (temp_img > 0).astype(np.float32)
            
            # Phase 3B & 3C: Chamfer Sweep
            # Perform cross-correlation to sum the distance transform values
            t0_sweep = time.time()
            sum_map = cv2.filter2D(dt, -1, kernel, anchor=(0, 0), borderType=cv2.BORDER_CONSTANT)
            
            # Crop to valid bounds where template fully fits
            valid_h = h_d - height + 1
            valid_w = w_d - width + 1
            
            if valid_h <= 0 or valid_w <= 0:
                print(f"Template {temp_id} does not fit in diagram {sld_name}, skipping.")
                continue
                
            cropped_sum = sum_map[0:valid_h, 0:valid_w]
            score_map = cropped_sum / edge_count
            t_sweep_elapsed = time.time() - t0_sweep
            
            # Accumulate evaluation statistics
            eval_positions = valid_h * valid_w
            total_positions_evaluated += eval_positions
            total_comparisons_made += eval_positions * edge_count
            
            # Phase 3D: Save Chamfer Score Map
            map_filename = f"{sld_name}_T_{scale:.3f}_{rotation:03d}.npy"
            np.save(os.path.join(SCORE_MAPS_DIR, map_filename), score_map)
            
            # Phase 3E: Candidate Proposal Extraction via Local Minima
            # We use erosion/dilation to detect local minima without flat plateaus
            t0_extract = time.time()
            kernel_morph = cv2.getStructuringElement(cv2.MORPH_RECT, (KERNEL_SIZE, KERNEL_SIZE))
            local_min = cv2.erode(score_map, kernel_morph)
            local_max = cv2.dilate(score_map, kernel_morph)
            
            # Local minima is where score is equal to local min, and min < max (excluding plateaus)
            is_minima = (score_map == local_min) & (local_min < local_max)
            y_coords, x_coords = np.where(is_minima)
            t_extract_elapsed = time.time() - t0_extract
            
            # Add to candidate list (preserving all without thresholding/pruning)
            cand_count_this = len(x_coords)
            for x, y in zip(x_coords, y_coords):
                raw_candidates.append({
                    "sld_name": sld_name,
                    "template_id": temp_id,
                    "scale": scale,
                    "rotation": rotation,
                    "x": int(x),
                    "y": int(y),
                    "score": float(score_map[y, x]),
                    "width": width,
                    "height": height
                })
            
            key = f"{sld_name}_{temp_id}"
            metadata_dict[key] = {
                "dimensions": [int(valid_w), int(valid_h)],
                "generation_time": float(t_sweep_elapsed + t_extract_elapsed),
                "memory_consumption": int(score_map.nbytes),
                "local_minima_count": int(cand_count_this),
                "file_size": int(os.path.getsize(os.path.join(SCORE_MAPS_DIR, map_filename)) if os.path.exists(os.path.join(SCORE_MAPS_DIR, map_filename)) else score_map.nbytes + 128)
            }
            
    # Save operational metadata once at the end
    import json
    meta_path = os.path.join(SCORE_MAPS_DIR, "generation_metadata.json")
    with open(meta_path, "w", encoding="utf-8") as json_f:
        json.dump(metadata_dict, json_f, indent=2)
                
    # 2. Save Raw Candidates
    raw_path = os.path.join(CANDIDATES_DIR, "raw_candidates.csv")
    with open(raw_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["sld_name", "template_id", "scale", "rotation", "x", "y", "score", "width", "height"])
        for c in raw_candidates:
            writer.writerow([c["sld_name"], c["template_id"], c["scale"], c["rotation"], c["x"], c["y"], c["score"], c["width"], c["height"]])
            
    # Phase 3F: Candidate Ranking (sort by score ascending)
    ranked_candidates = sorted(raw_candidates, key=lambda x: x["score"])
    
    ranked_path = os.path.join(CANDIDATES_DIR, "ranked_candidates.csv")
    with open(ranked_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["sld_name", "template_id", "scale", "rotation", "x", "y", "score", "width", "height"])
        for c in ranked_candidates:
            writer.writerow([c["sld_name"], c["template_id"], c["scale"], c["rotation"], c["x"], c["y"], c["score"], c["width"], c["height"]])
            
    print(f"Candidate Extraction complete. Total candidates extracted: {len(raw_candidates)}")
    
    # Save some operational metrics for later reports
    t_end = time.time()
    elapsed = t_end - t_start
    
    # Phase 3G: Response Field Visualizations for all processed SLDs
    target_slds = slds
    rep_template_scale = 0.150
    rep_template_rot = 0
    rep_filename_template = f"T_{rep_template_scale:.3f}_{rep_template_rot:03d}"
    
    for sld_name in target_slds:
        # Load DT
        dt_path = os.path.join(DT_DIR, f"{sld_name}_dt.tiff")
        if not os.path.exists(dt_path):
            continue
        dt_img = cv2.imread(dt_path, cv2.IMREAD_UNCHANGED)
        
        # Load Score Map for representative template
        map_path = os.path.join(SCORE_MAPS_DIR, f"{sld_name}_T_{rep_template_scale:.3f}_{rep_template_rot:03d}.npy")
        if not os.path.exists(map_path):
            continue
        score_map = np.load(map_path)
        
        # Get candidates for this specific SLD & template variant
        cand_coords = []
        for c in raw_candidates:
            if c["sld_name"] == sld_name and c["template_id"] == rep_filename_template:
                cand_coords.append((c["x"], c["y"]))
                
        # Generate side-by-side plots
        fig, axes = plt.subplots(1, 3, figsize=(15, 5))
        
        # 1. Distance Transform
        im0 = axes[0].imshow(dt_img, cmap='jet')
        axes[0].set_title(f"Distance Transform ({sld_name})")
        axes[0].axis('off')
        fig.colorbar(im0, ax=axes[0], fraction=0.046, pad=0.04)
        
        # 2. Chamfer Score Map
        im1 = axes[1].imshow(score_map, cmap='viridis')
        axes[1].set_title(f"Chamfer Score Map\n({rep_filename_template})")
        axes[1].axis('off')
        fig.colorbar(im1, ax=axes[1], fraction=0.046, pad=0.04)
        
        # 3. Candidate Locations (on original gray SLD if it exists)
        sld_original_path = os.path.join(DATA_SLDS_DIR, f"{sld_name}.png")
        if os.path.exists(sld_original_path):
            original = cv2.imread(sld_original_path)
            # Draw candidates
            for cc in cand_coords:
                cv2.circle(original, (cc[0], cc[1]), 5, (0, 0, 255), -1)
            axes[2].imshow(cv2.cvtColor(original, cv2.COLOR_BGR2RGB))
        else:
            axes[2].imshow(dt_img > 0, cmap='gray')
            for cc in cand_coords:
                axes[2].plot(cc[0], cc[1], 'ro', markersize=4)
        axes[2].set_title(f"Candidate Locations (N={len(cand_coords)})")
        axes[2].axis('off')
        
        plt.tight_layout()
        plt.savefig(os.path.join(SCORE_VIS_DIR, f"{sld_name}_response_field.png"), dpi=150, bbox_inches='tight')
        plt.close()
        
    # Phase 3H: Visual Validation (Top 10/25/50 and Worst 25) for SLD1, 4, 11
    # For each target SLD, filter the ranked list of candidates
    for sld_name in target_slds:
        sld_original_path = os.path.join(DATA_SLDS_DIR, f"{sld_name}.png")
        if not os.path.exists(sld_original_path):
            continue
            
        sld_candidates = [c for c in ranked_candidates if c["sld_name"] == sld_name]
        if not sld_candidates:
            continue
            
        # We want to draw: Top 10, Top 25, Top 50, and Worst 25 candidates
        # Let's write a helper to draw boxes
        def generate_overlay(cands, num_cands, suffix, color):
            original = cv2.imread(sld_original_path)
            
            # Select candidates
            subset = cands[:num_cands] if suffix != "worst_25" else cands[-num_cands:]
            
            for idx, c in enumerate(subset):
                rank = idx + 1 if suffix != "worst_25" else len(cands) - num_cands + idx + 1
                x, y, w, h = c["x"], c["y"], c["width"], c["height"]
                score = c["score"]
                scale = c["scale"]
                rot = c["rotation"]
                
                # Draw bounding box
                cv2.rectangle(original, (x, y), (x + w, y + h), color, 2)
                
                # Add text label
                label = f"#{rank} ({score:.2f}, S:{scale:.2f}, R:{rot})"
                cv2.putText(original, label, (x, max(0, y - 5)), cv2.FONT_HERSHEY_SIMPLEX, 0.4, color, 1)
                
            out_filename = f"{sld_name}_{suffix}_overlay.png"
            cv2.imwrite(os.path.join(CHAMFER_VIS_DIR, out_filename), original)
            
        # Draw top overlays (green: BGR (0, 255, 0))
        generate_overlay(sld_candidates, 10, "top_10", (0, 255, 0))
        generate_overlay(sld_candidates, 25, "top_25", (0, 255, 0))
        generate_overlay(sld_candidates, 50, "top_50", (0, 255, 0))
        
        # Draw worst overlay (red: BGR (0, 0, 255))
        generate_overlay(sld_candidates, 25, "worst_25", (0, 0, 255))
        
    print(f"Stage 3 Sweeping and candidate visual panel overlays generated in {elapsed:.2f} seconds.")

if __name__ == "__main__":
    main()
