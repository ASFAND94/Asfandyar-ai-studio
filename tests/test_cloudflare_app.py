import unittest
from types import SimpleNamespace

from cloudflare_app import health, root, storage_health


class FakeD1Statement:
    def __init__(self, row):
        self.row = row

    async def first(self):
        return self.row


class FakeD1Database:
    def prepare(self, sql):
        if sql == "SELECT 1 AS ok":
            return FakeD1Statement({"ok": 1})
        raise AssertionError("Unexpected SQL")


class CloudflareAppTests(unittest.IsolatedAsyncioTestCase):
    async def test_root_identifies_worker_shell(self):
        result = await root()
        self.assertEqual(result["status"], "worker-shell")

    async def test_health_is_healthy(self):
        self.assertEqual(await health(), {"status": "healthy"})

    async def test_storage_health_checks_bound_d1(self):
        request = SimpleNamespace(scope={
            "env": SimpleNamespace(DB=FakeD1Database())
        })
        result = await storage_health(request)
        self.assertEqual(result, {"status": "healthy", "storage": "connected"})


if __name__ == "__main__":
    unittest.main()
