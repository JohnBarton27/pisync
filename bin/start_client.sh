#!/bin/bash

pisync_bin=$(dirname "$(readlink -f "$0")")
pisync=$(dirname "$pisync_bin")
echo "The script is located at: $pisync"

cd $pisync

source venv/bin/activate
python client.py