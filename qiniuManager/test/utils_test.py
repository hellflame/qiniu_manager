# coding=utf8

import os
import sys
import random
import string
import base64
import unittest

from qiniuManager.utils import *


class UtilTest(unittest.TestCase):
    def test_mono_font_width(self):
        self.assertEqual(0, str_len(u''))
        self.assertEqual(1, str_len(u' '))
        self.assertEqual(2, str_len(u'✔'))
        self.assertEqual(3, str_len(u'✔ '))

    def test_random_mono_font_width(self):
        self.assertEqual(100, str_len(u''.join([random.choice(string.ascii_letters) for _ in range(100)])))
        if sys.version_info.major == 2:
            self.assertEqual(str_len(u''.join([unichr(random.randrange(3105, 65535)) for _ in range(100)])), 200)
        else:
            self.assertEqual(str_len(u''.join([chr(random.randrange(3105, 65535)) for _ in range(100)])), 200)

    def test_unit_change(self):
        self.assertEqual('0.00 B', unit_change(0))
        self.assertEqual("-10", unit_change(-10))
        self.assertEqual("1.00 KB", unit_change(1025))
        self.assertEqual("1024.00 B", unit_change(1024))
        self.assertEqual("1.00 MB", unit_change(1024 * 1024 + 1))

    def test_url_safe_base64(self):
        self.assertEqual(urlsafe_base64_encode("lin\bux\n"), base64.urlsafe_b64encode(b"lin\bux\n").decode())
        target = os.urandom(100)
        self.assertEqual(urlsafe_base64_encode(target), base64.urlsafe_b64encode(target).decode())


class AuthTest(unittest.TestCase):
    def setUp(self):
        self.ak = os.urandom(100)
        self.sk = os.urandom(100)
        self.test_data = os.urandom(200)
        self.auth = Auth(self.ak, self.sk)

    def test_token(self):
        self.assertEqual(self.auth._Auth__token(self.test_data), self.auth.token(self.test_data).split(":")[-1])

    def test_get_token(self):
        self.auth._Auth__token(u"中文")
        self.auth._Auth__token("Linux")

    def test_private_link(self):
        self.auth.private_download_url("http://whatever")
        self.auth.private_download_url("https://ok.co", 0)

    def test_upload_token(self):
        self.auth.upload_token("test")
        self.auth.upload_token("whatever", 'keykeykey')
        self.auth.upload_token("what ever is this", 'kekekeke', 0)


if __name__ == '__main__':
    unittest.main(verbosity=2)
