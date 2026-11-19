#!/bin/sh
set -eu
cd "$(dirname "$0")/.."
.venv/bin/python -m pytest -q
npm --prefix frontend test
npm --prefix frontend run build
