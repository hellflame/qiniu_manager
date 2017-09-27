# coding=utf8
import unittest
import string
import random
import shlex

from qiniuManager.run import *


class ParserTest(unittest.TestCase):
    def setUp(self):
        _, self.parser = parser()

    @staticmethod
    def generate_random_target(length):
        target = string.ascii_letters + string.digits + ' '
        return ''.join([random.choice(target) for _ in range(length)]).replace("'", "\\\'").replace("\"", "\\\"")

    def test_export(self):
        args = self.parser.parse_args(shlex.split("-x"))
        self.assertEqual(args.export, [None])

    def test_export_with_space(self):
        rand = self.generate_random_target(20)
        self.assertListEqual(self.parser.parse_args(shlex.split("-x '{}'".format(rand))).export, [rand])

    def test_file(self):
        rand = self.generate_random_target(50)
        self.assertEqual(self.parser.parse_args(shlex.split("'{}'".format(rand))).file, rand)

    def test_file_space(self):
        ran1, ran2 = self.generate_random_target(50), self.generate_random_target(50)
        parse = self.parser.parse_args(shlex.split("'{}' '{}'".format(ran1, ran2)))
        self.assertListEqual([parse.file, parse.space], [ran1, ran2])

    def test_key(self):
        ak, sk = self.generate_random_target(50), self.generate_random_target(50)
        parse = self.parser.parse_args(shlex.split("-k '{}' '{}'".format(ak, sk)))
        self.assertEqual(parse.key, [ak, sk])