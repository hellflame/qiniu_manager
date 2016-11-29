# coding=utf8
import socket
import cStringIO
import progress
import ssl
import time
import random


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
        self.chuck_left_size = 0

        self.file_handle = None

    def __del__(self):
        if self.file_handle:
            self.file_handle.close()

    @progress.bar()
    def http_response(self, file_path='', skip_body=False):
        if file_path and not self.file_handle:
            self.file_handle = open(file_path, 'wb')
            self.title = file_path
        # while True:
        data = self.socket.recv(self.chuck_size)
        temp = cStringIO.StringIO(data)
        if not data:
            self.progressed = self.total = 100
            return self.data

        if not self.head or not self.header:
            self.head = temp.readline()
            self.http_code = int(self.head.split(" ")[1])
            while True:
                partial = temp.readline()
                if not partial or partial == '\r\n':
                    if self.header.get("Content-Length"):
                        self.total = int(self.header.get("Content-Length"))
                    elif self.header.get("Transfer-Encoding") == 'chunked':
                        self.chucked = True
                        self.total = 100
                    break
                index = partial.index(":")
                key = partial[0: index].strip()
                val = partial[index + 1:].strip()
                self.header[key] = val
            if skip_body:
                self.total = self.progressed = 1
                return self.header
            left = temp.read()
            if self.chucked and left:
                left_io = cStringIO.StringIO(left)
                size = int(left_io.readline().strip(), 16)
                left = left_io.read(size)
                read_still = True
                while left and read_still:
                    if self.file_handle:
                        self.file_handle.write(left)
                    else:
                        self.data += left
                    next_line = left_io.readline()
                    if next_line and not next_line == '\r\n':
                        size = int(next_line.strip(), 16)
                        if size == 0:
                            self.total = self.progressed = 100
                            return
                        left = left_io.read(size)
                        if len(left) < size:
                            read_still = False
                    else:
                        if len(left) < size:
                            read_still = False
                if left:
                    self.chuck_left_size = len(left)
                    if self.file_handle:
                        self.file_handle.write(left)
                    else:
                        self.data += left

            elif left:
                if self.file_handle:
                    self.file_handle.write(left)
                else:
                    self.data += left

                self.progressed += len(left)

        else:
            if self.chucked:
                if not self.progressed == 100:
                    self.progressed = random.randint(self.progressed, 98)
                data = cStringIO.StringIO(data)
                if self.chuck_left_size:
                    last_left = data.read(self.chuck_left_size)
                    if self.file_handle:
                        self.file_handle.write(last_left)
                    else:
                        self.data += last_left

                chuck_size = int(data.readline().strip(), 16)
                if chuck_size == 0:
                    self.progressed = self.total
                    return
                left = data.read(chuck_size)
                read_still = True
                while left and read_still:
                    if self.file_handle:
                        self.file_handle.write(left)
                    else:
                        self.data += left
                    next_line = data.readline()
                    if next_line and not next_line == '\r\n':
                        size = int(next_line.strip(), 16)
                        if size == 0:
                            self.total = self.progressed = 100
                            return
                        left = data.read(size)
                        if len(left) < size:
                            read_still = False
                    else:
                        if len(left) < chuck_size:
                            read_still = False

                self.chuck_left_size = len(left) + 2
                if left:
                    if self.file_handle:
                        self.file_handle.write(left)
                    else:
                        self.data += left

            else:
                if self.last_stamp:
                    temp = self.progressed / (time.time() - self.last_stamp)
                    if temp > self.top_speed:
                        self.top_speed = temp
                if self.file_handle:
                    self.file_handle.write(data)
                    self.progressed += len(data)
                else:
                    self.data += data
                    self.progressed += len(data)


class HTTPCons:
    def __init__(self):
        self.host = ''
        self.port = 0
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
            head += "User-Agent: Chrome/52.0.2743.116 Safari/537.36"
        else:
            head = ""
            for i in headers:
                head += "{}: {}\r\n".format(i, headers[i])
            if 'Host' not in headers:
                head += """Host: {}\r\n""".format(self.host)
            if 'User-Agent' not in headers:
                head += "User-Agent: Chrome/52.0.2743.116 Safari/537.36\r\n"
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
        head += "\r\n"
        data = data.format(method=method, href=href, headers=head)
        # print data, 'EOL'
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


