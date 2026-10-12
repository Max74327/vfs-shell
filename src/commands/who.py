"""The who command — shows the current user and VFS name."""
import getpass
import os
import platform

from src.commands.base import CommandContext, CommandResult


def cmd_who(args: list, ctx: CommandContext) -> CommandResult:
    """Prints information about the current user and host."""
    if args:
        # who accepts no arguments in our emulator
        from src.commands.base import CommandError
        raise CommandError("who: too many arguments")
    user = _safe_user()
    host = platform.node() or "localhost"
    home = ctx.cwd if ctx.cwd != "/" else "/"
    lines = [
        f"{user}@{host}",
        f"  cwd:   {home}",
        f"  shell: vfs-shell",
    ]
    return CommandResult(output="\n".join(lines))


def _safe_user() -> str:
    """Returns the current user name without failing in odd environments."""
    try:
        return getpass.getuser()
    except Exception:
        return os.environ.get("USER", "user")
