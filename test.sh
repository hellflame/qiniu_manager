#!/bin/bash

if [ -x "`command -v python2`" ]; then

echo "Python2 Test"
command python2 -m qiniuManager.test.run
echo "----------"
fi

if [ -x "`command -v python3`" ]; then

echo "Python3 Test"
python3 -m qiniuManager.test.run
echo "----------"

fi

if [ -x "`command -v pypy3`" ]; then

echo "Pypy3 Test"
pypy3 -m qiniuManager.test.run
echo "----------"

fi