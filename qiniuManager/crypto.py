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



