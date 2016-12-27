# coding=utf8
import cStringIO
import progress
import socket
import time
import ssl
import os


class SockFeed:
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
            # print("\033[01;31m{}\033[00m Downloading".format(path_choice))
        # while True:
        data = self.socket.recv(self.chuck_size)
        temp = cStringIO.StringIO(data)
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
                        assert not self.chucked
                    break
                index = partial.index(":")
                key = partial[0: index].strip()
                val = partial[index + 1:].strip()
                self.header[key] = val
            if skip_body:
                self.total = self.progressed = 1
                return self.header
            left = temp.read()

            if left:
                if self.file_handle:
                    self.file_handle.write(left)
                else:
                    self.data += left

                self.progressed += len(left)

        else:
            if self.file_handle:
                self.file_handle.write(data)
                self.progressed += len(data)
            else:
                self.data += data
                self.progressed += len(data)


class HTTPCons:
    def __init__(self, debug=False):
        self.host = ''
        self.port = 0
        self.is_debug = debug
        self.connect = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    def https_init(self, host, port):
        context = ssl.SSLContext(ssl.PROTOCOL_TLSv1)
        context.verify_mode = ssl.CERT_REQUIRED
        context.check_hostname = True
        context.load_default_certs()
        self.connect = context.wrap_socket(self.connect, server_hostname=host)
        self.connect.settimeout(105)
        self.connect.connect((host, port))
        self.host = host
        self.port = port

    def http_init(self, host, port):
        self.connect.settimeout(100)
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
        data = """{method} {href} HTTP/1.1
{headers}
"""
        if not headers:
            head = """Host: {}\r\n""".format(self.host)
            head += "User-Agent: HELLFLAME"
        else:
            head = ""
            for i in headers:
                head += "{}: {}\r\n".format(i, headers[i])
            if 'Host' not in headers:
                head += """Host: {}\r\n""".format(self.host)
            if 'User-Agent' not in headers:
                head += "User-Agent: HELLFLAME\r\n"
        if method == 'POST':
            if data and type(data) == str:
                # upload for one time
                head += "Content-Length: {}\r\n\r\n".format(len(post_data))
                head += "{}".format(post_data)
            else:
                raise URLNotComplete(href, 'POST data')
        elif method == 'GET':
            if post_data:
                assert type(post_data) == dict
                if '?' not in href[-1]:
                    href += '?'

                for i in post_data:
                    href += '{}={}&'.format(i, post_data[i])
        # head += "\r\n"
        data = data.format(method=method, href=href, headers=head)
        if self.is_debug:
            print data
        self.connect.sendall(data)

    def __del__(self):
        self.connect.close()


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
