"""
Stage 2: Template Bank Generation.

Wraps the template pyramid generator without modifying the generation algorithm.
"""

import os
import logging
from src.framework.orchestrator import PipelineStage

logger = logging.getLogger("stage.template_bank")


class TemplateBankStage(PipelineStage):

    def name(self):
        return "template_bank"

    def description(self):
        return "Generate multi-scale, multi-rotation template bank using Method D3 (Coordinate Scaling + Subpixel Anti-Aliased Rasterization)."

    def dependencies(self):
        return ["preprocessing"]

    def outputs(self):
        return ["template_bank/scales/", "template_bank/rotations/", "template_bank_manifest.csv"]

    def run(self, context):
        root = context["project_root"]
        outputs_dir = context["outputs_dir"]

        # Patch paths used by the original module
        import src.template_bank.template_pyramid_generator as tpg

        tpg.TEMPLATE_PATH = os.path.join(outputs_dir, "template", "edges.png")
        tpg.TEMPLATE_BANK_DIR = os.path.join(outputs_dir, "template_bank")
        tpg.SCALES_DIR = os.path.join(tpg.TEMPLATE_BANK_DIR, "scales")
        tpg.ROTATIONS_DIR = os.path.join(tpg.TEMPLATE_BANK_DIR, "rotations")
        tpg.MANIFEST_PATH = os.path.join(tpg.TEMPLATE_BANK_DIR, "template_bank_manifest.csv")

        # Verify source template exists
        if not os.path.exists(tpg.TEMPLATE_PATH):
            logger.warning(
                "Template edges not found at %s.  "
                "Run preprocessing first to generate template edges.", tpg.TEMPLATE_PATH
            )
            return

        logger.info("Generating template pyramids...")
        tpg.generate_pyramids()
        
        # Patch the manifest to point to the correct timestamped paths
        # because the original module hardcodes "outputs/template_bank/rotations/"
        import csv
        with open(tpg.MANIFEST_PATH, "r", encoding="utf-8") as f:
            reader = list(csv.DictReader(f))
            
        for row in reader:
            filename = os.path.basename(row["filepath"])
            # Chamfer matching does: os.path.join(BASE_DIR, row["filepath"])
            # Make the path relative to project root
            row["filepath"] = os.path.relpath(os.path.join(tpg.ROTATIONS_DIR, filename), root).replace("\\", "/")
            
        with open(tpg.MANIFEST_PATH, "w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=reader[0].keys())
            writer.writeheader()
            writer.writerows(reader)
            
        logger.info("Template bank generation complete.")
