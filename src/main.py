"""
Entry point of the shell emulator.

By default the GUI is started; with --cli, or when PyQt6 is
unavailable, the console frontend is used instead.
"""
import argparse
import sys

from src.shell import Shell

VFS_NAME = "vfs20"
PROMPT = f"user@{VFS_NAME}:$ "


def _build_gui():
    """Tries to create the GUI frontend. Returns None on failure."""
    try:
        from src.frontends.gui import GuiFrontend
    except Exception as exc:
        print(f"[i] GUI unavailable ({exc}); using CLI.",
              file=sys.stderr)
        return None
    return GuiFrontend(VFS_NAME, PROMPT)


def _build_cli():
    """Creates the console frontend."""
    from src.frontends.cli import CliFrontend
    return CliFrontend(VFS_NAME, PROMPT)


def _run(frontend) -> int:
    """Attaches the shell core to the frontend and runs it."""
    shell = Shell(frontend)
    frontend.attach(shell)
    frontend.run()
    return 0


def main(argv=None) -> int:
    """Parses arguments and runs the selected frontend."""
    parser = argparse.ArgumentParser(
        description="VFS shell emulator",
    )
    parser.add_argument(
        "--cli", action="store_true",
        help="start in console mode (no GUI)",
    )
    args = parser.parse_args(argv)

    if args.cli:
        return _run(_build_cli())

    frontend = _build_gui()
    if frontend is None:
        return _run(_build_cli())
    return _run(frontend)


if __name__ == "__main__":
    raise SystemExit(main())
