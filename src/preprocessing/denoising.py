import cv2
import numpy as np
import yaml
import os

# Load config once
CONFIG_PATH = os.path.join(os.path.dirname(__file__), "..", "..", "config", "preprocessing.yaml")
with open(CONFIG_PATH, "r") as f:
    config = yaml.safe_load(f)

def apply_denoise(img_gray: np.ndarray) -> np.ndarray:
    """
    Applies the configured denoising strategy to the grayscale image.
    Selected strategy: Median blur (k=3)
    """
    strategy = config["denoise"]["strategy"]
    k_size = config["denoise"]["kernel_size"]
    
    if strategy == "median":
        return cv2.medianBlur(img_gray, k_size)
    elif strategy == "none":
        return img_gray.copy()
    else:
        raise ValueError(f"Unknown denoise strategy: {strategy}")
