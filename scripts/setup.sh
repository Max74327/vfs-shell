#!/usr/bin/env bash
#
# Create a local virtual environment and install all dependencies.
#
# Usage:
#   ./scripts/setup.sh          # create .venv and install everything
#   ./scripts/setup.sh --clean  # remove .venv and exit
#   ./scripts/setup.sh --force  # recreate .venv from scratch
#
# System packages (python, git) are detected through the platform
# package manager (pacman, apt, dnf, brew). Project dependencies
# are installed with pip inside .venv. PyQt6 is optional: it is
# installed from pip only if it is not already available, and the
# script suggests a system package when pip fails.

set -euo pipefail

PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$PROJECT_ROOT"

VENV_DIR=".venv"
PYTHON="${PYTHON:-python3}"
REQUIREMENTS_FILE="requirements.txt"

# ---------------------------------------------------------------- helpers

info()  { printf '[setup] %s\n' "$*"; }
warn()  { printf '[setup] warning: %s\n' "$*" >&2; }
die()   { printf '[setup] error: %s\n' "$*" >&2; exit 1; }

have() {
    command -v "$1" >/dev/null 2>&1
}

detect_pkg_manager() {
    if have pacman;  then echo pacman;  return; fi
    if have apt-get; then echo apt;     return; fi
    if have dnf;     then echo dnf;     return; fi
    if have zypper;  then echo zypper;  return; fi
    if have brew;    then echo brew;    return; fi
    echo none
}

# ---------------------------------------------------------------- actions

clean_venv() {
    if [ -d "$VENV_DIR" ]; then
        info "removing $VENV_DIR"
        rm -rf "$VENV_DIR"
    else
        info "no $VENV_DIR to remove"
    fi
}

ensure_python() {
    if ! have "$PYTHON"; then
        die "python3 is not installed; install it first"
    fi
    local version
    version="$("$PYTHON" -c 'import sys; print("%d.%d" % sys.version_info[:2])')"
    info "using $PYTHON ($version)"
    case "$version" in
        3.10|3.11|3.12|3.13|3.14) ;;
        *) warn "expected Python 3.10+, found $version" ;;
    esac
}

ensure_system_tools() {
    # These are needed before/around pip and are not pip-installable
    # on most distros.
    local pm
    pm="$(detect_pkg_manager)"

    case "$pm" in
        pacman)
            info "checking pacman packages"
            local missing=()
            for pkg in python bash git; do
                pacman -Q "$pkg" >/dev/null 2>&1 || missing+=("$pkg")
            done
            if [ "${#missing[@]}" -gt 0 ]; then
                warn "missing system packages: ${missing[*]}"
                warn "install them with: sudo pacman -S ${missing[*]}"
            fi
            ;;
        apt)
            info "checking apt packages"
            local missing=()
            for pkg in python3 bash git; do
                dpkg -s "$pkg" >/dev/null 2>&1 || missing+=("$pkg")
            done
            if [ "${#missing[@]}" -gt 0 ]; then
                warn "missing system packages: ${missing[*]}"
                warn "install them with: sudo apt install ${missing[*]}"
            fi
            ;;
        dnf)
            info "checking dnf packages"
            for pkg in python3 bash git; do
                rpm -q "$pkg" >/dev/null 2>&1 || \
                    warn "missing: $pkg (sudo dnf install $pkg)"
            done
            ;;
        zypper)
            info "checking zypper packages"
            for pkg in python3 bash git; do
                rpm -q "$pkg" >/dev/null 2>&1 || \
                    warn "missing: $pkg (sudo zypper install $pkg)"
            done
            ;;
        brew)
            info "checking brew packages"
            local missing=()
            for pkg in python bash git; do
                brew list --formula "$pkg" >/dev/null 2>&1 || \
                    missing+=("$pkg")
            done
            if [ "${#missing[@]}" -gt 0 ]; then
                warn "missing brew packages: ${missing[*]}"
                warn "install them with: brew install ${missing[*]}"
            fi
            ;;
        *)
            info "unknown package manager; skipping system checks"
            ;;
    esac
}

create_venv() {
    if [ -d "$VENV_DIR" ] && [ "${1:-}" != "--force" ]; then
        info "$VENV_DIR already exists; reusing"
        return
    fi
    if [ -d "$VENV_DIR" ] && [ "${1:-}" = "--force" ]; then
        clean_venv
    fi
    info "creating $VENV_DIR"
    "$PYTHON" -m venv "$VENV_DIR" || \
        die "failed to create venv; install python3-venv"
}

venv_python() {
    echo "$VENV_DIR/bin/python"
}

install_dependencies() {
    local py
    py="$(venv_python)"

    info "upgrading pip, setuptools, wheel"
    "$py" -m pip install --upgrade pip setuptools wheel >/dev/null

    if [ -f "$REQUIREMENTS_FILE" ]; then
        info "installing from $REQUIREMENTS_FILE"
        "$py" -m pip install -r "$REQUIREMENTS_FILE"
    else
        info "no $REQUIREMENTS_FILE; installing defaults"
        "$py" -m pip install pytest pycodestyle pdoc
    fi

    # PyQt6 is optional: if it fails, the app still runs in CLI mode.
    if ! "$py" -c "import PyQt6" >/dev/null 2>&1; then
        info "attempting to install PyQt6 (optional)"
        if ! "$py" -m pip install PyQt6; then
            warn "PyQt6 install failed; the GUI will not be available"
            case "$(detect_pkg_manager)" in
                pacman) warn "on Arch install it with: sudo pacman -S python-pyqt6" ;;
                apt)    warn "on Debian/Ubuntu install it with: sudo apt install python3-pyqt6" ;;
                dnf)    warn "on Fedora install it with: sudo dnf install python3-pyqt6" ;;
                brew)   warn "on macOS install it with: brew install pyqt@6" ;;
                *)      warn "install PyQt6 through your package manager" ;;
            esac
        fi
    else
        info "PyQt6 already available"
    fi
}

verify_install() {
    local py
    py="$(venv_python)"
    info "verifying imports"
    "$py" - <<'PY'
import importlib
import sys

required = ["pytest", "pycodestyle", "pdoc"]
optional = ["PyQt6"]

for name in required:
    try:
        importlib.import_module(name)
    except Exception as exc:
        print(f"  missing: {name} ({exc})")
        sys.exit(1)
    else:
        print(f"  ok: {name}")

for name in optional:
    try:
        importlib.import_module(name)
        print(f"  ok: {name} (optional)")
    except Exception:
        print(f"  skipped: {name} (optional)")
PY
}

print_next_steps() {
    cat <<EOF

[setup] done.

Next steps:
  source $VENV_DIR/bin/activate
  ./run.sh test
  ./run.sh cli
  ./run.sh docs

The venv is local to the repository and excluded by .gitignore.
EOF
}

# ---------------------------------------------------------------- main

main() {
    case "${1:-}" in
        --clean)
            clean_venv
            exit 0
            ;;
        --help|-h)
            sed -n '2,15p' "$0"
            exit 0
            ;;
    esac

    ensure_python
    ensure_system_tools
    create_venv "${1:-}"
    install_dependencies
    verify_install
    print_next_steps
}

main "$@"
