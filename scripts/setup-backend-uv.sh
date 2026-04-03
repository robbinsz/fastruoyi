#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT_DIR/ruoyi-fastapi-backend"

uv venv --python 3.10
uv pip install --python .venv/bin/python -r requirements.txt
