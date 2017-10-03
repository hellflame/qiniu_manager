# coding=utf8
"""
    Progress Bar decorator for classes
"""
import sys
import math
import functools

from subprocess import check_output
from itertools import cycle
from time import time
from qiniuManager.utils import str_len, unit_change

__all__ = ['bar']


def bar(width=0, fill='#'):
    """
    进度条处理
    :param width: 手动设置进度条宽度
    :param fill: 进度填充字符
    """
    def function_wrapper(func):
        @functools.wraps(func)
        def arguments(self, *args, **kwargs):
            if not hasattr(self, 'progressed') or not hasattr(self, 'total'):
                print("progressed, total attribute is needed!")
                return
            progress_cursor = 1
            last_update = time()
            while self.progressed <= self.total:
                func(self, *args, **kwargs)
                if not hasattr(self, 'disable_progress') or not self.disable_progress:
                    if self.total <= 0:
                        print("Total Length Invalid !")
                        self.progressed = self.total = 1
                        break
                    if not width:
                        try:
                            w = int(check_output("stty size", stderr=None, shell=True).split(b" ")[1])
                        except:
                            w = 50
                    else:
                        w = width
                    if time() - last_update > .1:
                        if not hasattr(self, 'chunked') or not self.chunked:
                            # 普通编码进度条
                            percent = self.progressed / float(self.total)
                            # marks count
                            percent_show = "{}%".format(int(percent * 100))
                            # marks width
                            title = getattr(self, 'title', '')
                            mark_width = w - len(percent_show) - str_len(title) - 7
                            mark_count = int(math.floor(mark_width * percent))
                            sys.stdout.write(
                                ' ' + title + ' ' +
                                '[' + fill * mark_count + ' ' * (mark_width - mark_count) + ']  ' + percent_show + '\r')
                        else:
                            # 分块编码进度条
                            progress_cursor += 1
                            title = getattr(self, 'title', '')
                            chunk_recved = unit_change(self.chunk_recved)
                            mark_width = w - str_len(title) - len(chunk_recved) - 6
                            sys.stdout.write(" " + title + " " +
                                             "[" +
                                             "".join([i for _, i in zip(range(mark_width),
                                                                        cycle([">> ", " >>", "> >"][progress_cursor % 3]))])
                                             + "] {}\r".format(chunk_recved))

                        sys.stdout.flush()
                        last_update = time()

                    if self.progressed == self.total:
                        sys.stdout.write(" " * w + '\r')
                        break
                else:
                    if self.progressed == self.total:
                        break
        return arguments
    return function_wrapper





