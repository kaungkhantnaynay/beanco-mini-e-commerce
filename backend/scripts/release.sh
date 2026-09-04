#!/bin/sh
set -eu

script_dir=$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)
backend_dir=$(dirname -- "$script_dir")
cd "$backend_dir"

if [ -x .venv/bin/python ]; then
  python_command=.venv/bin/python
else
  python_command=python3
fi

"$python_command" manage.py check --deploy
"$python_command" manage.py migrate --plan
"$python_command" manage.py migrate --noinput
