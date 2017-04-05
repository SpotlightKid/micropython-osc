# -*- coding: utf-8 -*-

import unittest

from uosc.server import Impulse, parse_bundle, parse_message


typegen = type((lambda: (yield))())


class TestParseMessage(unittest.TestCase):
    def assertMessage(self, expected, *args):
        self.assertEqual(parse_message(*args), expected)

    def assertError(self, exc, *args):
        self.assertRaises(exc, parse_message, *args)

    def test_parse_address(self):
        self.assertEqual(parse_message(b'/nil\0\0\0\0,\0\0\0')[0], '/nil')
        self.assertEqual(parse_message(b'/*\0\0,\0\0\0')[0], '/*')

    def test_parse_address_invalid(self):
        self.assertError(ValueError, b'nil\0,\0\0\0')

    def test_parse_typetags(self):
        self.assertEqual(parse_message(b'/i\0\0,i\0\0\0\0\0*')[1], 'i')
        self.assertEqual(parse_message(b'/is\0,is\0\0\0\0*foo\0')[1], 'is')
        self.assertEqual(parse_message(b'/nil\0\0\0\0,\0\0\0')[1], '')

    def test_parse_no_typetags(self):
        _, tags, args = parse_message(b'/nt\0')
        self.assertEqual(tags, '')
        self.assertEqual(args, ())
        _, tags, args = parse_message(b'/nt\0\0\0\0*')
        self.assertEqual(tags, '')
        self.assertEqual(args, ())

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
        self.assertEqual((1000, -1, 'hello', b'\x00\x01\x02\x03\x04\x05'),
                         args[:-2])
        self.assertAlmostEqual(args[-2], 1.234)
        self.assertAlmostEqual(args[-1], 5.678)


class TestParseBundle(unittest.TestCase):
    timetag = 3657147741.6552954
    data1 = (b'#bundle\x00\xd9\xfb\xa5]\xa7\xc1p\x00\x00\x00\x00\x10'
        b'/test1\x00\x00,i\x00\x00\x00\x00\x00*\x00\x00\x00\x10'
        b'/test2\x00\x00,f\x00\x00@I\x06%\x00\x00\x00\x14'
        b'/test3\x00\x00,s\x00\x00hello\x00\x00\x00')
    data2 = (b'#bundle\x00\xd9\xfb\xa5]\xa7\xc1p\x00\x00\x00\x00\x10'
        b'/test1\x00\x00,i\x00\x00\x00\x00\x00*'
        b'\x00\x00\x00$#bundle\x00\xd9\xfb\xa5]\xa7\xc1p\x00'
        b'\x00\x00\x00\x10/test2\x00\x00,f\x00\x00@I\x06%')

    def test_parse_bundle_nobundle(self):
        self.assertRaises(TypeError, next, parse_bundle(b''))
        self.assertRaises(TypeError, next, parse_bundle(b'/test1'))

    def test_parse_bundle_returns_generator(self):
        biter = parse_bundle(self.data1)
        self.assertTrue(isinstance(biter, typegen))

    def test_parse_bundle_structure(self):
        # parsing flat bundle
        elements = list(parse_bundle(self.data1))
        self.assertEqual(len(elements), 3)
        self.assertTrue(isinstance(elements[0], tuple))
        self.assertEqual(len(elements[0]), 2)
        self.assertTrue(isinstance(elements[0][0], float))
        self.assertTrue(isinstance(elements[0][1], tuple))
        self.assertEqual(len(elements[0][1]), 3)
        self.assertTrue(isinstance(elements[0][1][2], tuple))

        self.assertEqual(elements[0][0], elements[1][0],
            "timetag of first and second bundle element differ")
        self.assertEqual(elements[0][0], elements[2][0],
            "timetag of first and third bundle element differ")

        # parsing nested bundle
        elements = list(parse_bundle(self.data2))
        self.assertEqual(len(elements), 2)
        self.assertTrue(isinstance(elements[0], tuple))
        self.assertEqual(len(elements[0]), 2)
        self.assertTrue(isinstance(elements[0][0], float))
        self.assertTrue(isinstance(elements[0][1], tuple))
        self.assertEqual(len(elements[0][1]), 3)
        self.assertTrue(isinstance(elements[0][1][2], tuple))

        self.assertEqual(elements[0][0], elements[1][0],
            "timetag of first element and element from nested bundle differ")

    def test_parse_bundle_elements(self):
        # parsing flat bundle
        elements = list(parse_bundle(self.data1))
        self.assertEqual(elements[0][0], self.timetag)
        self.assertEqual(elements[0][1], ('/test1', 'i', (42,)))
        self.assertEqual(elements[1][0], self.timetag)
        self.assertEqual(elements[1][1][:2], ('/test2', 'f'))
        self.assertEqual(elements[2][0], self.timetag)
        self.assertAlmostEqual(elements[1][1][2][0], 3.141)
        self.assertEqual(elements[2][1], ('/test3', 's', ('hello',)))


if __name__ == '__main__':
    unittest.main()
