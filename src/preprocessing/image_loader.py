import os
import cv2
import numpy as np
from src.common.io_utils import load_image
from src.common.logging_utils import get_logger

logger = get_logger("image_loader")

def fetch_image(path: str) -> np.ndarray:
    """
    Loads an image from the filesystem and performs basic validation.
    """
    img = load_image(path)
    
    # Validation: Ensure it has actual spatial dimensions
    if len(img.shape) < 2 or img.shape[0] < 10 or img.shape[1] < 10:
        logger.error(f"Image {path} has invalid dimensions: {img.shape}")
        raise ValueError("Image dimensions are too small or invalid.")
        
    return img
