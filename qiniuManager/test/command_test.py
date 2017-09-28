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
        parse = self.parser.parse_args(shlex.split("--key '{}' '{}'".format(ak, sk)))
        self.assertEqual(parse.key, [ak, sk])

    def test_remove(self):
        name = self.generate_random_target(10)
        parse = self.parser.parse_args(shlex.split("-r '{}'".format(name)))
        self.assertTrue(parse.remove)
        parse = self.parser.parse_args(shlex.split("--remove '{}'".format(name)))
        self.assertTrue(parse.remove)

    def test_force_remove(self):
        name = self.generate_random_target(10)
        parse = self.parser.parse_args(shlex.split("-rf '{}'".format(name)))
        self.assertTrue(parse.force_remove)
        parse = self.parser.parse_args(shlex.split("--force-remove '{}'".format(name)))
        self.assertTrue(parse.force_remove)

    def test_revert(self):
        self.assertFalse(self.parser.parse_args(["--revert"]).revert)

    def test_size(self):
        self.assertTrue(self.parser.parse_args(["--size"]).size)

    def test_list(self):
        space = self.generate_random_target(10)
        parse = self.parser.parse_args(shlex.split("-l '{}'".format(space)))
        self.assertListEqual(parse.list, [space])
        parse = self.parser.parse_args(["-l"])
        self.assertListEqual(parse.list, [None])
        parse = self.parser.parse_args(shlex.split("--list '{}'".format(space)))
        self.assertListEqual(parse.list, [space])
        parse = self.parser.parse_args(["--list"])
        self.assertListEqual(parse.list, [None])

    def test_list_all(self):
        self.assertTrue(self.parser.parse_args(['-la']).list_all)
        self.assertTrue(self.parser.parse_args(['--list-all']).list_all)

    def test_list_debug(self):
        space = self.generate_random_target(10)
        self.assertListEqual(self.parser.parse_args(['-ld']).list_debug, [None])
        self.assertListEqual(self.parser.parse_args(['-ld', space]).list_debug, [space])

    def test_check_space(self):
        space = self.generate_random_target(10)
        self.assertListEqual(self.parser.parse_args(['-s']).space_check, [None])
        self.assertListEqual(self.parser.parse_args(['-s', space]).space_check, [space])


if __name__ == '__main__':
    unittest.main()
