# coding=utf8
"""
    HTTP/HTTPS Connection Basic Handler with ProgressBar support ~
"""
import socket
import cStringIO
import progress
import ssl
import time
import os


class SockFeed:
    def __init__(self, url='', method='GET', headers=None, data=None, chuck=1024, customize=False):
        self.con = HTTPCons()
        if not customize:
            self.con.request(url, method, headers, data, customize)
            self.socket = self.con.connect
        else:
            # export HTTPCons.connect by yourself after init
            self.socket = None
        self.buffer = None
        self.chuck_size = chuck
        self.head = ''
        self.header = {}
        self.http_code = 0
        self.data = ''
        self.progressed = 0
        self.total = 0
        self.disable_progress = False
        self.start_stamp = 0
        self.top_speed = 0
        self.avg_speed = 0

        self.file_handle = None

    def __del__(self):
        if self.file_handle:
            self.file_handle.close()

    @progress.bar()
    def http_response(self, file_path=''):
        if file_path and not self.file_handle:
            # print "Receiving"
            self.file_handle = open(file_path, 'wb')
            self.start_stamp = time.time()
        data = self.socket.recv(self.chuck_size)
        if not data:
            return self.data
        left = ''
        if not self.head or not self.header:
            # TODO: localhost Flask engine tests weird if chuck size too huge =.=
            temp = data
            while '\r\n\r\n' not in temp:
                temp += self.socket.recv(self.chuck_size)
            temp = cStringIO.StringIO(temp)
            self.head = temp.readline()
            self.http_code = int(self.head.split(" ")[1])
            while True:
                partial = temp.readline()
                if not partial or partial == '\r\n':
                    if self.header.get("Content-Length"):
                        self.total = int(self.header.get("Content-Length"))
                    break
                index = partial.index(":")
                key = partial[0: index].strip()
                val = partial[index + 1:].strip()
                self.header[key] = val
            if not self.http_code == 200:
                print "HTTP CODE {}".format(self.http_code)
                self.total = self.progressed = 1
                return
            left = temp.read()

        if self.start_stamp:
            # top_speed is some kind of average speed ...
            self.avg_speed = self.progressed / (time.time() - self.start_stamp)
            if self.avg_speed > self.top_speed:
                self.top_speed = self.avg_speed
        if not self.total:
            # TODO: chucked encoding unsettled
            print "unable to handle now"
            self.data = ''
            return

        if self.file_handle:
            if left:
                self.file_handle.write(left)
                self.progressed += len(left)
            else:
                self.file_handle.write(data)
                self.progressed += len(data)
        else:
            if left:
                self.data += left
                self.progressed += len(left)
            else:
                self.data += data
                self.progressed += len(data)


class HTTPCons:
    def __init__(self):
        self.host = ''
        self.port = 0
        self.progressed = 0
        self.total = 0
        self.disable_progress = False
        self.chuck = 64 * 1024
        self.file_handle = None
        self.str_cache = None
        self.customized = False
        self.basic_done = False
        self.start_stamp = 0
        self.avg_speed = 0
        self.top_speed = 0
        self.connect = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    def https_init(self, host, port):
        context = ssl.SSLContext(ssl.PROTOCOL_TLSv1_2)
        context.verify_mode = ssl.CERT_REQUIRED
        context.check_hostname = True
        context.load_default_certs()
        self.connect = context.wrap_socket(self.connect, server_hostname=host)
        self.connect.settimeout(5)
        self.connect.connect((host, port))
        self.host = host
        self.port = port

    def http_init(self, host, port):
        self.connect.settimeout(5)
        self.connect.connect((host, port))
        self.host = host
        self.port = port

    def request(self, url, method='GET', headers=None, data=None, customize=False):
        if not self.customized:
            if '//' not in url:
                raise URLNotComplete(url, 'url protocol')
            index = url.index('//')
            ishttps = url[0: index - 1].lower() == 'https'
            host_url = url[index + 2:]
            port = None
            if ':' in host_url:
                split = host_url.split(":")
                host = split[0]
                port = int(split[1].split("/")[0])
                url = '/' + '/'.join(split[1].split("/")[1:])
            else:
                if '/' not in host_url:
                    host = host_url
                    url = '/'
                else:
                    index = host_url.index('/')
                    host = host_url[0: index]
                    url = host_url[index:]

            if ishttps:
                if not port:
                    port = 443
                self.https_init(host, port)
            else:
                if not port:
                    port = 80
                self.http_init(host, port)
        if customize:
            self.customized = True
            return self.send_piece(url, method, headers, data)
        self.__send(url, method, headers, data)

    @progress.bar()
    def __send(self, href, method='GET', headers=None, post_data=None):
        self.send_piece(href, method, headers, post_data)

    def send_piece(self, href, method='GET', headers=None, post_data=None):
        """watch this method if you don't want the progress bar to handle the piece"""
        if not self.basic_done:
            # print "Uploading"
            self.basic_sender(href, method, headers, post_data)
            self.start_stamp = time.time()
        if method == 'POST' and isinstance(post_data, file):
            if not self.file_handle:
                self.file_handle = post_data
                self.total = os.stat(post_data.name).st_size
            data = self.file_handle.read(self.chuck)
            self.connect.send(data)
            self.progressed += len(data)
        elif method == 'POST' and len(post_data) > self.chuck:
            if not self.str_cache:
                self.str_cache = cStringIO.StringIO(post_data)
                self.total = len(post_data)
            data = self.str_cache.read(self.chuck)
            self.connect.send(data)
            self.progressed += len(data)
            return len(data)
        else:
            self.disable_progress = True

    def basic_sender(self, href, method='GET', headers=None, post_data=None):
        data = "{method} {href} HTTP/1.1\r\n{headers}\r\n"
        if not headers:
            head = "Host: {}\r\n".format(self.host)
            head += "User-Agent: Chrome/52.0.2743.116 Safari/537.36"
        else:
            head = ""
            if 'Host' not in headers:
                head += "Host: {}\r\n".format(self.host)
            if 'User-Agent' not in headers:
                head += "User-Agent: Chrome/52.0.2743.116 Safari/537.36\r\n"

            for i in headers:
                head += "{}: {}\r\n".format(i, headers[i])
        if method == 'POST':
            if post_data and type(post_data) == str and len(post_data) <= self.chuck:
                head += "Content-Length: {}\r\n".format(len(post_data))
                head += "{}".format(post_data)
            elif post_data and type(post_data) == str and len(post_data) > self.chuck:
                head += "Content-Length: {}\r\n".format(len(post_data))
            elif post_data and isinstance(post_data, file):
                head += "Content-Length: {}\r\n".format(os.stat(post_data.name).st_size)
            else:
                raise URLNotComplete(href, 'POST data')
        else:
            head += "\r\n"
        data = data.format(method=method, href=href, headers=head)
        # print data, '<==EOL'
        self.connect.sendall(data)
        self.basic_done = True

    def __del__(self):
        self.connect.close()


def unit_change(target):
    unit_list = ('B', 'KB', 'MB', 'GB', 'TB')
    index = 0
    while target > 1024:
        index += 1
        target /= 1024
    return "{} {}".format(round(target, 2), unit_list[index])


class URLNotComplete(Exception):
    def __init__(self, url, lack):
        self.url = url
        self.lack = lack

    def __str__(self):
        return "URL: {} missing {}"


class RequestFail(Exception):
    def __init__(self, code):
        self.status_code = code

    def __str__(self):
        return "Request Failed with status code {}".format(self.status_code)


if __name__ == '__main__':
    """feed = SockFeed('http://whatever.qiniudn.com/VPSBackup.tar.bz2', chuck=4096)"""
    with open("/home/hellflame/WallPaper/gamersky_08origin_15.jpg", 'rb') as file_handle:

        # Seemed quit boring
        feed = SockFeed(customize=True)
        data = file_handle.read()
        sends = feed.con.request("http://localhost:5000",
                                 method='POST',
                                 headers={'Content-Type': 'application/x-www-form-urlencoded'},
                                 data=data,
                                 customize=True)
        feed.socket = feed.con.connect
        while feed.con.progressed < feed.con.total:
            sends += feed.con.request("http://localhost:5000",
                                      method='POST',
                                      data=data,
                                      headers={'Content-Type': 'application/x-www-form-urlencoded'},
                                      customize=True)
        print sends, feed.con.progressed
        """
        feed = SockFeed('http://localhost:5000', method="POST",
                        headers={'Content-Type': 'application/x-www-form-urlencoded'},
                        data=file_handle)
        """
        feed.http_response(file_path="well.jpg")
        # print feed.data
        print feed.http_code, unit_change(feed.avg_speed) + '/s'


