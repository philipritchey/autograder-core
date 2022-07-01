# autograder-core
the core autograder functionality common to all assignments.

1. `run_tests.py` - the workhorse; you do not need this in your assignment-specific repository anymore
1. `run_autograder` - boilerplate for gradescope autograding entry point; keep your version with your assignment-specific repository
1. `setup.sh` - boilerplate for gradescope container setup; keep your version with your assignment-specific repository
1. `ssh_config` - ssh configuration file for pulling from 2 repos with 2 identities; keep a copy in your assignment-specific repository

## basic packaging for gradescope
`zip run_autograder setup.sh ssh_config deploy_key autograder_base_deploy_key`

1. `run_autograder` - assignment-specific script for running the autograder.
1. `setup.sh` - script to settp the container on gradescope
1. `ssh_config` - ssh configuration file
1. `deploy_key` - private key for accessing the assignment-specific repository
1. `autograder_core_deploy_key` - private key for accessing the autograder-core repository

an `autograder_core_deploy_key` can be obtained by emailing pcr@tamu.edu

## get started using for your assignment-specific repo
1. copy `ssh_config`, `seup.sh`, and `run_autograder` to your assignment-specific repo
1. in `ssh_config`:
   * you should not need to change anything, but you can if you need to (i.e. you know what you are doing)
   * make sure you have created a deploy key for you assignment-specific repo and you have an autogrdaer-core deploy key
1. in `setup.sh`:
   * at line 8, install any dependencies your tests require (e.g. valgrind for finding memory errors)
   * double-check: make sure you have created a deploy key for you assignment-specific repo and you have an autogrdaer-core deploy key
   * at line 34, change `$username` and `$repository` to your github username and assignment-specific repository, respectively
1. in `run_autograder`:
   * at line 19, list the files the students are required to submit
   * at line 50, copy all required assignment-specific testing files (that are not already in `io_tests` or `script_tests` or `approved_includes*`) into `$TESTBOX/`
     * you might not have any of these; that's OK
     * if you change the file name from `tests.cpp`, be sure to also change it at line 61 (in the `python3 run_tests.py ...` command)
1. you should be good to go.  happy testing!
