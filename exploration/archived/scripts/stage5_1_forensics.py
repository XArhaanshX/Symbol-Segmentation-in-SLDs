import os
import csv
import cv2
import numpy as np
from datetime import datetime
from collections import defaultdict

BASE_DIR = r"c:\Users\arhaa\OneDrive\Symbol Segmentor"
REPORTS_DIR = os.path.join(BASE_DIR, "reports")
OUTPUTS_DIR = os.path.join(BASE_DIR, "outputs")
CANDIDATES_DIR = os.path.join(OUTPUTS_DIR, "candidates")
DIAGRAMS_DIR = os.path.join(OUTPUTS_DIR, "diagrams")
TEMPLATE_BANK_DIR = os.path.join(OUTPUTS_DIR, "template_bank")
REVIEW_DIR = os.path.join(REPORTS_DIR, "stage51_top10_review")

TARGET_SLDS = ["SLD1", "SLD2", "SLD3", "SLD4", "SLD7", "SLD8", "SLD9", "SLD10", "SLD11", "SLD12"]

def draw_text_with_bg(img, text, position, font_scale=0.4, color=(255, 255, 255), thickness=1):
    font = cv2.FONT_HERSHEY_SIMPLEX
    (w, h), baseline = cv2.getTextSize(text, font, font_scale, thickness)
    x, y = position
    cv2.rectangle(img, (x, y - h - baseline), (x + w, y + baseline), (0, 0, 0), cv2.FILLED)
    cv2.putText(img, text, (x, y), font, font_scale, color, thickness)

def main():
    os.makedirs(REVIEW_DIR, exist_ok=True)
    
    print("Loading templates...")
    templates = {}
    manifest_path = os.path.join(TEMPLATE_BANK_DIR, "template_bank_manifest.csv")
    with open(manifest_path, "r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            templates[row["template_id"]] = row
            
    print("Loading candidates...")
    candidates = []
    with open(os.path.join(CANDIDATES_DIR, "ranked_by_combined_score.csv"), "r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            if row["sld_name"] in TARGET_SLDS:
                candidates.append(row)
                
    by_sld = defaultdict(list)
    for c in candidates:
        by_sld[c["sld_name"]].append(c)
        
    top10_candidates = []
    
    # Store candidate thumbnails for the montage
    # We will use 150x150 tiles
    TILE_SIZE = 150
    montage_tiles = []
    
    summary_rows = []
    review_rows = []
    
    print("Generating overlays and galleries...")
    for sld in TARGET_SLDS:
        cands = by_sld.get(sld, [])
        # Already sorted by combined score
        cands = cands[:10]
        
        # Load diagram
        diag_path = os.path.join(DIAGRAMS_DIR, sld, "edges.png")
        if not os.path.exists(diag_path):
            print(f"Warning: Missing diagram for {sld}")
            continue
            
        diagram = cv2.imread(diag_path, cv2.IMREAD_COLOR)
        h_diag, w_diag = diagram.shape[:2]
        
        gallery_tiles = []
        
        for rank, c in enumerate(cands, start=1):
            top10_candidates.append(c)
            c_id = c.get("candidate_id", f"{sld}_{rank}")
            x, y = int(c["x"]), int(c["y"])
            w = int(c.get("template_width", c.get("width", 24)))
            h = int(c.get("template_height", c.get("height", 15)))
            scale = float(c["scale"])
            rot = float(c["rotation"])
            cmb = float(c["CombinedScore"])
            vf = float(c["VerificationScore"])
            cov_a = float(c["CoverageAreaScore"])
            
            # Color logic
            if rank == 1:
                color = (0, 0, 255) # Red
            elif rank <= 5:
                color = (0, 165, 255) # Orange
            else:
                color = (0, 255, 255) # Yellow
                
            # Draw bbox
            cv2.rectangle(diagram, (x, y), (x + w, y + h), color, 2)
            
            # Draw labels
            label1 = f"R{rank} ID:{c_id}"
            label2 = f"C:{cmb:.2f} V:{vf:.2f} A:{cov_a:.2f}"
            label3 = f"S:{scale:.2f} R:{rot:.0f}"
            
            draw_text_with_bg(diagram, label1, (x, y - 30), color=color)
            draw_text_with_bg(diagram, label2, (x, y - 18), color=color)
            draw_text_with_bg(diagram, label3, (x, y - 6), color=color)
            
            # Record rows
            summary_rows.append({
                "SLD": sld,
                "Rank": rank,
                "CandidateID": c_id,
                "X": x, "Y": y, "Width": w, "Height": h,
                "Scale": scale, "Rotation": rot,
                "CoverageAreaScore": cov_a, "VerificationScore": vf, "CombinedScore": cmb
            })
            
            review_rows.append({
                "SLD": sld,
                "Rank": rank,
                "CandidateID": c_id,
                "Classification": "" # Blank for manual review
            })
            
            # Build gallery & montage tile
            t_id = c["template_id"]
            t_info = templates.get(t_id)
            
            cand_crop = np.zeros((h, w, 3), dtype=np.uint8)
            y1, y2 = max(0, y), min(h_diag, y + h)
            x1, x2 = max(0, x), min(w_diag, x + w)
            if y2 > y1 and x2 > x1:
                cand_crop[:y2-y1, :x2-x1] = diagram[y1:y2, x1:x2]
                
            t_img = None
            if t_info:
                t_path = os.path.join(BASE_DIR, t_info["filepath"])
                if os.path.exists(t_path):
                    t_img = cv2.imread(t_path, cv2.IMREAD_COLOR)
            
            if t_img is None:
                t_img = np.zeros((h, w, 3), dtype=np.uint8)
                
            # Resize crops for gallery
            gal_cand = cv2.resize(cand_crop, (200, 200))
            gal_temp = cv2.resize(t_img, (200, 200))
            
            gal_panel = np.zeros((250, 420, 3), dtype=np.uint8)
            gal_panel[40:240, 10:210] = gal_cand
            gal_panel[40:240, 210:410] = gal_temp
            
            cv2.putText(gal_panel, f"Rank {rank} - {sld}", (10, 25), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255,255,255), 1)
            cv2.putText(gal_panel, f"C:{cmb:.2f} S:{scale:.2f} R:{rot:.0f}", (210, 25), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (200,200,200), 1)
            
            gallery_tiles.append(gal_panel)
            
            # Montage Tile (just candidate crop)
            mon_tile = np.zeros((TILE_SIZE, TILE_SIZE, 3), dtype=np.uint8)
            mon_c = cv2.resize(cand_crop, (TILE_SIZE, TILE_SIZE))
            mon_tile[:] = mon_c
            # Darken top for text
            cv2.rectangle(mon_tile, (0, 0), (TILE_SIZE, 20), (0,0,0), -1)
            cv2.putText(mon_tile, f"{sld} R{rank}", (5, 15), cv2.FONT_HERSHEY_SIMPLEX, 0.5, color, 1)
            montage_tiles.append(mon_tile)
            
        cv2.imwrite(os.path.join(REVIEW_DIR, f"{sld}_top10_overlay.png"), diagram)
        
        if gallery_tiles:
            # Combine vertically
            full_gallery = np.vstack(gallery_tiles)
            cv2.imwrite(os.path.join(REVIEW_DIR, f"{sld}_top10_gallery.png"), full_gallery)
            
    print("Building global montage...")
    # 10 SLDs x 10 candidates = 100 tiles -> 10 x 10 grid
    grid_rows, grid_cols = 10, 10
    montage = np.zeros((grid_rows * TILE_SIZE, grid_cols * TILE_SIZE, 3), dtype=np.uint8)
    
    for i, tile in enumerate(montage_tiles):
        if i >= 100: break
        r = i // grid_cols
        c = i % grid_cols
        montage[r*TILE_SIZE:(r+1)*TILE_SIZE, c*TILE_SIZE:(c+1)*TILE_SIZE] = tile
        
    cv2.imwrite(os.path.join(REPORTS_DIR, "stage51_global_top10_montage.png"), montage)
    
    print("Writing CSVs and Reports...")
    with open(os.path.join(REPORTS_DIR, "stage51_top10_summary.csv"), "w", newline="", encoding="utf-8") as f:
        keys = ["SLD", "Rank", "CandidateID", "X", "Y", "Width", "Height", "Scale", "Rotation", "CoverageAreaScore", "VerificationScore", "CombinedScore"]
        writer = csv.DictWriter(f, fieldnames=keys)
        writer.writeheader()
        writer.writerows(summary_rows)
        
    with open(os.path.join(REPORTS_DIR, "stage51_failure_mode_review.csv"), "w", newline="", encoding="utf-8") as f:
        keys = ["SLD", "Rank", "CandidateID", "Classification"]
        writer = csv.DictWriter(f, fieldnames=keys)
        writer.writeheader()
        writer.writerows(review_rows)
        
    with open(os.path.join(REPORTS_DIR, "stage51_forensic_review.md"), "w", encoding="utf-8") as f:
        f.write("""# Stage 5.1: Top-10 Per-SLD Forensic Review

## 1. Does each SLD contain at least one visually plausible MR candidate in its Top 10?
[Awaiting Manual Review]

## 2. Does the Rank-1 candidate appear visually correct?
[Awaiting Manual Review]

## 3. What is the dominant false-positive category?
[Awaiting Manual Review]

## 4. Are false positives consistent across SLDs?
[Awaiting Manual Review]

## 5. Are true symbols typically appearing near the top or absent entirely?
[Awaiting Manual Review]

## 6. Is the failure mode primarily text, conductors, curved structures, transformers, or something else?
[Awaiting Manual Review]

## 7. Does the evidence justify proceeding to Stage 6?
[Awaiting Manual Review]

## 8. Does the evidence instead justify a new MR-specific verification stage?
[Awaiting Manual Review]
""")

    print("Stage 5.1 Complete.")

if __name__ == "__main__":
    main()
