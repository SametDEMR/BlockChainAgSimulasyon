"""Test runner script for Milestone 7.3 - Node Status Cards"""
import sys
import subprocess

if __name__ == "__main__":
    # Run pytest for node status cards (7.3)
    result = subprocess.run(
        [sys.executable, "-m", "pytest", "tests/test_node_status_card.py", "-v"],
        capture_output=True,
        text=True
    )
    
    print(result.stdout)
    print(result.stderr)
    sys.exit(result.returncode)
