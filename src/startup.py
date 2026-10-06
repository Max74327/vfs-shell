"""Startup script runner: reads a file, feeds lines to the shell."""
import os


class StartupError(Exception):
    """Raised when the startup script cannot be read."""


def read_script(path: str) -> list:
    """Reads a startup script, strips comments and blank lines."""
    if not os.path.isfile(path):
        raise StartupError(f"startup script not found: {path}")
    lines = []
    with open(path, "r", encoding="utf-8") as fh:
        for raw in fh:
            line = raw.rstrip("\n")
            stripped = line.strip()
            if not stripped:
                continue
            if stripped.startswith("#"):
                continue
            lines.append(line)
    return lines


def run_startup(shell, path: str) -> bool:
    """
    Feeds every line of the script to the shell.

    Prints both the input and the output, imitating a dialogue.
    Returns False if the shell terminated during the script.
    """
    for line in read_script(path):
        if not shell.process(line):
            return False
    return True
