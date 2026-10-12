"""The head command — prints the first lines of a file."""
from src.commands.base import (
    CommandContext, CommandResult, CommandError, resolve_path,
)
from src.vfs import VfsError

HEAD_FLAGS = {
    "-n": ("lines", True),
}
DEFAULT_LINES = 10


def cmd_head(args: list, ctx: CommandContext) -> CommandResult:
    """Prints the first N lines of each file argument."""
    flags, positionals = _parse(args)
    if not positionals:
        raise CommandError("head: missing file operand")
    chunks = []
    for target in positionals:
        chunks.append(_head_one(target, flags, ctx))
    return CommandResult(output="\n".join(chunks))


def _parse(args: list):
    """Parses -n NUM and returns (flags, positionals)."""
    flags = {}
    positionals = []
    i = 0
    while i < len(args):
        a = args[i]
        if a == "-n":
            if i + 1 >= len(args):
                raise CommandError("head: -n requires a number")
            flags["lines"] = _positive_int(args[i + 1])
            i += 2
        elif a.startswith("-n") and len(a) > 2:
            flags["lines"] = _positive_int(a[2:])
            i += 1
        elif a.startswith("-") and a != "-":
            raise CommandError(f"head: unknown flag: {a}")
        else:
            positionals.append(a)
            i += 1
    flags.setdefault("lines", DEFAULT_LINES)
    return flags, positionals


def _positive_int(text: str) -> int:
    """Parses a strictly positive integer."""
    try:
        value = int(text)
    except ValueError as exc:
        raise CommandError(f"head: invalid number: {text}") from exc
    if value < 0:
        raise CommandError(f"head: invalid number: {text}")
    return value


def _head_one(target: str, flags: dict, ctx: CommandContext) -> str:
    """Returns the first lines of a single file."""
    path = resolve_path(ctx.cwd, target)
    try:
        node = ctx.vfs.find(path)
    except VfsError as exc:
        raise CommandError(f"head: {target}: {exc}") from exc
    if node.is_dir:
        raise CommandError(f"head: {target}: is a directory")
    if node.binary:
        raise CommandError(f"head: {target}: binary file")
    lines = node.content.splitlines()
    limit = flags["lines"]
    return "\n".join(lines[:limit])
