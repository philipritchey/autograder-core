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

if go build code.go code_interactive.go > DEBUG 2>&1; then
    echo "X" | ./code > OUT
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
