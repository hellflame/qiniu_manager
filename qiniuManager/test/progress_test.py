# coding=utf8
import time
import unittest

from qiniuManager.progress import *


class Pro(object):
    def __init__(self):
        self.progressed = 0
        self.total = 100
        self.title = 'test'

    @bar(100, '=')
    def loader(self):
        time.sleep(0.01)
        self.progressed += 1
        self.title = "固定长度"

    @bar()
    def auto_loader(self):
        time.sleep(0.01)
        self.progressed += 1
        self.title = "长度占满"


class ProgressTester(unittest.TestCase):
    def test_100_progress(self):
        print("先换行")
        Pro().loader()

    def test_auto_width_progress(self):
        print("先换行")
        Pro().auto_loader()


if __name__ == '__main__':
    unittest.main()


