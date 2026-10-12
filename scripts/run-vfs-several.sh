#!/usr/bin/env bash
# Launch the emulator with a VFS that has several files.
set -euo pipefail
cd "$(dirname "$0")/.."
exec python3 -m src.main --cli --vfs data/vfs-several-files.csv
