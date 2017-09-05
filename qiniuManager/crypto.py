# coding=utf8
"""使用用户名加密API Key"""
import sys
import getpass
from itertools import cycle

if sys.version_info.major == 2:
    from base64 import encodestring, decodestring

    def encrypt(s):
        return encodestring(bytes(b''.join([bytes(chr(ord(i) ^ ord(j)).encode())
                                           for i, j in zip(s, cycle(getpass.getuser()))]))).replace(b'\n', b'')


    def decrypt(s):
        return b''.join([bytes(chr(ord(i) ^ ord(j)).encode()) for i, j in zip(decodestring(s), cycle(getpass.getuser()))])

else:
    from base64 import encodebytes, decodebytes

    def encrypt(s):
        return encodebytes(bytes(b''.join([bytes(chr(ord(i) ^ ord(j)).encode())
                                          for i, j in zip(s, cycle(getpass.getuser()))]))).replace(b'\n', b'')


    def decrypt(s):
        return b''.join([bytes(chr(i ^ ord(j)).encode()) for i, j in zip(decodebytes(s), cycle(getpass.getuser()))])

if __name__ == '__main__':
    print(encrypt("whatever"))
    print(decrypt(encrypt("whatever")))
    print(decrypt(encrypt("whatever")) == b'whatever')


