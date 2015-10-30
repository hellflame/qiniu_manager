#!/usr/bin/python
#coding=utf8
from qiniu import Auth, put_file, BucketManager
from os import popen, path
from sys import argv
__author__ = 'linux'

# change to your own directory
current_dir = __file__.replace(__file__.split('/')[-1], '')

if not path.exists(current_dir + 'conf/qiniu.conf'):
    print '''
    config file not found, copy the qiniu.conf.example as the qiniu.conf file please
    [base]
    access_key =
    secret_key =
    space_name =
    '''
    exit(1)


class Qiniu:
    def __init__(self):
        self.handle = ''
        self.config_pos = current_dir + 'conf/qiniu.conf'
        self.config = self.qiniu_conf()
        self.space_name = self.config.get('base', 'space_name')

    def qiniu_conf(self):
        from ConfigParser import ConfigParser
        config = ConfigParser()
        config.read(self.config_pos)
        try:
            self.handle = Auth(config.get('base', 'access_key'), config.get('base', 'secret_key'))
        except ValueError:
            pass
        return config

    def set_conf(self, key, value):
        from ConfigParser import ConfigParser
        config = ConfigParser()
        config.read(self.config_pos)
        config.set('base', key, value)
        fp = open(self.config_pos, 'w')
        config.write(fp)
        fp.close()
        self.qiniu_conf()

    def get_mime_type(self, abs_location):
        from commands import getoutput
        mime_type = getoutput('file -b --mime-type {}'.format(abs_location))
        return mime_type

    def upload(self, abs_location):
        if not path.exists(abs_location):
            print '→_→ {} 不存在'.format(abs_location)
            return False
        key = abs_location.split('/')[-1]
        token = self.handle.upload_token(self.space_name, key)
        mime_type = self.get_mime_type(abs_location)
        ret, info = put_file(up_token=token,
                             key=key,
                             mime_type=mime_type,
                             check_crc=True,
                             file_path=abs_location
                             )
        result = info.exception
        if not result:
            print '上传成功～～～～～～'
            return True
        print '上传失败了诶～～～～发生异常\n{}'.format(result.message)
        return False

    def download(self, file_name):
        from commands import getoutput
        cmd = 'wget http://{}.qiniudn.com/{}'.format(self.space_name, file_name)
        print getoutput(cmd)

    def terminal_print(self, data):
        terminal_width = int(popen('stty size').read().split(' ')[-1])
        for i in data:
            size = i['fsize']
            mark = 0
            refs = ['B', 'KB', 'MB', 'GB', 'TB', 'PB']
            while size > 1024:
                size /= 1024
                mark += 1
            size = "{} {}".format(size, refs[mark])
            left = terminal_width - len(i['key']) - len(size)
            print ' ' * 20 + i['key'] + ' ' * 5 + '-' * (left - 50) + ' ' * 5 + size + ' ' * 20

    def file_list(self):
        handle = BucketManager(self.handle)
        ret, eof, info = handle.list(self.space_name,
                                     limit=10)
        if not ret:
            print ("无法获取列表!!\n请检查网络或配置文件")
            return None
        self.terminal_print(ret['items'])
        while not eof:
            inputs = raw_input('\nnext page? [y/n] ')
            if inputs.lower() == 'n' or inputs.lower() == 'no':
                break
            else:
                ret, eof, info = handle.list(self.space_name,
                                             marker=ret['marker'],
                                             limit=10)
                self.terminal_print(ret.get('items'))

    def file_del(self, file_name):
        handle = BucketManager(self.handle)
        ret, info = handle.delete(self.space_name, file_name)
        if info.status_code == 612:
            print '→_→ {} 不存在诶'.format(file_name)
        elif info.status_code == 200:
            print '{} 删除成功'.format(file_name)
        elif info.connect_failed():
            print "网络连接失败"
        else:
            print '发生未知错误23333'

    def file_state(self, file_name):
        handle = BucketManager(self.handle)
        ret, info = handle.stat(self.space_name, file_name)
        if ret:
            size = ret['fsize']
            mark = 0
            refs = ['B', 'KB', 'MB', 'GB', 'TB', 'PB']
            while size > 1024:
                size /= 1024.0
                mark += 1
            ret['fsize'] = '{} {}'.format(size, refs[mark])
            ret['File Name'] = file_name
            terminal_width = int(popen('stty size').read().split(' ')[-1])
            from time import strftime, localtime
            ret['putTime'] = strftime('%Y-%m-%d', localtime(ret['putTime']/10000000))
            ret['Upload Time'] = ret['putTime']
            ret['Size'] = ret['fsize']
            ret['Type'] = ret['mimeType']
            ret['Hash'] = ret['hash']
            ret.pop('putTime')
            ret.pop('fsize')
            ret.pop('mimeType')
            ret.pop('hash')
            for i in ret:
                length = terminal_width - len(i) - len(ret[i])
                print ' ' * 30 + i + ' ' * 5 + '-' * (length - 70) + ' ' * 5 + ret[i] + ' ' * 30
        else:
            print '空间中没有这个→_→ {} 额'.format(file_name)

    def private_link(self, file_name):
        base_link = "http://{}.qiniudn.com/{}".format(self.space_name, file_name)
        print self.handle.private_download_url(base_link, expires=3600)


def argSeeker(header):
    temp = argv
    for i in temp:
        index = temp.index(i)
        if i == header and len(temp) - 1 > index and not temp[index + 1].startswith("--"):
            return temp[index + 1]
    return False


def main():
    map_desc = {
        '': '输入文件名即开始上传文件',
        '--upload': '选择要上传的文件',
        '--stat': '查看文件状态',
        '--list': '文件列表',
        '--access': '修改access key',
        '--secret': '修改secret key',
        '--space': '修改将要操作的空间名',
        '--help': '帮助',
        '--del': '删除云文件',
        '--download': '下载文件',
        '--private': '获取私有文件链接'
    }

    if len(argv) <= 1 or '--help' in argv or '-h' in argv:
        print '\n*********帮助模式*********\n'
        for i in map_desc:
            print '  ' + i + ' ===> ' + map_desc[i]
        exit(0)
    qiniu = Qiniu()
    if '--access' in argv:
        access = argSeeker('--access')
        if access:
            qiniu.set_conf('access_key', access)
        else:
            print("请输入 access key")
        exit(0)
    if '--secret' in argv:
        secret = argSeeker('--secret')
        if secret:
            qiniu.set_conf('secret_key', secret)
        else:
            print("请输入 secret key")
        exit(0)
    if '--space' in argv:
        space = argSeeker('--space')
        if space:
            qiniu.set_conf('space_name', space)
        else:
            print("请输入 空间名称")
        exit(0)
    if len(argv) == 2 and not argv[1].startswith('--'):
        qiniu.upload(argv[1])
        exit(0)
    if '--upload' in argv:
        qiniu.upload(argSeeker('--upload'))
        exit(0)
    if '--stat' in argv:
        qiniu.file_state(argSeeker('--stat'))
        exit(0)
    if '--list' in argv:
        qiniu.file_list()
        exit(0)
    if '--del' in argv:
        qiniu.file_del(argSeeker('--del'))
        exit(0)
    if '--download' in argv:
        qiniu.download(argSeeker('--download'))
        exit(0)
    if '--private' in argv:
        qiniu.private_link(argSeeker('--private'))
        exit(0)

    print '--help 可以帮助你'

if __name__ == '__main__':
    main()
