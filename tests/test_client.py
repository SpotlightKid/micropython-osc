# -*- coding: utf-8 -*-

import sys
import time
import unittest

from uosc.client import Bundle, create_message, pack_bundle
from uosc.common import NTP_DELTA

try:
    from struct import error as StructError
except ImportError:
    StructError = TypeError


PY3 = sys.version_info[:2] >= (3, 0)


class TestCreateMessage(unittest.TestCase):
    def assertMessage(self, expected, *args):
        self.assertEqual(create_message(*args), expected)

    def assertError(self, exc, *args):
        self.assertRaises(exc, create_message, *args)

    def test_create_message_address_nonascii(self):
        self.assertError(AssertionError, '/böse')

    def test_create_message_noargs(self):
        self.assertMessage(b'/nil\0\0\0\0,\0\0\0', '/nil')

    def test_create_message_shortaddress(self):
        """OSC address ends with zero byte and no further padding"""
        self.assertMessage(b'/ni\0,\0\0\0', '/ni')

    def test_create_message_int(self):
        self.assertMessage(b'/i\0\0,i\0\0\0\0\0*', '/i', 42)

    def test_create_message_int_tag(self):
        self.assertMessage(b'/i\0\0,i\0\0\0\0\0*', '/i', ('i', 42))

    if PY3:
        def test_create_message_int_fromfloat(self):
            self.assertError(StructError, '/i', ('i', 42.0))

    def test_create_message_float(self):
        self.assertMessage(b'/f\0\0,f\0\0B(\0\0', '/f', 42.0)

    def test_create_message_float_tag(self):
        self.assertMessage(b'/f\0\0,f\0\0B(\0\0', '/f', ('f', 42.0))

    def test_create_message_float_fromint(self):
        self.assertMessage(b'/f\0\0,f\0\0B(\0\0', '/f', ('f', 42))

    def test_create_message_str(self):
        self.assertMessage(b'/s\0\0,s\0\0spamm\0\0\0', '/s', u'spamm')

    def test_create_message_str_withtag(self):
        self.assertMessage(b'/s\0\0,s\0\0spamm\0\0\0', '/s', ('s', 'spamm'))

    def test_create_message_str_nonascii(self):
        self.assertError(AssertionError, '/s', u'müsic')

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

    def test_create_message_char(self):
        self.assertMessage(b'/c\0\0,c\0\0\0\0\0x', '/c', ('c', 'x'))

    def test_create_message_midi(self):
        self.assertMessage(b'/midi\0\0\0,m\0\0\0\xB0 \0', '/midi',
                          ('m', b'\0\xB0\x20\0'))

    def test_create_message_midi_fromtuple(self):
        self.assertMessage(b'/midi\0\0\0,m\0\0\0\xB0 \0', '/midi',
                          ('m', (0, 0xB0, 32, 0)))

    def test_create_message_midi_fromtuple(self):
        self.assertMessage(b'/midi\0\0\0,m\0\0\0\xB0 \0', '/midi',
                          ('m', [0, 0xB0, 32, 0]))

    def test_create_message_midi_frombytearray(self):
        self.assertMessage(b'/midi\0\0\0,m\0\0\0\xB0 \0', '/midi',
                          ('m', bytearray([0, 0xB0, 32, 0])))

    def test_create_message_rgba(self):
        self.assertMessage(b'/rgba\0\0\0,r\0\0\x80\x20\x20\xFF', '/rgba',
                          ('r', b'\x80\x20\x20\xFF'))

    def test_create_message_rgba_fromtuple(self):
        self.assertMessage(b'/rgba\0\0\0,r\0\0\x80\x20\x20\xFF', '/rgba',
                          ('r', (128, 32, 32, 255)))

    def test_create_message_rgba_fromlist(self):
        self.assertMessage(b'/rgba\0\0\0,r\0\0\x80\x20\x20\xFF', '/rgba',
                          ('r', [128, 32, 32, 255]))

    def test_create_message_rgba_frombytearray(self):
        self.assertMessage(b'/rgba\0\0\0,r\0\0\x80  \xFF', '/rgba',
                          ('r', bytearray([128, 32, 32, 255])))

    def test_create_message_combi(self):
        self.assertMessage(
            b'/big\0\0\0\0,iisbff\0\0\0\x03\xe8\xff\xff\xff\xffhello'
            b'\0\0\0\0\0\0\x06\0\x01\x02\x03\x04\x05\0\0'
            b'?\x9d\xf3\xb6@\xb5\xb2-',
            '/big', 1000, -1, u'hello', bytearray(range(6)), 1.234, 5.678)


class TestBundle(unittest.TestCase):
    timetag = 3657147741.6552954
    data1 = (b'#bundle\x00\xd9\xfb\xa5]\xa7\xc1p\x00\x00\x00\x00\x10'
        b'/test1\x00\x00,i\x00\x00\x00\x00\x00*\x00\x00\x00\x10'
        b'/test2\x00\x00,f\x00\x00@I\x06%\x00\x00\x00\x14'
        b'/test3\x00\x00,s\x00\x00hello\x00\x00\x00')
    data2 = (b'#bundle\x00\xd9\xfb\xa5]\xa7\xc1p\x00\x00\x00\x00\x10'
        b'/test1\x00\x00,i\x00\x00\x00\x00\x00*'
        b'\x00\x00\x00$#bundle\x00\xd9\xfb\xa5]\xa7\xc1p\x00'
        b'\x00\x00\x00\x10/test2\x00\x00,f\x00\x00@I\x06%')

    def test_create_bundle_withtimetag(self):
        t = time.time() + NTP_DELTA
        bundle = Bundle(t)
        self.assertEqual(bundle.timetag, t)
        bundle = Bundle(t, ('/test1',))
        self.assertEqual(bundle.timetag, t)

    def test_create_bundle_notimetag(self):
        t = time.time() + NTP_DELTA
        bundle = Bundle()
        self.assertTrue(bundle.timetag >= t)
        bundle = Bundle(('/test1',))
        self.assertTrue(bundle.timetag >= t)

    def test_pack_bundle_fromtuples(self):
        bundle = Bundle(self.timetag)
        bundle.add(('/test1', 42))
        bundle.add(('/test2', 3.141))
        bundle.add(('/test3', u'hello'))
        self.assertEqual(pack_bundle(bundle), self.data1)

    def test_pack_bundle_frommessages(self):
        bundle = Bundle(self.timetag)
        bundle.add(create_message('/test1', 42))
        bundle.add(create_message('/test2', 3.141))
        bundle.add(create_message('/test3', u'hello'))
        self.assertEqual(pack_bundle(bundle), self.data1)

    def test_pack_bundle_frombundle(self):
        bundle1 = Bundle(self.timetag)
        bundle1.add(('/test1', 42))
        bundle2 = Bundle(self.timetag, ('/test2', 3.141))
        bundle1.add(bundle2)
        self.assertEqual(pack_bundle(bundle1), self.data2)


if __name__ == '__main__':
    unittest.main()
