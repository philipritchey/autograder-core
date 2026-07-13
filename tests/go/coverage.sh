#!/usr/bin/env bash

fail () {
  echo 0 > OUTPUT
  exit 1
}

files=( "$@" )

# sanity check: ensure all files exist
for file in "${files[@]}"; do
    printf "%s exists? " "$file"  >> DEBUG
    if [ -f "$file" ]; then
        printf "OK\n"  >> DEBUG
    else
        printf "NO\n" >> DEBUG
        fail
    fi
done

if ! go test -cover "${files[@]}" > OUTPUT 2>&1; then
    echo "Tests failed to run." >> DEBUG
    fail
fi
coverage=$(grep -oP 'coverage:\K.*' OUTPUT | cut -d% -f1)
cat OUTPUT >> DEBUG

if (( $(echo "${coverage} < 90" | bc -l) )); then
  printf "\nFAIL: coverage < 90%%\n" >> DEBUG
  fail
fi
printf "\nPASS: coverage >= 90%%\n" >> DEBUG
echo 100 > OUTPUT
