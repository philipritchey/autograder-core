# autograder-core
the core autograder functionality common to all assignments.

* You do **not** need a copy of these in your assignment-specific repo
  1. `run_tests.py` - the workhorse
  1. `tests/cs12x_test.h` - bootleg version of GoogleTest (C++ testing framework)
  1. `tests/approved_includes.sh` - script for verifying that all includes are approved
  1. `tests/compiles.sh` - script for verifying that the code compiles
  1. `tests/coverage.sh` - script for measuring code coverage of test
  1. `tests/memory_errors.sh` - script for testing for the presence of memory errors
  1. `run_autograder_script.sh` - the part of the full autograder script that is not assignment-specific

* You need a copy of these, specialized for your assignment, in your assignment-specific repo
  1. `run_autograder` - boilerplate for gradescope autograding entry point
  1. `setup.sh` - boilerplate for gradescope container setup
  1. `ssh_config` - ssh configuration file for pulling from 2 repos with 2 identities


## get started integrating with your assignment-specific repo
1. copy `ssh_config`, `setup.sh`, and `run_autograder` to your assignment-specific repo
1. in `ssh_config`:
   * you should not need to change anything, but you can if you need to (i.e. you know what you are doing)
   * make sure you have created a deploy key for your assignment-specific repo and you have an autograder-core deploy key
1. in `setup.sh`:
   * at line 8, install any dependencies your tests require (e.g. valgrind for finding memory errors)
   * double-check: make sure you have created a deploy key for your assignment-specific repo and you have an autograder-core deploy key
   * at lines 51 and 52, set `username` and `repository` to your github username and assignment-specific repository, respectively
1. in `run_autograder`:
   * at line 6, list the files the students are required to submit
   * at line 11, list the files that are provided
     * provided files are expected to be a folder named `provided` in the root of the repo
1. you should be good to go.  happy testing!

## writing tests
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
  script_tests/custom.sh
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

an `autograder_core_deploy_key` can be obtained by emailing pcr@tamu.edu
