# coding=utf8
import sys
from setuptools import setup
reload(sys)
sys.setdefaultencoding('utf8')
__author__ = 'hellflame'
__version__ = '1.1.0'

setup(
    name='qiniuManager',
    version=__version__,
    keywords=('qiniu', 'qiniu console manager'),
    description="终端管理七牛云空间",
    license="MIT",
    author=__author__,
    author_email='hellflamedly@gmail.com',
    url='https://github.com/hellflame/qiniu_manager',
    packages=[
        'qiniuManager'
    ],
    install_requires=[
        'qiniu'
    ],
    platforms="UNIX like",
    classifiers=[
        'Development Status :: 4 - Beta',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        "Environment :: Console",
        "Operating System :: MacOS",
        "Operating System :: MacOS :: MacOS X",
        "Operating System :: POSIX :: Linux",
        'Programming Language :: Python :: 2.7'
    ],
    entry_points={
        'console_scripts': [
            'qiniu=qiniuManager.run:main'
        ]
    }
)

