"""The mv command — moves or renames a file or directory."""
from src.commands.base import (
    CommandContext, CommandResult, CommandError, resolve_path,
)
from src.vfs import VfsError

MV_FLAGS = {}


def cmd_mv(args: list, ctx: CommandContext) -> CommandResult:
    """Moves or renames a node inside the VFS."""
    if len(args) < 2:
        raise CommandError("mv: missing operand")
    if len(args) > 2:
        raise CommandError("mv: too many arguments")
    src, dst = args
    src_path = resolve_path(ctx.cwd, src)
    dst_path = resolve_path(ctx.cwd, dst)
    try:
        ctx.vfs.move(src_path, dst_path)
    except VfsError as exc:
        raise CommandError(f"mv: {src}: {exc}") from exc
    return CommandResult()
