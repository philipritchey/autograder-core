#!/usr/bin/env bash

# java compile test script

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

# clean up before compiling
rm -f *.class

printf "compiles without errors? " >> DEBUG
classpath=.:./lib/hamcrest-2.2.jar:./lib/junit-4.13.2.jar
if javac -Xlint -g -cp $classpath "${source[@]}" 1>OUT 2>ERR; then
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
