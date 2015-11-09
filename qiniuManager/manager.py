#!/usr/bin/python
# coding=utf8
from qiniu import Auth, put_file, BucketManager
from os import popen, path, mkdir, remove
from sys import argv
from json import loads, dumps
import sys
from commands import getstatusoutput
from ConfigParser import ConfigParser, NoOptionError
reload(sys)
sys.setdefaultencoding('utf8')
__author__ = 'linux'
__version__ = "0.9.17"

# change to your own directory
home = popen("echo $HOME").read().strip()
conf_path = home + '/.qiniuManager/qiniu.conf'

if not path.exists(conf_path):
    print '''
    config file not found, I will create the configuration file @ {}

    →_→ However YOU HAVE TO CONFIG THE FILE YOURSELF BY DEPLOY LIKE
    qiniu --access "access key"
    qiniu --secret "secret key"
    qiniu --space "space name"

    above all three are essential
    '''.format(conf_path)
    if not path.exists(home + '/.qiniuManager'):
        mkdir(home + '/.qiniuManager')
    with open(conf_path, 'w') as handle:
        handle.write("[base]\naccess_key = \nsecret_key = \nspace_name = \nspace_list = {}\n")
    exit(1)


class Qiniu:
    def __init__(self):
        self.handle = ''
        self.config_pos = conf_path
        self.config = self.qiniu_conf()
        self.space_name = self.config.get('base', 'space_name')
        self.subdom = self.get_sub_domain()

    def qiniu_conf(self):
        config = ConfigParser()
        config.read(self.config_pos)
        try:
            self.handle = Auth(config.get('base', 'access_key'), config.get('base', 'secret_key'))
        except ValueError:
            pass
        return config

    def get_sub_domain(self):
        try:
            domain_list = self.config.get('base', 'space_dict')
        except NoOptionError:
            return ''

        if self.space_name:
            domain_list = loads(domain_list)
            return domain_list.get(self.space_name, '')
        return ""

    def set_conf(self, key, value):

        config = self.config
        config.set('base', key, value)
        fp = open(self.config_pos, 'w')
        config.write(fp)
        fp.close()
        self.qiniu_conf()

    def get_conf(self, key):
        config = self.config
        try:
            return config.get('base', key)
        except NoOptionError:
            return "未配置"

    def set_private_space_name(self, private_name):
        if not self.space_name:
            return "请先配置当前空间名"
        config = self.config

        try:
            space_dict = config.get('base', 'space_dict')
        except NoOptionError:
            with open(self.config_pos, 'a') as handle:
                handle.write("space_dict = \n")
            config.read(self.config_pos)
            space_dict = config.get('base', 'space_dict')

        if not space_dict:
            space_dict = '{}'
        space_dict = loads(space_dict)
        space_dict[self.space_name] = private_name
        config.set('base', 'space_dict', dumps(space_dict))
        with open(self.config_pos, 'w') as handle:
            config.write(handle)
        print("默认域名设置成功 \n{}.qiniudn.com == {}".format(self.space_name, private_name))

    def get_private_space_name(self):
        if not self.space_name:
            return "请先配置当前空间名"
        config = self.config
        try:
            result = config.get('base', 'space_dict')
            return loads(result).get(self.space_name, '当前空间 {} 未配置默认域名'.format(self.space_name))
        except NoOptionError:
            return "请先设置默认域名"

    def get_mime_type(self, abs_location):
        from commands import getoutput
        mime_type = getoutput('file -b --mime-type {}'.format(abs_location))
        return mime_type

    def upload(self, abs_location):
        if not path.exists(abs_location):
            print ('→_→ {} 不存在'.format(abs_location))
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

    def download(self, file_name, link=False):
        if not self.file_exist(file_name):
            print('空间中没有这个→_→ {} 额'.format(file_name))
            return False
        if self.subdom:
            base_link = "http://{}/{}".format(self.subdom, file_name)
        else:
            base_link = "http://{}.qiniudn.com/{}".format(self.space_name, file_name)
        if link:
            print("以下为下载链接:")
            print(base_link)
            return base_link
        cmd = "curl '{}' -o {}".format(base_link, file_name)
        print("Downloading {} . . .".format(file_name))
        result = getstatusoutput(cmd)
        if not result[0] == 0:
            cmd = "wget '{}' -O {} -q".format(base_link, file_name)
            result = getstatusoutput(cmd)
            # print(cmd)
            if result[0] == 0:
                print("Download success !")
            else:
                print("下载失败\n检查是否为私有空间文件以及网络连接 以下是下载链接:\n\n{}\n".format(base_link))
                if path.exists(file_name):
                    remove("{}".format(file_name))
        else:
            print("Download success !")

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
            sider = int(terminal_width * 0.15)
            internal = int(sider / 4)
            # print(sider)
            print ' ' * sider + \
                  i['key'] +\
                  ' ' * internal +\
                  '-' * (left - int(terminal_width * 0.4)) + \
                  ' ' * internal + \
                  size + \
                  ' ' * sider

    def file_list(self):
        handle = BucketManager(self.handle)
        ret, eof, info = handle.list(self.space_name,
                                     limit=10)
        if not ret:
            print ("无法获取列表!!\n请检查网络或配置文件")
            return None
        self.terminal_print(ret['items'])
        while not eof:
            inputs = raw_input('\nNext? 否[q or n] ')
            if 'n' in inputs.lower() or 'q' in inputs.lower():
                break
            else:
                ret, eof, info = handle.list(self.space_name,
                                             marker=ret['marker'],
                                             limit=10)
                if ret:
                    self.terminal_print(ret.get('items'))
                else:
                    print("\t暂时无法获取当前列表！！")

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

    def file_exist(self, file_name):
        handle = BucketManager(self.handle)
        ret, info = handle.stat(self.space_name, file_name)
        if ret:
            return True
        else:
            return False

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

    def private_link(self, file_name, link=False):
        if not self.file_exist(file_name):
            print('空间中没有这个→_→ {} 额'.format(file_name))
            return False
        if not self.subdom:
            print("私有链接请设置默认域名")
            return None

        base_link = "http://{}/{}".format(self.subdom, file_name)
        target = self.handle.private_download_url(base_link, expires=3600)

        if link:
            print("以下为文件私有链接:")
            print(target)
            return target

        curl_target = "curl '{}' -o {}".format(target, file_name)
        print("Downloading {} . . .".format(file_name))

        result = getstatusoutput(curl_target)
        if not result[0] == 0:
            wget_target = "wget '{}' -O {} -q ".format(target, file_name)
            result = getstatusoutput(wget_target)
            if not result[0] == 0:
                print("由于未找到 wget 和 curl，以下为目标链接:\n{}\n".format(target))
                if path.exists(file_name):
                    remove("{}".format(file_name))
        else:
            print("Download success !")


def argSeeker(header):
    temp = argv
    for i in temp:
        index = temp.index(i)
        if i == header and len(temp) - 1 > index and not temp[index + 1].startswith("--"):
            return temp[index + 1]
    return False


def main():
    map_desc = {
        '': "输入文件名即开始上传文件, 文件名请勿以 '--' 开头",
        '--upload': '选择要上传的文件',
        '--stat': '查看文件状态',
        '--list': '文件列表',
        '--access': '修改或查看access key',
        '--secret': '修改或查看secret key',
        '--space': '修改或查看当前空间名',
        '--help': '帮助',
        '--del': '删除云文件',
        '--download': '下载文件',
        '--private': '下载私有文件(若无法下载则返回下载链接)',
        '--subdom': '设置或查看当前空间默认域名(7xiy1.com1.z0.glb.clouddn.com)',
        '--link': '返回下载文件的下载链接',
        '--plink': '返回私有空间文件下载链接',
        '--version': '当前版本号'
    }

    short = {
        '--upload': '-u',
        '--stat': '-s',
        '--list': '-l',
        '--access': '-A',
        '--secret': '-S',
        '--space': '-P',
        '--help': '-h',
        '--del': '-e',
        '--download': '-d',
        '--private': '-p',
        '--subdom': '-b',
        '--link': '-k',
        '--plink': '-pk',
        '--version': '-v'
    }

    if len(argv) <= 1 or '--help' in argv or '-h' in argv:
        print '\n*********帮助模式*********\n'
        deploy_ex = "  deploy like this\n\t" \
                    "qiniu your.file\n\t" \
                    "qiniu --access 'your access key'\n\t" \
                    "qiniu --secret 'your secret key'\n\t" \
                    "qiniu --space 'space name'\n"
        print(deploy_ex)
        for i in map_desc:
            print '  ' + i + '\t' + map_desc[i]
        exit(0)
    qiniu = Qiniu()
    if '--access' in argv:
        access = argSeeker('--access')
        if access:
            qiniu.set_conf('access_key', access)
        else:
            print("当前 access key")
            print(qiniu.get_conf('access_key'))
        exit(0)
    if '--secret' in argv:
        secret = argSeeker('--secret')
        if secret:
            qiniu.set_conf('secret_key', secret)
        else:
            print("当前 secret key")
            print(qiniu.get_conf('secret_key'))
        exit(0)
    if '--space' in argv:
        space = argSeeker('--space')
        if space:
            qiniu.set_conf('space_name', space)
        else:
            print("当前空间名")
            print(qiniu.get_conf('space_name'))
        exit(0)
    if '--subdom' in argv:
        subdom = argSeeker('--subdom')
        if subdom:
            qiniu.set_private_space_name(subdom)
        else:
            print("当前空间默认域名")
            print(qiniu.get_private_space_name())
        exit(0)
    if len(argv) == 2 and not argv[1].startswith('--'):
        qiniu.upload(argv[1])
        exit(0)
    if '--upload' in argv:
        args = argSeeker('--upload')
        if args:
            qiniu.upload(args)
            exit(0)
        else:
            print("请输入文件位置")
    if '--stat' in argv:
        args = argSeeker('--stat')
        if args:
            qiniu.file_state(args)
            exit(0)
        else:
            print("请输入文件名")
    if '--list' in argv:
        qiniu.file_list()
        exit(0)
    if '--del' in argv:
        args = argSeeker('--del')
        if args:
            qiniu.file_del(args)
            exit(0)
        else:
            print("请输入文件名")
    if '--download' in argv:
        args = argSeeker('--download')
        if args:
            qiniu.download(args)
            exit(0)
        else:
            print("请输入文件名")
    if '--private' in argv:
        args = argSeeker('--private')
        if args:
            qiniu.private_link(args)
            exit(0)
        else:
            print("请输入文件名")
    if '--link' in argv:
        args = argSeeker('--link')
        if args:
            qiniu.download(args, True)
            exit(0)
        else:
            print("请输入文件名")
    if '--plink' in argv:
        args = argSeeker('--plink')
        if args:
            qiniu.private_link(args, True)
            exit(0)
        else:
            print("请输入文件名")
    if '--version' in argv:
        print("当前版本为: {}".format(__version__))
        exit(0)

    print '--help 可以帮助你'

if __name__ == '__main__':
    main()
