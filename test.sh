#!/bin/bash

function module_exist {
    if [ -f "./qiniuManager/test/$1_test.py" ]; then
        return 0
    fi
    return 1
}

function test_module {
    py="$1"
    module="$2"
    path=`command -v $py`
    if [ -x "$path" ]; then
        echo "using $path"
        if module_exist $module; then
            echo "Testing $2"
            eval "$path -m qiniuManager.test.$2_test "
        else
            eval "$path -m qiniuManager.test.run"
        fi
    else
        echo "$py 不可执行"
    fi
}


function test {
    py_exe="$1"
    module="$2"
    if [ -n "$py_exe" ]; then
        test_module $py_exe $module

    else
        echo "自动测试"
        if [ -x "`command -v python2`" ]; then

            echo "Python2 Test"
            python2 --version
            command python2 -m qiniuManager.test.run
            echo "----------"

        fi

        if [ -x "`command -v python3`" ]; then

            echo "Python3 Test"
            python3 --version
            python3 -m qiniuManager.test.run
            echo "----------"

        fi

        if [ -x "`command -v pypy3`" ]; then

            echo "Pypy3 Test"
            pypy3 --version
            pypy3 -m qiniuManager.test.run
            echo "----------"

        fi
    fi
}

test $1 $2