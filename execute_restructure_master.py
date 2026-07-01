import os
import shutil
import csv
import logging
from pathlib import Path

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(levelname)s: %(message)s')
logger = logging.getLogger(__name__)

ROOT_DIR = r"c:\Users\arhaa\OneDrive\Symbol Segmentor"
# Normalize ROOT_DIR
ROOT_DIR = os.path.normpath(ROOT_DIR)

def safe_move(src, dst):
    src_path = os.path.join(ROOT_DIR, os.path.normpath(src))
    dst_path = os.path.join(ROOT_DIR, os.path.normpath(dst))
    
    if not os.path.exists(src_path):
        logger.warning(f"Source not found: {src}")
        return False
        
    if os.path.exists(dst_path):
        logger.warning(f"Destination already exists, overwriting: {dst}")
        
    os.makedirs(os.path.dirname(dst_path), exist_ok=True)
    try:
        shutil.move(src_path, dst_path)
        logger.debug(f"Moved: {src} -> {dst}")
        return True
    except Exception as e:
        logger.error(f"Failed to move {src} to {dst}: {e}")
        return False

def safe_remove_dir(target):
    target_path = os.path.join(ROOT_DIR, os.path.normpath(target))
    if os.path.exists(target_path) and os.path.isdir(target_path):
        try:
            shutil.rmtree(target_path)
            logger.info(f"Removed directory: {target}")
        except Exception as e:
            logger.error(f"Failed to remove directory {target}: {e}")

def create_placeholder_readme(target, content):
    target_path = os.path.join(ROOT_DIR, os.path.normpath(target))
    os.makedirs(os.path.dirname(target_path), exist_ok=True)
    try:
        with open(target_path, 'w', encoding='utf-8') as f:
            f.write(content)
    except Exception as e:
        logger.error(f"Failed to create README at {target}: {e}")

def remove_pycache():
    for root, dirs, files in os.walk(ROOT_DIR):
        if "__pycache__" in dirs:
            pycache_dir = os.path.join(root, "__pycache__")
            logger.info(f"Removing {pycache_dir}")
            shutil.rmtree(pycache_dir, ignore_errors=True)
            dirs.remove("__pycache__")

def phase_2():
    logger.info("--- Phase 2: Clean Dead Weight ---")
    remove_pycache()
    safe_move("execute_restructure_phase0_1.py", "exploration/archived/scripts/execute_restructure_phase0_1.py")
    safe_move("execute_restructure_phase2_7.py", "exploration/archived/scripts/execute_restructure_phase2_7.py")
    safe_remove_dir("PRD")
    safe_remove_dir("scratch")

def phase_3():
    logger.info("--- Phase 3: Restructure data/ ---")
    if os.path.exists(os.path.join(ROOT_DIR, "Data")):
        os.rename(os.path.join(ROOT_DIR, "Data"), os.path.join(ROOT_DIR, "data"))
        
    safe_remove_dir("data/SLDs")
    safe_remove_dir("data/Symbol")
    
    safe_move("data/templates/certified/MR_Symbol.png", "data/raw/templates/MR_Symbol.png")
    safe_remove_dir("data/templates/certified")
    
    # Processed features renaming
    safe_move("data/processed/candidate_features/stage58_discovery_dataset.csv", "data/intermediate/candidate_features/structural_discriminator_features.csv")
    safe_move("data/processed/candidate_features/stage59a_stroke_consistency_dataset.csv", "data/intermediate/candidate_features/template_stroke_consistency_features.csv")
    safe_move("data/processed/candidate_features/stage59b_discovery_dataset.csv", "data/intermediate/candidate_features/existence_feature_discovery.csv")
    safe_move("data/processed/candidate_features/stage59b_existence_features.csv", "data/intermediate/candidate_features/symbol_existence_features.csv")
    safe_move("data/processed/candidate_features/stage59b_promoted_noise_dataset.csv", "data/intermediate/candidate_features/promoted_noise_candidates.csv")
    
    # Move other datasets
    for f in os.listdir(os.path.join(ROOT_DIR, "data/processed/candidate_features")):
        if f.endswith('.csv') and "stage" not in f:
            safe_move(f"data/processed/candidate_features/{f}", f"data/intermediate/candidate_features/{f}")
            
    safe_move("data/processed/candidate_features/dataset_stats.json", "data/metadata/dataset_stats.json")
    safe_remove_dir("data/processed/candidate_features")

def phase_4():
    logger.info("--- Phase 4: Restructure src/ ---")
    # Move main pipeline files
    safe_move("src/pipeline/main.py", "src/pipeline/run_pipeline.py")
    safe_move("src/pipeline/pipeline.py", "src/pipeline/pipeline_orchestrator.py")
    
    # Create configuration
    create_placeholder_readme("src/pipeline/pipeline_configuration.py", "# Placeholder for configuration loading\n")
    
    # Preprocessing
    safe_move("src/pipeline/grayscale.py", "src/preprocessing/grayscale_conversion.py")
    safe_move("src/pipeline/denoise.py", "src/preprocessing/denoising.py")
    safe_move("src/pipeline/thresholding.py", "src/preprocessing/binarization.py")
    safe_move("src/pipeline/image_loader.py", "src/preprocessing/image_loader.py")
    
    # Candidate Generation
    safe_move("src/pipeline/pyramid.py", "src/template_bank/template_pyramid_generator.py")
    
    # Template Matching
    safe_move("src/template_matching/chamfer_score_map_validation.py", "src/template_matching/score_map_validation.py")
    
    # Template Bank
    safe_move("src/pipeline/characterize.py", "src/template_bank/template_characterization.py")
    safe_move("src/pipeline/validate.py", "src/template_bank/template_validation.py")
    safe_move("src/pipeline/readiness.py", "src/template_bank/template_readiness.py")
    safe_move("src/pipeline/archive_legacy_bank.py", "src/template_bank/legacy_bank_archival.py")
    
    # Scoring (new module)
    create_placeholder_readme("src/scoring/combined_ranking.py", "# Placeholder for combined ranking logic\n")
    
    # Visualization
    safe_move("src/visualization/visualization.py", "src/visualization/validation_grid_generator.py")
    safe_move("src/pipeline/annotation_viewer.py", "src/visualization/annotation_viewer.py")
    safe_move("src/pipeline/annotation_exporter.py", "src/visualization/annotation_exporter.py")
    
    # Benchmarking
    safe_move("src/exploration/unified_pipeline_benchmark.py", "src/benchmarking/unified_pipeline_benchmark.py")
    safe_move("src/exploration/nms_diagnostic_evaluation.py", "src/benchmarking/nms_diagnostic_evaluation.py")
    
    # Diagnostics
    safe_move("src/pipeline/distance_transform_validation.py", "src/diagnostics/distance_transform_validation.py")
    safe_move("src/pipeline/validate_architecture.py", "src/diagnostics/validate_architecture.py")
    safe_move("src/pipeline/revalidate_and_compare.py", "src/diagnostics/revalidate_and_compare.py")
    safe_move("src/pipeline/empirical_survey.py", "src/diagnostics/empirical_survey.py")
    safe_move("src/pipeline/investigate.py", "src/diagnostics/investigate.py")
    safe_move("src/pipeline/manual_annotator.py", "src/diagnostics/manual_annotator.py")
    
    # Remove old dirs
    safe_remove_dir("src/localization")
    safe_remove_dir("src/exploration")

def phase_5_6_7_8():
    logger.info("--- Phase 5-8: Exploration, Reports, Outputs, Config Restructure ---")
    
    # Config
    safe_move("exploration/archived/misc/preprocessing.yaml", "config/preprocessing.yaml")
    safe_move("exploration/archived/misc/chamfer.yaml", "config/chamfer_matching.yaml")
    safe_move("exploration/archived/misc/template_bank.yaml", "config/template_bank.yaml")
    safe_move("exploration/archived/misc/stage5_verification.yaml", "config/verification.yaml")
    safe_move("exploration/archived/misc/PRD_Symbol_Localization.md", "docs/PRD_Symbol_Localization.md")
    safe_move("exploration/archived/misc/PRD_Symbol_Localization.pdf", "docs/PRD_Symbol_Localization.pdf")
    
    # We will use a generalized string replacement approach for file renames to avoid exhaustively listing everything.
    
    # Rename Reports in exploration/archived/reports
    reports_archive_dir = os.path.join(ROOT_DIR, "exploration/archived/reports")
    if os.path.exists(reports_archive_dir):
        for f in os.listdir(reports_archive_dir):
            if f.endswith(".md"):
                new_name = f
                new_name = new_name.replace("stage1_", "preprocessing_")
                new_name = new_name.replace("stage2_", "template_bank_")
                new_name = new_name.replace("stage3_", "chamfer_")
                new_name = new_name.replace("stage4_", "coverage_area_")
                new_name = new_name.replace("stage52_", "scale_root_cause_")
                new_name = new_name.replace("stage56_", "ranking_formula_")
                new_name = new_name.replace("stage59_", "stroke_integration_")
                if new_name != f:
                    safe_move(f"exploration/archived/reports/{f}", f"exploration/archived/reports/{new_name}")

    # Rename Scripts in exploration/archived/scripts
    scripts_archive_dir = os.path.join(ROOT_DIR, "exploration/archived/scripts")
    if os.path.exists(scripts_archive_dir):
        for f in os.listdir(scripts_archive_dir):
             if f.endswith(".py"):
                 new_name = f
                 new_name = new_name.replace("stage510_", "")
                 new_name = new_name.replace("stage59a_", "")
                 new_name = new_name.replace("stage59b_", "")
                 if new_name != f:
                     safe_move(f"exploration/archived/scripts/{f}", f"exploration/archived/scripts/{new_name}")
                     
    # Rename Verification Cascades Reports
    vc_reports_dir = os.path.join(ROOT_DIR, "reports/verification_cascades")
    if os.path.exists(vc_reports_dir):
        for f in os.listdir(vc_reports_dir):
            if f.startswith("stage510_"):
                new_name = f.replace("stage510_", "")
                safe_move(f"reports/verification_cascades/{f}", f"reports/verification_cascades/{new_name}")
                
    # Outputs restructuring
    outputs_dirs = [
        ("outputs/diagrams", "outputs/visual/pipeline_outputs/diagrams"),
        ("outputs/template", "outputs/visual/pipeline_outputs/template"),
        ("outputs/score_maps", "outputs/visual/diagnostics/score_maps"),
        ("outputs/score_map_visualizations", "outputs/visual/diagnostics/score_map_visualizations"),
        ("outputs/chamfer_visualizations", "outputs/visual/diagnostics/chamfer_visualizations"),
        ("outputs/distance_transforms", "outputs/visual/diagnostics/distance_transforms"),
        ("outputs/nms_overlays", "outputs/visual/overlays/nms"),
        ("outputs/candidates", "outputs/visual/galleries/candidates"),
        ("outputs/top_100_crops", "outputs/visual/galleries/top_candidates"),
        ("outputs/empirical_symbols", "outputs/visual/galleries/empirical_symbols"),
        ("outputs/template_bank", "outputs/visual/template_bank"),
        ("outputs/stage4_visualizations", "outputs/visual/pipeline_outputs/coverage_rescoring"),
        ("outputs/stage5_visualizations", "outputs/visual/pipeline_outputs/verification")
    ]
    for src, dst in outputs_dirs:
        if os.path.exists(os.path.join(ROOT_DIR, src)):
            safe_move(src, dst)

def phase_9():
    logger.info("--- Phase 9: Update Imports ---")
    import_replacements = {
        "src.pipeline.run_pipeline": "src.pipeline.run_pipeline",
        "src.pipeline.pipeline_orchestrator": "src.pipeline.pipeline_orchestrator_orchestrator",
        "src.preprocessing.grayscale_conversion": "src.preprocessing.grayscale_conversion",
        "src.preprocessing.denoising": "src.preprocessing.denoising",
        "src.preprocessing.binarization": "src.preprocessing.binarization",
        "src.preprocessing.image_loader": "src.preprocessing.image_loader",
        "src.template_bank.template_pyramid_generator": "src.template_bank.template_pyramid_generator",
        "src.template_matching.score_map_validation": "src.template_matching.score_map_validation",
        "src.template_bank.template_characterization": "src.template_bank.template_characterization",
        "src.template_bank.template_validation": "src.template_bank.template_validation",
        "src.template_bank.template_readiness": "src.template_bank.template_readiness",
        "src.template_bank.legacy_bank_archival": "src.template_bank.legacy_bank_archival",
        "src.visualization.validation_grid_generator": "src.visualization.validation_grid_generator",
        "src.visualization.annotation_viewer": "src.visualization.annotation_viewer",
        "src.visualization.annotation_exporter": "src.visualization.annotation_exporter",
        "src.benchmarking.unified_pipeline_benchmark": "src.benchmarking.unified_pipeline_benchmark",
        "src.benchmarking.nms_diagnostic_evaluation": "src.benchmarking.nms_diagnostic_evaluation",
        "src.diagnostics.distance_transform_validation": "src.diagnostics.distance_transform_validation",
        "src.template_bank.template_validation_architecture": "src.diagnostics.validate_architecture",
        "src.diagnostics.revalidate_and_compare": "src.diagnostics.revalidate_and_compare",
        "os.path.join(BASE_DIR, \"Data\")": "os.path.join(BASE_DIR, \"data\")",
    }
    
    py_files = list(Path(ROOT_DIR).rglob("*.py"))
    for py_file in py_files:
        try:
            content = py_file.read_text(encoding='utf-8')
            new_content = content
            for old, new in import_replacements.items():
                new_content = new_content.replace(old, new)
            
            if new_content != content:
                py_file.write_text(new_content, encoding='utf-8')
                logger.debug(f"Updated imports in {py_file}")
        except Exception as e:
            logger.error(f"Error updating imports in {py_file}: {e}")
            
def phase_11():
    logger.info("--- Phase 11: Create READMEs ---")
    readmes = [
        ("src/README.md", "# Source Code\nThis directory contains the production pipeline for Symbol Segmentor.\n"),
        ("src/pipeline/README.md", "# Pipeline\nOrchestrates the various stages of the localization pipeline.\n"),
        ("src/preprocessing/README.md", "# Preprocessing\nHandles image ingestion, grayscale conversion, denoising, and binarization.\n"),
        ("src/candidate_generation/README.md", "# Candidate Generation\nExtracts edges and computes distance transforms for template matching.\n"),
        ("src/template_matching/README.md", "# Template Matching\nPerforms Chamfer matching and score map validation.\n"),
        ("src/template_bank/README.md", "# Template Bank\nGenerates and validates multi-scale, multi-orientation templates.\n"),
        ("src/verification/README.md", "# Verification\nPerforms coverage audits and structural verification of candidates.\n"),
        ("src/scoring/README.md", "# Scoring\nCombines coverage, area, and structural metrics to produce a final ranking.\n"),
        ("src/visualization/README.md", "# Visualization\nGenerates validation grids, overlays, and debugging visual artifacts.\n"),
        ("src/benchmarking/README.md", "# Benchmarking\nEvaluates pipeline performance and NMS diagnostics.\n"),
        ("src/diagnostics/README.md", "# Diagnostics\nTools for investigating pipeline failures and architecture validation.\n"),
        ("src/common/README.md", "# Common\nShared utilities for I/O and logging.\n"),
        ("data/README.md", "# Data\nStructured dataset management: raw images, intermediate features, and processed metrics.\n"),
        ("outputs/README.md", "# Outputs\nGenerated artifacts categorized by visual diagnostics and tabular metrics.\n"),
        ("reports/README.md", "# Reports\nTopic-based analysis and visual forensics.\n"),
        ("exploration/README.md", "# Exploration\nIsolated research code and archived experiments.\n"),
        ("docs/README.md", "# Documentation\nProject guides, architectures, and monographs.\n"),
        ("config/README.md", "# Config\nYAML configuration files for pipeline stages.\n"),
        ("tests/README.md", "# Tests\nUnit and integration tests.\n"),
    ]
    
    for path, content in readmes:
        create_placeholder_readme(path, content)
        
    # Init files for modules
    for d in Path(os.path.join(ROOT_DIR, "src")).iterdir():
        if d.is_dir():
            init_file = d / "__init__.py"
            if not init_file.exists():
                init_file.write_text("")

def main():
    logger.info("Starting refactoring execution...")
    phase_2()
    phase_3()
    phase_4()
    phase_5_6_7_8()
    phase_9()
    phase_11()
    logger.info("Refactoring execution completed successfully.")

if __name__ == "__main__":
    main()
