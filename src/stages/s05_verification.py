"""
Stage 5: Structural Verification.

Wraps the structural verification cascade without modifying the algorithm.
"""

import os
import logging
from src.framework.orchestrator import PipelineStage

logger = logging.getLogger("stage.verification")


class VerificationStage(PipelineStage):

    def name(self):
        return "verification"

    def description(self):
        return "Extract structural features, compute verification scores, and produce combined-score rankings."

    def dependencies(self):
        return ["coverage_rescoring"]

    def outputs(self):
        return ["candidates/verified_candidates.csv", "candidates/ranked_by_verification.csv",
                "candidates/ranked_by_combined_score.csv"]

    def run(self, context):
        root = context["project_root"]
        outputs_dir = context["outputs_dir"]
        reports_dir = context["reports_dir"]

        import src.verification.structural_verification as sv

        # Patch paths
        sv.BASE_DIR = root
        sv.CONFIG_PATH = os.path.join(root, "config", "verification.yaml")
        sv.REPORTS_DIR = reports_dir
        sv.OUTPUTS_DIR = outputs_dir
        sv.CANDIDATES_DIR = os.path.join(outputs_dir, "candidates")
        sv.DIAGRAMS_DIR = os.path.join(outputs_dir, "diagrams")
        sv.TEMPLATE_BANK_DIR = os.path.join(outputs_dir, "template_bank")
        sv.VISUALS_DIR = os.path.join(outputs_dir, "stage5_visualizations")

        # Check prerequisites
        source_file = os.path.join(sv.CANDIDATES_DIR, sv.CANDIDATE_DATASET_SOURCE)
        if not os.path.exists(source_file):
            logger.warning("Candidate source file not found at %s. Run coverage_rescoring stage first.", source_file)
            return

        if not os.path.exists(sv.CONFIG_PATH):
            logger.warning("Verification config not found at %s.", sv.CONFIG_PATH)
            return

        logger.info("Starting structural verification...")
        sv.main()
        logger.info("Structural verification complete.")
