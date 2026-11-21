"""Small async adapter for Cloudflare D1 bindings.

This module is deliberately separate from the current SQLite managers.
It does not silently replace local storage: route-by-route migration and
tests are required before the Cloudflare Worker can serve the full dashboard.

Usage inside a FastAPI request handled by Python Workers:
    store = D1Store.from_request(request)
    row = await store.one("SELECT id FROM admin_user WHERE id = ?", 1)

All values must be supplied as bound parameters. Never interpolate user input
into SQL strings.
"""


def _plain(value):
    """Convert Pyodide proxy values to ordinary Python values when supported."""
    converter = getattr(value, "to_py", None)
    if callable(converter):
        return converter()
    return value


class D1Store:
    """Async wrapper over the Cloudflare D1 Worker binding."""

    def __init__(self, database_binding):
        if database_binding is None:
            raise RuntimeError("Cloudflare D1 binding 'DB' is not configured.")
        self.db = database_binding

    @classmethod
    def from_request(cls, request):
        env = request.scope.get("env")
        if env is None:
            raise RuntimeError("Cloudflare Worker environment is unavailable.")
        return cls(getattr(env, "DB", None))

    def _statement(self, sql, params):
        statement = self.db.prepare(sql)
        if params:
            statement = statement.bind(*params)
        return statement

    async def one(self, sql, *params):
        result = await self._statement(sql, params).first()
        return _plain(result)

    async def all(self, sql, *params):
        result = await self._statement(sql, params).run()
        rows = getattr(result, "results", [])
        return _plain(rows) or []

    async def execute(self, sql, *params):
        result = await self._statement(sql, params).run()
        return _plain(getattr(result, "meta", result))

    async def batch(self, statements):
        """Run a list of (SQL, parameter_tuple) pairs in one D1 batch."""
        prepared = [
            self._statement(sql, tuple(params))
            for sql, params in statements
        ]
        if not prepared:
            return []
        result = await self.db.batch(prepared)
        return _plain(result)
