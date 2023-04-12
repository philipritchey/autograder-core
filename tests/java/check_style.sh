#! /usr/bin/env bash

echo "Checking style..." >> DEBUG
java -jar lib/checkstyle-10.7.0-all.jar -c /google_checks.xml $@ > checkstyle.out 2>&1
{
  if [ "$(grep -cE '^Checkstyle ends with [1-9][0-9]* errors\.$' checkstyle.out)" == "0" ]; then
    # no errors during checkstyle
    count=$(grep -cE '^\[WARN\]' checkstyle.out)
    if [ "$count" == "0" ]; then
      # no style warnings
      echo 100 > OUTPUT
      echo ""
      echo "Style Check Passing"
      echo ""
    else
      # [WARN] style warnings
      echo 0 > OUTPUT
      echo ""
      echo "${count} violations found."
      echo "Style Check Failed"
      echo ""
      exit 1
    fi
  else
    # some error(s)
    echo 0 > OUTPUT
    echo ""
    echo "Fatal Error During Style Check"
    echo ""
    exit 1
  fi
} >> DEBUG
