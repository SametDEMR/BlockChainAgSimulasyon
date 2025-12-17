"""
Quick Test Runner for Fork Real-Time Tests
Runs tests directly without pytest complexity
"""
import sys
import os

# Proje root'unu path'e ekle
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', '..'))
sys.path.insert(0, project_root)

print("=" * 70)
print("🚀 RUNNING FORK REAL-TIME TESTS")
print("=" * 70)

# Pytest'i çalıştır
import subprocess

result = subprocess.run(
    [sys.executable, "-m", "pytest", __file__.replace("run_fork_real_time_test.py", "test_fork_real_time.py"), "-v", "-s"],
    cwd=project_root
)

sys.exit(result.returncode)
