"""
Stage 6: Benchmarking.

Wraps the unified pipeline benchmark suite.
"""

import os
import logging
from src.framework.orchestrator import PipelineStage

logger = logging.getLogger("stage.benchmarking")


class BenchmarkingStage(PipelineStage):

    def name(self):
        return "benchmarking"

    def description(self):
        return "Execute the unified benchmark suite: localization metrics, ranking metrics, retrieval metrics, bootstrap stability, failure mode breakdown, and pipeline leaderboard."

    def dependencies(self):
        return ["verification"]

    def outputs(self):
        return ["reports/benchmark/executive_summary.md", "reports/benchmark/pipeline_leaderboard.md",
                "reports/benchmark/unified_benchmark_report.md"]

    def run(self, context):
        import sys
        root = context["project_root"]
        outputs_dir = context["outputs_dir"]
        reports_dir = context["reports_dir"]

        cands_dir = os.path.join(outputs_dir, "candidates")
        
        legacy_exports = os.path.join(root, "outputs", "tabular", "exports")
        legacy_metrics = os.path.join(root, "outputs", "tabular", "metrics")
        legacy_reports = os.path.join(root, "reports", "benchmark")
        
        os.makedirs(legacy_exports, exist_ok=True)
        os.makedirs(legacy_metrics, exist_ok=True)
        os.makedirs(legacy_reports, exist_ok=True)
        
        gt_path = os.path.join(legacy_metrics, "ground_truth_symbols.json")
        if not os.path.exists(gt_path):
            alt_gt = os.path.join(root, "data", "metadata", "ground_truth_symbols.json")
            if os.path.exists(alt_gt):
                import shutil
                shutil.copy2(alt_gt, gt_path)
            else:
                logger.warning("ground_truth_symbols.json not found. Skipping benchmarking.")
                return

        import shutil
        file_map = {
            "raw_candidates.csv": "raw_candidates.csv",
            "ranked_by_verification.csv": "ranked_by_verification.csv",
            "ranked_by_coverage_area.csv": "ranked_by_coverage_area.csv",
            "ranked_by_combined_score.csv": "ranked_by_combined_score.csv"
        }
        for src, dst in file_map.items():
            src_path = os.path.join(cands_dir, src)
            if os.path.exists(src_path):
                shutil.copy2(src_path, os.path.join(legacy_exports, dst))
                
        logger.info("Starting unified benchmark suite...")
        import subprocess
        env = os.environ.copy()
        env["PYTHONPATH"] = root
        try:
            result = subprocess.run(
                [sys.executable, "-m", "src.benchmarking.unified_pipeline_benchmark"],
                cwd=root, env=env, capture_output=True, text=True
            )
            if result.returncode != 0:
                logger.error("Benchmark failed:\n%s", result.stderr)
            else:
                out_lines = result.stdout.splitlines()
                if out_lines:
                    logger.info("Benchmark complete. %s", out_lines[-1])
                else:
                    logger.info("Benchmark complete.")
        except Exception as exc:
            logger.error("Failed to run benchmark subprocess: %s", exc)

        run_bench_reports = os.path.join(reports_dir, "benchmark")
        os.makedirs(run_bench_reports, exist_ok=True)
        for f in os.listdir(legacy_reports):
            shutil.copy2(os.path.join(legacy_reports, f), os.path.join(run_bench_reports, f))
