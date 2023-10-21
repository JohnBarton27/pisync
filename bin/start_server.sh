#!/bin/bash

pgrep -f "server.py" > /dev/null && exit 0 || echo "Starting PiSync Server..."

pisync_bin=$(dirname "$(readlink -f "$0")")
pisync=$(dirname "$pisync_bin")

cd $pisync

source venv/bin/activate
python server.py & > $HOME/pisync.log 2>&1