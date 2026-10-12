"""The exit command."""
from src.commands.base import CommandContext, CommandResult


def cmd_exit(args: list, ctx: CommandContext) -> CommandResult:
    """Signals the shell to terminate."""
    return CommandResult(exit=True)
