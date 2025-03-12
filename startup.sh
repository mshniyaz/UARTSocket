DIR="$( cd "$( dirname "$0" )" && pwd )"

# Enable virtualenv if available
if [ -d "$DIR/venv/bin" ]; then
    source $DIR/venv/bin/activate
elif [ -d "$DIR/env/bin" ]; then
    source $DIR/env/bin/activate
fi

python3 "$DIR/src/main.py" "$@"