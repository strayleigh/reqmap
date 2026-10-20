#!/usr/bin/env bash
# Runner script for ReqMap
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
cd "$SCRIPT_DIR"

if [ -f ".venv/bin/python" ]; then
    PYTHON_EXEC=".venv/bin/python"
else
    PYTHON_EXEC="python3"
fi

export PYTHONPATH="$SCRIPT_DIR:$PYTHONPATH"
exec "$PYTHON_EXEC" -m app.main "$@"
