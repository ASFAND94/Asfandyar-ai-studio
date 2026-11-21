import unittest

from cloudflare_d1 import _plain


class ProxyValue:
    def __init__(self, value):
        self.value = value

    def to_py(self):
        return self.value


class CloudflareD1HelperTests(unittest.TestCase):
    def test_plain_converts_runtime_proxy(self):
        self.assertEqual(_plain(ProxyValue({"ok": True})), {"ok": True})

    def test_plain_keeps_native_values(self):
        self.assertEqual(_plain([1, 2, 3]), [1, 2, 3])
        self.assertIsNone(_plain(None))


if __name__ == "__main__":
    unittest.main()
