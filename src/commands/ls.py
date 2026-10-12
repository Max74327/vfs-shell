"""The ls command."""
from src.commands.base import (
    CommandContext, CommandResult, CommandError,
    parse_flags, resolve_path, format_mode,
)
from src.vfs import VfsError

LS_FLAGS = {
    "-l": ("long", False),
    "-a": ("all", False),
    "-1": ("one", False),
}


def cmd_ls(args: list, ctx: CommandContext) -> CommandResult:
    """Lists directory contents."""
    flags, positionals = parse_flags(args, LS_FLAGS)
    targets = positionals or [ctx.cwd]
    chunks = []
    for target in targets:
        chunks.append(_list_one(target, flags, ctx))
    return CommandResult(output="\n".join(chunks))


def _list_one(target: str, flags: dict, ctx: CommandContext) -> str:
    """Lists a single target (file or directory)."""
    path = resolve_path(ctx.cwd, target)
    try:
        node = ctx.vfs.find(path)
    except VfsError as exc:
        raise CommandError(f"ls: {target}: {exc}") from exc

    if not node.is_dir:
        return _format_long(node) if flags.get("long") else node.name

    entries = ctx.vfs.listdir(path)
    if not flags.get("all"):
        entries = [n for n in entries if not n.name.startswith(".")]

    if flags.get("long"):
        return "\n".join(_format_long(e) for e in entries)

    names = [e.name for e in entries]
    if flags.get("one"):
        return "\n".join(names)
    return "  ".join(names)


def _format_file(node, flags: dict) -> str:
    """Formats a single file for -l or plain output."""
    if flags.get("long"):
        return _format_long(node)
    return node.name


def _format_long(node) -> str:
    """Formats one entry in ls -l style."""
    kind = "d" if node.is_dir else "-"
    perm = format_mode(node)[1:]  # drop leading kind, we add it back
    size = len(node.content) if not node.is_dir else 0
    return f"{kind}{perm}  {size:>6}  {node.name}"
