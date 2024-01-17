#!/usr/bin/env bash

# update and upgrade
apt-get update
apt-get -y upgrade

#
# TODO?(you)
#
# install dependencies
apt-get -y install apt-utils valgrind num-utils

# python version check (run_tests.py requires 3.8+)
typeset -i python3_version=$(python3 --version | cut -d. -f2)
if [ $python3_version -lt 8 ]; then
  if [ "$(which python3.8)" == ""  ]; then
    # install python3.8
    apt-get install software-properties-common
    add-apt-repository -y ppa:deadsnakes/ppa
    apt-get -y install python3.8
  fi
fi

