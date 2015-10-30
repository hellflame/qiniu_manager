#!/usr/bin/python
"""
    this python file is specially designed to deal with some case that failed to get private space links
    some how .... the main function sometimes seemed to work fine with private links
"""

from urllib2 import urlopen, Request, HTTPCookieProcessor, install_opener, build_opener, HTTPHandler
from urllib import urlencode
from cookielib import LWPCookieJar
__author__ = 'linux'


class Private:
    def __init__(self):
        self.__username = ""
        self.__password = ""
        self.__login_url = ""
        self.basic_info()
        self.login()

    def basic_info(self):
        from ConfigParser import ConfigParser
        from os import path
        current_dir = __file__.replace('private_dealer.py', '')
        if path.exists(current_dir + "qiniu.conf"):
            config = ConfigParser()
            config.read(current_dir + "qiniu.conf")
            self.__username = config.get('ext', 'username')
            self.__password = config.get('ext', 'password')
            self.__login_url = config.get('ext', 'login_url')
        else:
            print 'config missing!!'
            exit(1)

    def login(self):
        cookie = LWPCookieJar()
        cookie_support = HTTPCookieProcessor(cookie)
        opener = build_opener(cookie_support, HTTPHandler)
        install_opener(opener)
        post_data = {
            'goto': '',
            'username': self.__username,
            'password': self.__password
        }
        headers = {
            'Referer': 'https://portal.qiniu.com/signin'
        }
        request = Request(self.__login_url, urlencode(post_data), headers=headers)
        urlopen(request)

    def file_lists(self, bucket):
        response = urlopen('https://portal.qiniu.com/bucket/{}/files?marker=&limit=169&prefix='.format(bucket))
        from json import loads
        return loads(response.read())


if __name__ == '__main__':
    from sys import argv
    for i in Private().file_lists('backup').get('items', []):
        if argv[1] == i.get('key', ''):
            print i.get('signed_download_url', '')
