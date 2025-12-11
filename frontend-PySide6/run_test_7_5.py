"""Test runner script for Milestone 7.5 - System Metrics"""
import sys
import subprocess

if __name__ == "__main__":
    result = subprocess.run(
        [sys.executable, "-m", "pytest", "tests/test_system_metrics.py", "-v"],
        capture_output=True,
        text=True
    )
    
    print(result.stdout)
    print(result.stderr)
    sys.exit(result.returncode)
