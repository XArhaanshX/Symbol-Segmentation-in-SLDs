"""
Console Progress Display.

Provides a clean, numbered progress indicator for pipeline stages.
Outputs directly to stdout so it is visible even when logging is file-only.
"""

import sys
import time


class ProgressDisplay:
    """Displays ``[n/total] Stage Name  ... done (Xs)`` on the console."""

    def __init__(self, total_stages):
        self._total = total_stages
        self._current = 0
        self._stage_start = None

    def begin_stage(self, name):
        """Mark the start of a new stage."""
        self._current += 1
        self._stage_start = time.time()
        msg = f"  [{self._current}/{self._total}] {name}"
        sys.stdout.write(msg)
        sys.stdout.flush()

    def end_stage(self):
        """Mark the current stage as complete."""
        elapsed = time.time() - self._stage_start if self._stage_start else 0
        sys.stdout.write(f"  ... done ({elapsed:.1f}s)\n")
        sys.stdout.flush()

    def skip_stage(self, reason="skipped"):
        """Mark the current stage as skipped."""
        sys.stdout.write(f"  ... {reason}\n")
        sys.stdout.flush()

    def banner(self, text):
        """Print a prominent banner line."""
        width = 60
        sys.stdout.write("\n" + "=" * width + "\n")
        sys.stdout.write(f"  {text}\n")
        sys.stdout.write("=" * width + "\n\n")
        sys.stdout.flush()

    def summary(self, elapsed_seconds, outputs_dir, reports_dir, log_path):
        """Print a final summary block."""
        from src.framework.logger import format_duration
        duration = format_duration(elapsed_seconds)

        sys.stdout.write("\n" + "-" * 60 + "\n")
        sys.stdout.write(f"  Completed in {duration}\n")
        sys.stdout.write(f"  Outputs  : {outputs_dir}\n")
        sys.stdout.write(f"  Reports  : {reports_dir}\n")
        sys.stdout.write(f"  Log      : {log_path}\n")
        sys.stdout.write("-" * 60 + "\n\n")
        sys.stdout.flush()
