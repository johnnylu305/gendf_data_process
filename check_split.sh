#!/usr/bin/env bash
set -euo pipefail

# arg check
[[ $# -ge 1 ]] || { echo "usage: $0 /path/to/BASE_DIR (e.g., .../040625-LundoBin)"; exit 1; }

BASE="${1%/}"
SCENE="$BASE/$(basename "$BASE")-All"

trap 'echo "[ERROR] failed at line $LINENO (exit $?)"' ERR

echo "==> $(date -Is) Start | BASE=$BASE | SCENE=$SCENE"

python3 check_split.py "$SCENE"



