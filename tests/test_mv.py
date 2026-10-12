"""Tests for the mv command."""
import pytest

from src.commands import CommandContext, CommandError
from src.commands.mv import cmd_mv
from src.vfs import Vfs


def _ctx(vfs=None, cwd="/"):
    vfs = vfs or Vfs()
    return CommandContext(vfs=vfs, cwd=cwd)


def test_mv_renames_file():
    """mv renames a file in place."""
    vfs = Vfs()
    vfs.create_file("/a.txt", content="hi")
    cmd_mv(["/a.txt", "/b.txt"], _ctx(vfs))
    assert vfs.find("/b.txt").content == "hi"
    with pytest.raises(Exception):
        vfs.find("/a.txt")


def test_mv_moves_file_into_directory():
    """mv moves a file into an existing directory."""
    vfs = Vfs()
    vfs.create_file("/a.txt")
    vfs.mkdir("/dir")
    cmd_mv(["/a.txt", "/dir"], _ctx(vfs))
    assert vfs.find("/dir/a.txt").name == "a.txt"


def test_mv_rejects_root():
    """The root cannot be moved."""
    vfs = Vfs()
    with pytest.raises(CommandError):
        cmd_mv(["/", "/x"], _ctx(vfs))


def test_mv_missing_operand():
    """mv requires two operands."""
    with pytest.raises(CommandError):
        cmd_mv(["/a"], _ctx())


def test_mv_too_many_arguments():
    """mv rejects three operands."""
    with pytest.raises(CommandError):
        cmd_mv(["/a", "/b", "/c"], _ctx())


def test_mv_directory_into_itself():
    """Moving a directory into itself is refused."""
    vfs = Vfs()
    vfs.mkdir("/a/b")
    with pytest.raises(CommandError):
        cmd_mv(["/a", "/a/b"], _ctx(vfs))


def test_mv_overwrites_file():
    """Moving onto an existing file replaces it."""
    vfs = Vfs()
    vfs.create_file("/a.txt", content="A")
    vfs.create_file("/b.txt", content="B")
    cmd_mv(["/a.txt", "/b.txt"], _ctx(vfs))
    assert vfs.find("/b.txt").content == "A"
