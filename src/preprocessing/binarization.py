import cv2
import numpy as np
import yaml
import os

CONFIG_PATH = os.path.join(os.path.dirname(__file__), "..", "..", "config", "preprocessing.yaml")
with open(CONFIG_PATH, "r") as f:
    config = yaml.safe_load(f)

def apply_threshold(img_gray: np.ndarray) -> np.ndarray:
    """
    Applies the configured thresholding strategy to generate a binary image.
    Foreground (lines) becomes white (255), Background becomes black (0).
    Selected strategy: Otsu
    """
    strategy = config["thresholding"]["strategy"]
    
    if strategy == "otsu":
        # THRESH_BINARY_INV so lines are 255
        _, binary = cv2.threshold(img_gray, 0, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU)
        return binary
    else:
        raise ValueError(f"Unknown thresholding strategy: {strategy}")
