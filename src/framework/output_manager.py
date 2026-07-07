"""
Output Manager.

Creates timestamped output directories for each run and optionally mirrors
the latest results to ``outputs/latest/`` and ``reports/latest/``.
Historical runs are never overwritten.
"""

import os
import shutil
from datetime import datetime
from src.framework.config_manager import get_project_root


def create_run_directories(run_timestamp=None):
    """Create timestamped output and report directories for this run.

    Returns
    -------
    tuple[str, str]
        (outputs_run_dir, reports_run_dir)
    """
    root = get_project_root()
    ts = run_timestamp or datetime.now().strftime("%Y-%m-%d_%H%M%S")

    outputs_run = os.path.join(root, "outputs", "runs", ts)
    reports_run = os.path.join(root, "reports", "runs", ts)

    os.makedirs(outputs_run, exist_ok=True)
    os.makedirs(reports_run, exist_ok=True)

    return outputs_run, reports_run


def mirror_to_latest(outputs_run, reports_run):
    """Copy the latest run outputs to ``outputs/latest`` and ``reports/latest``.

    The ``latest`` symlinks/directories are recreated each time so they always
    point to the most recent run.
    """
    root = get_project_root()

    for src_dir, latest_name in [(outputs_run, os.path.join(root, "outputs", "latest")),
                                  (reports_run, os.path.join(root, "reports", "latest"))]:
        # Remove existing latest
        if os.path.islink(latest_name):
            os.unlink(latest_name)
        elif os.path.isdir(latest_name):
            shutil.rmtree(latest_name, ignore_errors=True)

        # Copy tree (symlinks are unreliable across Windows environments)
        if os.path.isdir(src_dir) and os.listdir(src_dir):
            shutil.copytree(src_dir, latest_name, dirs_exist_ok=True)


def ensure_base_directories():
    """Create all standard top-level directories if they do not exist."""
    root = get_project_root()
    for d in ["outputs", "reports", "logs", "data", "config"]:
        os.makedirs(os.path.join(root, d), exist_ok=True)
