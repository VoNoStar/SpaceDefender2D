#!/bin/sh
set -eu

PROJECT_DIR=$(CDPATH= cd -- "$(dirname -- "$0")" && pwd)
cd "$PROJECT_DIR"

if [ ! -x ".venv/bin/python" ]; then
    PYTHON=
    for candidate in python3 python; do
        if command -v "$candidate" >/dev/null 2>&1 &&
            "$candidate" -c 'import sys; raise SystemExit(sys.version_info < (3, 10))'; then
            PYTHON=$candidate
            break
        fi
    done
    if [ -z "$PYTHON" ]; then
        echo "Python 3.10 or newer is required. Install Python and try again." >&2
        exit 1
    fi
    "$PYTHON" -m venv .venv
fi

if ! .venv/bin/python -c 'import sys; raise SystemExit(sys.version_info < (3, 10))'; then
    echo "The project's .venv must use Python 3.10 or newer." >&2
    echo "Remove only the .venv folder and run this launcher again." >&2
    exit 1
fi

if ! .venv/bin/python -c "import pathlib, pygame, spacedefender; assert pathlib.Path(spacedefender.__file__).resolve().parent == pathlib.Path('src/spacedefender').resolve()" >/dev/null 2>&1; then
    .venv/bin/python -m pip install -e .
    .venv/bin/python -c "import pathlib, pygame, spacedefender; assert pathlib.Path(spacedefender.__file__).resolve().parent == pathlib.Path('src/spacedefender').resolve()" || {
        echo "The game could not be loaded from this project folder." >&2
        exit 1
    }
fi

exec .venv/bin/python -m spacedefender "$@"
