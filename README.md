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
1. `autograder_core_deploy_key` - private key for accessing the autograder-base repository

an `autograder_core_deploy_key` can be obtained by emailing pcr@tamu.edu