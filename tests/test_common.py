import sys; sys.path.insert(0, '..')
import unittest

from uosc.common import create_message


class TestCreateMessage(unittest.TestCase):
    def assertMessage(self, expected, *args):
        self.assertEqual(expected, create_message(*args))

    def assertTypeError(self, *args):
        self.assertRaises(TypeError, create_message, *args)

    def test_create_message_int(self):
        self.assertMessage(b'/test1\0\0,i\0\0\0\0\0*', '/test1', 42)

    def test_create_message_int_tag(self):
        self.assertMessage(b'/test1\0\0,i\0\0\0\0\0*', '/test1', ('i', 42))

    def test_create_message_int_fromfloat(self):
        self.assertTypeError('/test1', ('i', 42.0))

    def test_create_message_float(self):
        self.assertMessage(b'/test1\0\0,f\0\0B(\0\0', '/test1', 42.0)

    def test_create_message_float_tag(self):
        self.assertMessage(b'/test1\0\0,f\0\0B(\0\0', '/test1', ('f', 42.0))

    def test_create_message_float_fromint(self):
        self.assertMessage(b'/test1\0\0,f\0\0B(\0\0', '/test1', ('f', 42))


if __name__ == '__main__':
    unittest.main()
