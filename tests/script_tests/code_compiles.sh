fail () {
  printf "FAIL\n" >> DEBUG
  exit 1
}

echo 0 > OUTPUT

# TODO(you): update with necessary source and header files
SOURCE=( code.cpp code_tests.cpp)
HEADERS=( code.h)
FILES=("${SOURCE[@]}" "${HEADERS[@]}")

for file in "${FILES[@]}"; do
printf "%s exists? " "$file" >> DEBUG
if [ -f "$file" ]; then
  printf "OK\n" >> DEBUG
else
  printf "NO\n" >> DEBUG
  fail
fi
done

printf "compiles without errors? " >> DEBUG
if g++ -std=c++17 -Wall -Wextra -Weffc++ -pedantic-errors "${SOURCE[@]}" 1>OUT 2>ERR; then
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
