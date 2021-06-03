import subprocess
import pytest
from unittest.mock import patch
from modin.config import TestRayClient

server_proc = None

def pytest_sessionstart(session):
    if TestRayClient.get():
        import ray.util
        from ray.util.client.common import ClientBaseRef, ClientObjectRef
        # This part fixes an issue in ray 1.3 that will be resolved in the 1.4
        # release (https://github.com/ray-project/ray/pull/15320)
        # Can be removed once the ray version for the ray client tests is bumped
        # to 1.4
        def patched_eq(self, other):
            return isinstance(other, ClientBaseRef) and self.id == other.id
        ClientObjectRef.__eq__ = patched_eq

        port = '50051'
        global server_proc
        server_proc = subprocess.Popen([
            'python', '-m', 'ray.util.client.server', '--port', port, '--redis-address', '0.0.0.0:12345'])
        # ray.util.connect(f"0.0.0.0:{port}")

def pytest_sessionfinish(session):
    if server_proc and TestRayClient.get():
        try:
            import ray
            ray.util.disconnect()
        except RuntimeError as e:
            # Mimic behavior of 1.4+ where disconnect is idempotent
            pass
        if server_proc.poll() is None:
            server_proc.kill()