"""The cd command."""
from src.commands.base import (
    CommandContext, CommandResult, CommandError, resolve_path,
)
from src.vfs import VfsError

CD_FLAGS = {}


def cmd_cd(args: list, ctx: CommandContext) -> CommandResult:
    """Changes the current directory inside the VFS."""
    if len(args) > 1:
        raise CommandError("cd: too many arguments")
    target = args[0] if args else "/"
    path = resolve_path(ctx.cwd, target)
    path = ctx.vfs.normalize(path)
    try:
        node = ctx.vfs.find(path)
    except VfsError as exc:
        raise CommandError(f"cd: {target}: {exc}") from exc
    if not node.is_dir:
        raise CommandError(f"cd: {target}: not a directory")
    return CommandResult(new_cwd=path)
