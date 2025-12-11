"""Test runner script for Milestone 7.2 - Real-time Graph"""
import sys
import subprocess

if __name__ == "__main__":
    # Run pytest for metrics graph (7.2)
    result = subprocess.run(
        [sys.executable, "-m", "pytest", "tests/test_metrics_graph.py", "-v"],
        capture_output=True,
        text=True
    )
    
    print(result.stdout)
    print(result.stderr)
    sys.exit(result.returncode)
