import sys; sys.path.insert(0, '..')
import unittest

from uosc.common import create_message


class TestCreateMessage(unittest.TestCase):
    def assertMessage(self, args, expected):
        self.assertEqual(create_message(*args), expected)

    def test_create_message_int(self):
        self.assertMessage(('/test1', 42), b'/test1\0\0,i\0\0\0\0\0*')

    def test_create_message_float(self):
        self.assertMessage(('/test1', 42.0), b'/test1\0\0,f\0\0B(\0\0')


if __name__ == '__main__':
    unittest.main()
