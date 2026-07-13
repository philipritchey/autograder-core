#!/usr/bin/env bash

# go compile test script

fail () {
  echo "FAIL" >> DEBUG
  echo 0 > OUTPUT
  exit 1
}

source=( "$@" )

for file in "${source[@]}"; do
  printf "%s exists? " "$file" >> DEBUG
  if [ -f "$file" ]; then
    echo "OK" >> DEBUG
  else
    echo "NO" >> DEBUG
    fail
  fi
done

printf "compiles? " >> DEBUG
if go build "${source[@]}" 1>OUT 2>ERR; then
  echo "OK" >> DEBUG
else
  echo "NO" >> DEBUG
  cat OUT >> DEBUG
  cat ERR >> DEBUG
  fail
fi

echo 100 > OUTPUT
