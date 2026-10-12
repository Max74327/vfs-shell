#!/usr/bin/env bash
# Launch the emulator with the minimal VFS.
set -euo pipefail
cd "$(dirname "$0")/.."
exec python3 -m src.main --cli --vfs data/vfs-minimal.csv
