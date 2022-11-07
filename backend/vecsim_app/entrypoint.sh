#!/bin/sh
cd $(dirname $0) && pwd  # cd to the script's directory

python load_data.py
python main.py
