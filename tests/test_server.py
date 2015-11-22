# -*- coding: utf-8 -*-

import unittest

from uosc.server import Impulse, parse_message


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

    def test_parse_message_double(self):
        self.assertMessage(('/d', 'd', (42.0,)), b'/d\0\0,d\0\0@E\0\0\0\0\0\0')

    def test_parse_message_true(self):
        self.assertMessage(('/T', 'T', (True,)), b'/T\0\0,T\0\0')

    def test_parse_message_false(self):
        self.assertMessage(('/F', 'F', (False,)), b'/F\0\0,F\0\0')

    def test_parse_message_none(self):
        self.assertMessage(('/N', 'N', (None,)), b'/N\0\0,N\0\0')

    def test_parse_message_impulse(self):
        self.assertMessage(('/I', 'I', (Impulse,)), b'/I\0\0,I\0\0')

    def test_parse_message_midi(self):
        self.assertMessage(('/midi', 'm', ((0, 0xB0, 32, 0),)),
                           b'/midi\0\0\0,m\0\0\0\xB0 \0')

    def test_parse_message_rgba(self):
        self.assertMessage(('/rgba', 'r', ((128, 32, 32, 255),)),
                           b'/rgba\0\0\0,r\0\0\x80  \xFF')

    def test_parse_message_symbol(self):
        self.assertMessage(('/S', 'S', ('SPAMM',)), b'/S\0\0,S\0\0SPAMM\0\0\0')

    def test_parse_message_char(self):
        self.assertMessage(('/c', 'c', ('x',)), b'/c\0\0,c\0\0\0\0\0x')

    def test_parse_message_bigint(self):
        self.assertMessage(('/h', 'h', (42,)), b'/h\0\0,h\0\0\0\0\0\0\0\0\0*')

    def test_parse_message_combi(self):
        addr, tags, args = parse_message(
            b'/big\0\0\0\0,iisbff\0\0\0\x03\xe8\xff\xff\xff\xffhello'
            b'\0\0\0\0\0\0\x06\0\x01\x02\x03\x04\x05\0\0'
            b'?\x9d\xf3\xb6@\xb5\xb2-')

        self.assertEqual(addr, '/big')
        self.assertEqual(tags, 'iisbff')
        self.assertEqual((1000, -1, 'hello', bytes(range(6))), args[:-2])
        self.assertAlmostEqual(args[-2], 1.234)
        self.assertAlmostEqual(args[-1], 5.678)


if __name__ == '__main__':
    unittest.main()
