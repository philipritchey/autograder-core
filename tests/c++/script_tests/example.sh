#! /usr/bin/env bash

# an example script (custom) test

usage() {
  echo "Usage: $0 [-h]"
  echo "  -h show this help message and exit"
}

debugmode=0
while getopts "dht:" flag; do
  case "${flag}" in
    h | *) # display help
      usage >> DEBUG
      echo 100 > OUTPUT
      echo "PASS: correct behavior" >> DEBUG
      exit 0
      ;;
  esac
done

if g++ -std=c++23 -pedantic-errors -g code.cpp code_interactive.cpp > DEBUG 2>&1; then
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
