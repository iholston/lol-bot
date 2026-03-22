#!/usr/bin/env bash

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(cd "${SCRIPT_DIR}/.." && pwd)"
VENV_DIR="${REPO_ROOT}/.venv"
VENV_PY="${VENV_DIR}/bin/python"

echo "==> LoL Bot setup and launch"

if ! command -v python3 >/dev/null 2>&1; then
  echo "Error: python3 is not installed."
  echo "Install Python 3.10+ from https://www.python.org/downloads/"
  exit 1
fi

PYTHON_OK=$(python3 - <<'PY'
import sys
print("yes" if sys.version_info >= (3, 10) else "no")
PY
)

if [ "${PYTHON_OK}" != "yes" ]; then
  echo "Error: Python 3.10+ is required."
  echo "Current version: $(python3 --version 2>&1)"
  exit 1
fi

if [ ! -d "${VENV_DIR}" ]; then
  echo "==> Creating virtual environment in .venv"
  python3 -m venv "${VENV_DIR}"
fi

echo "==> Upgrading pip"
"${VENV_PY}" -m pip install --upgrade pip

echo "==> Installing dependencies"
"${VENV_PY}" -m pip install -r "${REPO_ROOT}/requirements.txt"

echo "==> Launching LoL Bot"
cd "${REPO_ROOT}"
"${VENV_PY}" "${REPO_ROOT}/main.pyw"
