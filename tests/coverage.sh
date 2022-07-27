#!/usr/bin/env bash

target=$1
shift
main=$1
shift
source=( "$@" )

#echo "target: $target"
#echo "main: $main"
#echo "source: ${source[@]}"

fail () {
  printf "FAIL\n" >> DEBUG
  echo 0 > OUTPUT
  exit 1
}

FILES=( ${source[@]} $target $main )

# sanity check
for file in "${FILES[@]}"; do
printf "%s exists? " "$file"  >> DEBUG
if [ -f "$file" ]; then
  printf "OK\n"  >> DEBUG
else
  printf "NO\n" >> DEBUG
  fail
fi
done

# clean up before compile and run
rm -f *.gcda *.gcno *.gcov

# compile and execute code with coverage
if g++ -std=c++17 --coverage "${source[@]}" "$main" >>DEBUG 2>&1; then
  echo -e "\nCompiles without error\n" >> DEBUG
else
  echo -e "\nCompile-time errors" >> DEBUG
  fail
fi

if ./a.out >> DEBUG 2>&1; then
  echo -e "\nRuns without error" >> DEBUG
else
  echo "Run-time errors (return code != 0). Make sure main returns 0." >> DEBUG
  fail
fi

# TODO(pcr): unfuck this
# filename actually depends on whether target is .cpp or .h
filename=$(basename -- "$target")
target_extension="${filename##*.}"
if [ $target_extension == "h" ]; then
  filename=$(basename -- "$main")
fi
filename="${filename%.*}"
#echo "filename: $filename"
if [ ! -f "$filename.gcda" ]; then
	echo -e "Unknown FATAL error (a required coverage file was not generated)." >> DEBUG
	fail
fi

gcov -mnr "$filename" | \
	grep -A 2 "$target" | \
	grep "Lines executed:" | \
	cut -d : -f 2 | \
	cut -d % -f 1 | \
	cut -d . -f 1\
	1>OUTPUT 2>GCOV_ERRORS

{
  printf "\n%% coverage: "
  cat OUTPUT
} >> DEBUG

typeset -i coverage=$(cat OUTPUT)

#echo "coverage: $coverage"

if [ $coverage -lt 90 ]; then
  echo "< 90% coverage" >> DEBUG
  fail
else
  echo 100 > OUTPUT
fi

