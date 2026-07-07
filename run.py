"""
Symbol Segmentor — Central Pipeline Orchestrator.

Usage:
    python run.py                              Run the complete pipeline
    python run.py --benchmark                  Run benchmarking only
    python run.py --visualize                  Run visualization only
    python run.py --pipeline localization      Run a specific pipeline subset
    python run.py --dataset path/to/slds       Use an external dataset
    python run.py --config custom_config.yaml  Use a custom configuration
    python run.py --help                       Show all options

This is the single official entry point for the research framework.
No Python source files need to be opened or edited to execute experiments.
"""

import os
import sys
import argparse
import time
from datetime import datetime

# ---------------------------------------------------------------------------
# Ensure the project root is on sys.path so ``src.*`` imports resolve
# ---------------------------------------------------------------------------
PROJECT_ROOT = os.path.dirname(os.path.abspath(__file__))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)


def build_cli():
    """Build the argument parser."""
    parser = argparse.ArgumentParser(
        prog="run.py",
        description="Symbol Segmentor — Automated Circuit Symbol Localization Pipeline",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python run.py                     Run the complete pipeline
  python run.py --benchmark         Run only the benchmark suite
  python run.py --visualize         Run only visual output generation
  python run.py --pipeline preprocessing   Run preprocessing only
  python run.py --config my.yaml    Use a custom configuration file
  python run.py --dataset ./new_slds/      Override the SLD dataset path
""",
    )
    parser.add_argument(
        "--benchmark", action="store_true",
        help="Run only the benchmarking stage.",
    )
    parser.add_argument(
        "--visualize", action="store_true",
        help="Run only the visualization stage.",
    )
    parser.add_argument(
        "--pipeline", type=str, default=None, metavar="NAME",
        help="Run only stages whose name contains NAME (e.g., 'localization', 'preprocessing').",
    )
    parser.add_argument(
        "--dataset", type=str, default=None, metavar="PATH",
        help="Override the SLD dataset directory.",
    )
    parser.add_argument(
        "--config", type=str, default=None, metavar="FILE",
        help="Use a custom YAML configuration file.",
    )
    return parser


def main():
    parser = build_cli()
    args = parser.parse_args()

    # ------------------------------------------------------------------
    # Timestamp for this run
    # ------------------------------------------------------------------
    run_ts = datetime.now().strftime("%Y-%m-%d_%H%M%S")
    run_start = time.time()

    # ------------------------------------------------------------------
    # Load configuration
    # ------------------------------------------------------------------
    from src.framework.config_manager import load_config, get_config, get_project_root

    config_path = args.config
    if config_path and not os.path.isabs(config_path):
        config_path = os.path.join(PROJECT_ROOT, config_path)

    try:
        cfg = load_config(config_path)
    except FileNotFoundError as exc:
        sys.stdout.write(f"\n  ERROR: {exc}\n\n")
        sys.exit(1)

    # Apply CLI overrides
    if args.dataset:
        cfg.setdefault("paths", {})["raw_slds"] = args.dataset

    # ------------------------------------------------------------------
    # Set up logging
    # ------------------------------------------------------------------
    from src.framework.logger import setup_logging, get_log_path, get_elapsed_seconds, format_duration, shutdown_logging

    log_path = setup_logging(run_ts)

    import logging
    logger = logging.getLogger("run")
    logger.info("Pipeline run started: %s", run_ts)

    # ------------------------------------------------------------------
    # Output directories
    # ------------------------------------------------------------------
    from src.framework.output_manager import create_run_directories, mirror_to_latest, ensure_base_directories

    ensure_base_directories()
    outputs_dir, reports_dir = create_run_directories(run_ts)

    # ------------------------------------------------------------------
    # Repository validation
    # ------------------------------------------------------------------
    from src.framework.validator import validate_repository, generate_validation_report

    passed, issues = validate_repository(cfg)
    if not passed:
        report_path = generate_validation_report(issues)
        sys.stdout.write("\n  Repository validation FAILED.\n")
        for issue in issues:
            sys.stdout.write(f"    - {issue}\n")
        sys.stdout.write(f"\n  See report: {report_path}\n\n")
        shutdown_logging()
        sys.exit(1)

    # ------------------------------------------------------------------
    # Discover and filter stages
    # ------------------------------------------------------------------
    from src.framework.orchestrator import get_all_stages, resolve_execution_order, filter_stages

    all_stages = get_all_stages()

    if args.benchmark:
        stages = [s for s in all_stages if "benchmark" in s.name()]
    elif args.visualize:
        stages = [s for s in all_stages if "visual" in s.name()]
    elif args.pipeline:
        stages = filter_stages(all_stages, args.pipeline)
    else:
        stages = all_stages

    ordered_stages = resolve_execution_order(stages)

    # ------------------------------------------------------------------
    # Progress display
    # ------------------------------------------------------------------
    from src.framework.progress import ProgressDisplay

    progress = ProgressDisplay(len(ordered_stages))
    progress.banner("Symbol Segmentor Pipeline")

    # ------------------------------------------------------------------
    # Build context shared across all stages
    # ------------------------------------------------------------------
    context = {
        "project_root": get_project_root(),
        "config": cfg,
        "outputs_dir": outputs_dir,
        "reports_dir": reports_dir,
        "run_timestamp": run_ts,
        "log_path": log_path,
    }

    # ------------------------------------------------------------------
    # Execute stages
    # ------------------------------------------------------------------
    from src.framework.error_handler import handle_error

    failed = False
    for stage in ordered_stages:
        progress.begin_stage(stage.name().replace("_", " ").title())
        logger.info(">>> Starting stage: %s", stage.name())

        try:
            stage.run(context)
            progress.end_stage()
            logger.info("<<< Completed stage: %s", stage.name())
        except Exception as exc:
            progress.skip_stage("FAILED")
            handle_error(exc, stage_name=stage.name())
            failed = True
            # Continue with remaining stages where possible
            logger.error("Stage %s failed: %s", stage.name(), exc)

    # ------------------------------------------------------------------
    # Reproducibility report
    # ------------------------------------------------------------------
    from src.framework.reproducibility import generate_reproducibility_report

    elapsed = time.time() - run_start
    try:
        generate_reproducibility_report(
            run_timestamp=run_ts,
            elapsed_seconds=elapsed,
            config_snapshot=cfg,
            outputs_run_dir=outputs_dir,
            reports_run_dir=reports_dir,
            log_path=log_path,
        )
    except Exception as exc:
        logger.error("Failed to generate reproducibility report: %s", exc)

    # ------------------------------------------------------------------
    # Mirror to latest
    # ------------------------------------------------------------------
    if cfg.get("execution", {}).get("mirror_latest", True):
        try:
            mirror_to_latest(outputs_dir, reports_dir)
        except Exception as exc:
            logger.warning("Failed to mirror to latest: %s", exc)

    # ------------------------------------------------------------------
    # Summary
    # ------------------------------------------------------------------
    progress.summary(elapsed, outputs_dir, reports_dir, log_path)

    if failed:
        sys.stdout.write("  Some stages failed. Check the error report and log file.\n\n")

    shutdown_logging()
    sys.exit(1 if failed else 0)


if __name__ == "__main__":
    main()
