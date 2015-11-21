# -*- coding: utf-8 -*-

#import sys; sys.path.insert(0, '..')
import unittest

from uosc.common import create_message, parse_message


class TestCreateMessage(unittest.TestCase):
    def assertMessage(self, expected, *args):
        self.assertEqual(create_message(*args), expected)

    def assertError(self, exc, *args):
        self.assertRaises(exc, create_message, *args)

    def test_create_message_address_nonascii(self):
        self.assertError(AssertionError, '/böse')

    def test_create_message_noargs(self):
        self.assertMessage(b'/nil\0\0\0\0,\0\0\0', '/nil')

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

    def test_create_message_double(self):
        self.assertMessage(b'/d\0\0,d\0\0@E\0\0\0\0\0\0', '/d', ('d', 42.0))

    def test_create_message_symbol(self):
        self.assertMessage(b'/S\0\0,S\0\0SPAMM\0\0\0', '/S', ('S', 'SPAMM'))

    def test_create_message_midi(self):
        self.assertMessage(b'/midi\0\0\0,m\0\0\0\xB0 \0', '/midi',
                          ('m', b'\0\xB0\x20\0'))

    def test_create_message_midi_fromtuple(self):
        self.assertMessage(b'/midi\0\0\0,m\0\0\0\xB0 \0', '/midi',
                          ('m', (0, 0xB0, 32, 0)))

    def test_create_message_midi_frombytearray(self):
        self.assertMessage(b'/midi\0\0\0,m\0\0\0\xB0 \0', '/midi',
                          ('m', bytearray([0, 0xB0, 32, 0])))

    def test_create_message_rgba(self):
        self.assertMessage(b'/rgba\0\0\0,r\0\0\x80\x20\x20\xFF', '/rgba',
                          ('r', b'\x80\x20\x20\xFF'))

    def test_create_message_rgba_fromtuple(self):
        self.assertMessage(b'/rgba\0\0\0,r\0\0\x80\x20\x20\xFF', '/rgba',
                          ('r', (128, 32, 32, 255)))

    def test_create_message_rgba_frombytearray(self):
        self.assertMessage(b'/rgba\0\0\0,r\0\0\x80\x20\x20\xFF', '/rgba',
                          ('r', bytearray([128, 32, 32, 255])))


class TestParseMessage(unittest.TestCase):
    def assertMessage(self, expected, *args):
        self.assertEqual(parse_message(*args), expected)

    def test_parse_address(self):
        self.assertEqual(parse_message(b'/nil\0\0\0\0,\0\0\0')[0], '/nil')
        self.assertEqual(parse_message(b'/*\0\0,\0\0\0')[0], '/*')

    def test_parse_typetags(self):
        self.assertEqual(parse_message(b'/i\0\0,i\0\0\0\0\0*')[1], 'i')
        self.assertEqual(parse_message(b'/is\0,is\0\0\0\0*foo\0')[1], 'is')
        self.assertEqual(parse_message(b'/nil\0\0\0\0,\0\0\0')[1], '')

    def test_parse_message_int(self):
        self.assertMessage(('/i', 'i', (42,)), b'/i\0\0,i\0\0\0\0\0*')

    def test_parse_message_float(self):
        self.assertMessage(('/f', 'f', (42.0,)), b'/f\0\0,f\0\0B(\0\0')

    def test_parse_message_str(self):
        self.assertMessage(('/s', 's', ('foo',)), b'/s\0\0,s\0\0foo\0')

    def test_parse_message_float(self):
        self.assertMessage(('/f', 'f', (42.0,)), b'/f\0\0,f\0\0B(\0\0')

    def test_parse_message_blob(self):
        self.assertMessage(('/b', 'b', (b'\xDE\xAD\xBE\xEF',)),
                           b'/b\0\0,b\0\0\0\0\0\x04\xDE\xAD\xBE\xEF')

    def test_parse_message_big(self):
        addr, tags, args = parse_message(
            b'/big\0\0\0\0,iisbff\0\0\0\x03\xe8\xff\xff\xff\xffhello'
            b'\0\0\0\0\0\0\x06\0\x01\x02\x03\x04\x05\0\0'
            b'?\x9d\xf3\xb6@\xb5\xb2-')

        self.assertEqual(addr, '/big')
        self.assertEqual(tags, 'iisbff')
        self.assertEqual((1000, -1, 'hello', bytes(range(6))), args[:-2])
        self.assertAlmostEqual(args[-2], 1.234)
        self.assertAlmostEqual(args[-1], 5.678)

    def test_parse_message_double(self):
        self.assertMessage(('/d', 'd', (42.0,)), b'/d\0\0,d\0\0@E\0\0\0\0\0\0')

    def test_parse_message_true(self):
        self.assertMessage(('/T', 'T', (True,)), b'/T\0\0,T\0\0')

    def test_parse_message_false(self):
        self.assertMessage(('/F', 'F', (False,)), b'/F\0\0,F\0\0')

    def test_parse_message_none(self):
        self.assertMessage(('/N', 'N', (None,)), b'/N\0\0,N\0\0')


if __name__ == '__main__':
    unittest.main()
