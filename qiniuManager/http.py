# coding=utf8
from __future__ import print_function
from qiniuManager import progress
import socket
import time
import sys
import ssl
import os

if sys.version_info.major == 2:
    from cStringIO import StringIO

    def s2b(s):
        return s

    def b2s(s):
        return s
else:
    from io import StringIO

    def s2b(s):
        if isinstance(s, bytes):
            return s
        return bytes(s.encode())

    def b2s(s):
        if isinstance(s, str):
            return s
        return s.decode(errors='ignore')


class SockFeed(object):
    def __init__(self, httpConnection, chuck=1024):
        self.socket = httpConnection.connect
        self.buffer = None
        self.chuck_size = chuck
        self.head = None
        self.header = {}
        self.http_code = 0
        self.data = ''
        self.progressed = 0
        self.total = 0
        self.disable_progress = False
        self.last_stamp = time.time()
        self.top_speed = 0
        self.chucked = False
        self.title = ''

        self.file_handle = None

    def __del__(self):
        if self.file_handle:
            self.file_handle.close()

    @progress.bar()
    def http_response(self, file_path='', skip_body=False):
        if file_path and not self.file_handle:
            file_index = 1
            path_choice = file_path
            while os.path.exists(path_choice):
                path_choice = '{}.{}'.format(file_path, file_index)
                file_index += 1

            self.file_handle = open(path_choice, 'wb')
            self.title = path_choice
        if self.head and self.progressed == self.total:
            self.total = self.progressed = 100
            return self.data
        data = self.socket.recv(self.chuck_size)
        temp = StringIO(b2s(data))
        if not data:
            self.progressed = self.total = 100
            return self.data

        if not self.head or not self.header:
            self.head = temp.readline().strip()
            self.http_code = int(self.head.split(" ")[1])
            if not self.http_code == 200:
                self.total = self.progressed = 1
                if self.file_handle:
                    current_file_name = self.file_handle.name
                    self.file_handle.close()
                    os.remove(current_file_name)
                return False
            while True:
                partial = temp.readline()
                if not partial or partial == '\r\n':
                    if self.header.get("Content-Length"):
                        self.total = int(self.header.get("Content-Length"))
                    elif self.header.get("Transfer-Encoding") == 'chunked':
                        self.chucked = True
                        print("\033[01;31mchucked encoding is not supported here for now\033[00m")
                        assert False
                    break
                index = partial.index(":")
                key = partial[0: index].strip()
                val = partial[index + 1:].strip()
                self.header[key] = val
            if skip_body:
                self.total = self.progressed = 100
                return self.header
            left = temp.read()

            if left:
                if self.file_handle:
                    self.file_handle.write(s2b(left))
                else:
                    self.data += b2s(left)

                self.progressed += len(s2b(left))

        else:
            if self.file_handle:
                self.file_handle.write(s2b(data))
            else:
                self.data += b2s(data)
            self.progressed += len(s2b(data))


class HTTPCons(object):
    def __init__(self, debug=False):
        self.host = ''
        self.port = 0
        self.is_debug = debug
        self.s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.connect = None

    def https_init(self, host, port):
        context = ssl.create_default_context()
        context.check_hostname = True
        context.verify_mode = ssl.CERT_REQUIRED
        context.load_default_certs()
        self.connect = context.wrap_socket(self.s, server_hostname=host)
        # self.connect.settimeout(65)
        self.connect.connect((host, port))
        self.host = host
        self.port = port

    def http_init(self, host, port):
        self.connect = self.s
        # self.connect.settimeout(60)
        self.connect.connect((host, port))
        self.host = host
        self.port = port

    def request(self, url, method='GET', headers=None, data=None):
        if '//' not in url:
            raise URLNotComplete(url, 'url protocol')
        index = url.index('//')
        ishttps = url[0: index - 1].lower() == 'https'
        host_url = url[index + 2:]
        if "/" not in host_url:
            host_url += '/'
        index = host_url.index("/")
        host_port = host_url[0: index]
        url = host_url[index:]
        port = None
        if ':' in host_port:
            split = host_port.split(":")
            host = split[0]
            port = int(split[1].split("/")[0])
        else:
            host = host_port

        if ishttps:
            if not port:
                port = 443
            self.https_init(host, port)
        else:
            if not port:
                port = 80
            self.http_init(host, port)
        self.__send(url, method, headers, post_data=data)

    def __send(self, href, method='GET', headers=None, post_data=None):
        data = """{method} {href} HTTP/1.1\r\n{headers}\r\n\r\n"""
        if not headers:
            head = """Host: {}\r\n""".format(self.host)
            head += "User-Agent: HELLFLAME"
        else:
            head = "\r\n".join(["{}: {}".format(x, headers[x]) for x in headers])
            if 'Host' not in headers:
                head += """\r\nHost: {}""".format(self.host)
            if 'User-Agent' not in headers:
                head += "\r\nUser-Agent: HELLFLAME"
        if method == 'POST':
            if data and type(data) == str:
                # upload for one time
                head += "\r\nContent-Length: {}".format(len(post_data))
                head += "\r\n{}".format(post_data)
            else:
                raise URLNotComplete(href, 'POST data')
        elif method == 'GET':
            if post_data:
                assert type(post_data) == dict
                if '?' not in href[-1]:
                    href += '?'

                for i in post_data:
                    href += '{}={}&'.format(i, post_data[i])
        data = data.format(method=method, href=href, headers=head)
        if self.is_debug:
            print("\033[01;33mRequest:\033[00m\033[01;31m(DANGER)\033[00m")
            print(data.__repr__().strip("'"))
        self.connect.sendall(s2b(data))

    def __del__(self):
        if self.connect is self.s:
            self.connect.close()
        else:
            self.connect.close()
            self.s.close()


def unit_change(target):
    unit_list = ('B', 'KB', 'MB', 'GB', 'TB')
    index = 0
    target = float(target)
    while target > 1024:
        index += 1
        target /= 1024
    return "{} {}".format(round(target, 2), unit_list[index])


class URLNotComplete(Exception):
    def __init__(self, url, lack):
        self.url = url
        self.lack = lack

    def __str__(self):
        return "URL: {} missing {}".format(self.url, self.lack)
