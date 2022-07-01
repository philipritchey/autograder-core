fail () {
  printf "FAIL\n"
  exit 1
}

# TODO(you): update this
# the tests written by the student
tests="code_tests.cpp"

# TODO(you): update this
# the code (single file) being tested
target_cpp="code.cpp"
target_h="code.h"

echo 0 > OUTPUT

SOURCE=("$target_cpp" "$tests")
HEADERS=("$target_h")
FILES=("${SOURCE[@]}" "${HEADERS[@]}")

{
  for file in "${FILES[@]}"; do
    printf "%s exists? " "$file"
    if [ -f "$file" ]; then
      printf "OK\n"
    else
      printf "NO\n"
      fail
    fi
  done
} >> DEBUG

# compile and execute code with coverage
if g++ -std=c++17 --coverage "${SOURCE[@]}" >>DEBUG 2>&1; then
  echo -e "\nCompiles without error\n" >> DEBUG
else
  echo -e "\nCompile-time errors" >> DEBUG
	fail
fi

# clean up before running student code
# TODO?

if ./a.out >> DEBUG 2>&1; then
  echo -e "\nRuns without error" >> DEBUG
else
  echo "Run-time errors (return code != 0). Make sure main returns 0." >> DEBUG
  fail
fi

filename="${target_cpp%.*}"
if [ ! -f "$filename.gcda" ]; then
	echo -e "Unknown FATAL error (a required coverage file was not generated)." >> DEBUG
	fail
fi

# TODO(you): update this (use target_cpp or target_h depending on task)
gcov -mnr "$filename" | \
	grep -A 2 "$target_cpp" | \
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

# TODO(you): update this (currently threshhold for credit is 90% coverage)
if [ $coverage -lt 90 ]; then
  echo "FAIL: < 90% coverage" >> DEBUG
  echo "0" > OUTPUT
else
  echo "100" > OUTPUT
fi
