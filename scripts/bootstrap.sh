#!/usr/bin/env bash
# Bootstrap script to create a Python venv and install dev dependencies
set -euo pipefail

ROOT_DIR=$(cd "$(dirname "$0")/.." && pwd)
VENV_DIR="$ROOT_DIR/.venv"

if [ -d "$VENV_DIR" ]; then
	echo "Virtualenv already exists at $VENV_DIR — will use existing venv"
else
	echo "Creating virtualenv at $VENV_DIR"
	python3 -m venv "$VENV_DIR"
fi

echo "Activating venv and upgrading pip..."
source "$VENV_DIR/bin/activate"
pip install --upgrade pip

echo "Installing minimal dev dependencies (pytest)."
pip install pytest || true

echo "Note: To install the full project dependencies (FAISS, sentence-transformers, chromadb, etc.) run:"
echo "  pip install -r requirements.txt"
echo "Bootstrap complete. Activate venv with: source $VENV_DIR/bin/activate"
