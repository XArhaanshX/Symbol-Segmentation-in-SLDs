# Module Development Guide

## Overview

This guide explains how to create new pipeline stages, extend existing modules, and integrate additional algorithms into the framework.

## Creating a New Pipeline Stage

### Step 1: Create the Stage Wrapper

Create a new file in `src/stages/`:

```python
# src/stages/s08_new_analysis.py

import os
import logging
from src.framework.orchestrator import PipelineStage

logger = logging.getLogger("stage.new_analysis")


class NewAnalysisStage(PipelineStage):

    def name(self):
        return "new_analysis"

    def description(self):
        return "Describe what this stage does."

    def dependencies(self):
        return ["verification"]  # List stages that must run first

    def outputs(self):
        return ["output_file_1.csv", "output_file_2.png"]

    def run(self, context):
        root = context["project_root"]
        cfg = context["config"]
        outputs_dir = context["outputs_dir"]
        reports_dir = context["reports_dir"]

        # Your analysis logic here
        logger.info("Running new analysis...")

        # Use outputs_dir for generated files
        out_path = os.path.join(outputs_dir, "new_analysis_results.csv")
        # ...

        logger.info("New analysis complete.")
```

### Step 2: Register the Stage

Edit `src/framework/orchestrator.py`:

```python
def get_all_stages():
    # ... existing imports ...
    from src.stages.s08_new_analysis import NewAnalysisStage

    return [
        # ... existing stages ...
        NewAnalysisStage(),
    ]
```

### Step 3: Add Configuration (Optional)

Add a new section to `config/project_config.yaml`:

```yaml
new_analysis:
  threshold: 0.5
  max_iterations: 100
```

Access it in your stage:
```python
analysis_cfg = cfg.get("new_analysis", {})
threshold = analysis_cfg.get("threshold", 0.5)
```

## The Context Dictionary

Every stage's `run()` method receives a `context` dictionary:

| Key | Type | Description |
|-----|------|-------------|
| `project_root` | `str` | Absolute path to repository root |
| `config` | `dict` | Loaded `project_config.yaml` |
| `outputs_dir` | `str` | Timestamped output directory for this run |
| `reports_dir` | `str` | Timestamped reports directory for this run |
| `run_timestamp` | `str` | `YYYY-MM-DD_HHMMSS` timestamp |
| `log_path` | `str` | Path to log file |

## Wrapping Existing Modules

When wrapping an existing module that uses hardcoded paths:

```python
def run(self, context):
    import src.existing_module as mod

    # Patch the hardcoded paths
    mod.BASE_DIR = context["project_root"]
    mod.OUTPUT_DIR = context["outputs_dir"]

    # Call the original function
    mod.main()
```

## Logging Best Practices

```python
import logging
logger = logging.getLogger("stage.your_stage")

logger.info("Starting processing...")      # Routine progress
logger.warning("File not found, skipping") # Non-fatal issues
logger.error("Critical failure: %s", exc)  # Errors (with %s formatting)
logger.debug("Variable x = %d", x)        # Verbose debug info
```

All log output goes to the run's log file.  Only `WARNING` and above appear on the console.

## Testing Your Stage

```bash
# Run only your stage
python run.py --pipeline new_analysis

# Check outputs
ls outputs/latest/

# Check logs
cat logs/run_*.log | tail -50
```
