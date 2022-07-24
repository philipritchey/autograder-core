# TODO(you): write memory error test in tests/memory_errors_test.cpp
#            if you need several, you can use prefixes, e.g. codeA_memory_errors_test.cpp, codeB_memory_errors_test.cpp
#              then have a version of this file for each
#              TODO(pcr): abstract mem error test filename as an arg to the script 
mv memory_errors_test.cpp main.cpp

# TODO(you): specify the name(s) of the source file(s) to use
CODE=( main.cpp )
if g++ -std=c++17 -pedantic-errors -g "${CODE[@]}" >> DEBUG 2>&1; then
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
