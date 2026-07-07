"""
Stage 1: Image Preprocessing.

Wraps the existing preprocessing pipeline without modifying the algorithms.
"""

import os
import glob
import logging
from src.framework.orchestrator import PipelineStage

logger = logging.getLogger("stage.preprocessing")


class PreprocessingStage(PipelineStage):

    def name(self):
        return "preprocessing"

    def description(self):
        return "Load raw SLD images and MR symbol template, convert to grayscale, denoise, binarize, and extract edges."

    def dependencies(self):
        return []

    def outputs(self):
        return ["gray.png", "binary.png", "edges.png per input image", "validation grids"]

    def run(self, context):
        root = context["project_root"]
        cfg = context["config"]
        outputs_dir = context["outputs_dir"]

        paths_cfg = cfg.get("paths", {})
        raw_slds = os.path.join(root, paths_cfg.get("raw_slds", "data/raw/slds"))
        raw_templates = os.path.join(root, paths_cfg.get("raw_templates", "data/raw/templates"))
        mr_path = os.path.join(raw_templates, "MR_Symbol.png")

        sld_files = sorted(glob.glob(os.path.join(raw_slds, "SLD*.png")))
        all_paths = ([mr_path] if os.path.exists(mr_path) else []) + sld_files

        if not all_paths:
            logger.warning("No input images found.  Skipping preprocessing.")
            return

        # Import the original pipeline orchestrator
        from src.pipeline.pipeline_orchestrator import run_preprocessing_stage

        for path in all_paths:
            if not os.path.exists(path):
                logger.warning("File not found, skipping: %s", path)
                continue
            try:
                run_preprocessing_stage(path, outputs_dir)
            except Exception as exc:
                logger.error("Error processing %s: %s", os.path.basename(path), exc)

        # Generate validation grids for selected targets
        validation_targets = cfg.get("pipeline", {}).get("validation_targets", ["MR_Symbol", "SLD1", "SLD4", "SLD11"])
        vis_dir = os.path.join(context["reports_dir"], "visual_validation")
        os.makedirs(vis_dir, exist_ok=True)

        from src.visualization.validation_grid_generator import generate_validation_grid

        for path in all_paths:
            base_name = os.path.splitext(os.path.basename(path))[0]
            if base_name in validation_targets:
                try:
                    original, gray, binary, edges = run_preprocessing_stage(path, outputs_dir)
                    grid_path = os.path.join(vis_dir, f"{base_name}_validation_grid.png")
                    generate_validation_grid(original, gray, binary, edges, grid_path,
                                             title=f"Stage 1 Validation: {base_name}")
                    logger.info("Generated validation grid for %s", base_name)
                except Exception as exc:
                    logger.error("Validation grid error for %s: %s", base_name, exc)

        logger.info("Preprocessing complete. Processed %d images.", len(all_paths))
