"""Command package: registry and public helpers."""
from src.commands.base import (
    CommandContext, CommandResult, CommandError,
)
from src.commands.ls import cmd_ls
from src.commands.cd import cmd_cd
from src.commands.who import cmd_who
from src.commands.head import cmd_head
from src.commands.tree import cmd_tree
from src.commands.exit import cmd_exit

COMMANDS = {
    "ls": cmd_ls,
    "cd": cmd_cd,
    "who": cmd_who,
    "head": cmd_head,
    "tree": cmd_tree,
    "exit": cmd_exit,
}

__all__ = [
    "CommandContext", "CommandResult", "CommandError",
    "COMMANDS", "cmd_ls", "cmd_cd", "cmd_who", "cmd_head",
    "cmd_tree", "cmd_exit",
]
