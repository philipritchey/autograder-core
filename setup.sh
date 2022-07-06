#!/usr/bin/env bash

# update and upgrade
apt-get update
apt-get -y upgrade

# install dependencies
#apt-get -y install apt-utils valgrind

# python3.8
#apt install software-properties-common
#add-apt-repository -y ppa:deadsnakes/ppa
#apt-get -y install python3.8

cd /autograder/source
mkdir -p /root/.ssh
cp ssh_config /root/.ssh/config

#
# TODO(you)
#
# Make sure to include your private key here (as `deploy_key`)
#   this is the deploy key for the assignment-specific repo
mv deploy_key /root/.ssh/deploy_key
chmod 600 /root/.ssh/deploy_key

# you can get an `autograder_core_deploy_key` from pcr@tamu.edu
mv autograder_core_deploy_key /root/.ssh/autograder_core_deploy_key
chmod 600 /root/.ssh/autograder_core_deploy_key

# To prevent host key verification errors at runtime
ssh-keyscan -t rsa github.com >> ~/.ssh/known_hosts

# Clone autograder files
#
# TODO(you)
#
# set your username and repository for the assignment-specific content (i.e. tests)
git clone git@assignment:$username/$repository.git /autograder/autograder-code
git clone git@core:CSCE-12x/autograder-core.git /autograder/autograder-core

