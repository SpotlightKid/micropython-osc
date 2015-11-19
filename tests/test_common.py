# -*- coding: utf-8 -*-

#import sys; sys.path.insert(0, '..')
import unittest

from uosc.common import create_message


class TestCreateMessage(unittest.TestCase):
    def assertMessage(self, expected, *args):
        self.assertEqual(create_message(*args), expected)

    def assertError(self, exc, *args):
        self.assertRaises(exc, create_message, *args)

    def test_create_message_int(self):
        self.assertMessage(b'/i\0\0,i\0\0\0\0\0*', '/i', 42)

    def test_create_message_int_tag(self):
        self.assertMessage(b'/i\0\0,i\0\0\0\0\0*', '/i', ('i', 42))

    def test_create_message_int_fromfloat(self):
        self.assertError(TypeError, '/i', ('i', 42.0))

    def test_create_message_float(self):
        self.assertMessage(b'/f\0\0,f\0\0B(\0\0', '/f', 42.0)

    def test_create_message_float_tag(self):
        self.assertMessage(b'/f\0\0,f\0\0B(\0\0', '/f', ('f', 42.0))

    def test_create_message_float_fromint(self):
        self.assertMessage(b'/f\0\0,f\0\0B(\0\0', '/f', ('f', 42))

    def test_create_message_str(self):
        self.assertMessage(b'/s\0\0,s\0\0spamm\0\0\0', '/s', 'spamm')

    def test_create_message_str_withtag(self):
        self.assertMessage(b'/s\0\0,s\0\0spamm\0\0\0', '/s', ('s', 'spamm'))

    def test_create_message_str_nonascii(self):
        self.assertError(AssertionError, '/s', 'müsic')

    def test_create_message_blob(self):
        self.assertMessage(b'/b\0\0,b\0\0\0\0\0\x04\xDE\xAD\xBE\xEF',
                           '/b', b'\xDE\xAD\xBE\xEF')

    def test_create_message_blob_frombytearray(self):
        self.assertMessage(b'/b\0\0,b\0\0\0\0\0\x04\xDE\xAD\xBE\xEF',
                           '/b', bytearray([222, 173, 190, 239]))

    def test_create_message_blob_fromstr(self):
        self.assertMessage(b'/b\0\0,b\0\0\0\0\0\x03ni!\0', '/b', ('b', 'ni!'))

    def test_create_message_nil(self):
        self.assertMessage(b'/nil\0\0\0\0,N\0\0', '/nil', None)

    def test_create_message_nil_fromtag(self):
        self.assertMessage(b'/nil\0\0\0\0,N\0\0', '/nil', ('N', 'dummy'))

    def test_create_message_true(self):
        self.assertMessage(b'/true\0\0\0,T\0\0', '/true', True)

    def test_create_message_true_fromtag(self):
        self.assertMessage(b'/true\0\0\0,T\0\0', '/true', ('T', 'dummy'))

    def test_create_message_false(self):
        self.assertMessage(b'/false\0\0,F\0\0', '/false', False)

    def test_create_message_false_fromtag(self):
        self.assertMessage(b'/false\0\0,F\0\0', '/false', ('F', 'dummy'))

    def test_create_message_bigint(self):
        self.assertMessage(b'/h\0\0,h\0\0\0\0\0\0\0\0\0*', '/h', ('h', 42))


if __name__ == '__main__':
    unittest.main()
