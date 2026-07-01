import cv2
import numpy as np

def convert_to_grayscale(img: np.ndarray) -> np.ndarray:
    """
    Converts an image to grayscale deterministically.
    Preserves dimensions.
    """
    if len(img.shape) == 2:
        return img.copy()
        
    if len(img.shape) == 3:
        if img.shape[2] == 4:
            # Handle RGBA images by blending with a white background
            # so transparent areas become white (background) instead of black.
            alpha_channel = img[:, :, 3] / 255.0
            white_background = np.ones_like(img[:, :, :3], dtype=np.uint8) * 255
            for c in range(3):
                white_background[:, :, c] = (alpha_channel * img[:, :, c] + 
                                             (1 - alpha_channel) * white_background[:, :, c])
            return cv2.cvtColor(white_background, cv2.COLOR_BGR2GRAY)
        elif img.shape[2] == 3:
            return cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
            
    raise ValueError(f"Unsupported image shape for grayscale conversion: {img.shape}")
