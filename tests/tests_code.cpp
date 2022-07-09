/*
@number: 00
@name: approved includes for code.cpp
@points: 0
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
@points: 0
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
@points: 0
@type: approved_includes
@show_output: True
@target: code_tests.cpp
*/
<test>
cstddef
iostream
stdexcept
code.h
<test>

/*
@number: 1
@name: code compiles without errors or warnings
@points: 10
@show_output: True
@type: script
@target: code.cpp
*/
<test>
  script_tests/code_compiles.sh
</test>

/*
@number: 2
@name: memory errors
@points: 10
@show_output: True
@type: script
@target: code.cpp
*/
<test>
  script_tests/code_memory_errors.sh
</test>

/*
@number: 3
@name: test coverage
@points: 10
@show_output: True
@type: script
@target: code_tests.cpp
*/
<test>
  script_tests/code_coverage.sh
</test>

/*
@number: 4
@name: example
@points: 5
@show_output: True
@type: unit
@target: code.cpp
*/
<test>
    EXPECT_EQ(foo(867), 5309);
</test>
