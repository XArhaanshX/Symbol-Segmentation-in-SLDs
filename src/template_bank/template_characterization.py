import os
import cv2
import numpy as np
from datetime import datetime

BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
TEMPLATE_PATH = os.path.join(BASE_DIR, "outputs", "template", "edges.png")
REPORTS_DIR = os.path.join(BASE_DIR, "reports")
REPORT_PATH = os.path.join(REPORTS_DIR, "template_characterization.md")

def characterize_template():
    if not os.path.exists(TEMPLATE_PATH):
        raise FileNotFoundError(f"Source template not found: {TEMPLATE_PATH}")

    # Load edge image
    edges = cv2.imread(TEMPLATE_PATH, cv2.IMREAD_GRAYSCALE)
    if edges is None:
        raise ValueError(f"Failed to load image: {TEMPLATE_PATH}")

    # Metrics
    h, w = edges.shape
    aspect_ratio = w / h if h > 0 else 0
    edge_pixels = np.count_nonzero(edges)
    total_pixels = w * h
    foreground_ratio = edge_pixels / total_pixels if total_pixels > 0 else 0

    # Connected Components
    # Assuming 8-connectivity for structural elements
    num_labels, labels = cv2.connectedComponents(edges, connectivity=8)
    # The background is label 0, so actual components is num_labels - 1
    component_count = num_labels - 1

    # Contours
    # Using RETR_EXTERNAL or RETR_LIST? The PRD asks for contour count. Let's use RETR_LIST to count all structural paths
    contours, _ = cv2.findContours(edges, cv2.RETR_LIST, cv2.CHAIN_APPROX_SIMPLE)
    contour_count = len(contours)

    # Bounding Box of actual foreground
    # In an edge map, ideally the bounding box matches the image bounds unless padded
    coords = cv2.findNonZero(edges)
    if coords is not None:
        x, y, bw, bh = cv2.boundingRect(coords)
        bbox = f"({x}, {y}, {bw}, {bh})"
    else:
        bbox = "(0, 0, 0, 0)"

    # Generate Report
    timestamp = datetime.utcnow().strftime('%Y-%m-%dT%H:%M:%SZ')
    
    with open(REPORT_PATH, 'w') as f:
        f.write("# Template Characterization Report\n\n")
        f.write("## Traceability\n")
        f.write(f"- **Source Template**: `outputs/template/edges.png`\n")
        f.write(f"- **Generation Timestamp**: {timestamp}\n")
        f.write(f"- **Template Count**: 1\n")
        f.write(f"- **PRD Version Used**: PRD_Symbol_Localization.md (Current)\n\n")
        
        f.write("## Geometric Characteristics\n")
        f.write(f"- **Width**: {w} pixels\n")
        f.write(f"- **Height**: {h} pixels\n")
        f.write(f"- **Bounding Box (x, y, w, h)**: {bbox}\n")
        f.write(f"- **Aspect Ratio (W/H)**: {aspect_ratio:.4f}\n")
        f.write(f"- **Edge Pixel Count**: {edge_pixels}\n")
        f.write(f"- **Foreground Ratio**: {foreground_ratio:.4f}\n")
        f.write(f"- **Connected Components**: {component_count}\n")
        f.write(f"- **Contour Count**: {contour_count}\n\n")
        
        f.write("## Purpose\n")
        f.write("This formal specification establishes the baseline geometry of the MR Symbol edge representation. "
                "These structural metrics will serve as the truth data during the Geometry Preservation Validation "
                "phase, ensuring that scaled and rotated variants strictly preserve the topology defined here.\n")

    print(f"Template characterization saved to {REPORT_PATH}")

if __name__ == "__main__":
    os.makedirs(REPORTS_DIR, exist_ok=True)
    characterize_template()
