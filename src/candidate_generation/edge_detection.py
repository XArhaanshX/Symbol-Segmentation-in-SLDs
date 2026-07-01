import cv2
import numpy as np
import yaml
import os

CONFIG_PATH = os.path.join(os.path.dirname(__file__), "..", "..", "config", "preprocessing.yaml")
with open(CONFIG_PATH, "r") as f:
    config = yaml.safe_load(f)

def apply_edge_detection(img_gray: np.ndarray) -> np.ndarray:
    """
    Applies the configured edge detection strategy.
    Selected strategy: Canny with auto-median thresholding.
    """
    strategy = config["edge_detection"]["strategy"]
    auto_thresh = config["edge_detection"]["auto_threshold"]
    sigma = config["edge_detection"]["auto_sigma"]
    
    if strategy == "canny":
        if auto_thresh:
            v = np.median(img_gray)
            lower = int(max(0, (1.0 - sigma) * v))
            upper = int(min(255, (1.0 + sigma) * v))
        else:
            # Fallback if hardcoded in config
            lower = config["edge_detection"].get("lower_thresh", 50)
            upper = config["edge_detection"].get("upper_thresh", 150)
            
        edges = cv2.Canny(img_gray, lower, upper)
        return edges
    else:
        raise ValueError(f"Unknown edge detection strategy: {strategy}")
