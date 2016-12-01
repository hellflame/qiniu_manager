"""
    Progress Bar decorator for classes
"""
import sys
import os
import math


def bar(width=0, fill='#'):
    def function_wrapper(function):
        def arguments(self, *args, **kwargs):
            if not hasattr(self, 'progressed') or not hasattr(self, 'total'):
                raise EssentialException
            while self.progressed <= self.total:
                function(self, *args, **kwargs)
                if not hasattr(self, 'disable_progress') or not self.disable_progress:
                    if self.total <= 0:
                        raise InvalidBar("Total Length Invalid !")
                    if not width:
                        try:
                            w = int(os.popen("stty size 2>/dev/null").read().split(" ")[1])
                        except Exception as e:
                            w = 50
                    else:
                        w = width
                    percent = self.progressed / float(self.total)
                    # marks count
                    percent_show = "{}%".format(int(percent * 100))
                    # marks width
                    if hasattr(self, 'title'):
                        title = self.title
                    else:
                        title = ''
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


class EssentialException(Exception):
    def __str__(self):
        return "instance must have `progressed` and `total` attributes"


class InvalidBar(Exception):
    def __init__(self, reason):
        self.reason = reason

    def __str__(self):
        return "This progress bar is invalid for: {}".format(self.reason)


