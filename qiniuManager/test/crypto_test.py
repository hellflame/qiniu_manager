import unittest
import random
import string

from qiniuManager.crypto import *


class Tests(unittest.TestCase):
    def setUp(self):
        self.words = "".join([random.choice(string.ascii_letters + string.digits + string.punctuation)
                              for _ in range(1024)])

    def test_is_str(self):
        self.assertIsInstance(self.words,
                              str,
                              "参数应该为字符串，而不是 {}".format(type(self.words)))

    def test_enc(self):
        enc = encrypt(self.words)
        self.assertIsInstance(enc,
                              str,
                              "加密结果应该为字符串，而不是 {}".format(type(enc)))

    def test_dec(self):
        self.assertEqual(self.words,
                         decrypt(encrypt(self.words)),
                         "对称加密算法失败！")

    def test_dec_is_str(self):
        dec = decrypt(encrypt(self.words))
        self.assertIsInstance(dec,
                              str,
                              "解密结果应该为字符串，而不是 {}".format(type(dec)))

    def test_cycle(self):
        times = random.randrange(13, 30)

        def toggle(t):
            if t % 2:
                return decrypt
            return encrypt

        # string 为不可变量
        result = self.words
        for i in range(times):
            result = toggle(i)(result)

        if times % 2:
            self.assertEqual(decrypt(result), self.words, "对称加密算法失败")
        else:
            self.assertEqual(result, self.words)


if __name__ == '__main__':
    unittest.main(verbosity=2)

