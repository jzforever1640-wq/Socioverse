#!/bin/sh
set -eu
# Reversible setup only; never calls an LLM. Run from a writable working directory.
SV_CORE_COMMIT=9c3ac774816511c121184ca11f539dc398ba1544
SV_SETUP_ROOT=${1:-./phase18-runtime}
mkdir -p "$SV_SETUP_ROOT"
if [ ! -d "$SV_SETUP_ROOT/SocioVerse2/.git" ]; then
  git clone https://github.com/sii-research/SocioVerse2.git "$SV_SETUP_ROOT/SocioVerse2"
fi
git -C "$SV_SETUP_ROOT/SocioVerse2" checkout --detach "$SV_CORE_COMMIT"
python3 -m venv "$SV_SETUP_ROOT/venv"
"$SV_SETUP_ROOT/venv/bin/python" -m pip install -e "$SV_SETUP_ROOT/SocioVerse2" pytest jsonschema
printf '%s\n' 'Setup complete. Use requirements.lock.txt to reproduce the recorded dependency versions when compatible with your platform. No simulation or LLM call was started.'
