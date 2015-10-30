# coding=utf8
import sys
from setuptools import setup, find_packages
reload(sys)
sys.setdefaultencoding('utf8')
__author__ = 'hellflame'

setup(
    name='qiniuManager',
    version='0.8.0',
    keywords=('qiniu', 'console manager', 'qiniu upload'),
    description="终端管理七牛云空间",
    license="MIT",
    author=__author__,
    author_email='hellflamedly@gmail.com',
    url='https://github.com/hellflame/qiniu',
    packages=find_packages(),
    platforms="linux, mac os",
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 2.7'
    ],
    entry_points={
        'console_scripts': [
            'qiniu=qiniu_manager.manager:'
        ]
    }
)

