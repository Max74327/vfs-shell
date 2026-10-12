"""Tests for the cd command."""
import pytest

from src.commands import CommandContext, CommandError
from src.commands.cd import cmd_cd
from src.vfs import Vfs


def _ctx(vfs=None, cwd="/"):
    vfs = vfs or Vfs()
    return CommandContext(vfs=vfs, cwd=cwd)


def test_cd_to_directory():
    """cd returns new_cwd when target exists."""
    vfs = Vfs()
    vfs.mkdir("/home/user")
    result = cmd_cd(["/home/user"], _ctx(vfs))
    assert result.new_cwd == "/home/user"


def test_cd_no_args_goes_root():
    """cd with no arguments goes to the root."""
    vfs = Vfs()
    result = cmd_cd([], _ctx(vfs, cwd="/home"))
    assert result.new_cwd == "/"


def test_cd_relative():
    """cd resolves relative paths against cwd."""
    vfs = Vfs()
    vfs.mkdir("/a/b")
    result = cmd_cd(["b"], _ctx(vfs, cwd="/a"))
    assert result.new_cwd == "/a/b"


def test_cd_to_file_raises():
    """cd on a file raises CommandError."""
    vfs = Vfs()
    vfs.create_file("/file")
    with pytest.raises(CommandError):
        cmd_cd(["/file"], _ctx(vfs))


def test_cd_too_many_args():
    """cd with two arguments raises CommandError."""
    with pytest.raises(CommandError):
        cmd_cd(["a", "b"], _ctx())
