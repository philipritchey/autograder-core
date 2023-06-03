#!/usr/bin/env bash

# update and upgrade
apt-get update
apt-get -y upgrade

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

cd /autograder/source
mkdir -p /root/.ssh
cp ssh_config /root/.ssh/config

#
# TODO(you)
#
# Make sure to include your private key here (as `deploy_key`)
#   this is the deploy key for the assignment-specific repo
#   how-to:
#     $ ssh-keygen -t ed25519 -C "gradescope deploy key"
#     save as ./deploy_key in assignment folder
#     no passphrase
#     $ mv ./deploy_key ./secrets/deploy_key
#     add a new deploy key on github (Repo/Settings/Security/Deploy Keys)
#       paste contents of ./deploy_key.pub
mv deploy_key /root/.ssh/deploy_key
chmod 600 /root/.ssh/deploy_key

# you should fork https://github.com/philipritchey/autograder-core and follow
# the above instructions to make your own autograder-core deploy key(s)
mv autograder_core_deploy_key /root/.ssh/autograder_core_deploy_key
chmod 600 /root/.ssh/autograder_core_deploy_key

# To prevent host key verification errors at runtime
ssh-keyscan -t rsa github.com >> ~/.ssh/known_hosts

# Clone autograder files
#
# TODO(you)
#
# set your username and repository for the assignment-specific content (i.e. tests)
username=your_username
repository=repository_for_assignment
git clone git@assignment:$username/$repository.git /autograder/autograder-code
git clone git@core:CSCE-12x/autograder-core.git /autograder/autograder-core

