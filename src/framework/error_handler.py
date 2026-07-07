"""
Error Handler.

Catches exceptions at the top level and converts them into human-readable
messages with possible causes and suggested fixes.  No Python tracebacks
are shown to the end user.
"""

import os
import sys
import logging
import traceback
from datetime import datetime
from src.framework.config_manager import get_project_root


def handle_error(exc, stage_name=None):
    """Handle an exception gracefully.

    Parameters
    ----------
    exc : Exception
        The caught exception.
    stage_name : str, optional
        Name of the pipeline stage where the error occurred.

    Returns
    -------
    str
        Path to the generated error report.
    """
    logger = logging.getLogger("error_handler")
    logger.error("Pipeline error in %s: %s", stage_name or "unknown", exc, exc_info=True)

    root = get_project_root()
    report_dir = os.path.join(root, "reports", "system")
    os.makedirs(report_dir, exist_ok=True)
    report_path = os.path.join(report_dir, "error_report.md")

    exc_type = type(exc).__name__
    exc_msg = str(exc)
    tb = traceback.format_exception(type(exc), exc, exc.__traceback__)

    # Determine cause and fix suggestions
    cause, fix = _diagnose(exc)

    lines = [
        "# Pipeline Error Report\n",
        f"**Timestamp**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}  ",
        f"**Stage**: {stage_name or 'Unknown'}  ",
        f"**Error Type**: `{exc_type}`\n",
        "## What Happened\n",
        f"{exc_msg}\n",
        "## Possible Cause\n",
        f"{cause}\n",
        "## Suggested Fix\n",
        f"{fix}\n",
        "## Technical Details\n",
        "```",
        "".join(tb).strip(),
        "```\n",
    ]

    with open(report_path, "w", encoding="utf-8") as fh:
        fh.write("\n".join(lines))

    # Print user-friendly message to console
    sys.stdout.write(f"\n  ERROR in {stage_name or 'pipeline'}: {exc_msg}\n")
    sys.stdout.write(f"  See report: {report_path}\n\n")
    sys.stdout.flush()

    return report_path


def _diagnose(exc):
    """Return (cause, fix) strings based on exception type."""
    name = type(exc).__name__
    msg = str(exc).lower()

    if isinstance(exc, FileNotFoundError):
        return (
            "A required file or directory is missing.",
            "Ensure the dataset is in place under `data/raw/` and run `python install.py` to regenerate directories.",
        )
    if isinstance(exc, PermissionError):
        return (
            "The process does not have write access to a required directory.",
            "Check file permissions.  On a company VM, verify that the repository is not on a read-only network share.",
        )
    if isinstance(exc, ImportError) or isinstance(exc, ModuleNotFoundError):
        return (
            f"A required Python package is not installed: {exc}",
            "Run `python install.py` to install all dependencies.",
        )
    if "yaml" in msg or "config" in msg:
        return (
            "A configuration file is missing or malformed.",
            "Verify that `config/project_config.yaml` exists and contains valid YAML.",
        )
    if "memory" in msg or "MemoryError" == name:
        return (
            "The system ran out of available RAM.",
            "Close other applications or reduce the dataset size in `config/project_config.yaml`.",
        )
    return (
        "An unexpected error occurred during pipeline execution.",
        "Check the technical details above and the log file under `logs/` for more context.",
    )
