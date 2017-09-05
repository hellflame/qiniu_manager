# coding=utf8
import sys
from setuptools import setup
from qiniuManager import __author__, __version__

if sys.version_info.major == 2:
    reload(sys)
    sys.setdefaultencoding('utf8')


setup(
    name='qiniuManager',
    version=__version__,
    keywords=('qiniu', 'qiniu manager'),
    description="终端管理七牛云空间",
    license="MIT",
    author=__author__,
    author_email='hellflamedly@gmail.com',
    url='https://github.com/hellflame/qiniu_manager',
    packages=[
        'qiniuManager'
    ],
    platforms="UNIX like",
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        "Environment :: Console",
        "Operating System :: MacOS",
        "Operating System :: MacOS :: MacOS X",
        "Operating System :: POSIX",
        "Operating System :: POSIX :: Linux",
        'Programming Language :: Python :: 2.7'
    ],
    entry_points={
        'console_scripts': [
            'qiniu=qiniuManager.run:main'
        ]
    }
)

