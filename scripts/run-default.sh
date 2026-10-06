#!/usr/bin/env bash
# Launch without any configuration: pure defaults, CLI mode.
set -euo pipefail
cd "$(dirname "$0")/.."
exec python3 -m src.main --cli
