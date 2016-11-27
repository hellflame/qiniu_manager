#!/usr/bin/env python
# coding=utf8
import os
import sys
import manager

__version__ = '1.1.0'

short = {
    '--check': '-c',
    '--list': '-l',
    '--key': '-k',
    '--space': '-s',
    '--help': '-h',
    '--remove': '-r',
    '--download': '-d',
    '--private': '-p',
    '--link': '-i',
    '--version': '-v',
    '--clean': '-e',
    '--rename': '-n'
    }

map_target = {
    '--check': '查看文件状态',
    '--list': '文件列表',
    '--key': '修改或查看access key，secret key',
    '--space': '修改或查看当前空间名',
    '--help': '帮助',
    '--remove': '删除云文件',
    '--download': '下载文件',
    '--private': '返回私有文件下载链接',
    '--link': '返回开放云空间文件下载链接',
    '--version': '当前版本号',
    '--clean': '清除缓存',
    '--rename': "重命名"
    }


def help_menu():
    print("\n七牛云存储 Qiniu Manager\n")
    print("Usage:")
    print("  qiniu <your file> [space]\t\t选择文件位置上传，指定空间名或使用默认空间名")
    print("  qiniu [option] <file name> [space]\t对云空间中文件进行操作")
    print("  qiniu [--key|-k] <access key> <secret key>\t设置密钥\n")
    for i in map_target:
        print("  {},{}\t{}".format(i, short[i], map_target[i]))
    print("\n\033[01;31m首次使用\033[00m请设置密钥对 qiniu [--key|-k] <access key> <secret key>")
    print("必要情况下请设置默认空间名")


def main():
    argv = sys.argv
    argv_len = len(argv)
    if argv_len == 1:
        help_menu()
    else:
        arg = argv[1:]
        qiniu = manager.Qiniu()
        if argv_len == 2:
            if arg[0] in ('-v', '--version'):
                print("Qiniu Manager {}".format(__version__))
                print("Qiniu SDK {}".format(manager.sdk_version))
            elif arg[0] in ('-h', '--help'):
                help_menu()
            elif arg[0] in ('-l', '--list'):
                qiniu.list()

            elif arg[0] in ('-s', '--space'):
                data = qiniu.config.get_default_space()
                space_list = qiniu.config.get_space_list()
                print("Known Space Names Below\n")
                for i in space_list:
                    print("{} {} {}".format(space_list.index(i) + 1, i[0], i[1]))
                if data:
                    print ('\ndefault space name:\t{}'.format(data[0]))

            elif arg[0] in ('-k', '--key'):
                data = qiniu.config.access_list(include_discard=False)
                if data:
                    for i in data:
                        print ("{} {} {}".format(data.index(i) + 1, i[1], i[2]))
                else:
                    print("no access secret key pair found")

            elif arg[0] in ('-e', '--clean'):
                qiniu.config.clean_all_cache()
                print("upload cache is cleaned now!")

            else:
                target = arg[0]
                if os.path.exists(target):
                    qiniu.upload(target)
                    if qiniu.state:
                        print("\033[01;31m{}\033[00m upload in \033[01;32m{}\033[00m @\033[01;32m{}\033[00m"
                              .format(
                               os.path.basename(target),
                               qiniu.avg_speed,
                               qiniu.config.get_default_space()[0]
                              ))
                    else:
                        print("\033[01;31m{}\033[00m uploaded \033[01;31mFailed\033[00m !!".
                              format(os.path.basename(target)))
                else:
                    print("\033[01;31m{}\033[00m not exist, use '-h' to help".format(target))
        elif argv_len == 3:
            if arg[0] in ('-c', '--check'):
                qiniu.check(arg[1])

            elif arg[0] in ('-l', '--list'):
                qiniu.list(arg[1])

            elif arg[0] in ('-s', '--space'):
                qiniu.config.set_space(arg[1])
                print("space \033[01;31m{}\033[00m is added and as the default space now".format(arg[1]))

            elif arg[0] in ('-r', '--remove'):
                qiniu.remove(arg[1])

            elif arg[0] in ('-d', '--download'):
                qiniu.download(arg[1])

            elif arg[0] in ('-p', '--private'):
                print(qiniu.private_download_link(arg[1]))

            elif arg[0] in ('-i', '--link'):
                print(qiniu.regular_download_link(arg[1]))

            else:
                target = arg[0]
                if os.path.exists(target):
                    if qiniu.config.get_space(arg[1]):
                        qiniu.upload(target, arg[1])
                        if qiniu.state:
                            print("\033[01;31m{}\033[00m upload in \033[01;32m{}\033[00m @\033[01;32m{}\033[00m".
                                  format(os.path.basename(target), arg[1], qiniu.avg_speed))
                        else:
                            print("\033[01;31m{}\033[00m upload FAILED, check the space name or network".format(os.path.basename(target)))
                    else:
                        print("space {} not exist, use qiniu -s {} to add it".format(arg[1], arg[1]))
                else:
                    print("{} not exist, use qiniu -h for help".format(target))
        elif argv_len == 4:
            if arg[0] in ('-k', '--key'):
                qiniu.config.add_access(arg[1], arg[2])
                print("new key pair add")
                print("access:\t{}".format(arg[1]))
                print("secret:\t{}".format(arg[2]))

            elif arg[0] in ('-c', '--check'):
                qiniu.check(arg[1], arg[2])

            elif arg[0] in ('-r', '--remove'):
                qiniu.remove(arg[1], arg[2])

            elif arg[0] in ('-d', '--download'):
                qiniu.download(arg[1], arg[2])

            elif arg[0] in ('-p', '--private'):
                print(qiniu.private_download_link(arg[1], arg[2]))

            elif arg[0] in ('-i', '--link'):
                print(qiniu.regular_download_link(arg[1], arg[2]))

            elif arg[0] in ('-s', '--space'):
                qiniu.config.set_space(arg[1], arg[2])
                print("space \033[01;31m{}\033[00m now has the alias domain \033[01;31m{}\033[00m".format(arg[1], arg[2]))

            elif arg[0] in ('-n', '--rename'):
                qiniu.rename(arg[1], arg[2])

            else:
                help_menu()
        elif argv_len == 5:
            if arg[0] in ('-n', '--rename'):
                qiniu.rename(arg[1], arg[2], arg[3])

            else:
                help_menu()
        else:
            help_menu()


if __name__ == '__main__':
    main()

