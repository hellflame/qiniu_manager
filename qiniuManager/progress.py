# coding=utf8
"""
    Progress Bar decorator for classes
"""
import sys
import os
import math

__all__ = ['bar']


def bar(width=0, fill='#'):
    """
    进度条处理
    :param width: 手动设置进度条宽度
    :param fill: 进度填充字符
    """
    def function_wrapper(func):
        def arguments(self, *args, **kwargs):
            if not hasattr(self, 'progressed') or not hasattr(self, 'total'):
                print("progressed, total attribute is needed!")
                return
            while self.progressed <= self.total:
                func(self, *args, **kwargs)
                if not hasattr(self, 'disable_progress') or not self.disable_progress:
                    if self.total <= 0:
                        print("Total Length Invalid !")
                        self.progressed = self.total = 1
                        break
                    if not width:
                        try:
                            w = int(os.popen("stty size 2>/dev/null").read().split(" ")[1])
                        except:
                            w = 50
                    else:
                        w = width
                    percent = self.progressed / float(self.total)
                    # marks count
                    percent_show = "{}%".format(int(percent * 100))
                    # marks width
                    title = getattr(self, 'title', '')
                    mark_width = w - len(percent_show) - 5 - len(title) - 2
                    mark_count = int(math.floor(mark_width * percent))
                    sys.stdout.write(
                        ' ' + title + ' ' +
                        '[' + fill * mark_count + ' ' * (mark_width - mark_count) + ']  ' + percent_show + '\r')
                    sys.stdout.flush()
                    if self.progressed == self.total:
                        sys.stdout.write(" " * w + '\r')
                        sys.stdout.flush()
                        break
                else:
                    if self.progressed == self.total:
                        break
        return arguments
    return function_wrapper



