#!/bin/bash

# Get current dir
DIR="$( cd "$( dirname "$0" )" && pwd )"

# Enable virtualenv if available (Both Windows & UNIX)
if [ -d "$DIR/venv/bin" ]; then
    source "$DIR/venv/bin/activate"
elif [ -d "$DIR/env/bin" ]; then
    source "$DIR/env/bin/activate"
elif [ -d "$DIR/venv/Scripts" ]; then
    source "$DIR/venv/Scripts/activate"
elif [ -d "$DIR/env/Scripts" ]; then
    source "$DIR/env/Scripts/activate"
fi

# Install dependencies into the venv
if [ -f "$DIR/requirements.txt" ]; then
    pip install -r "$DIR/requirements.txt"
fi

# Determine null device (to dump python -v output into)
NULL_DEVICE="/dev/null"
if [[ "$OSTYPE" == "msys" || "$OSTYPE" == "cygwin" ]]; then
    NULL_DEVICE="NUL"
fi

# Check whether to use python3 or python
if command -v python3 &>"$NULL_DEVICE"; then
    PYTHON_CMD=python3
elif command -v python &>"$NULL_DEVICE"; then
    PYTHON_CMD=python
else
    echo "Python not installed"
    exit 1
fi

# Run the main Python script
$PYTHON_CMD "$DIR/src/main.py" "$@"