# coding=utf8
import os
import unittest
import hashlib
import tempfile

from qiniuManager.http import *


class HTTPTest(unittest.TestCase):
    """
    static.hellflame.net
        域名下的文件大多数情况下大文件都是chunked编码，小文件可能会被缓存为正常编码
        文件内容为大小与hash已知的随机二进制文件
    raw.githubusercontent.com
        域名下文件未分块
        文件来自 https://raw.githubusercontent.com/hellflame/qiniu_manager/v1.4.6/qiniuManager/manager.py
    """
    @staticmethod
    def chunked_info(resp):
        return "分块编码" if resp.chunked else "常规编码"

    def test_https_request(self):
        req = HTTPCons()
        connect = req.request("https://static.hellflame.net/resource/de5ca9cf5320673dc43b526e3d737f05")
        self.assertEqual(req.host, 'static.hellflame.net')
        self.assertEqual(req.port, 443)
        self.assertIs(connect, req.connect)
        resp = SockFeed(req)
        resp.disable_progress = True
        resp.http_response(skip_body=True)

    def test_http_request(self):
        req = HTTPCons()
        connect = req.request("http://static.hellflame.net/resource/de5ca9cf5320673dc43b526e3d737f05")
        self.assertEqual(req.host, 'static.hellflame.net')
        self.assertEqual(req.port, 80)
        self.assertIs(connect, req.connect)
        resp = SockFeed(req)
        resp.disable_progress = True
        resp.http_response(skip_body=True)

    def test_response_in_memory(self):
        req = HTTPCons()
        req.request("https://static.hellflame.net/resource/c8c12b1c34af9808c34fa60d862016b7")
        resp = SockFeed(req)
        resp.disable_progress = True
        resp.http_response()
        self.assertEqual(hashlib.md5(resp.data).hexdigest(),
                         '9a50ddbef4c82eb9003bd496a00e0989',
                         "请保持数据获取正确完整, " + self.chunked_info(resp))

    def test_response_downloading(self):
        file_path = os.path.join(tempfile.gettempdir(), '1m.data')
        req = HTTPCons()
        req.request("https://static.hellflame.net/resource/c8c12b1c34af9808c34fa60d862016b7")
        resp = SockFeed(req)
        resp.disable_progress = True
        resp.http_response(file_path, overwrite=True)

        with open(file_path, 'rb') as handle:
            # 如果上面请求结束未关闭文件，这里将无法读取全部文件
            content = handle.read()

        os.remove(resp.file_handle.name)
        self.assertEqual(hashlib.md5(content).hexdigest(),
                         '9a50ddbef4c82eb9003bd496a00e0989',
                         "这里出错，多半是因为没有关闭文件, " + self.chunked_info(resp))

    def test_small_response_in_memory(self):
        req = HTTPCons()
        req.request("https://static.hellflame.net/resource/5573012afe7227ab4457331df42af57d")
        resp = SockFeed(req)
        resp.disable_progress = True
        resp.http_response()
        self.assertEqual(hashlib.md5(resp.data).hexdigest(),
                         '8688229badcaa3cb2730dab99a618be6',
                         "请保持数据获取正确完整, " + self.chunked_info(resp))

    def test_small_response_downloading(self):
        file_path = os.path.join(tempfile.gettempdir(), '3k.data')
        req = HTTPCons()
        req.request("https://static.hellflame.net/resource/5573012afe7227ab4457331df42af57d")
        resp = SockFeed(req)
        resp.disable_progress = True
        resp.http_response(file_path, overwrite=True)
        with open(file_path, 'rb') as handle:
            # 如果上面请求结束未关闭文件，这里将无法读取全部文件
            content = handle.read()
        os.remove(resp.file_handle.name)
        self.assertEqual(hashlib.md5(content).hexdigest(),
                         '8688229badcaa3cb2730dab99a618be6',
                         "这里出错，多半是因为没有关闭文件, " + self.chunked_info(resp))

    def test_non_chunked_in_memory(self):
        req = HTTPCons()
        req.request("https://raw.githubusercontent.com/hellflame/qiniu_manager/v1.4.6/qiniuManager/manager.py")
        resp = SockFeed(req)
        resp.disable_progress = True
        resp.http_response()
        self.assertEqual(hashlib.md5(resp.data).hexdigest(),
                         '276efce035d49f7f3ea168b720075523',
                         "请保持数据获取正确完整，" + self.chunked_info(resp))

    def test_test_non_chunked_downloading(self):
        file_path = os.path.join(tempfile.gettempdir(), 'manager.py')
        req = HTTPCons()
        req.request("https://raw.githubusercontent.com/hellflame/qiniu_manager/v1.4.6/qiniuManager/manager.py")
        resp = SockFeed(req)
        resp.disable_progress = True
        resp.http_response(file_path, overwrite=True)
        with open(file_path, 'rb') as handle:
            content = handle.read()
        os.remove(resp.file_handle.name)
        self.assertEqual(hashlib.md5(content).hexdigest(),
                         '276efce035d49f7f3ea168b720075523',
                         "请保持数据获取正确完整，" + self.chunked_info(resp))


if __name__ == '__main__':
    unittest.main(verbosity=2)

