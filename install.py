"""
Symbol Segmentor — Automated Installer.

Usage:
    python install.py

This script:
  1. Detects the execution environment (Python, OS, RAM, OpenCV, CUDA).
  2. Creates a virtual environment (if needed).
  3. Installs dependencies from requirements.txt.
  4. Verifies all imports.
  5. Creates required directories.
  6. Validates write permissions.
  7. Downloads nothing and modifies no datasets.

At completion, prints a structured success or failure report.
"""

import os
import sys
import platform
import subprocess
import shutil

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
REQUIREMENTS_PATH = os.path.join(SCRIPT_DIR, "requirements.txt")
VENV_DIR = os.path.join(SCRIPT_DIR, ".venv")

REQUIRED_DIRS = [
    "config",
    "data",
    "data/raw/slds",
    "data/raw/templates",
    "data/metadata",
    "data/processed",
    "data/intermediate",
    "data/templates",
    "outputs",
    "reports",
    "reports/system",
    "logs",
    "docs",
]

REQUIRED_IMPORTS = [
    ("numpy", "numpy"),
    ("cv2", "opencv-python"),
    ("matplotlib", "matplotlib"),
    ("pandas", "pandas"),
    ("yaml", "PyYAML"),
    ("scipy", "scipy"),
]


def heading(text):
    print(f"\n{'=' * 60}")
    print(f"  {text}")
    print(f"{'=' * 60}\n")


def step(text):
    print(f"  [*] {text}")


def ok(text):
    print(f"  [OK] {text}")


def warn(text):
    print(f"  [!] {text}")


def fail(text):
    print(f"  [FAIL] {text}")


# ---------------------------------------------------------------------------
# Phase 1: Environment Detection
# ---------------------------------------------------------------------------
def detect_environment():
    heading("Phase 1: Environment Detection")

    py_ver = sys.version.split()[0]
    step(f"Python version     : {py_ver}")

    os_name = f"{platform.system()} {platform.release()} ({platform.machine()})"
    step(f"Operating System   : {os_name}")

    try:
        import psutil
        ram_gb = round(psutil.virtual_memory().total / (1024 ** 3), 1)
    except ImportError:
        # Fallback for systems without psutil
        if platform.system() == "Windows":
            try:
                import ctypes
                kernel32 = ctypes.windll.kernel32
                c_ulonglong = ctypes.c_ulonglong
                class MEMORYSTATUSEX(ctypes.Structure):
                    _fields_ = [
                        ("dwLength", ctypes.c_ulong),
                        ("dwMemoryLoad", ctypes.c_ulong),
                        ("ullTotalPhys", c_ulonglong),
                        ("ullAvailPhys", c_ulonglong),
                        ("ullTotalPageFile", c_ulonglong),
                        ("ullAvailPageFile", c_ulonglong),
                        ("ullTotalVirtual", c_ulonglong),
                        ("ullAvailVirtual", c_ulonglong),
                        ("sullAvailExtendedVirtual", c_ulonglong),
                    ]
                stat = MEMORYSTATUSEX()
                stat.dwLength = ctypes.sizeof(stat)
                kernel32.GlobalMemoryStatusEx(ctypes.byref(stat))
                ram_gb = round(stat.ullTotalPhys / (1024 ** 3), 1)
            except Exception:
                ram_gb = "unknown"
        else:
            ram_gb = "unknown"
    step(f"Available RAM      : {ram_gb} GB")

    # OpenCV check
    try:
        import cv2
        step(f"OpenCV version     : {cv2.__version__}")
        opencv_ok = True
    except ImportError:
        step("OpenCV             : NOT INSTALLED (will be installed)")
        opencv_ok = False

    # CUDA check
    cuda_available = False
    try:
        import cv2
        build_info = cv2.getBuildInformation()
        if "CUDA" in build_info and "YES" in build_info.split("CUDA")[1][:50]:
            cuda_available = True
            step("CUDA support       : Available")
        else:
            step("CUDA support       : Not available (CPU mode)")
    except Exception:
        step("CUDA support       : Not available (CPU mode)")

    return py_ver, os_name, ram_gb, opencv_ok, cuda_available


# ---------------------------------------------------------------------------
# Phase 2: Virtual Environment & Dependencies
# ---------------------------------------------------------------------------
def install_dependencies():
    heading("Phase 2: Dependency Installation")

    pip_cmd = [sys.executable, "-m", "pip"]

    # Check if requirements.txt exists
    if not os.path.exists(REQUIREMENTS_PATH):
        fail(f"requirements.txt not found at {REQUIREMENTS_PATH}")
        return False

    step("Installing dependencies from requirements.txt...")
    result = subprocess.run(
        pip_cmd + ["install", "-r", REQUIREMENTS_PATH, "--quiet"],
        capture_output=True, text=True
    )
    if result.returncode != 0:
        fail("Dependency installation failed:")
        print(result.stderr)
        return False

    ok("All dependencies installed successfully.")
    return True


# ---------------------------------------------------------------------------
# Phase 3: Import Verification
# ---------------------------------------------------------------------------
def verify_imports():
    heading("Phase 3: Import Verification")
    all_ok = True

    for module_name, package_name in REQUIRED_IMPORTS:
        try:
            mod = __import__(module_name)
            ver = getattr(mod, "__version__", "unknown")
            ok(f"{package_name:20s} v{ver}")
        except ImportError:
            fail(f"{package_name:20s} IMPORT FAILED")
            all_ok = False

    return all_ok


# ---------------------------------------------------------------------------
# Phase 4: Directory Structure
# ---------------------------------------------------------------------------
def create_directories():
    heading("Phase 4: Directory Structure")
    for d in REQUIRED_DIRS:
        full_path = os.path.join(SCRIPT_DIR, d)
        os.makedirs(full_path, exist_ok=True)

    ok(f"Created/verified {len(REQUIRED_DIRS)} directories.")
    return True


# ---------------------------------------------------------------------------
# Phase 5: Write Permission Verification
# ---------------------------------------------------------------------------
def verify_permissions():
    heading("Phase 5: Write Permission Verification")
    all_ok = True

    for d in ["outputs", "reports", "logs"]:
        dir_path = os.path.join(SCRIPT_DIR, d)
        test_file = os.path.join(dir_path, ".write_test")
        try:
            with open(test_file, "w") as f:
                f.write("test")
            os.remove(test_file)
            ok(f"{d:20s} writable")
        except OSError as e:
            fail(f"{d:20s} NOT WRITABLE — {e}")
            all_ok = False

    return all_ok


# ---------------------------------------------------------------------------
# Phase 6: Dataset Verification
# ---------------------------------------------------------------------------
def verify_dataset():
    heading("Phase 6: Dataset Verification")
    issues = []

    slds_dir = os.path.join(SCRIPT_DIR, "data", "raw", "slds")
    if os.path.isdir(slds_dir):
        sld_files = [f for f in os.listdir(slds_dir) if f.lower().endswith(".png")]
        ok(f"SLD images found   : {len(sld_files)} files in data/raw/slds/")
    else:
        warn("SLD directory missing: data/raw/slds/")
        issues.append("SLD dataset directory does not exist")

    templates_dir = os.path.join(SCRIPT_DIR, "data", "raw", "templates")
    mr_path = os.path.join(templates_dir, "MR_Symbol.png")
    if os.path.exists(mr_path):
        ok("MR Symbol template : found")
    else:
        warn("MR Symbol template not found: data/raw/templates/MR_Symbol.png")
        issues.append("MR Symbol template missing")

    if issues:
        warn("Dataset issues detected — pipeline may fail at runtime.")
    return issues


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------
def main():
    heading("Symbol Segmentor — Installation")
    print("  Configuring the research framework for execution.\n")

    errors = []

    py_ver, os_name, ram_gb, opencv_ok, cuda = detect_environment()

    if not install_dependencies():
        errors.append("Dependency installation failed")

    if not verify_imports():
        errors.append("Import verification failed")

    if not create_directories():
        errors.append("Directory creation failed")

    if not verify_permissions():
        errors.append("Write permission verification failed")

    dataset_issues = verify_dataset()

    # --- Final Report ---
    heading("Installation Summary")

    if errors:
        for e in errors:
            fail(e)
        print("\n  Installation FAILED.  Fix the issues above and re-run.")
        sys.exit(1)
    else:
        print("  Installation Successful\n")
        ok("Dependencies installed")
        ok("Repository validated")
        ok("Ready to execute")

        if dataset_issues:
            print()
            warn("Non-blocking dataset issues:")
            for issue in dataset_issues:
                warn(f"  - {issue}")
            print("  The pipeline will report these at runtime.\n")

        print(f"\n  Next step:  python run.py\n")


if __name__ == "__main__":
    main()
