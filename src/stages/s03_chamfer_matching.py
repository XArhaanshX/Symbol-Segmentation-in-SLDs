"""
Stage 3: Chamfer Matching.

Wraps the Chamfer matching engine without modifying the algorithm.
Patches hardcoded absolute paths to use the run's output directory.

NOTE: The chamfer_matching module loads config and creates directories at
module level (import time).  We must ensure the config file exists at the
path it expects BEFORE importing the module.
"""

import os
import sys
import logging
import shutil
from src.framework.orchestrator import PipelineStage

logger = logging.getLogger("stage.chamfer_matching")


class ChamferMatchingStage(PipelineStage):

    def name(self):
        return "chamfer_matching"

    def description(self):
        return "Compute distance transforms, sweep template bank across SLD edge maps, extract candidate proposals via local minima detection."

    def dependencies(self):
        return ["template_bank"]

    def outputs(self):
        return ["distance_transforms/", "score_maps/", "candidates/raw_candidates.csv", "candidates/ranked_candidates.csv"]

    def run(self, context):
        root = context["project_root"]
        cfg = context["config"]
        outputs_dir = context["outputs_dir"]

        # Ensure the chamfer config file exists at the expected path.
        # The original module looks for config/chamfer.yaml at module level.
        config_source = os.path.join(root, "config", "chamfer_matching.yaml")
        config_target = os.path.join(root, "config", "chamfer.yaml")
        if os.path.exists(config_source) and not os.path.exists(config_target):
            shutil.copy2(config_source, config_target)

        # The module uses BASE_DIR at module level to construct all paths and
        # immediately creates directories + loads config on import.
        # We must reload it to pick up patched paths.
        # Since the original module reads BASE_DIR, CONFIG_PATH, etc. at
        # module level, we need to ensure the module is freshly imported
        # with the correct state.

        # Remove from cache if already imported so it re-executes module-level code
        mod_name = "src.template_matching.chamfer_matching"
        if mod_name in sys.modules:
            del sys.modules[mod_name]

        # Temporarily patch the module constants by modifying the source module's
        # global namespace after import
        import src.template_matching.chamfer_matching as cm

        # Patch output paths
        cm.BASE_DIR = root
        cm.MANIFEST_PATH = os.path.join(outputs_dir, "template_bank", "template_bank_manifest.csv")
        cm.DIAGRAMS_DIR = os.path.join(outputs_dir, "diagrams")
        cm.DATA_SLDS_DIR = os.path.join(root, cfg.get("paths", {}).get("raw_slds", "data/raw/slds"))
        cm.DT_DIR = os.path.join(outputs_dir, "distance_transforms")
        cm.SCORE_MAPS_DIR = os.path.join(outputs_dir, "score_maps")
        cm.CANDIDATES_DIR = os.path.join(outputs_dir, "candidates")
        cm.CHAMFER_VIS_DIR = os.path.join(outputs_dir, "chamfer_visualizations")
        cm.SCORE_VIS_DIR = os.path.join(outputs_dir, "score_map_visualizations")

        # Ensure directories exist
        for d in [cm.DT_DIR, cm.SCORE_MAPS_DIR, cm.CANDIDATES_DIR, cm.CHAMFER_VIS_DIR, cm.SCORE_VIS_DIR]:
            os.makedirs(d, exist_ok=True)

        # Verify prerequisites
        if not os.path.exists(cm.MANIFEST_PATH):
            logger.warning("Template bank manifest not found. Run template_bank stage first.")
            return

        if not os.path.isdir(cm.DIAGRAMS_DIR):
            logger.warning("Diagram edges directory not found. Run preprocessing stage first.")
            return

        logger.info("Starting Chamfer matching engine...")
        cm.main()
        logger.info("Chamfer matching complete.")
