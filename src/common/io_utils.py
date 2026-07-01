import os
import cv2
import numpy as np
from src.common.logging_utils import get_logger

logger = get_logger("io_utils")

def load_image(path: str) -> np.ndarray:
    """Safely loads an image, ensuring it exists."""
    if not os.path.exists(path):
        logger.error(f"Image not found at path: {path}")
        raise FileNotFoundError(f"Image not found: {path}")
    
    img = cv2.imread(path, cv2.IMREAD_UNCHANGED)
    if img is None:
        logger.error(f"Failed to decode image at path: {path}")
        raise ValueError(f"Failed to decode image: {path}")
        
    logger.info(f"Loaded image from {path} with shape {img.shape}")
    return img

def save_image(img: np.ndarray, output_dir: str, filename: str):
    """Saves an image to the specified directory, creating the directory if needed."""
    os.makedirs(output_dir, exist_ok=True)
    out_path = os.path.join(output_dir, filename)
    success = cv2.imwrite(out_path, img)
    if success:
        logger.info(f"Saved intermediate image to {out_path}")
    else:
        logger.error(f"Failed to save image to {out_path}")
        raise IOError(f"Could not write image {out_path}")
