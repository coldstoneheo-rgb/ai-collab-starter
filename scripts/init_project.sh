#!/usr/bin/env bash
set -e
ROOT=$(pwd)
echo "Initializing ai-collab-starter into $ROOT"

# install python venv optionally
if [ ! -d ".venv" ]; then
  python3 -m venv .venv || true
  source .venv/bin/activate || true
  pip install --upgrade pip || true
fi

# Build local index
python scripts/index_docs.py || true

git init || true
git add .
git commit -m "chore: init ai-collab-starter template" || true
echo "Done. Please set remote origin and push: git remote add origin <url> && git push -u origin main"
