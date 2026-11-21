"""Async adapter for Cloudflare D1 bindings.

All user values must be passed as prepared-statement parameters.
"""
def _plain(value):
    converter = getattr(value, "to_py", None)
    if callable(converter):
        return converter()
    return value


def _get(value, key, default=None):
    if isinstance(value, dict):
        return value.get(key, default)
    return getattr(value, key, default)


class D1Store:
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
        return _plain(await self._statement(sql, params).first())

    async def all(self, sql, *params):
        result = _plain(await self._statement(sql, params).run())
        return _plain(_get(result, "results", [])) or []

    async def execute(self, sql, *params):
        result = _plain(await self._statement(sql, params).run())
        return _plain(_get(result, "meta", result))

    async def batch(self, statements):
        prepared = [
            self._statement(sql, tuple(params))
            for sql, params in statements
        ]
        if not prepared:
            return []
        return _plain(await self.db.batch(prepared))
