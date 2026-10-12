"""Tests for the tree command."""
import pytest

from src.commands import CommandContext, CommandError
from src.commands.tree import cmd_tree
from src.vfs import Vfs


def _ctx(vfs, cwd="/"):
    return CommandContext(vfs=vfs, cwd=cwd)


def test_tree_prints_paths_and_stats():
    """tree prints the subtree and a summary line."""
    vfs = Vfs()
    vfs.mkdir("/a/b")
    vfs.create_file("/a/b/c.txt")
    vfs.create_file("/a/d.txt")
    out = cmd_tree(["/a"], _ctx(vfs)).output
    assert "b" in out and "c.txt" in out and "d.txt" in out
    assert "directories" in out and "files" in out


def test_tree_depth_limit():
    """tree -L 1 shows only the first level."""
    vfs = Vfs()
    vfs.mkdir("/a/b/c")
    out = cmd_tree(["-L", "1", "/a"], _ctx(vfs)).output
    assert "b" in out
    assert "c" not in out


def test_tree_missing_path_raises():
    """tree on a missing path raises CommandError."""
    with pytest.raises(CommandError):
        cmd_tree(["/nope"], _ctx(Vfs()))
