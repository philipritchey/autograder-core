#!/usr/bin/env bash

fail () {
  printf "FAIL\n" >> DEBUG
  echo 0 > OUTPUT
  exit 1
}

summary() {
  local missed=$1
  local covered=$2
  local category=$3
  local total=$((missed+covered))

  if [ $total -eq 0 ]; then
    percent="100.0"
  else
    percent=$(echo "100 * $covered / $total" | bc -l | cut -c-5)
  fi
  if [ "$percent" != "100.0" ]; then
    hundredPercent=false
  fi
  printf "%11s: $percent%% ($covered / $total)\n" $category >> DEBUG
  percentSum=$(echo "$percentSum + $percent" | bc -l)
}

target=$1
shift
main=$1
shift
source=( "$@" )

# TODO(pcr): if target is a .java file, add it to source list

FILES=( ${source[@]} $target $main )

# clean up before compile and run
rm -f jacoco.exec coverage0.csv coverage.csv

echo "" >> DEBUG
echo "Compiling..." >> DEBUG
if ./compiles.sh "${source[@]}" "$main" >>DEBUG 2>&1; then
  echo -e "\nCompiles without error\n" >> DEBUG
else
  echo -e "\nCompile-time errors" >> DEBUG
  fail
fi

echo "" >> DEBUG
echo "Running Tests..." >> DEBUG
classpath=.:./lib/hamcrest-2.2.jar:./lib/junit-4.13.2.jar
if java -classpath "$classpath" -javaagent:./lib/jacocoagent.jar "${main:0:-5}" >> DEBUG 2>&1; then
  echo -e "\nRuns without error" >> DEBUG
else
  echo "Run-time errors (return code != 0). Check for unhandled exceptions and System.exit calls." >> DEBUG
  fail
fi

echo "" >> DEBUG
echo "Computing Coverage..." >> DEBUG

if [ -z "$1" ]; then
  # run coverage over all files
  java -jar ./lib/jacococli.jar report jacoco.exec --classfiles . --sourcefiles . --csv coverage0.csv >> DEBUG 2>&1;

  # summarize coverage.csv
  {
    echo "GROUP,PACKAGE,CLASS,INSTRUCTION_MISSED,INSTRUCTION_COVERED,BRANCH_MISSED,BRANCH_COVERED,LINE_MISSED,LINE_COVERED,COMPLEXITY_MISSED,COMPLEXITY_COVERED,METHOD_MISSED,METHOD_COVERED"
    printf "%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s\n" `numsum -s, -c coverage0.csv`
  } > coverage.csv

  rm coverage0.csv

else
  # run coverage over only specified file
  java -jar ./lib/jacococli.jar report jacoco.exec --classfiles $(find . -type f -name "${target:0:-5}.class") --sourcefiles . --csv coverage.csv >> DEBUG 2>&1;
fi

echo "" >> DEBUG
echo "coverage" >> DEBUG
echo "--------" >> DEBUG

hundredPercent=true
ninetyPercent=false
percentSum=0

missed=$(sed -n '2p' coverage.csv | cut -d, -f4)
covered=$(sed -n '2p' coverage.csv | cut -d, -f5)
summary $missed $covered "instruction"

missed=$(sed -n '2p' coverage.csv | cut -d, -f6)
covered=$(sed -n '2p' coverage.csv | cut -d, -f7)
summary $missed $covered "branch"

missed=$(sed -n '2p' coverage.csv | cut -d, -f8)
covered=$(sed -n '2p' coverage.csv | cut -d, -f9)
summary $missed $covered "line"

missed=$(sed -n '2p' coverage.csv | cut -d, -f10)
covered=$(sed -n '2p' coverage.csv | cut -d, -f11)
summary $missed $covered "complexity"

missed=$(sed -n '2p' coverage.csv | cut -d, -f12)
covered=$(sed -n '2p' coverage.csv | cut -d, -f13)
summary $missed $covered "method"

echo 100 > OUTPUT
{
  echo ""
  if [ "$(echo "$percentSum / 5 == 100" | bc -l)" == "1" ]; then
    echo "100% Coverge"
  elif [ "$(echo "$percentSum / 5 >= 90" | bc -l)" == "1" ]; then
    echo "Coverage >= 90%"
  else
    echo "Coverage < 90%"
    fail
  fi
  echo ""
} >> DEBUG
