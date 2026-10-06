"""Entry point of the shell emulator."""
import sys

from src.config import ConfigError, format_debug, resolve_config
from src.shell import Shell
from src.startup import StartupError, run_startup

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


def _pick_frontend(cfg):
    """Returns the frontend according to the configuration."""
    if cfg.cli_mode:
        return _build_cli()
    frontend = _build_gui()
    if frontend is None:
        return _build_cli()
    return frontend


def _run_startup_script(frontend, cfg) -> bool:
    """Runs the startup script, if one was configured."""
    if not cfg.startup_script:
        return True
    try:
        return run_startup(frontend.shell, cfg.startup_script)
    except StartupError as exc:
        frontend.write(f"Startup error: {exc}")
        return True


def main(argv=None) -> int:
    """Parses arguments, prints debug info, and runs the emulator."""
    try:
        cfg = resolve_config(argv)
    except ConfigError as exc:
        print(f"Configuration error: {exc}", file=sys.stderr)
        return 2

    frontend = _pick_frontend(cfg)
    shell = Shell(frontend)
    frontend.attach(shell)

    shell.write(format_debug(cfg))
    shell.banner()

    if not _run_startup_script(frontend, cfg):
        return 0

    frontend.run()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
