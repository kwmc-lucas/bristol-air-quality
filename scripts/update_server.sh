#!/bin/bash

# *********** Example usage ***********

# bash scripts/update_server.sh --identity_file ~/.ssh/bristol_approach_air_quality_id_rsa --dir ~/tmp/citizensensing/bristol-air-quality


# ************* Arguments *************

# Script template from: https://stackoverflow.com/a/29754866

# saner programming env: these switches turn some bugs into errors
set -o errexit -o pipefail -o noclobber -o nounset

! getopt --test > /dev/null
if [[ ${PIPESTATUS[0]} -ne 4 ]]; then
    echo "I’m sorry, `getopt --test` failed in this environment."
    exit 1
fi

OPTIONS=vi:d:
LONGOPTS=verbose,identity_file:,dir:

# -use ! and PIPESTATUS to get exit code with errexit set
# -temporarily store output to be able to check for errors
# -activate quoting/enhanced mode (e.g. by writing out “--options”)
# -pass arguments only via   -- "$@"   to separate them correctly
! PARSED=$(getopt --options=$OPTIONS --longoptions=$LONGOPTS --name "$0" -- "$@")
if [[ ${PIPESTATUS[0]} -ne 0 ]]; then
    # e.g. return value is 1
    #  then getopt has complained about wrong arguments to stdout
    exit 2
fi
# read getopt’s output this way to handle the quoting right:
eval set -- "$PARSED"

v=false identity_file='' root_dir=..
# now enjoy the options in order and nicely split until we see --
while true; do
    case "$1" in
        -v|--verbose)
            v=true
            shift
            ;;
        -i|--identity_file)
            # The path to GitHub SSH private key file
            identity_file="$2"
            shift 2
            ;;
        -d|--dir)
            # The root directory to Luftdaten project
            root_dir="$2"
            shift 2
            ;;
        --)
            shift
            break
            ;;
        *)
            echo "Programming error"
            exit 3
            ;;
    esac
done

# handle non-option arguments
#if [[ $# -ne 1 ]]; then
#    echo "$0: A single input file is required."
#    exit 4
#fi
#echo "not optional arg: $1"


# ************* Script *************

root_dir="$root_dir"
script_dir="${root_dir}/scripts"
python_exe="${root_dir}/env/bin/python"



if [ $v = "true" ]; then
    echo "verbose: $v, root_dir: $root_dir, identity_file: $identity_file"
    echo "Downloading latest data an updating the server..."
fi

#if [ ! -f "id_rsa" ]; then \
#    echo "Missing private SSH key for syncing with GitHub (id_rsa)."; \
#    echo "Generate a private key for your GitHub account and place it in the root dir."; \
#    exit 1; \
#fi

if [ ! -f $python_exe ]; then \
    echo "Couldn't find the python executeable. Generate Python virtual environment, as per the README."; \
    exit 1; \
fi

# GitHub setup
#git_cmd='git'
#if [ -n "$identity_file" ]; then
#    git_cmd="GIT_SSH_COMMAND=\"ssh -i $identity_file -F /dev/null\" git"
#fi
#echo "$git_cmd"

# Make sure project is up to date
if [ -z "$identity_file" ]; then
    git pull
else
    GIT_SSH_COMMAND="ssh -i $identity_file -F /dev/null" git pull
fi

# Process latest data
cd $script_dir
$python_exe download_data.py
$python_exe process_data.py

# Update the server
data_files="$root_dir/data/luftdaten/aggregated/*"
git add $data_files
git commit -m "Add new data."

if [ -z "$identity_file" ]; then
    git push origin master
else
    GIT_SSH_COMMAND="ssh -i $identity_file -F /dev/null" git push origin master
fi
