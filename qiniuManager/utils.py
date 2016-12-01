# coding=utf8
"""
The MIT License (MIT)

Copyright (c) 2014 Qiniu, Ltd.<sdk@qiniu.com>

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
SOFTWARE.

utils extracted from Qiniu SDK `https://github.com/qiniu/python-sdk`
due to some reasons, directly import from sdk caused exceptions when using python3
whatever, I just need few parts of the project and handle the http request manually

and now, py3 makes me awful, it upgraded nothing but chaos

"""


import sys
import time
import json
import hmac

from hashlib import sha1
from urlparse import urlparse
from base64 import urlsafe_b64encode


reload(sys)
sys.setdefaultencoding('utf8')


def b(data):
    return bytes(data)


def s(data):
    return bytes(data)


def urlsafe_base64_encode(data):
    """urlsafe的base64编码:

    对提供的数据进行urlsafe的base64编码。规格参考：
    http://developer.qiniu.com/docs/v6/api/overview/appendix.html#urlsafe-base64

    Args:
        data: 待编码的数据，一般为字符串

    Returns:
        编码后的字符串
    """
    ret = urlsafe_b64encode(b(data))
    return s(ret)


class Auth(object):
    """七牛安全机制类

    该类主要内容是七牛上传凭证、下载凭证、管理凭证三种凭证的签名接口的实现，以及回调验证。

    Attributes:
        __access_key: 账号密钥对中的accessKey，详见 https://portal.qiniu.com/setting/key
        __secret_key: 账号密钥对重的secretKey，详见 https://portal.qiniu.com/setting/key
    """

    def __init__(self, access_key, secret_key):
        """初始化Auth类"""
        self.__access_key = access_key
        self.__secret_key = b(secret_key)

    def __token(self, data):
        data = b(data)
        hashed = hmac.new(self.__secret_key, data, sha1)
        return urlsafe_base64_encode(hashed.digest())

    def token(self, data):
        return '{0}:{1}'.format(self.__access_key, self.__token(data))

    def token_with_data(self, data):
        data = urlsafe_base64_encode(data)
        return '{0}:{1}:{2}'.format(self.__access_key, self.__token(data), data)

    def token_of_request(self, url):
        """带请求体的签名（本质上是管理凭证的签名）

        Args:
            url:          待签名请求的url

        Returns:
            管理凭证
        """
        parsed_url = urlparse(url)
        query = parsed_url.query
        path = parsed_url.path
        data = path
        if query != '':
            data = ''.join([data, '?', query])
        data = ''.join([data, "\n"])

        return '{0}:{1}'.format(self.__access_key, self.__token(data))

    def private_download_url(self, url, expires=3600):
        """生成私有资源下载链接

        Args:
            url:     私有空间资源的原始URL
            expires: 下载凭证有效期，默认为3600s

        Returns:
            私有资源的下载链接
        """
        deadline = int(time.time()) + expires
        if '?' in url:
            url += '&'
        else:
            url += '?'
        url = '{0}e={1}'.format(url, str(deadline))

        token = self.token(url)
        return '{0}&token={1}'.format(url, token)

    def upload_token(self, bucket, key=None, expires=3600):
        """生成上传凭证

        Args:
            bucket:  上传的空间名
            key:     上传的文件名，默认为空
            expires: 上传凭证的过期时间，默认为3600s
            policy:  上传策略，默认为空

        Returns:
            上传凭证
        """
        if bucket is None or bucket == '':
            raise ValueError('invalid bucket name')

        scope = bucket
        if key is not None:
            scope = '{0}:{1}'.format(bucket, key)

        args = dict(
            scope=scope,
            deadline=int(time.time()) + expires,
        )

        return self.__upload_token(args)

    def __upload_token(self, policy):
        data = json.dumps(policy, separators=(',', ':'))
        return self.token_with_data(data)

