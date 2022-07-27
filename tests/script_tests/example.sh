#! /usr/bin/env bash

if g++ -std=c++17 -pedantic-errors -g code.cpp code_interactive.cpp > DEBUG 2>&1; then
    echo "X" | ./a.out > OUT
    if grep -qi "invalid input" OUT; then
        echo 100 > OUTPUT
        echo "PASS: correct behavior" >> DEBUG
    else
        echo 0 > OUTPUT
        echo "FAIL: incorrect behavior" >> DEBUG
    fi
else
    echo 0 > OUTPUT
    echo "FAIL: compilation errors" >> DEBUG
fi
