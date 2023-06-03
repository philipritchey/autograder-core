#!/usr/bin/env bash

usage() {
  echo "Usage: $0 [-d] [-h] [-t <number>]"
  echo "  -d            run tests in debug mode"
  echo "  -h            show this help message and exit"
  echo "  -l <language> expected programming language"
  echo "  -t <number>   run test(s) with specified number"
}

# default language is c++ (legacy)
language=c++

debugmode=0
while getopts "dhl:t:" flag; do
  case "${flag}" in
    d)
      debugmode=1
      ;;
    l)
      language=${OPTARG}
      ;;
    t)
      tests=${OPTARG}
      ;;
    h | *) # display help
      usage
      exit 0
      ;;
  esac
done
shift $(( OPTIND - 1 ))

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
  SUBMISSION=/autograder/submission
  RESULTS_DIR=/autograder/results

else
  echo "gradescope-like environment not detected."

  TESTBOX=testbox
  REPO=$BASE_DIR
  AUTOGRADER_CORE_REPO=$BASE_DIR/../autograder-core
  if [ -d $BASE_DIR/solution/$language ]; then
    SUBMISSION=$BASE_DIR/solution/$language
  else
    SUBMISSION=$BASE_DIR/solution/
  fi
  RESULTS_DIR=$BASE_DIR

fi

case "$language" in
  c++ | java)
    ;;
  *)
    echo "Unsupported Language: $language"
    exit 1
esac

if [ -d $REPO/tests/$language ]; then
  TESTS=$REPO/tests/$language
else
  TESTS=$REPO/tests
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
cp $AUTOGRADER_CORE_REPO/attributes.py $TESTBOX/
cp $AUTOGRADER_CORE_REPO/config.py $TESTBOX/
cp $AUTOGRADER_CORE_REPO/results.py $TESTBOX/
cp $AUTOGRADER_CORE_REPO/test_parsing.py $TESTBOX/
cp $AUTOGRADER_CORE_REPO/test_types.py $TESTBOX/
cp -r $AUTOGRADER_CORE_REPO/tests/$language/* $TESTBOX/
if [ "${language}" == "c++" ]; then
  cp $AUTOGRADER_CORE_REPO/support/cpp/test_writing.py $TESTBOX/
  cp $AUTOGRADER_CORE_REPO/support/cpp/test_compiling.py $TESTBOX/
  cp $AUTOGRADER_CORE_REPO/support/cpp/test_running.py $TESTBOX/

  testFile=tests.cpp
  testPattern="*.tests"

elif [ "${language}" == "java" ]; then
  cp $AUTOGRADER_CORE_REPO/support/java/test_writing.py $TESTBOX/
  cp $AUTOGRADER_CORE_REPO/support/java/test_compiling.py $TESTBOX/
  cp $AUTOGRADER_CORE_REPO/support/java/test_running.py $TESTBOX/

  testFile=tests.java
  testPattern="*.tests"

else
  echo "[FATAL] unsupported language: ${language}"
  exit 1
fi

# copy tests to testbox
cp -r $TESTS/* $TESTBOX/

# collect and enable tests
cd $TESTBOX
touch $testFile
for file in $TESTS/$testPattern; do
  if [ -f "$file" ]; then
    cat $file >> $testFile
    printf "\n" >> $testFile
  fi
done

scripts=( approved_includes.sh compiles.sh coverage.sh memory_errors.sh check_style.sh )
for file in "${scripts[@]}"; do
  if [ -f "$file" ]; then
    chmod +x $file
  fi
done

# run tests <tests file> [-r results file]
flags="-l $language"
if [ $debugmode -eq 1 ]; then
  flags="$flags --debugmode"
fi
if [ ! -z  "${tests}" ]; then
  flags="$flags -t $tests"
fi
$python run_tests.py $flags $testFile -r $RESULTS_DIR/results.json
