#!/usr/bin/env bash
# Launch in CLI mode with an explicit startup script.
set -euo pipefail
cd "$(dirname "$0")/.."
exec python3 -m src.main --cli \
    --vfs data/vfs-nested.csv \
    --startup scripts/startup-all-commands.sh
