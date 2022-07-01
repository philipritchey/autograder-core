# autograder-core
the core autograder functionality common to all assignments.

1. `run_tests.py` - the workhorse; you do not need this in your assignment-specific repository anymore
1. `run_autograder` - boilerplate for gradescope autograding entry point; keep your version with your assignment-specific repository
1. `setup.sh` - boilerplate for gradescope container setup; keep your version with your assignment-specific repository
1. `ssh_config` - ssh configuration file for pulling from 2 repos with 2 identities; keep a copy in your assignment-specific repository

## get started integrating with your assignment-specific repo
1. copy `ssh_config`, `seup.sh`, and `run_autograder` to your assignment-specific repo
1. in `ssh_config`:
   * you should not need to change anything, but you can if you need to (i.e. you know what you are doing)
   * make sure you have created a deploy key for your assignment-specific repo and you have an autogrdaer-core deploy key
1. in `setup.sh`:
   * at line 8, install any dependencies your tests require (e.g. valgrind for finding memory errors)
   * double-check: make sure you have created a deploy key for your assignment-specific repo and you have an autogrdaer-core deploy key
   * at line 34, change `$username` and `$repository` to your github username and assignment-specific repository, respectively
1. in `run_autograder`:
   * at line 19, list the files the students are required to submit
   * at line 50, copy all required assignment-specific testing files (that are not already in `io_tests` or `script_tests` or `approved_includes*`) into `$TESTBOX/`
     * you might not have any of these; that's OK
     * if you change the file name from `tests.cpp`, be sure to also change it at line 61 (in the `python3 run_tests.py ...` command)
1. you should be good to go.  happy testing!

## writing tests
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
	input
	io_tests/example/input.txt
	output
	io_tests/example/output.txt
</test>
```

### script tests
TODO

```
/*
@number: 1
@name: compiles without errors or warnings
@points: 10
@show_output: True
@type: script
@target: code.cpp
*/
<test>
  script
  script_tests/code_compiles.sh
</test>
```

## basic packaging for gradescope
this is how you should package the autograder files for gradescope.  do this from your assignment-specific repository.

`zip run_autograder setup.sh ssh_config deploy_key autograder_base_deploy_key`

1. `run_autograder` - assignment-specific script for running the autograder.
1. `setup.sh` - script to settp the container on gradescope
1. `ssh_config` - ssh configuration file
1. `deploy_key` - private key for accessing the assignment-specific repository
1. `autograder_core_deploy_key` - private key for accessing the autograder-core repository

an `autograder_core_deploy_key` can be obtained by emailing pcr@tamu.edu
