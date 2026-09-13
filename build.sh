#!/usr/bin/env bash
#
# Full pipeline: CC-CEDICT source -> tab file -> OPF/HTML -> .mobi dictionary
#
# Usage:
#   ./build.sh [CEDICT_SOURCE]
#
# CEDICT_SOURCE defaults to cedict_1_0_ts_utf-8_mdbg.txt (the filename
# cedict_to_tab.py already expects).

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

CEDICT_SOURCE="${1:-cedict_1_0_ts_utf-8_mdbg.txt}"
OUTPUT_DIR="output"
TAB_FILE="$OUTPUT_DIR/dictionary.txt"

for cmd in python3 kindlegen; do
    if ! command -v "$cmd" >/dev/null 2>&1; then
        echo "Error: '$cmd' is required but not found on PATH." >&2
        exit 1
    fi
done

if [ ! -f "$CEDICT_SOURCE" ]; then
    echo "Error: CC-CEDICT source file not found: $CEDICT_SOURCE" >&2
    exit 1
fi

echo "[1/3] Building tab file from $CEDICT_SOURCE..."
python3 cedict_to_tab.py

echo "[2/3] Converting $TAB_FILE to OPF/HTML..."
python3 tab_to_opf.py -utf "$TAB_FILE"

echo "[3/3] Building .mobi with kindlegen..."
kindlegen "$OUTPUT_DIR/dictionary.opf"

cp "$OUTPUT_DIR/dictionary.mobi" .

echo "Done: dictionary.mobi"
