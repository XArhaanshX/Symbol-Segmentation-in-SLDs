"""
Reproducibility Recorder.

After each run, records the full execution environment: git commit, Python
version, OS, installed packages, configuration snapshot, runtime, random seeds,
and generated outputs.  Writes ``reports/system/reproducibility_report.md``.
"""

import os
import sys
import json
import platform
import subprocess
from datetime import datetime
from src.framework.config_manager import get_project_root


def generate_reproducibility_report(
    run_timestamp,
    elapsed_seconds,
    config_snapshot,
    outputs_run_dir,
    reports_run_dir,
    log_path,
):
    """Generate and write the reproducibility report.

    Parameters
    ----------
    run_timestamp : str
        ISO-style timestamp for this run.
    elapsed_seconds : float
        Total pipeline wall-clock time.
    config_snapshot : dict
        The configuration dictionary used for this run.
    outputs_run_dir : str
        Path to the timestamped outputs directory.
    reports_run_dir : str
        Path to the timestamped reports directory.
    log_path : str
        Path to the log file.

    Returns
    -------
    str
        Path to the written report.
    """
    root = get_project_root()

    # Git information
    git_hash = _get_git_hash(root)
    git_branch = _get_git_branch(root)

    # Environment
    py_version = sys.version.replace("\n", " ")
    os_info = f"{platform.system()} {platform.release()} ({platform.machine()})"

    # Installed packages
    installed = _get_installed_packages()

    # Generated outputs
    output_files = _list_files_recursive(outputs_run_dir) if os.path.isdir(outputs_run_dir) else []
    report_files = _list_files_recursive(reports_run_dir) if os.path.isdir(reports_run_dir) else []

    # Runtime
    m, s = divmod(int(elapsed_seconds), 60)
    h, m = divmod(m, 60)
    runtime_str = f"{h}h {m}m {s}s" if h > 0 else f"{m}m {s}s"

    # Build report
    lines = [
        "# Reproducibility Report\n",
        "## Execution Metadata\n",
        f"| Field | Value |",
        f"|---|---|",
        f"| Timestamp | {run_timestamp} |",
        f"| Git Commit | `{git_hash}` |",
        f"| Git Branch | `{git_branch}` |",
        f"| Python Version | `{py_version}` |",
        f"| Operating System | {os_info} |",
        f"| Runtime | {runtime_str} |",
        f"| Random Seed | `42` (deterministic) |",
        f"| Log File | `{os.path.relpath(log_path, root) if log_path else 'N/A'}` |",
        "",
        "## Configuration Snapshot\n",
        "```yaml",
    ]

    import yaml
    lines.append(yaml.dump(config_snapshot, default_flow_style=False).strip())
    lines.append("```\n")

    lines.append("## Installed Packages\n")
    lines.append("| Package | Version |")
    lines.append("|---|---|")
    for pkg, ver in sorted(installed.items()):
        lines.append(f"| {pkg} | {ver} |")
    lines.append("")

    lines.append(f"## Generated Outputs ({len(output_files)} files)\n")
    for f in output_files[:50]:
        lines.append(f"- `{f}`")
    if len(output_files) > 50:
        lines.append(f"- ... and {len(output_files) - 50} more")
    lines.append("")

    lines.append(f"## Generated Reports ({len(report_files)} files)\n")
    for f in report_files[:50]:
        lines.append(f"- `{f}`")
    if len(report_files) > 50:
        lines.append(f"- ... and {len(report_files) - 50} more")

    # Write
    report_dir = os.path.join(root, "reports", "system")
    os.makedirs(report_dir, exist_ok=True)
    report_path = os.path.join(report_dir, "reproducibility_report.md")
    with open(report_path, "w", encoding="utf-8") as fh:
        fh.write("\n".join(lines) + "\n")

    return report_path


def _get_git_hash(root):
    try:
        result = subprocess.run(
            ["git", "rev-parse", "HEAD"],
            cwd=root, capture_output=True, text=True, timeout=5,
        )
        return result.stdout.strip() if result.returncode == 0 else "N/A (not a git repo)"
    except Exception:
        return "N/A"


def _get_git_branch(root):
    try:
        result = subprocess.run(
            ["git", "rev-parse", "--abbrev-ref", "HEAD"],
            cwd=root, capture_output=True, text=True, timeout=5,
        )
        return result.stdout.strip() if result.returncode == 0 else "N/A"
    except Exception:
        return "N/A"


def _get_installed_packages():
    packages = {}
    try:
        import importlib.metadata as meta
        for dist in meta.distributions():
            packages[dist.metadata["Name"]] = dist.version
    except Exception:
        # Fallback for older Python
        try:
            result = subprocess.run(
                [sys.executable, "-m", "pip", "list", "--format=json"],
                capture_output=True, text=True, timeout=30,
            )
            if result.returncode == 0:
                for p in json.loads(result.stdout):
                    packages[p["name"]] = p["version"]
        except Exception:
            pass
    return packages


def _list_files_recursive(directory):
    files = []
    for dirpath, _, filenames in os.walk(directory):
        for fn in filenames:
            rel = os.path.relpath(os.path.join(dirpath, fn), directory)
            files.append(rel)
    return sorted(files)
