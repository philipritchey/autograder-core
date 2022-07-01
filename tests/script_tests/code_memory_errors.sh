# TODO(you): write memory test subject here
{
  echo "#include <iostream>"
  echo "int main() {"
  echo "   // use the function(s)"
  echo "   return 0;"
  echo "}"
} > main.cpp

# TODO(you): replace $code with the name(s) of the source file(s) to use
if g++ -std=c++17 -pedantic-errors -g $code.cpp main.cpp >> DEBUG 2>&1; then
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
