import os
import glob
from src.common.logging_utils import get_logger
from src.visualization.validation_grid_generator import generate_validation_grid
from src.pipeline.pipeline_orchestrator import run_preprocessing_stage

logger = get_logger("main")

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_DIR = os.path.join(BASE_DIR, "data")
OUTPUT_DIR = os.path.join(BASE_DIR, "outputs")
REPORTS_DIR = os.path.join(BASE_DIR, "reports")
VIS_DIR = os.path.join(REPORTS_DIR, "visual_validation")

MR_SYMBOL_PATH = os.path.join(DATA_DIR, "Symbol", "MR_Symbol.png")
SLD_PATHS = sorted(glob.glob(os.path.join(DATA_DIR, "SLDs", "SLD*.png")))

VALIDATION_TARGETS = ["MR_Symbol", "SLD1", "SLD4", "SLD11"]

def main():
    logger.info("Initializing Stage 1 Preprocessing Pipeline...")
    
    os.makedirs(OUTPUT_DIR, exist_ok=True)
    os.makedirs(VIS_DIR, exist_ok=True)
    
    all_paths = [MR_SYMBOL_PATH] + SLD_PATHS
    
    for path in all_paths:
        if not os.path.exists(path):
            logger.warning(f"File not found, skipping: {path}")
            continue
            
        filename = os.path.basename(path)
        base_name, _ = os.path.splitext(filename)
        
        try:
            original, gray, binary, edges = run_preprocessing_stage(path, OUTPUT_DIR)
            
            # Generate visual validation grid if this is a validation target
            if base_name in VALIDATION_TARGETS:
                grid_path = os.path.join(VIS_DIR, f"{base_name}_validation_grid.png")
                generate_validation_grid(
                    original, gray, binary, edges, 
                    grid_path, 
                    title=f"Stage 1 Validation: {base_name}"
                )
                logger.info(f"Generated validation grid for {base_name}")
                
        except Exception as e:
            logger.error(f"Error processing {filename}: {str(e)}")
            
    logger.info("Stage 1 Preprocessing Pipeline Complete.")

if __name__ == "__main__":
    main()
