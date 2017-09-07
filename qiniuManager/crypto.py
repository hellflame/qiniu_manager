# coding=utf8
"""使用用户名加密API Key"""
import sys
import getpass
from itertools import cycle

__all__ = ['encrypt', 'decrypt']

if sys.version_info.major == 2:
    from base64 import encodestring, decodestring

    def encrypt(s):
        """
        (py2) encrypt with xor cycle username
        :param s: str
        :return: str
        """
        return encodestring(bytes(b''.join([bytes(chr(ord(i) ^ ord(j)).encode())
                                           for i, j in zip(s,
                                                           cycle(getpass.getuser()))]))).replace(b'\n', b'')


    def decrypt(s):
        """
        (py2) decrypt with xor cycle username
        :param s: str
        :return: str
        """
        return b''.join([bytes(chr(ord(i) ^ ord(j)).encode())
                         for i, j in zip(decodestring(s),
                                         cycle(getpass.getuser()))])

else:
    from base64 import encodebytes, decodebytes

    def encrypt(s):
        """
        (py3) encrypt with xor cycle username
        :param s: str
        :return: str
        """
        return encodebytes(bytes(b''.join([bytes(chr(i ^ ord(j)).encode())
                                          for i, j in zip(s.encode(),
                                                          cycle(getpass.getuser()))]))).replace(b'\n', b'').decode()


    def decrypt(s):
        """
        (py3) decrypt with xor cycle username
        :param s: str
        :return: str
        """
        return (b''.join([bytes(chr(i ^ ord(j)).encode())
                          for i, j in zip(decodebytes(s.encode()),
                                          cycle(getpass.getuser()))])).decode()

if __name__ == '__main__':
    """
    Test Pass Platforms:
    
    - Python 2.7.13 (default, Jul 30 2017, 15:55:47)
      [GCC 4.2.1 Compatible Apple LLVM 8.1.0 (clang-802.0.42)] on darwin
    - Python 3.5.3 (a37ecfe5f142bc971a86d17305cc5d1d70abec64, Jun 10 2017, 18:23:14)
      [PyPy 5.8.0-beta0 with GCC 4.2.1 Compatible Apple LLVM 8.1.0 (clang-802.0.42)] on darwin
    - Python 3.6.2 (default, Sep  4 2017, 19:45:38)
      [GCC 4.2.1 Compatible Apple LLVM 8.1.0 (clang-802.0.42)] on darwin
      
    """
    import unittest
    import random
    import string

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

    unittest.main()



