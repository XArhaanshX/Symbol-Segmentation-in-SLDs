import os
import csv
import cv2

BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
DATA_DIR = os.path.join(BASE_DIR, "data")
SLD_DIR = os.path.join(DATA_DIR, "SLDs")
ANNOTATIONS_DIR = os.path.join(BASE_DIR, "annotations")
CSV_PATH = os.path.join(ANNOTATIONS_DIR, "draft_annotations.csv")
VERIFICATION_DIR = os.path.join(BASE_DIR, "LLM Verification")

os.makedirs(VERIFICATION_DIR, exist_ok=True)

def run_viewer():
    if not os.path.exists(CSV_PATH):
        print(f"Error: {CSV_PATH} does not exist.")
        return
        
    annotations = []
    with open(CSV_PATH, "r") as f:
        reader = csv.DictReader(f)
        annotations = list(reader)
        
    if not annotations:
        print("No annotations found in CSV.")
        return
        
    # Group by file
    from collections import defaultdict
    grouped = defaultdict(list)
    for ann in annotations:
        grouped[ann["file"]].append(ann)
        
    for filename, anns in grouped.items():
        img_path = os.path.join(SLD_DIR, filename)
        if not os.path.exists(img_path):
            print(f"Image not found: {img_path}")
            continue
            
        img = cv2.imread(img_path, cv2.IMREAD_UNCHANGED)
        # Convert to BGR if RGBA to draw colored boxes
        if len(img.shape) == 3 and img.shape[2] == 4:
            # White background for transparent regions
            alpha = img[:, :, 3] / 255.0
            bg = np.ones_like(img[:, :, :3], dtype=np.uint8) * 255
            for c in range(3):
                bg[:, :, c] = (alpha * img[:, :, c] + (1 - alpha) * bg[:, :, c])
            img = bg
        elif len(img.shape) == 2:
            img = cv2.cvtColor(img, cv2.COLOR_GRAY2BGR)
            
        for ann in anns:
            x, y = int(ann["x"]), int(ann["y"])
            w, h = int(ann["width"]), int(ann["height"])
            ann_id = ann["annotation_id"]
            rot = ann["rotation"]
            conf = ann["confidence"]
            
            # Draw highly visible bounding box (Red, thickness 3)
            cv2.rectangle(img, (x, y), (x + w, y + h), (0, 0, 255), 3)
            
            # Draw label background
            text = f"{ann_id} | {conf} | {rot}deg"
            font = cv2.FONT_HERSHEY_SIMPLEX
            font_scale = 0.6
            thickness = 2
            
            (tw, th), baseline = cv2.getTextSize(text, font, font_scale, thickness)
            cv2.rectangle(img, (x, y - th - 10), (x + tw, y), (0, 0, 255), -1)
            cv2.putText(img, text, (x, y - 5), font, font_scale, (255, 255, 255), thickness)
            
        out_name = filename.replace(".png", "_verified.png")
        out_path = os.path.join(VERIFICATION_DIR, out_name)
        cv2.imwrite(out_path, img)
        print(f"Generated verification image: {out_path}")

if __name__ == "__main__":
    import numpy as np # imported locally for blending
    print("Generating Verification Images...")
    run_viewer()
    print("Done.")
