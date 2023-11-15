"""Unit tests for the uosc.dispatch module."""

import unittest

from uosc.dispatch import get_global_root, OSCAddressContainer, OSCMethod, TYPETAGS_ANY


class TestCreateMessage(unittest.TestCase):
    def setUp(self):
        def _dummy(*args, **kw):
            pass

        self.root = root = get_global_root()
        root.register_method(_dummy, "/ops/math/add", "ii")
        root.register_method(_dummy, "/ops/math/sum", TYPETAGS_ANY)
        root.register_method(_dummy, "/ops/string/add", "ii")
        root.register_method(_dummy, "/ops/array/add", "ii")
        root.register_method(_dummy, "/ops/math/sub", "ii")

    def tearDown(self):
        self.root.clear()

    def test_get_global_root(self):
        root = get_global_root()
        self.assertTrue(root is self.root)

    def test_osc_address_space(self):
        self.assertTrue(isinstance(self.root, OSCAddressContainer))
        self.assertEqual(self.root.name, "/")

    def test_match_address(self):
        results = self.root.match("/ops/math/add")
        self.assertTrue(isinstance(results, list))
        self.assertEqual(len(results), 1)
        self.assertTrue(isinstance(results[0], OSCMethod))
        self.assertEqual(results[0].name, "/ops/math/add")
        self.assertTrue(callable(results[0]))

    def test_match_address_with_typetags(self):
        results = self.root.match("/ops/math/add", "ii")
        self.assertTrue(isinstance(results, list))
        self.assertEqual(len(results), 1)
        self.assertTrue(isinstance(results[0], OSCMethod))
        self.assertEqual(results[0].name, "/ops/math/add")
        self.assertTrue(callable(results[0]))
        self.assertEqual(results[0].typetags, "ii")
        results = self.root.match("/ops/math/add", "f")
        self.assertTrue(isinstance(results, list))
        self.assertEqual(len(results), 0)


if __name__ == '__main__':
    unittest.main()
