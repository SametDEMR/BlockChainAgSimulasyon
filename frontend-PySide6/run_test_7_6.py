"""Test runner script for Milestone 7.6 - Real-time Updater"""
import sys
import subprocess

if __name__ == "__main__":
    result = subprocess.run(
        [sys.executable, "-m", "pytest", "tests/test_updater_thread.py", "-v", "-s"],
        capture_output=True,
        text=True
    )
    
    print(result.stdout)
    print(result.stderr)
    sys.exit(result.returncode)
