"""
scripts/setup_upstream_tests.py — Automatic upstream html5lib-tests repository downloader and synchronizer.

Usage:
    python scripts/setup_upstream_tests.py [--force]
"""

import os
import sys
import subprocess
import shutil
import urllib.request
import zipfile
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
TARGET_DIR = PROJECT_ROOT / "html5lib-tests"
REPO_URL = "https://github.com/html5lib/html5lib-tests.git"
ZIP_URL = "https://github.com/html5lib/html5lib-tests/archive/refs/heads/master.zip"


def sync_upstream_tests(force: bool = False) -> bool:
    print("=" * 65)
    print("  Official html5lib-tests Downloader & Setup")
    print("=" * 65)

    if TARGET_DIR.exists() and not force:
        tree_dir = TARGET_DIR / "tree-construction"
        if tree_dir.exists():
            test_files = list(tree_dir.glob("*.dat"))
            print(f"[OK] html5lib-tests already present at: {TARGET_DIR}")
            print(f"[OK] Found {len(test_files)} .dat compliance test suites.")
            print("  (Use --force to re-download or update)")
            return True

    if TARGET_DIR.exists() and force:
        print(f"Removing existing directory: {TARGET_DIR}")
        shutil.rmtree(TARGET_DIR, ignore_errors=True)

    # Method 1: Git clone
    try:
        print(f"Attempting git clone from {REPO_URL} ...")
        res = subprocess.run(["git", "clone", "--depth", "1", REPO_URL, str(TARGET_DIR)],
                             cwd=str(PROJECT_ROOT), capture_output=True, text=True)
        if res.returncode == 0 and TARGET_DIR.exists():
            print("[OK] Successfully cloned html5lib-tests via git!")
            return True
        else:
            print(f"Git clone failed or git not on PATH: {res.stderr.strip()}")
    except Exception as e:
        print(f"Git execution exception: {e}")

    # Method 2: Fallback ZIP download
    try:
        print(f"Falling back to direct ZIP download from {ZIP_URL} ...")
        zip_path = PROJECT_ROOT / "html5lib_tests_temp.zip"
        urllib.request.urlretrieve(ZIP_URL, str(zip_path))
        
        with zipfile.ZipFile(str(zip_path), 'r') as zip_ref:
            zip_ref.extractall(str(PROJECT_ROOT))
            
        extracted_dir = PROJECT_ROOT / "html5lib-tests-master"
        if extracted_dir.exists():
            if TARGET_DIR.exists():
                shutil.rmtree(TARGET_DIR, ignore_errors=True)
            shutil.move(str(extracted_dir), str(TARGET_DIR))
            
        if zip_path.exists():
            zip_path.unlink()
            
        print("[OK] Successfully downloaded and extracted html5lib-tests ZIP!")
        return True
    except Exception as e:
        print(f"[ERROR] Failed to download zip archive: {e}")
        return False


if __name__ == "__main__":
    force_download = "--force" in sys.argv
    success = sync_upstream_tests(force=force_download)
    sys.exit(0 if success else 1)
