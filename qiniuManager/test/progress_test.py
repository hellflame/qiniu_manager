# coding=utf8
import time
import random
import unittest

from qiniuManager.progress import *


class Pro(object):
    def __init__(self):
        self.progressed = 0
        self.total = 100
        self.title = 'test'
        self.chunked = False
        self.chunk_recved = 0
        self.start = time.time()

    @bar(100, '=')
    def loader(self):
        self._normal_loader()
        self.title = "固定长度"

    @bar(fill='x')
    def loader_x(self):
        self._normal_loader()
        self.title = "x"

    @bar()
    def auto_loader(self):
        self._normal_loader()
        self.title = "长度占满宽度"

    def _normal_loader(self):
        time.sleep(0.01)
        self.progressed += 1

    def _chunked_loader(self):
        self.chunked = True
        time.sleep(0.01)

        self.chunk_recved += random.randrange(3, 1000000)

        if time.time() - self.start > 5:
            self.progressed = self.total

    @bar()
    def chunked_loader(self):
        self._chunked_loader()
        self.title = "full width"

    @bar(100)
    def fixed_chunked_loader(self):
        self._chunked_loader()
        self.title = "fixed width"


class ProgressTester(unittest.TestCase):
    def test_100_progress(self):
        print("进度条换行")
        Pro().loader()
        Pro().loader_x()

    def test_auto_width_progress(self):
        print("进度条换行")
        Pro().auto_loader()

    def test_disable_progress(self):
        pro = Pro()
        pro.disable_progress = True
        pro.title = "无进度条，也就是说应该看不到这串字符才对"
        pro.loader()

    def test_chunked_progress(self):
        print("进度条换行")
        Pro().chunked_loader()

    def test_fixed_chunked_progress(self):
        print("进度条换行")
        Pro().fixed_chunked_loader()


if __name__ == '__main__':
    unittest.main(verbosity=2)


