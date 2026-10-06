#!/usr/bin/env bash
# Demonstrates priority: CLI value --vfs is overridden by config.json,
# but --startup is not present in the config, so CLI value is used.
set -euo pipefail
cd "$(dirname "$0")/.."
exec python3 -m src.main --cli \
    --vfs data/vfs-ignored.csv \
    --startup scripts/startup-all-commands.sh \
    --config configs/example.json
