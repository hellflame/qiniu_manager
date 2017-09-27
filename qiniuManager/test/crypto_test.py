import unittest
import random
import string

from qiniuManager.crypto import *

"""
    Test Pass Platforms:

    - Python 2.7.13 (default, Jul 30 2017, 15:55:47)
      [GCC 4.2.1 Compatible Apple LLVM 8.1.0 (clang-802.0.42)] on darwin
    - Python 3.5.3 (a37ecfe5f142bc971a86d17305cc5d1d70abec64, Jun 10 2017, 18:23:14)
      [PyPy 5.8.0-beta0 with GCC 4.2.1 Compatible Apple LLVM 8.1.0 (clang-802.0.42)] on darwin
    - Python 3.6.2 (default, Sep  4 2017, 19:45:38)
      [GCC 4.2.1 Compatible Apple LLVM 8.1.0 (clang-802.0.42)] on darwin

"""


class Tests(unittest.TestCase):
    def setUp(self):
        self.words = "".join([random.choice(string.ascii_letters + string.digits + string.punctuation)
                              for _ in range(1024)])

    def test_is_str(self):
        self.assertIsInstance(self.words, str)

    def test_enc(self):
        self.assertIsInstance(encrypt(self.words), str)

    def test_dec(self):
        self.assertEqual(self.words, decrypt(encrypt(self.words)))

    def test_dec_is_str(self):
        self.assertIsInstance(decrypt(encrypt(self.words)), str)


if __name__ == '__main__':
    unittest.main()

