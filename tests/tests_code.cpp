/*
@number: 00
@name: approved includes for code.cpp
@points: 1
@type: approved_includes
@show_output: True
@target: code.cpp
*/
<test>
cstddef
iostream
stdexcept
code.h
</test>

/*
@number: 0
@name: approved includes for code.h
@points: 1
@type: approved_includes
@show_output: True
@target: code.h
*/
<test>
cstddef
iostream
stdexcept
</test>

/*
@number: 0
@name: approved includes for code_tests.cpp
@points: 1
@type: approved_includes
@show_output: True
@target: code_tests.cpp
*/
<test>
cstddef
iostream
stdexcept
code.h
</test>

/*
@number: 1
@name: code compiles without errors or warnings
@points: 1
@show_output: True
@type: compile
@target: code.cpp
*/
<test>
code_tests.cpp
code.cpp
</test>

/*
@number: 2
@name: memory errors
@points: 1
@show_output: True
@type: memory_errors
@target: code.cpp
@timeout: 30
*/
<test>
memory_errors_test.cpp
code.cpp
</test>

/*
@number: 3
@name: test coverage
@points: 1
@show_output: True
@type: coverage
@target: code_tests.cpp
@timeout: 30
*/
<test>
  source: code.cpp
  main: code_tests.cpp
  target: code.cpp
</test>

/*
@number: 4
@name: unit example
@points: 1
@show_output: True
@type: unit
@target: code.cpp
*/
<test>
    EXPECT_FALSE(is_prime(867));
    EXPECT_TRUE(is_prime(5309));
    EXPECT_TRUE(is_prime(8675309));
</test>

/*
@number: 5.1
@name: i/o example with output shown
@points: 1
@show_output: True
@type: i/o
@target: code_interactive.cpp
@include: code.cpp
*/
<test>
  input: io_tests/example/input.txt
  output: io_tests/example/output.txt
</test>

/*
@number: 5.2
@name: i/o example with output NOT shown
@points: 1
@show_output: False
@type: i/o
@target: code_interactive.cpp
@include: code.cpp
*/
<test>
  input: io_tests/example/input.txt
  output: io_tests/example/output.txt
</test>

/*
@number: 6
@name: performance example
@points: 1
@show_output: True
@type: performance
@target: code.cpp
@timeout: 30
*/
<test>
    auto start = std::chrono::steady_clock::now();
    size_t cnt = 1;
    for (unsigned n = 3; n < 2000000; n++) {
      if (is_prime(n)) cnt++;
    }
    auto end = std::chrono::steady_clock::now();
    auto microseconds = std::chrono::duration_cast<std::chrono::microseconds>(end - start).count();
    std::cout << "operation took " << microseconds << " µs." << std::endl;
    std::cout << "  found " << cnt << " primes." << std::endl;
    EXPECT_EQ(cnt, 148933);
</test>

/*
@number: 7
@name: script example
@points: 1
@show_output: True
@type: script
@target: code_interactive.cpp
*/
<test>
  script_tests/example.sh
</test>

/*
@number: number
@name: semantically invalid
@points: -F
@type: type
@target: target
*/
<test>
</test>

/*
@skip: True
@number: 8
@name: skipped example
@points: 1
@show_output: True
@type: script
@target: code_interactive.cpp
*/
<test>
  script_tests/example.sh
</test>

/*
@number: 9
@name: example with args
@points: 1
@show_output: True
@type: script
@target: code_interactive.cpp
*/
<test>
  script_tests/example.sh -h
</test>
