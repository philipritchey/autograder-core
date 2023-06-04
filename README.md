# autograder-core
the core autograder functionality common to all assignments.

## fork me

you should [fork this repo](https://github.com/philipritchey/autograder-core/fork).

if you do any development on your own, do it in feature branches.  if it is very nice, consider making a pull request.

before every semester, you should update your fork:
```bash
git checkout main
git pull upstream main
```

## running autograder on gradescope (or locally)
this is how you can use the `run_autograder` script when debugging on gradescope (or locally).

```
./run_autograder  # run exactly as gradescope would
```

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

## get started integrating with your assignment-specific repo
[Use the autograded-assignment-template repo](https://github.com/philipritchey/autograded-assignment-template)

