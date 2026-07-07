"""
Structured Logging System.

Every pipeline execution produces a timestamped log file under ``logs/``.
Console output is kept minimal and clean; verbose detail goes to the log file.
"""

import os
import sys
import logging
import time
from datetime import datetime
from src.framework.config_manager import get_project_root


_file_handler = None
_log_path = None
_start_time = None


def setup_logging(run_timestamp=None):
    """Initialise the logging system for a pipeline run.

    Creates ``logs/run_YYYYMMDD_HHMMSS.log`` and configures the root logger.

    Returns
    -------
    str
        Absolute path to the log file.
    """
    global _file_handler, _log_path, _start_time

    _start_time = time.time()
    root = get_project_root()
    log_dir = os.path.join(root, "logs")
    os.makedirs(log_dir, exist_ok=True)

    ts = run_timestamp or datetime.now().strftime("%Y%m%d_%H%M%S")
    _log_path = os.path.join(log_dir, f"run_{ts}.log")

    # Reset root logger
    root_logger = logging.getLogger()
    root_logger.setLevel(logging.DEBUG)

    # Remove any existing handlers (e.g. from prior imports of logging_utils)
    for h in root_logger.handlers[:]:
        root_logger.removeHandler(h)

    # File handler — verbose
    _file_handler = logging.FileHandler(_log_path, encoding="utf-8")
    _file_handler.setLevel(logging.DEBUG)
    file_fmt = logging.Formatter(
        "%(asctime)s | %(levelname)-8s | %(name)-20s | %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )
    _file_handler.setFormatter(file_fmt)
    root_logger.addHandler(_file_handler)

    # Console handler — clean, minimal
    console = logging.StreamHandler(sys.stdout)
    console.setLevel(logging.WARNING)
    console_fmt = logging.Formatter("%(message)s")
    console.setFormatter(console_fmt)
    root_logger.addHandler(console)

    logging.info("Logging initialised.  Log file: %s", _log_path)
    return _log_path


def get_log_path():
    """Return the path to the current log file."""
    return _log_path


def get_elapsed_seconds():
    """Seconds elapsed since logging was initialised."""
    if _start_time is None:
        return 0.0
    return time.time() - _start_time


def format_duration(seconds):
    """Format seconds into a human-readable string."""
    m, s = divmod(int(seconds), 60)
    h, m = divmod(m, 60)
    if h > 0:
        return f"{h} hr {m} min {s} sec"
    if m > 0:
        return f"{m} min {s} sec"
    return f"{s} sec"


def shutdown_logging():
    """Flush and close the log file handler."""
    global _file_handler
    if _file_handler is not None:
        _file_handler.close()
        logging.getLogger().removeHandler(_file_handler)
        _file_handler = None
