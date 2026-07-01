import os
from src.common.logging_utils import get_logger
from src.common.io_utils import save_image
import yaml

from src.preprocessing.image_loader import fetch_image
from src.preprocessing.grayscale_conversion import convert_to_grayscale
from src.preprocessing.denoising import apply_denoise
from src.preprocessing.binarization import apply_threshold
from src.candidate_generation.edge_detection import apply_edge_detection

logger = get_logger("pipeline")

CONFIG_PATH = os.path.join(os.path.dirname(__file__), "..", "..", "config", "preprocessing.yaml")
with open(CONFIG_PATH, "r") as f:
    config = yaml.safe_load(f)

def run_preprocessing_stage(input_path: str, output_base_dir: str):
    """
    Orchestrates the Stage 1 preprocessing pipeline:
    Load -> Grayscale -> Denoise -> Threshold -> Edge Extract
    Saves intermediate outputs based on config.
    Returns: (original, gray, binary, edges)
    """
    logger.info(f"Starting pipeline for: {input_path}")
    
    # 1. Load
    original = fetch_image(input_path)
    
    # 2. Grayscale
    gray = convert_to_grayscale(original)
    
    # 3. Denoise
    denoised_gray = apply_denoise(gray)
    
    # 4. Threshold (Binary)
    binary = apply_threshold(denoised_gray)
    
    # 5. Edge Detection
    # Note: Canny operates on the blurred grayscale image, not the binary, 
    # to utilize the continuous intensity gradients.
    edges = apply_edge_detection(denoised_gray)
    
    # Save intermediates if configured
    if config["pipeline"]["save_intermediate"]:
        filename = os.path.basename(input_path)
        base_name, _ = os.path.splitext(filename)
        
        # Determine subfolder structure
        if "MR_Symbol" in filename:
            out_dir = os.path.join(output_base_dir, "template")
        else:
            out_dir = os.path.join(output_base_dir, "diagrams", base_name)
            
        os.makedirs(out_dir, exist_ok=True)
        
        save_image(gray, out_dir, "gray.png")
        save_image(binary, out_dir, "binary.png")
        save_image(edges, out_dir, "edges.png")
        logger.info(f"Saved intermediates to {out_dir}")

    # TODO Stage 2: Scale Pyramid
    # TODO Stage 3: Chamfer Matching
    # TODO Stage 7: PCA Verification
    
    return original, gray, binary, edges
