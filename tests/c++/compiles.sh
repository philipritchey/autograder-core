#!/usr/bin/env bash

# c++ compile test script

fail () {
  printf "FAIL\n" >> DEBUG
  echo 0 > OUTPUT
  exit 1
}

source=( "$@" )

for file in "${source[@]}"; do
  printf "%s exists? " "$file" >> DEBUG
  if [ -f "$file" ]; then
    printf "OK\n" >> DEBUG
  else
    printf "NO\n" >> DEBUG
    fail
  fi
done

printf "compiles without errors? " >> DEBUG
if g++ -std=c++23 -Wall -Wextra -Weffc++ -pedantic-errors "${source[@]}" 1>OUT 2>ERR; then
  printf "OK\n" >> DEBUG
else
  printf "NO\n" >> DEBUG
  cat OUT >> DEBUG
  cat ERR >> DEBUG
  fail
fi

printf "compiles without warnings? " >> DEBUG
if [ -s ERR ]; then
  printf "NO\n" >> DEBUG
  cat OUT >> DEBUG
  cat ERR >> DEBUG
  fail
else
  printf "OK\n" >> DEBUG
fi

echo 100 > OUTPUT
