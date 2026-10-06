#!/usr/bin/env bash
# Launch the GUI with a configuration file.
set -euo pipefail
cd "$(dirname "$0")/.."
exec python3 -m src.main --config configs/example.json
