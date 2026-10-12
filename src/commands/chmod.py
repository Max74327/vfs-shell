"""The chmod command — changes file mode bits."""
import re

from src.commands.base import (
    CommandContext, CommandResult, CommandError, resolve_path,
)
from src.vfs import VfsError, Node

OCTAL_MODE = re.compile(r"^[0-7]{3,4}$")
SYMBOLIC_MODE = re.compile(r"^([ugoa]+)([+-=])([rwx]+)$")

PERM_BITS = {
    "u": {"r": 0o400, "w": 0o200, "x": 0o100},
    "g": {"r": 0o040, "w": 0o020, "x": 0o010},
    "o": {"r": 0o004, "w": 0o002, "x": 0o001},
}
MODE_MASK = 0o7777


def cmd_chmod(args: list, ctx: CommandContext) -> CommandResult:
    """Changes the mode of one or more nodes."""
    if len(args) < 2:
        raise CommandError("chmod: missing operand")
    mode_expr, *targets = args
    for target in targets:
        _apply_to_target(mode_expr, target, ctx)
    return CommandResult()


def _apply_to_target(expr: str, target: str, ctx: CommandContext) -> None:
    """Applies the mode expression to a single target."""
    path = resolve_path(ctx.cwd, target)
    try:
        node = ctx.vfs.find(path)
    except VfsError as exc:
        raise CommandError(f"chmod: {target}: {exc}") from exc
    new_mode = _compute_mode(node.mode, expr)
    node.mode = new_mode & MODE_MASK


def _compute_mode(current: int, expr: str) -> int:
    """Computes the new mode from either an octal or a symbolic form."""
    if OCTAL_MODE.match(expr):
        return int(expr, 8)
    if SYMBOLIC_MODE.match(expr):
        return _apply_symbolic(current, expr)
    raise CommandError(f"chmod: invalid mode: {expr}")


def _apply_symbolic(current: int, expr: str) -> int:
    """Applies a symbolic mode like 'u+x', 'go-w', 'a=r'."""
    who, op, perms = SYMBOLIC_MODE.match(expr).groups()
    if "a" in who:
        who = "ugo"
    mask = 0
    for group in who:
        for perm in perms:
            mask |= PERM_BITS[group][perm]
    if op == "+":
        return current | mask
    if op == "-":
        return current & ~mask
    # op == '='
    cleared = current
    for group in who:
        group_mask = sum(PERM_BITS[group].values())
        cleared &= ~group_mask
    return cleared | mask
