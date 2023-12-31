#!/bin/bash

pgrep -f "client.py" > /dev/null && exit 0 || echo "Starting PiSync Client..."

pisync_bin=$(dirname "$(readlink -f "$0")")
pisync=$(dirname "$pisync_bin")

cd $pisync

source venv/bin/activate
python client.py & > $HOME/pisync.log 2>&1