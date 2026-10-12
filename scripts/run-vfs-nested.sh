#!/usr/bin/env bash
# Launch the emulator with a VFS that has three or more levels.
set -euo pipefail
cd "$(dirname "$0")/.."
exec python3 -m src.main --cli --vfs data/vfs-nested.csv
