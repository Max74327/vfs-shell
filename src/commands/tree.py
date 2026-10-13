"""The tree command — prints the VFS subtree as ASCII art."""
from src.commands.base import (
    CommandContext, CommandResult, CommandError, resolve_path,
)
from src.vfs import VfsError

TREE_FLAGS = {
    "-L": ("depth", True),
}


def cmd_tree(args: list, ctx: CommandContext) -> CommandResult:
    """Prints the subtree starting at the given path."""
    flags, positionals = _parse(args)
    if len(positionals) > 1:
        raise CommandError("tree: too many arguments")
    target = positionals[0] if positionals else ctx.cwd
    path = resolve_path(ctx.cwd, target)
    try:
        node = ctx.vfs.find(path)
    except VfsError as exc:
        raise CommandError(f"tree: {target}: {exc}") from exc

    max_depth = flags.get("depth", 0)
    lines = [path if path != "/" else "/"]
    stats = {"dirs": 0, "files": 0}
    _walk(ctx, node, "", max_depth, 1, lines, stats)
    lines.append("")
    lines.append(f"{stats['dirs']} directories, {stats['files']} files")
    return CommandResult(output="\n".join(lines))


def _parse(args: list):
    """Parses -L NUM."""
    flags = {}
    positionals = []
    i = 0
    while i < len(args):
        a = args[i]
        if a == "-L":
            if i + 1 >= len(args):
                raise CommandError("tree: -L requires a number")
            flags["depth"] = _positive_int(args[i + 1])
            i += 2
        elif a.startswith("-L") and len(a) > 2:
            flags["depth"] = _positive_int(a[2:])
            i += 1
        elif a.startswith("-") and a != "-":
            raise CommandError(f"tree: unknown flag: {a}")
        else:
            positionals.append(a)
            i += 1
    return flags, positionals


def _positive_int(text: str) -> int:
    """Parses a strictly positive integer."""
    try:
        value = int(text)
    except ValueError as exc:
        raise CommandError(f"tree: invalid number: {text}") from exc
    if value <= 0:
        raise CommandError(f"tree: invalid number: {text}")
    return value


def _walk(ctx, node, prefix, max_depth, level, lines, stats):
    """Recursively formats children using box-drawing characters."""
    if not node.is_dir:
        return
    if max_depth and level > max_depth:
        return
    children = sorted(node.children.values(),
                      key=lambda n: (not n.is_dir, n.name))
    count = len(children)
    for idx, child in enumerate(children):
        last = idx == count - 1
        branch = "└── " if last else "├── "
        lines.append(prefix + branch + child.name)
        if child.is_dir:
            stats["dirs"] += 1
            extension = "    " if last else "│   "
            _walk(ctx, child, prefix + extension,
                  max_depth, level + 1, lines, stats)
        else:
            stats["files"] += 1
