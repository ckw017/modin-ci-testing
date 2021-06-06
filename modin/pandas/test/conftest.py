import subprocess
import pytest
from unittest.mock import patch
from modin.config import TestRayClient


def _import_pandas(*args):
    import pandas

def pytest_sessionstart(session):
    import ray
    from packaging import version
    if version.parse(ray.__version__) <= version.parse("1.3.0"):
        from ray.util.client.common import ClientBaseRef, ClientObjectRef
        # This part fixes an issue in ray 1.3 that will be resolved in the 1.4
        # release (https://github.com/ray-project/ray/pull/15320)
        # Can be removed once the ray version for the ray client tests is bumped
        # to 1.4
        def patched_eq(self, other):
            return isinstance(other, ClientBaseRef) and self.id == other.id
        ClientObjectRef.__eq__ = patched_eq

    if TestRayClient.get():
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