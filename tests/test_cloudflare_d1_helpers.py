import unittest

from cloudflare_d1 import D1Store, _plain


class ProxyValue:
    def __init__(self, value):
        self.value = value

    def to_py(self):
        return self.value


class FakeStatement:
    def __init__(self, sql):
        self.sql = sql
        self.params = ()

    def bind(self, *params):
        self.params = params
        return self

    async def first(self):
        return ProxyValue({"id": 1, "sql": self.sql, "params": self.params})

    async def run(self):
        return ProxyValue(type("Result", (), {
            "results": [{"name": "admin_user"}],
            "meta": {"changes": 1},
        })())


class FakeDatabase:
    def __init__(self):
        self.last_statement = None

    def prepare(self, sql):
        self.last_statement = FakeStatement(sql)
        return self.last_statement

    async def batch(self, statements):
        return ProxyValue([{"success": True} for _ in statements])


class FakeRequest:
    scope = {"env": type("Env", (), {"DB": FakeDatabase()})()}


class CloudflareD1HelperTests(unittest.IsolatedAsyncioTestCase):
    def test_plain_converts_runtime_proxy(self):
        self.assertEqual(_plain(ProxyValue({"ok": True})), {"ok": True})

    def test_plain_keeps_native_values(self):
        self.assertEqual(_plain([1, 2, 3]), [1, 2, 3])
        self.assertIsNone(_plain(None))

    async def test_parameterized_query_uses_bind(self):
        store = D1Store(FakeRequest.scope["env"].DB)
        row = await store.one("SELECT id FROM admin_user WHERE id = ?", 1)
        self.assertEqual(row["id"], 1)
        self.assertEqual(FakeRequest.scope["env"].DB.last_statement.params, (1,))

    async def test_all_returns_result_rows(self):
        store = D1Store(FakeRequest.scope["env"].DB)
        rows = await store.all("SELECT name FROM sqlite_master")
        self.assertEqual(rows, [{"name": "admin_user"}])

    async def test_execute_returns_metadata(self):
        store = D1Store(FakeRequest.scope["env"].DB)
        meta = await store.execute("DELETE FROM admin_sessions WHERE token_hash = ?", "digest")
        self.assertEqual(meta, {"changes": 1})

    async def test_from_request_reads_d1_binding(self):
        store = D1Store.from_request(FakeRequest())
        self.assertIsInstance(store, D1Store)


if __name__ == "__main__":
    unittest.main()
