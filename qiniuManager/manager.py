# coding=utf8
import os
import sys
import time
import json
import Queue
import random
import sqlite3
import hashlib
import progress
import threading

from qiniu import Auth, BucketManager, config as q_config
from qiniu.http import USER_AGENT
from qiniu.utils import urlsafe_base64_encode

from qiniuManager import http

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
            return function(*args, **kwargs)
        else:
            print "Please Set At Lease one pair of usable access and secret".title()
            return ''
    return access_wrap


def auth(function):
    def auth_ok(self, *args, **kwargs):
        if self.auth:
            return function(*args, **kwargs)
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
    raise IOError


class TimeOut(Exception):
    def __init__(self, when):
        self.when = when

    def __str__(self):
        return "{} TOO SLOW".format(self.when)


class Config:
    def __init__(self):
        self.config_path = os.path.join(os.path.expanduser("~"), '.qiniu.sql')
        self.db = None
        self.cursor = None
        self.API_keys = 'API_keys'
        self.SPACE_ALIAS = 'spaceAlias'
        self.CACHE = 'up_down_cache'
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
                                "downloading INTEGER NOT NULL DEFAULT 0,"
                                "up_to INTEGER NOT NULL DEFAULT 0,"
                                "down_to INTEGER NOT NULL DEFAULT 0,"
                                "stamp INTEGER NOT NULL DEFAULT 0)".format(self.CACHE))
            self.clean_expired_cache()
        except Exception as e:
            print e

    @db_ok
    def clean_cache(self, md5):
        self.cursor.execute("delete from {} WHERE md5 = '{}'".format(self.CACHE, md5))

    @db_ok
    def upset_cache(self, md5, status='uploading', clip=0):
        self.cursor.execute("select md5 from {} WHERE md5 = '{}'".format(self.CACHE, md5))
        result = self.cursor.fetchone()
        if not result:
            sql = "insert into {} ".format(self.CACHE)
            if status == 'uploading':
                sql += "(uploading, up_to, stamp) values (1, {}, {})".format(clip, int(time.time()))
            else:
                sql += "(downloading, down_to, stamp) values (1, {}, {})".format(clip, int(time.time()))
        else:
            sql = "update {} ".format(self.CACHE)
            if status == 'uploading':
                sql += "set uploading = 1, up_to = {}, downloading = 0".format(clip)
            else:
                sql += "set downloading = 1, down_to = {}, uploading = 0".format(clip)
            sql += " where md5 = '{}'".format(result[0])
        self.cursor.execute(sql)

    @db_ok
    def get_cache(self, md5, status='uploading'):
        if status == 'uploading':
            sql = "select uploading, up_to from {} WHERE md5 = '{}'".format(self.CACHE, md5)
        else:
            sql = "select downloading, down_to from {} WHERE md5 = '{}'".format(self.CACHE, md5)
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
        self.cursor.execute("select id from {} WHERE access = '{}'".format(self.API_keys, access))
        result = self.cursor.fetchone()
        if not result:
            self.cursor.execute("insert into {} (access, secret) "
                                "VALUES ('{}', '{}')".format(self.API_keys, access, secret))
        else:
            # TODO: sometimes it's better to update the database, now it is not quite gentle
            self.cursor.execute("delete from {} WHERE id = {}".format(self.API_keys, result[0]))
            self.add_access(access, secret)

    @db_ok
    def remove_access(self, _id=0, access=''):
        sql = "delete from {} ".format(self.API_keys)
        if _id:
            sql += "WHERE id = {}".format(_id)
        elif access:
            sql += "WHERE access = '{}'".format(access)
        self.cursor.execute(sql)

    @db_ok
    def upset_alias(self, space, alias, as_default=True):
        self.cursor.execute("select id from {} WHERE name = '{}'".format(self.SPACE_ALIAS, space))
        result = self.cursor.fetchone()
        if result:
            self.cursor.execute("update {} set alias = '{}', as_default={}"
                                " WHERE id = {}".format(self.SPACE_ALIAS, alias, 1 if as_default else 0, result[0]))
        else:
            self.cursor.execute("insert into {} (name, alias, as_default)"
                                " VALUES ('{}', '{}', {})".format(self.SPACE_ALIAS, space,
                                                                  alias, 1 if as_default else 0))
        self.cursor.execute("update {} set as_default = 0 "
                            "WHERE as_default = 1 AND name != '{}'".format(self.SPACE_ALIAS, space))

    @db_ok
    def set_current_space(self, space):
        if self.get_space_alias(space):
            self.cursor.execute("UPDATE {} SET as_default = 1 WHERE name = '{}'".format(self.SPACE_ALIAS,
                                                                                        space))
            return True
        else:
            return False

    @db_ok
    def get_space_alias(self, space_name):
        self.cursor.execute("select alias from {} WHERE name = '{}'".format(self.SPACE_ALIAS, space_name))
        result = self.cursor.fetchone()
        if result:
            return result[0]
        return ''

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
    def __init__(self):
        self.config = Config()
        self.access, self.secret = self.config.get_one_access()
        self.auth = None
        self.get_auth()
        self.prepared = False
        self.pre_upload_info = None
        self.progressed = 0
        self.total = 0
        self.file_handle = None

        self.data_queue = Queue.Queue(7)
        self.msg_queue = Queue.Queue()
        self.progress_queue = Queue.Queue()
        self.finished_queue = Queue.Queue()
        self.upload_labors = 8
        self.block_status = []

        # API restrict
        self.R_BLOCK_SIZE = 4 * 1024 * 1024

        # labors must finish their first 4M in 100s
        self.UP_TIME_OUT = 100

    def __del__(self):
        if self.file_handle:
            self.file_handle.close()

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

    def __make_url(self, path, file_name='', **kwargs):
        if not os.path.exists(path):
            raise IOError
        host = q_config.get_default('default_up_host')
        url = list(['http://{0}/mkfile/{1}'.format(host, os.stat(path).st_size)])
        # add key
        key = os.path.basename(path)
        url.append('key/{0}'.format(urlsafe_base64_encode(key)))
        # get_mime_type method makes sure the mime-type is not None
        url.append('mimeType/{0}'.format(urlsafe_base64_encode(self.get_mime_type(path))))

        if file_name:
            url.append('fname/{0}'.format(urlsafe_base64_encode(file_name)))
        else:
            url.append('fname/{0}'.format(urlsafe_base64_encode(key)))

        if kwargs:
            for k, v in kwargs.items():
                url.append('{0}/{1}'.format(k, urlsafe_base64_encode(v)))
        url = '/'.join(url)
        # print url
        return url

    @auth
    def __pre_upload(self, path):
        file_name = os.path.basename(path)
        space, alias = self.config.get_default_space()
        token = self.auth.upload_token(space if space else alias, file_name, 7200)
        mime_type = self.get_mime_type(path)
        md5 = get_md5(path)
        offset = self.config.get_cache(md5)
        offset = offset[1] if offset else 0
        self.file_handle = open(path, 'rb')
        self.file_handle.seek(offset)
        self.total = os.stat(path).st_size - offset + 2
        self.pre_upload_info = (file_name, md5, space if space else alias, token, mime_type, offset)

        self.prepared = True

    @auth
    def __data_msg(self):
        """must deploy after __pre_upload keep generating str data for uploading
        used in multi processing
        """
        timeout = 0
        while True:
            self.config.upset_cache(self.pre_upload_info[1], clip=self.file_handle.tell())

            if self.file_handle.tell() == os.stat(self.file_handle.name).st_size:
                for i in range(self.upload_labors):
                    # signal 1 means original file read completed
                    self.msg_queue.put(1)
                break
            if not self.data_queue.full():
                self.data_queue.put(self.file_handle.read(self.R_BLOCK_SIZE))
                timeout = 0
            else:
                # sleep some time to waiting for some upload labors to finish his uploading
                time.sleep(1)
                timeout += 1
                if timeout > self.UP_TIME_OUT:
                    raise TimeOut("UPLOADING")

    def __labor_uploader(self):
        """upload data"""
        while True:
            if not self.data_queue.empty():
                data = self.data_queue.get()
                host = q_config.get_default("default_up_host")
                size = len(data)
                url = 'http://{0}/mkblk/{1}'.format(host, size)
                labor = http.SockFeed(customize=True)
                sends = labor.con.request(url, 'POST',
                                          {'Authorization': 'UpToken {}'.format(self.pre_upload_info[3]),
                                           'User-Agent': USER_AGENT},
                                          data=data,
                                          customize=True)
                labor.socket = labor.con.connect
                self.progress_queue.put(sends)
                while labor.con.progressed < labor.con.total:
                    self.progress_queue.put(labor.con.request(url, 'POST',
                                            {'Authorization': 'UpToken {}'.format(self.pre_upload_info[3]),
                                             'User-Agent': USER_AGENT},
                                          data=data,
                                          customize=True))
                labor.http_response()
                print labor.data
                return
                if labor.http_code // 100 == 5 and labor.http_code != 579 or labor.http_code == 996:
                    # trying to retry
                    self.data_queue.put(data)
                else:
                    self.finished_queue.put(json.loads(labor.data))
            else:
                if not self.msg_queue.empty():
                    msg = self.msg_queue.get()
                    if msg == 1:
                        self.msg_queue.put(0)
                        break
                    else:
                        self.msg_queue.put(msg)
                else:
                    time.sleep(0.1)

    def __finish_clean(self):
        tick = 0
        while True:
            if not self.finished_queue.empty():
                self.block_status.append(self.finished_queue.get())
            else:
                if not self.msg_queue.empty():
                    msg = self.msg_queue.get()
                    if msg == 0:
                        tick += 1
                        if tick == self.upload_labors:
                            print "All Finished Waiting Reduce"
                            self.progress_queue.put(2)
                            break
                    else:
                        self.msg_queue.put(msg)
                else:
                    time.sleep(0.1)

    @progress.bar()
    def __progress_recoder(self):
        """progress recoder"""
        if not self.progress_queue.empty():
            self.progressed += self.progress_queue.get()
        else:
            time.sleep(0.1)

    @auth
    def upload_loop(self):
        data_msg = threading.Thread(target=self.__data_msg)
        progress_recorder = threading.Thread(target=self.__progress_recoder)
        finish = threading.Thread(target=self.__finish_clean)
        labors = []
        for i in range(self.upload_labors):
            labors.append(threading.Thread(target=self.__labor_uploader))

        data_msg.start()
        for i in labors:
            i.start()
        progress_recorder.start()
        finish.start()

        for i in labors:
            i.join()
        finish.join()
        progress_recorder.join()
        data_msg.join()


    @auth
    def upload(self, abs_location):
        if not self.prepared:
            self.__pre_upload(abs_location)
        else:
            key, file_md5, space, token, mime_type, offset = self.pre_upload_info


if __name__ == '__main__':
    # main()
    # q = Auth('hellflame', 'windows')
    # print q.upload_token("asdasd", 'ljklj')
    qiniu = Qiniu()

