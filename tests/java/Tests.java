/*
@number: 1
@name: code compiles without errors or warnings
@points: 1
@show_output: True
@type: compile
@target: Code.java
*/
<test>
Code.java
</test>

/*
@number: 5.1
@name: i/o example with output shown
@points: 1
@show_output: True
@type: i/o
@target: Code.java
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
@target: Code.java
*/
<test>
  input: io_tests/example/input.txt
  output: io_tests/example/output.txt
</test>
