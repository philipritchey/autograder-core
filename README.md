# autograder-core
the core autograder functionality common to all assignments.

| :exclamation:  You need a copy of these, specialized for your assignment, in your assignment-specific repo |
|-----------------------------------------------------------------------------------------------------------------|


Easy way: [Use the autograded-assignment-template repo](https://github.com/philipritchey/autograded-assignment-template)

| :warning: You do **not** need a copy of these in your assignment-specific repo |
|--------------------------------------------------------------------------------|


## get started integrating with your assignment-specific repo
1. copy `ssh_config`, `setup.sh`, and `run_autograder` to your assignment-specific repo
1. in `ssh_config`:
   * you should not need to change anything, but you can if you need to (i.e. you know what you are doing)
   * make sure you have created a deploy key for your assignment-specific repo and you have an autograder-core deploy key
1. in `setup.sh`:
   * at line 8, install any dependencies your tests require (e.g. valgrind for finding memory errors)
   * double-check: make sure you have created a deploy key for your assignment-specific repo and you have an autograder-core deploy key
     * Note that if your editor uses CRLF the deploy keys will not work. Ensure that your document is LF only.
   * at lines 51 and 52, set `username` and `repository` to your github username and assignment-specific repository, respectively
1. in `run_autograder`:
   * at line 6, list the files the students are required to submit
   * at line 11, list the files that are provided
     * provided files are expected to be a folder named `provided` in the root of the repo
1. in `tests/`:
   * define your tests in file(s) named `tests_X`.
1. you should be good to go.  happy testing!

## writing tests

tests must be located in `tests/` and the filename(s) must match `tests_*`.

### test attributes
```
@number: 2                  // required. actually a string, used for sorting tests
@name: example              // required. a descriptive name for the test
@points: 5                  // required. a floating-point value for the weight of the test
@type: unit                 // required. type of test
@target: code.cpp           // required. target file of test, is #included in unit test code
@show_output: True          // optional. string value (case insensitive "true" / "false", default = false)
@include: <sstream> "foo.h" // optional. files to include in unit test (default = empty)
@timeout: 20                // optional. floating-point number of seconds before test times out (default = 10)
@skip: True                 // optional. string value (case insensitive "true" / "false", default = false)
```

### test types
* `approved_includes`
* `compile`
* `coverage`
* `i/o`
* `memory_errors`
* `performance`
* `script`
* `unit`

### unit tests
TODO

```
/*
@number: 2
@name: example
@points: 5
@show_output: True
@type: unit
@target: code.cpp
*/
<test>
    // unit test code, e.g.
    EXPECT_EQ(foo(input), expected_value);
</test>
```

### i/o tests
TODO

```
/*
@number: 3
@name: example
@points: 5
@show_output: True
@type: i/o
@target: code.cpp
*/
<test>
    input: io_tests/example/input.txt
    output: io_tests/example/output.txt
</test>
```

### compile tests
```
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
```

### script tests
TODO

```
/*
@number: 1
@name: custom checks
@points: 10
@show_output: True
@type: script
@target: code.cpp
*/
<test>
  script_tests/custom.sh [optional command line arguments]
</test>
```

## basic packaging for gradescope
this is how you should package the autograder files for gradescope.  do this from your assignment-specific repository.

`zip run_autograder setup.sh ssh_config deploy_key autograder_core_deploy_key`

1. `run_autograder` - assignment-specific bootstrap script for running the autograder.
1. `setup.sh` - script to settp the container on gradescope
1. `ssh_config` - ssh configuration file
1. `deploy_key` - private key for accessing the assignment-specific repository
1. `autograder_core_deploy_key` - private key for accessing the autograder-core repository

you should fork this repo and make your own `autograder_core_deploy_key`.

## running autograder on gradescope (or locally)
this is how you can use the `run_autograder` script when debugging on gradescope.

```
./run_autograder -h  # print the usage message and exit
```

```
./run_autograder -d  # run in debugmode (all test output is forced visible)
```

```
./run_autograder -t <number>  # run test(s) with specified number; "5" includes "5.1, 5.2, ..."
```

the `-d` and `-t` options can be combined to run a specific test (or group of tests) in debugmode.
