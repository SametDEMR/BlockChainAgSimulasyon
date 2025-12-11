"""Test runner script for Milestone 7.1"""
import sys
import subprocess

if __name__ == "__main__":
    # Run pytest for metrics widget
    result = subprocess.run(
        [sys.executable, "-m", "pytest", "tests/test_metrics_widget.py", "-v"],
        capture_output=True,
        text=True
    )
    
    print(result.stdout)
    print(result.stderr)
    sys.exit(result.returncode)
