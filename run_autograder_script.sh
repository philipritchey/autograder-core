#!/usr/bin/env bash

# python version check (requires 3.8+)
python=python3
typeset -i python3_version=$($python --version | cut -d. -f2)
if [ $python3_version -lt 8 ]; then
  if [ "$(which python3.8)" == ""  ]; then
    echo "[FATAL] requires Python 3.8+ (because pcr _insists_ on using type hints)"
    echo "        for gradescope: make sure setup.sh includes the python3.8 install steps"
    echo "        for local: follow the python3.8 install steps in setup.sh"
    exit 1
  else
    python=python3.8
  fi
fi

BASE_DIR=$(pwd)


if [ -d /autograder ]; then
  # gradescope-like environment detected

  TESTBOX=/autograder/testbox
  REPO=/autograder/autograder-code
  AUTOGRADER_CORE_REPO=/autograder/autograder-core
  TESTS=$REPO/tests
  SUBMISSION=/autograder/submission
  RESULTS_DIR=/autograder/results

else
  echo "gradescope-like environment not detected."

  TESTBOX=testbox
  REPO=$BASE_DIR
  AUTOGRADER_CORE_REPO=$BASE_DIR/../autograder-core
  TESTS=$REPO/tests
  SUBMISSION=$BASE_DIR/solution
  RESULTS_DIR=$BASE_DIR

fi

rm -rf $TESTBOX
mkdir $TESTBOX

# take list of expected/required files from command line args
src_list=( "$@" )

# sanity check
for file in "${src_list[@]}"; do
  if [ ! -f $SUBMISSION/"$file" ]; then
    echo "[FATAL] $file does not exist. exiting."
    echo "{\"score\": 0, \"output\": \"$file does not exist.\"}" > $RESULTS_DIR/results.json
    exit 1
  fi
done

# copy submitted (but only required/expected) code to testbox
for file in "${src_list[@]}"; do
  cp $SUBMISSION/$file $TESTBOX/
done

# copy core test runners to testbox
cp $AUTOGRADER_CORE_REPO/run_tests.py $TESTBOX/
cp $AUTOGRADER_CORE_REPO/tests/approved_includes.sh $TESTBOX/
cp $AUTOGRADER_CORE_REPO/tests/compiles.sh $TESTBOX/
cp $AUTOGRADER_CORE_REPO/tests/coverage.sh $TESTBOX/
cp $AUTOGRADER_CORE_REPO/tests/cs12x_test.h $TESTBOX/
cp $AUTOGRADER_CORE_REPO/tests/memory_errors.sh $TESTBOX/


# copy tests to testbox
cp -r $REPO/tests/* $TESTBOX/

# collect and enable tests
cd $TESTBOX
touch tests.cpp
for file in $TESTS/tests_*; do
  if [ -f "$file" ]; then
	cat $file >> tests.cpp
    printf "\n" >> tests.cpp
  fi
done

chmod +x ./approved_includes.sh

# run tests <tests file> [results file]
$python run_tests.py tests.cpp $RESULTS_DIR/results.json

