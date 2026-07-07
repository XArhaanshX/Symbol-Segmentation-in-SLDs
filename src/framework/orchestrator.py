"""
Module Registry & Pipeline Orchestrator.

Discovers pipeline stages, resolves dependencies, and executes them in
the correct order.  Each stage module exposes a standard interface:
    run(), name(), description(), dependencies(), outputs()
"""

import logging

logger = logging.getLogger("orchestrator")


class PipelineStage:
    """Base class for pipeline stages."""

    def name(self):
        raise NotImplementedError

    def description(self):
        return ""

    def dependencies(self):
        """Return a list of stage names this stage depends on."""
        return []

    def outputs(self):
        """Return a list of output descriptions."""
        return []

    def run(self, context):
        """Execute the stage.

        Parameters
        ----------
        context : dict
            Shared context with keys: project_root, config, outputs_dir,
            reports_dir, run_timestamp, etc.
        """
        raise NotImplementedError


def resolve_execution_order(stages):
    """Topological sort of stages based on declared dependencies.

    Parameters
    ----------
    stages : list[PipelineStage]

    Returns
    -------
    list[PipelineStage]
        Stages in dependency-resolved execution order.
    """
    by_name = {s.name(): s for s in stages}
    visited = set()
    order = []

    def _visit(stage):
        sn = stage.name()
        if sn in visited:
            return
        visited.add(sn)
        for dep in stage.dependencies():
            if dep in by_name:
                _visit(by_name[dep])
            else:
                logger.warning("Dependency '%s' required by '%s' not found — skipping", dep, sn)
        order.append(stage)

    for s in stages:
        _visit(s)

    return order


def get_all_stages():
    """Import and return instances of all registered pipeline stages."""
    from src.stages.s01_preprocessing import PreprocessingStage
    from src.stages.s02_template_bank import TemplateBankStage
    from src.stages.s03_chamfer_matching import ChamferMatchingStage
    from src.stages.s04_coverage_rescoring import CoverageRescoringStage
    from src.stages.s05_verification import VerificationStage
    from src.stages.s06_benchmarking import BenchmarkingStage
    from src.stages.s07_visualization import VisualizationStage

    return [
        PreprocessingStage(),
        TemplateBankStage(),
        ChamferMatchingStage(),
        CoverageRescoringStage(),
        VerificationStage(),
        BenchmarkingStage(),
        VisualizationStage(),
    ]


def filter_stages(all_stages, pipeline_filter=None):
    """Filter stages based on CLI flags.

    Parameters
    ----------
    all_stages : list[PipelineStage]
    pipeline_filter : str or None
        If provided, run only stages whose name contains this string.

    Returns
    -------
    list[PipelineStage]
    """
    if pipeline_filter is None:
        return all_stages

    keyword = pipeline_filter.lower()
    filtered = [s for s in all_stages if keyword in s.name().lower()]
    if not filtered:
        logger.warning("No stages matched filter '%s'.  Running all stages.", pipeline_filter)
        return all_stages
    return filtered
