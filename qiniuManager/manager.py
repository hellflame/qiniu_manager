# coding=utf8
import os
import sys
import time
import json
import random
import urllib
import sqlite3
import hashlib
import progress

from qiniu import Auth, __version__ as sdk_version
from qiniu.utils import urlsafe_base64_encode

import http

reload(sys)
sys.setdefaultencoding('utf8')


def db_ok(function):
    def func_wrapper(self, *args, **kwargs):
        if self.db and self.cursor:
            return function(self, *args, **kwargs)
        else:
            print "Failed To Access {}, please check you authority".format(self.config_path).title()
            return ''
    return func_wrapper


def access_ok(function):
    def access_wrap(self, *args, **kwargs):
        if self.access and self.secret:
            return function(self, *args, **kwargs)
        else:
            print "Please Set At Lease one pair of usable access and secret".title()
            return ''
    return access_wrap


def auth(function):
    def auth_ok(self, *args, **kwargs):
        if self.auth:
            return function(self, *args, **kwargs)
        else:
            self.get_auth()
            if not self.auth:
                print "failed to initialize the authorization".title()
                return ''
            else:
                return function(*args, **kwargs)
    return auth_ok


def get_md5(path):
    if os.path.exists(path):
        hash_md5 = hashlib.md5()
        with open(path, 'rb') as handle:
            for chuck in iter(lambda: handle.read(4096), b""):
                hash_md5.update(chuck)
        return hash_md5.hexdigest()
    else:
        raise IOError


class Config:
    def __init__(self):
        self.config_path = os.path.join(os.path.expanduser("~"), '.qiniu.sql')
        self.db = None
        self.cursor = None
        self.API_keys = 'API_keys'
        self.SPACE_ALIAS = 'spaceAlias'
        self.CACHE = 'upload_cache'
        self.init_db()

    def init_db(self):
        try:
            self.db = sqlite3.connect(self.config_path)
            self.cursor = self.db.cursor()
            self.cursor.execute("CREATE TABLE IF NOT EXISTS {} ("
                                "id INTEGER PRIMARY KEY AUTOINCREMENT,"
                                "access VARCHAR(64) NOT NULL UNIQUE,"
                                "secret VARCHAR(64) NOT NULL,"
                                "discard INTEGER NOT NULL DEFAULT 0)".format(self.API_keys))
            self.cursor.execute("CREATE TABLE IF NOT EXISTS {} ("
                                "id INTEGER PRIMARY KEY AUTOINCREMENT,"
                                "name VARCHAR(50) NOT NULL DEFAULT '',"
                                "alias VARCHAR(50) NOT NULL DEFAULT '',"
                                "as_default INTEGER NOT NULL DEFAULT 0)".format(self.SPACE_ALIAS))
            # upload or download cache
            self.cursor.execute("CREATE TABLE IF NOT EXISTS {} ("
                                "md5 VARCHAR(32) NOT NULL UNIQUE,"
                                "uploading INTEGER NOT NULL DEFAULT 0,"
                                "up_to INTEGER NOT NULL DEFAULT 0,"
                                "stamp INTEGER NOT NULL DEFAULT 0)".format(self.CACHE))
            self.clean_expired_cache()
        except Exception as e:
            print e

    @db_ok
    def clean_cache(self, md5):
        self.cursor.execute("delete from {} WHERE md5 = '{}'".format(self.CACHE, md5))

    @db_ok
    def clean_all_cache(self):
        self.cursor.execute("delete from {}".format(self.CACHE))

    @db_ok
    def upset_cache(self, md5, clip=0):
        self.cursor.execute("select md5 from {} WHERE md5 = '{}'".format(self.CACHE, md5))
        result = self.cursor.fetchone()
        if not result:
            sql = "insert into {} ".format(self.CACHE)
            sql += "(md5, uploading, up_to, stamp) values ('{}',1, {}, {})".format(md5, clip, int(time.time()))
        else:
            sql = "update {} ".format(self.CACHE)
            sql += "set uploading = 1, up_to = {}".format(clip)
            sql += " where md5 = '{}'".format(result[0])
        self.cursor.execute(sql)

    @db_ok
    def get_cache(self, md5):
        sql = "select uploading, up_to from {} WHERE md5 = '{}'".format(self.CACHE, md5)
        self.cursor.execute(sql)
        result = self.cursor.fetchone()
        if not result:
            return None
        return result

    @db_ok
    def clean_expired_cache(self, expire=86400):
        """clean unsettled files, uploading or downloading.
        files left from yesterday will be regard as waste as default"""
        self.cursor.execute("delete from {} WHERE stamp < {}".format(self.CACHE, int(time.time()) - expire))

    @db_ok
    def get_one_access(self):
        self.cursor.execute("select access, secret from {} WHERE discard = 0".format(self.API_keys))
        result = self.cursor.fetchall()
        if not result:
            return '', ''
        return random.choice(result)

    @db_ok
    def access_list(self, include_discard=True):
        sql = "select * from {} ".format(self.API_keys)
        if not include_discard:
            sql += "where discard = 0"
        self.cursor.execute(sql)
        result = self.cursor.fetchall()
        if not result:
            return None
        return result

    @db_ok
    def add_access(self, access, secret):
        """Though two pair of key pair is allowed, but I hate to operate on this"""
        self.cursor.execute("delete from {}".format(self.API_keys))
        self.cursor.execute("insert into {} (access, secret) "
                            "VALUES ('{}', '{}')".format(self.API_keys, access, secret))
    """
    @db_ok
    def remove_access(self, _id=0, access=''):
        sql = "delete from {} ".format(self.API_keys)
        if _id:
            sql += "WHERE id = {}".format(_id)
        elif access:
            sql += "WHERE access = '{}'".format(access)
        self.cursor.execute(sql)
    """

    @db_ok
    def set_space(self, space, alias=''):
        self.cursor.execute("update {} set as_default = 0".format(self.SPACE_ALIAS))
        self.cursor.execute("select id from {} WHERE name = '{}'".format(self.SPACE_ALIAS, space))
        result = self.cursor.fetchone()
        if result:
            if alias:
                self.cursor.execute("update {} set alias = '{}', as_default=1"
                                    " WHERE id = {}".format(self.SPACE_ALIAS, alias, result[0]))
            else:
                self.cursor.execute("update {} set as_default=1 WHERE id = {}".format(self.SPACE_ALIAS,
                                                                                      result[0]))
        else:
            self.cursor.execute("insert into {} (name, alias, as_default)"
                                " VALUES ('{}', '{}', 1)".format(self.SPACE_ALIAS, space, alias))
        return True

    @db_ok
    def get_space(self, space_name):
        self.cursor.execute("select name, alias from {} WHERE name = '{}'".format(self.SPACE_ALIAS, space_name))
        result = self.cursor.fetchone()
        if result:
            return result
        return '', ''

    @db_ok
    def get_space_list(self):
        self.cursor.execute("select name, alias from {}".format(self.SPACE_ALIAS))
        return self.cursor.fetchall()

    @db_ok
    def get_default_space(self):
        self.cursor.execute("select name, alias from {} WHERE as_default = 1".format(self.SPACE_ALIAS))
        result = self.cursor.fetchone()
        if result:
            return result
        return '', ''

    def __del__(self):
        if self.db:
            self.db.commit()
            self.db.close()


class Qiniu:
    """Single Line"""
    def __init__(self):
        self.config = Config()
        self.access, self.secret = self.config.get_one_access()
        self.auth = None

        self.prepared = False
        self.pre_upload_info = None
        self.progressed = 0
        self.total = 0
        self.title = ''
        self.file_handle = None
        self.block_status = []

        self.start_stamp = 0

        self.state = False
        self.avg_speed = ''

        # API restrict
        self.R_BLOCK_SIZE = 4 * 1024 * 1024
        self.list_host = "http://rsf.qbox.me"
        self.manager_host = 'http://rs.qbox.me'
        self.get_auth()

    def __del__(self):
        if self.file_handle:
            self.file_handle.close()

    @auth
    def regular_download_link(self, target, space=None):
        if not space:
            space, alias = self.config.get_default_space()
        else:
            space, alias = self.config.get_space(space)

        if alias:
            host = "http://{}".format(alias)
        else:
            host = "http://{}.qiniudn.com".format(space)
        link = "{}/{}".format(host, urllib.quote(target))
        return link

    @auth
    def private_download_link(self, target, space=None):
        link = self.regular_download_link(target, space)
        private_link = self.auth.private_download_url(link, expires=3600)
        return private_link

    @auth
    def download(self, target, space=None):
        link = self.private_download_link(target, space)
        downloader = http.HTTPCons()
        downloader.request(link)
        feed = http.SockFeed(downloader, 5 * 1024 * 1024)
        start = time.time()
        feed.http_response(target)
        end = time.time()
        size = int(feed.header.get('Content-Length', 1))
        print("\033[01;31m{}\033[00m downloaded @speed \033[01;32m{}/s\033[00m"
              .format(target,
                      http.unit_change(size / (end - start))))

    @auth
    def rename(self, target, to_target, space=None):
        """I don't want to move files between buckets,
        so you can not move file to different bucket by default"""
        if not space:
            space = self.config.get_default_space()[0]
        manager_rename = http.HTTPCons()
        url = self.manager_host + '/move/{}/{}/force/false'.format(
            urlsafe_base64_encode("{}:{}".format(space, target)),
            urlsafe_base64_encode("{}:{}".format(space, to_target))
        )
        manager_rename.request(url,
                               headers={'Authorization': 'QBox {}'.format(self.auth.token_of_request(url))})
        feed = http.SockFeed(manager_rename)
        feed.disable_progress = True
        feed.http_response()
        data = feed.data
        if 'error' in data:
            data = json.loads(data)
            print("Error Occur: \033[01;31m{}\033[00m".format(data['error']))
        else:
            print("\033[01;31m{}\033[00m now RENAME as \033[01;32m{}\033[00m".format(target, to_target))

    @auth
    def remove(self, target, space=None):
        if not space:
            space = self.config.get_default_space()[0]
        manager_remove = http.HTTPCons()
        url = self.manager_host + '/delete/{}'.format(urlsafe_base64_encode("{}:{}".format(space, target)))
        manager_remove.request(url,
                               headers={'Authorization': 'QBox {}'.format(self.auth.token_of_request(url))})
        feed = http.SockFeed(manager_remove)
        feed.disable_progress = True
        feed.http_response()
        data = feed.data
        if 'error' in data:
            data = json.loads(data)
            print("Error Occur: \033[01;31m{}\033[00m".format(data['error']))
        else:
            print("\033[01;31m{}\033[00m DELETED from \033[01;32m{}\033[00m".format(target, space))

    @auth
    def check(self, target, space=None):
        if not space:
            space = self.config.get_default_space()[0]
        manager_check = http.HTTPCons()
        url = self.manager_host + '/stat/{}'.format(urlsafe_base64_encode("{}:{}".format(space, target)))
        manager_check.request(url,
                              headers={'Authorization': 'QBox {}'.format(self.auth.token_of_request(url))})
        feed = http.SockFeed(manager_check)
        feed.disable_progress = True
        feed.http_response()
        data = json.loads(feed.data)
        if 'error' in data:
            print("Error Occur: \033[01;31m{}\033[00m".format(data['error']))
        else:
            print("  {}  {}  {}".format('Filename', '·' * (30 - len('filename')), target))
            print("  {}  {}  {}".format('Size', '·' * (30 - len('size')), http.unit_change(data['fsize'])))
            print("  {}  {}  {}".format('MimeType',  '·' * (30 - len('MimeType')), data['mimeType']))
            print("  {}  {}  {}".format('Date', '·' * (30 - len('date')),
                                        time.strftime('%Y-%m-%d %H:%M:%S',
                                                      time.localtime(data['putTime']/10000000))))

    @auth
    def list(self, space=None):
        if not space:
            space = self.config.get_default_space()[0]
        manager_list = http.HTTPCons()
        url = self.list_host + '/list?bucket={}'.format(space)
        manager_list.request(url,
                             headers={'Authorization': 'QBox {}'.format(self.auth.token_of_request(url))})
        feed = http.SockFeed(manager_list, 10 * 1024)
        feed.http_response()
        data = json.loads(feed.data)
        if 'error' in data:
            print("Error Occur: \033[01;31m{}\033[00m".format(data['error']))
        else:
            if 'items' in data:
                total_size = 0
                for i in sorted(data['items'], key=lambda x: x['putTime'], reverse=True):
                    print("  {}  {}  {}".format(i['key'], '·' * (30 - len(i['key'])), http.unit_change(i['fsize'])))
                    total_size += i['fsize']
                print("\n  \033[01;31m{}\033[00m  \033[01;32m{}\033[00m  \033[01;31m{}\033[00m".format(
                    'Total',
                    '·' * (30 - len('total')),
                    http.unit_change(total_size)))

    @access_ok
    def get_auth(self):
        try:
            self.auth = Auth(self.access, self.secret)
        except:
            self.auth = None

    @staticmethod
    def get_mime_type(abs_path):
        try:
            return os.popen("file -b --mime-type {}".format(abs_path)).read()
        except Exception:
            return 'application/octet-stream'

    def __make_url(self, path, **kwargs):
        url = list(['{0}/mkfile/{1}'.format(self.pre_upload_info[-1], os.stat(path).st_size)])
        # add key
        key = os.path.basename(path)
        url.append('key/{0}'.format(urlsafe_base64_encode(key)))
        # get_mime_type method makes sure the mime-type is not None
        # url.append('mimeType/{0}'.format(urlsafe_base64_encode(self.get_mime_type(path))))
        url.append('fname/{0}'.format(urlsafe_base64_encode(key)))

        if kwargs:
            for k, v in kwargs.items():
                url.append('{0}/{1}'.format(k, urlsafe_base64_encode(v)))
        url = '/'.join(url)
        # print url
        return url

    @auth
    def __pre_upload(self, path, space=None):
        file_name = os.path.basename(path)
        if space:
            token = self.auth.upload_token(space, file_name, 7200)
        else:
            space, alias = self.config.get_default_space()
            token = self.auth.upload_token(space, file_name, 7200)
        # mime_type = self.get_mime_type(path)
        md5 = get_md5(path)
        self.file_handle = open(path, 'rb')
        self.title = file_name
        self.total = os.stat(path).st_size + 2
        self.progressed = 0
        self.pre_upload_info = (file_name, md5, space,
                                token, 0, 'http://up.qiniu.com')
        self.prepared = True

    @progress.bar(100)
    def upload(self, abs_path, space=None):
        """upload data"""
        if not self.prepared:
            self.__pre_upload(abs_path, space)
            self.start_stamp = time.time()
        data = self.file_handle.read(self.R_BLOCK_SIZE)
        if not data:
            file_url = self.__make_url(abs_path)
            mkfile = http.HTTPCons()
            mkfile.request(file_url, 'POST',
                           {'Authorization': 'UpToken {}'.format(self.pre_upload_info[3])},
                           data=','.join(self.block_status))
            feed = http.SockFeed(mkfile)
            feed.http_response()
            data = json.loads(feed.data)
            # print data
            avg_speed = http.unit_change(self.progressed / (time.time() - self.start_stamp))
            self.progressed = self.total = 1
            if data.get('key', '') == self.pre_upload_info[0]:
                self.config.clean_cache(self.pre_upload_info[1])
                self.state = True
                self.avg_speed = '{}/s'.format(avg_speed)
                return True
            return False

        size = len(data)
        url = '{0}/mkblk/{1}'.format(self.pre_upload_info[-1], size)
        labor = http.HTTPCons()
        labor.request(url, 'POST',
                      {'Authorization': 'UpToken {}'.format(self.pre_upload_info[3])},
                      data=data)
        feed = http.SockFeed(labor)
        feed.http_response()
        # print feed.data
        self.block_status.append(json.loads(feed.data).get('ctx'))
        self.progressed += size


