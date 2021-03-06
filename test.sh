#!/bin/bash

MODULE_NAME=qiniuManager

function module_exist {
    if [ -f "./$MODULE_NAME/test/$1_test.py" ]; then
        return 0
    fi
    return 1
}

function test_module {
    py="$1"
    module="$2"
    path=`command -v ${py}`
    if [ -x "$path" ]; then
        echo "using $path"
        if module_exist ${module}; then
            echo "Testing $2"
            eval "${path} -m ${MODULE_NAME}.test.${module}_test "
        else
            eval "${path} -m ${MODULE_NAME}.test.run"
        fi
    else
        echo "$py 不可执行"
    fi
}


function test_runner {
    py_exe="$1"
    module="$2"
    if [ -n "$py_exe" ]; then
        test_module ${py_exe} ${module}

    else
        echo "自动测试"
        if [ -x "`command -v python2`" ]; then

            echo "Python2 Test"
            command python2 --version
            command python2 -m ${MODULE_NAME}.test.run
            echo "----------"

        fi

        if [ -x "`command -v python3`" ]; then

            echo "Python3 Test"
            command python3 --version
            command python3 -m ${MODULE_NAME}.test.run
            echo "----------"

        fi

        if [ -x "`command -v pypy3`" ]; then

            echo "Pypy3 Test"
            command pypy3 --version
            command pypy3 -m ${MODULE_NAME}.test.run
            echo "----------"

        fi
    fi
}

test_runner $1 $2