import os
import csv
from datetime import datetime

BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
ANNOTATIONS_DIR = os.path.join(BASE_DIR, "annotations")
REPORTS_DIR = os.path.join(BASE_DIR, "reports")
DRAFT_CSV = os.path.join(ANNOTATIONS_DIR, "draft_annotations.csv")
VERIFIED_CSV = os.path.join(ANNOTATIONS_DIR, "verified_annotations.csv")

os.makedirs(REPORTS_DIR, exist_ok=True)

def generate_review_guide():
    """Generates the review guide from draft annotations."""
    if not os.path.exists(DRAFT_CSV):
        print(f"Error: {DRAFT_CSV} not found.")
        return
        
    with open(DRAFT_CSV, "r") as f:
        drafts = list(csv.DictReader(f))
        
    out_path = os.path.join(REPORTS_DIR, "annotation_review_guide.md")
    with open(out_path, "w") as f:
        f.write("# Annotation Review Guide\n\n")
        f.write("Use this guide alongside the images in `LLM Verification/` to validate the draft annotations.\n\n")
        
        # Group by file
        from collections import defaultdict
        grouped = defaultdict(list)
        for d in drafts:
            grouped[d["file"]].append(d)
            
        for filename, anns in grouped.items():
            f.write(f"## {filename}\n")
            f.write("| ID | Coordinates (x,y,w,h) | Rotation | Confidence | Notes | Action (KEEP/DELETE/ADJUST) |\n")
            f.write("|---|---|---|---|---|---|\n")
            for ann in anns:
                coords = f"{ann['x']}, {ann['y']}, {ann['width']}, {ann['height']}"
                f.write(f"| {ann['annotation_id']} | {coords} | {ann['rotation']}° | {ann['confidence']} | {ann['notes']} | **[ ]** |\n")
            f.write("\n")
            
    print(f"Generated {out_path}")

def generate_dataset_characterization():
    """Generates all reports based ONLY on verified_annotations.csv"""
    if not os.path.exists(VERIFIED_CSV):
        print(f"Error: {VERIFIED_CSV} not found. Human review must be completed first.")
        return
        
    with open(VERIFIED_CSV, "r") as f:
        verified = list(csv.DictReader(f))
        
    # Placeholder for full dataset characterization logic
    # This will be fleshed out after verified_annotations.csv is created by the human reviewer.
    # It will generate: occurrence_survey.md, scale_distribution.md, rotation_distribution.md,
    # ground_truth_summary.md, template_bank_design.md, search_space_risks.md, stage3_readiness.md
    print("Dataset characterization placeholder. Will fully execute once verified annotations are provided.")

if __name__ == "__main__":
    import sys
    if len(sys.argv) > 1 and sys.argv[1] == "--characterize":
        generate_dataset_characterization()
    else:
        generate_review_guide()
