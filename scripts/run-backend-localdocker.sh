#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT_DIR/ruoyi-fastapi-backend"

if [ ! -x ".venv/bin/python" ]; then
  echo "Missing backend virtualenv. Run 'make install-backend' first."
  exit 1
fi

.venv/bin/python app.py --env=localdocker
