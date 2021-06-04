import subprocess
import pytest
from unittest.mock import patch
from modin.config import TestRayClient


def _import_pandas(*args):
    import pandas

def pytest_sessionstart(session):
    if TestRayClient.get():
        import modin.pandas
        import ray

        port = '50051'
        # Clean up any extra processes from previous runs
        subprocess.check_output(["ray", "stop", "--force"])
        subprocess.check_output(["ray", "start", "--head", "--num-cpus", "2",
            "--ray-client-server-port", port])
        ray.util.connect(f"0.0.0.0:{port}")
        ray.worker.global_worker.run_function_on_all_workers(_import_pandas)

def pytest_sessionfinish(session):
    if TestRayClient.get():
        subprocess.check_output(["ray", "stop", "--force"])