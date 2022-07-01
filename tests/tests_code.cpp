/*
@number: 1
@name: code compiles without errors or warnings
@points: 10
@show_output: True
@type: script
@target: code.cpp
*/
{
  script
  script_tests/code_compiles.sh
}

/*
@number: 2
@name: selection: memory errors
@points: 10
@show_output: True
@type: script
@target: code.cpp
*/
{
  script
  script_tests/code_memory_errors.sh
}

/*
@number: 3
@name: selection: test coverage
@points: 10
@show_output: True
@type: script
@target: code_tests.cpp
*/
{
  script
  script_tests/code_coverage.sh
}

/*
@number: 4
@name: example
@points: 5
@show_output: True
@type: unit
@target: selection.cpp
*/
{
    EXPECT_EQ(foo(867), 5309);
}

/*
@number: 0
@name: approved includes for code.cpp
@points: 0
@type: approved_includes
@target: code.cpp
*/
{
}

/*
@number: 0
@name: approved includes for code.h
@points: 0
@type: approved_includes
@target: code.h
*/
{
}

/*
@number: 0
@name: approved includes for code_tests.cpp
@points: 0
@type: approved_includes
@target: code_tests.cpp
*/
{
}
