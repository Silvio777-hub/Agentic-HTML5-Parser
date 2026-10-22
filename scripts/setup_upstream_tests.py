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
BRANCH = "newtests"
REPO_URL = "https://github.com/html5lib/html5lib-tests.git"
ZIP_URL = f"https://github.com/html5lib/html5lib-tests/archive/refs/heads/{BRANCH}.zip"


def sync_upstream_tests(force: bool = False) -> bool:
    print("=" * 65)
    print("  Official html5lib-tests Downloader & Setup")
    print("=" * 65)

    tree_dir = TARGET_DIR / "tree-construction"
    if tree_dir.exists() and not force:
        test_files = list(tree_dir.glob("*.dat"))
        if test_files:
            print(f"[OK] html5lib-tests already present at: {TARGET_DIR}")
            print(f"[OK] Found {len(test_files)} .dat compliance test suites.")
            print("  (Use --force to re-download or update)")
            return True

    if TARGET_DIR.exists() and force:
        print(f"Removing existing directory: {TARGET_DIR}")
        shutil.rmtree(TARGET_DIR, ignore_errors=True)

    tree_dir.mkdir(parents=True, exist_ok=True)

    # Method 1: Git clone with newtests branch
    try:
        print(f"Attempting git clone ({BRANCH} branch) from {REPO_URL} ...")
        res = subprocess.run(
            ["git", "clone", "--depth", "1", "--branch", BRANCH, REPO_URL, str(TARGET_DIR)],
            cwd=str(PROJECT_ROOT), capture_output=True, text=True
        )
        if res.returncode == 0 and (TARGET_DIR / "tree-construction").exists():
            test_files = list((TARGET_DIR / "tree-construction").glob("*.dat"))
            print(f"[OK] Successfully cloned html5lib-tests ({len(test_files)} .dat files found)!")
            return True
        else:
            print(f"Git clone not successful or git not on PATH: {res.stderr.strip() or res.stdout.strip()}")
    except Exception as e:
        print(f"Git execution exception: {e}")

    # Method 2: Direct ZIP download from newtests branch
    try:
        print(f"Falling back to direct ZIP download from {ZIP_URL} ...")
        req = urllib.request.Request(ZIP_URL, headers={"User-Agent": "html5parser-thesis"})
        with urllib.request.urlopen(req, timeout=60) as resp:
            data = resp.read()

        import io
        with zipfile.ZipFile(io.BytesIO(data)) as z:
            for member in z.namelist():
                if "tree-construction/" in member and member.endswith(".dat"):
                    fname = os.path.basename(member)
                    if fname:
                        out_path = tree_dir / fname
                        with open(out_path, "wb") as f:
                            f.write(z.read(member))

        test_files = list(tree_dir.glob("*.dat"))
        print(f"[OK] Successfully extracted {len(test_files)} .dat test suites to {tree_dir}!")
        return len(test_files) > 0
    except Exception as e:
        print(f"[ERROR] Failed to download and extract zip archive: {e}")
        return False


if __name__ == "__main__":
    force_download = "--force" in sys.argv
    success = sync_upstream_tests(force=force_download)
    sys.exit(0 if success else 1)
