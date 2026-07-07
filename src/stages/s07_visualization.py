"""
Stage 7: Visualization.

Generates validation grids and visual overlays from pipeline outputs.
"""

import os
import logging
from src.framework.orchestrator import PipelineStage

logger = logging.getLogger("stage.visualization")


class VisualizationStage(PipelineStage):

    def name(self):
        return "visualization"

    def description(self):
        return "Generate visual validation grids and candidate overlay images for quality inspection."

    def dependencies(self):
        return ["preprocessing"]

    def outputs(self):
        return ["visual_validation/ grids"]

    def run(self, context):
        # Visualization is already done inside preprocessing and other stages.
        # This stage serves as a hook for --visualize mode.
        reports_dir = context["reports_dir"]
        vis_dir = os.path.join(reports_dir, "visual_validation")

        if os.path.isdir(vis_dir) and os.listdir(vis_dir):
            logger.info("Validation grids already generated (%d files).", len(os.listdir(vis_dir)))
        else:
            logger.info("No standalone visualization required (handled by preprocessing stage).")
