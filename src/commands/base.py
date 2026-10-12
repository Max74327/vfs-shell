"""Shared helpers for all commands."""
from dataclasses import dataclass

from src.vfs import Vfs, Node, VfsError


@dataclass
class CommandContext:
    """Everything a command needs to run."""

    vfs: Vfs
    cwd: str


@dataclass
class CommandResult:
    """What a command returns to the shell core."""

    output: str = ""
    new_cwd: str | None = None
    exit: bool = False


class CommandError(Exception):
    """Raised by a command to signal a user-visible error."""


def parse_flags(args: list, spec: dict) -> tuple:
    """
    Minimal flag parser.

    spec maps short/long flag to a name and a boolean 'takes_value'.
    Example: {"-l": ("long", False), "--all": ("all", False)}

    Returns (flags, positionals).
    """
    flags = {}
    positionals = []
    i = 0
    while i < len(args):
        a = args[i]
        if a in spec:
            name, takes_value = spec[a]
            if takes_value:
                if i + 1 >= len(args):
                    raise CommandError(f"{a}: missing value")
                flags[name] = args[i + 1]
                i += 2
            else:
                flags[name] = True
                i += 1
        elif a.startswith("-") and a != "-":
            raise CommandError(f"{a}: unknown flag")
        else:
            positionals.append(a)
            i += 1
    return flags, positionals


def resolve_path(cwd: str, path: str) -> str:
    """Resolves a possibly relative path against the current directory."""
    if not path:
        return cwd
    if path.startswith("/"):
        return path
    if cwd == "/":
        return "/" + path
    return cwd + "/" + path


def human_mode(node: Node) -> str:
    """Returns a 10-character ls-style mode string, e.g. 'drwxr-xr-x'."""
    kind = "d" if node.is_dir else "-"
    bits = node.mode
    out = []
    for shift, char in ((6, "r"), (5, "w"), (4, "x"),
                        (3, "r"), (2, "w"), (1, "x"),
                        (0, "r"), (None, None)):
        pass  # placeholder, real loop below

    # Simple, explicit, no magic:
    def trio(base: int) -> str:
        s = ""
        s += "r" if bits & (4 << base) else "-"
        s += "w" if bits & (2 << base) else "-"
        s += "x" if bits & (1 << base) else "-"
        return s
    return kind + trio(6) + trio(3) + trio(0)


def format_mode(node: Node) -> str:
    """Same as human_mode but with a trailing 't'/'T' for sticky."""
    base = human_mode(node)
    if node.mode & 0o1000:
        base = base[:-1] + ("t" if node.mode & 0o001 else "T")
    return base
