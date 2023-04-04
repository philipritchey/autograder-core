#!/usr/bin/env bash

code=( "$@" )

if g++ -std=c++17 -pedantic-errors -g "${code[@]}" >> DEBUG 2>&1; then
  if valgrind --leak-check=full --error-exitcode=1 ./a.out >> DEBUG 2>&1; then
	  echo 100 > OUTPUT
	  echo 'PASS: no memory errors detected' >> DEBUG
  else
	  echo 0 > OUTPUT
	  echo 'FAIL: memory errors detected, e.g. memory leak, use after free, double free, uninitialized use, access out of bounds' >> DEBUG
  fi
else
  echo 0 > OUTPUT
  echo "FAIL: compilation errors" >> DEBUG
fi
