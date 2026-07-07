"""
Repository Validator.

Before any pipeline execution, validates that required datasets, templates,
configuration files, and output directories exist.  Generates a structured
validation report on failure instead of crashing with stack traces.
"""

import os
import json
from src.framework.config_manager import get_project_root, get_config


def validate_repository(cfg=None):
    """Run a complete repository validation.

    Returns
    -------
    tuple[bool, list[str]]
        (passed, list_of_issues)
    """
    root = get_project_root()
    cfg = cfg or get_config()
    issues = []

    # --- Dataset validation ---
    paths_cfg = cfg.get("paths", {})
    raw_slds_dir = os.path.join(root, paths_cfg.get("raw_slds", "data/raw/slds"))
    raw_templates_dir = os.path.join(root, paths_cfg.get("raw_templates", "data/raw/templates"))

    if not os.path.isdir(raw_slds_dir):
        issues.append(f"Dataset directory missing: {raw_slds_dir}")
    else:
        sld_files = [f for f in os.listdir(raw_slds_dir) if f.lower().endswith(".png")]
        if not sld_files:
            issues.append(f"No SLD images (*.png) found in {raw_slds_dir}")

    if not os.path.isdir(raw_templates_dir):
        issues.append(f"Template directory missing: {raw_templates_dir}")
    else:
        mr_file = os.path.join(raw_templates_dir, "MR_Symbol.png")
        if not os.path.exists(mr_file):
            issues.append(f"MR Symbol template not found: {mr_file}")

    # --- Configuration validation ---
    config_dir = os.path.join(root, "config")
    required_configs = [
        "project_config.yaml",
        "preprocessing.yaml",
        "template_bank.yaml",
    ]
    for rc in required_configs:
        if not os.path.exists(os.path.join(config_dir, rc)):
            issues.append(f"Configuration file missing: config/{rc}")

    # --- Output directory writability ---
    for dir_key in ["outputs", "reports", "logs"]:
        dir_path = os.path.join(root, dir_key)
        os.makedirs(dir_path, exist_ok=True)
        test_file = os.path.join(dir_path, ".write_test")
        try:
            with open(test_file, "w") as f:
                f.write("test")
            os.remove(test_file)
        except OSError:
            issues.append(f"No write permission for directory: {dir_path}")

    # --- Metadata validation ---
    metadata_path = os.path.join(root, "data", "metadata", "dataset_stats.json")
    if os.path.exists(metadata_path):
        try:
            with open(metadata_path, "r", encoding="utf-8") as f:
                json.load(f)
        except (json.JSONDecodeError, OSError):
            issues.append(f"Metadata file is corrupt: {metadata_path}")

    return (len(issues) == 0), issues


def generate_validation_report(issues):
    """Write a human-readable validation report."""
    root = get_project_root()
    report_dir = os.path.join(root, "reports", "system")
    os.makedirs(report_dir, exist_ok=True)
    report_path = os.path.join(report_dir, "validation_report.md")

    lines = [
        "# Repository Validation Report\n",
        "> [!CAUTION]",
        "> Pipeline execution was halted because the repository failed validation.\n",
        "## Issues Found\n",
    ]
    for idx, issue in enumerate(issues, 1):
        lines.append(f"{idx}. {issue}")

    lines.append("\n## Suggested Actions\n")
    lines.append("- Ensure all dataset files are present in `data/raw/slds/` and `data/raw/templates/`.")
    lines.append("- Run `python install.py` to regenerate missing directories and validate the environment.")
    lines.append("- Verify write permissions on the repository directory.\n")

    with open(report_path, "w", encoding="utf-8") as f:
        f.write("\n".join(lines))

    return report_path
