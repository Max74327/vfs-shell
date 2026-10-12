"""Tests for the who command."""
import pytest

from src.commands import CommandContext, CommandError
from src.commands.who import cmd_who
from src.vfs import Vfs


def test_who_prints_user_and_cwd():
    """who prints user, host and cwd."""
    vfs = Vfs()
    ctx = CommandContext(vfs=vfs, cwd="/home")
    out = cmd_who([], ctx).output
    assert "cwd:" in out
    assert "/home" in out


def test_who_rejects_args():
    """who accepts no positional arguments."""
    vfs = Vfs()
    ctx = CommandContext(vfs=vfs, cwd="/")
    with pytest.raises(CommandError):
        cmd_who(["x"], ctx)
