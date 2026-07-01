import os
import shutil

BASE_DIR = r"c:\Users\arhaa\OneDrive\Symbol Segmentor"
ARCHIVE_DIR = os.path.join(BASE_DIR, "outputs", "archive")

def copy_if_exists(src, dest):
    if not os.path.exists(src):
        print(f"Skipping (does not exist): {src}")
        return
    
    if os.path.isdir(src):
        # If destination directory exists, remove it first to do a clean copy
        if os.path.exists(dest):
            shutil.rmtree(dest)
        shutil.copytree(src, dest)
        print(f"Copied directory: {src} -> {dest}")
    else:
        # Ensure parent directory of destination exists
        os.makedirs(os.path.dirname(dest), exist_ok=True)
        shutil.copy2(src, dest)
        print(f"Copied file: {src} -> {dest}")

def run_archiving():
    print("Starting Archival Process...")
    os.makedirs(ARCHIVE_DIR, exist_ok=True)
    
    # 1. Method A Template Bank
    copy_if_exists(
        os.path.join(BASE_DIR, "outputs", "template_bank", "scales"),
        os.path.join(ARCHIVE_DIR, "stage2_method_A_template_bank", "scales")
    )
    copy_if_exists(
        os.path.join(BASE_DIR, "outputs", "template_bank", "rotations"),
        os.path.join(ARCHIVE_DIR, "stage2_method_A_template_bank", "rotations")
    )
    
    # 2. Legacy Manifest
    copy_if_exists(
        os.path.join(BASE_DIR, "outputs", "template_bank", "template_bank_manifest.csv"),
        os.path.join(ARCHIVE_DIR, "stage2_legacy_manifests", "template_bank_manifest.csv")
    )
    
    # 3. Validation Reports
    validation_files = [
        "template_bank_validation.md",
        "template_bank_statistics.md",
        "stage2_readiness.md",
        "stage2_revalidation_verdict.md"
    ]
    for vf in validation_files:
        copy_if_exists(
            os.path.join(BASE_DIR, "reports", vf),
            os.path.join(ARCHIVE_DIR, "stage2_validation_reports", vf)
        )
    copy_if_exists(
        os.path.join(BASE_DIR, "reports", "template_bank_visual_validation"),
        os.path.join(ARCHIVE_DIR, "stage2_validation_reports", "template_bank_visual_validation")
    )
    
    # 4. Forensics
    forensic_files = [
        "degradation_threshold.md",
        "topology_preservation_analysis.md"
    ]
    for ff in forensic_files:
        copy_if_exists(
            os.path.join(BASE_DIR, "reports", ff),
            os.path.join(ARCHIVE_DIR, "stage2_forensics", ff)
        )
    copy_if_exists(
        os.path.join(BASE_DIR, "reports", "template_bank_forensics"),
        os.path.join(ARCHIVE_DIR, "stage2_forensics", "template_bank_forensics")
    )
    
    # 5. Stage 2.4 Provenance Audit
    provenance_files = [
        "prd_scale_assumption_audit.md",
        "prd_scale_dependency_analysis.md",
        "prd_scale_evidence_audit.md",
        "prd_scale_range_provenance.md",
        "prd_scale_rationale_analysis.md",
        "prd_scale_references.md"
    ]
    for pf in provenance_files:
        copy_if_exists(
            os.path.join(BASE_DIR, "reports", pf),
            os.path.join(ARCHIVE_DIR, "stage2_4_provenance_audit", pf)
        )
        
    # 6. Stage 2.6 Method Benchmark
    benchmark_files = [
        "baseline_template_metrics.md",
        "baseline_edge_generation_audit.md",
        "prd_scale_support_assessment.md",
        "chamfer_readiness_assessment.md",
        "template_generation_strategy_comparison.md",
        "stage2_final_resolution.md",
        "template_generation_metrics_db.json"
    ]
    for bf in benchmark_files:
        copy_if_exists(
            os.path.join(BASE_DIR, "reports", bf),
            os.path.join(ARCHIVE_DIR, "stage2_6_method_benchmark", bf)
        )
        
    # 7. Stage 2.6 Visual Forensics
    copy_if_exists(
        os.path.join(BASE_DIR, "reports", "template_generation_forensics"),
        os.path.join(ARCHIVE_DIR, "stage2_6_visual_forensics")
    )
    
    print("Archival Process completed successfully.")

if __name__ == "__main__":
    run_archiving()
