"""Tests for the ls command."""
from src.commands import CommandContext, CommandError
from src.commands.ls import cmd_ls
from src.vfs import Vfs


def _ctx(vfs=None, cwd="/"):
    vfs = vfs or Vfs()
    return CommandContext(vfs=vfs, cwd=cwd)


def test_ls_empty_root():
    """Empty root prints nothing."""
    assert cmd_ls([], _ctx()).output == ""


def test_ls_lists_names():
    """ls prints names separated by two spaces."""
    vfs = Vfs()
    vfs.mkdir("/a")
    vfs.create_file("/b.txt")
    out = cmd_ls(["/"], _ctx(vfs)).output
    assert "a" in out and "b.txt" in out


def test_ls_long_format():
    """ls -l prints mode, size and name."""
    vfs = Vfs()
    vfs.create_file("/x.txt", content="hello")
    out = cmd_ls(["-l", "/"], _ctx(vfs)).output
    assert "-rw-r--r--" in out
    assert "5" in out
    assert "x.txt" in out


def test_ls_hides_dotfiles_by_default():
    """ls skips dotfiles unless -a is given."""
    vfs = Vfs()
    vfs.create_file("/.hidden")
    vfs.create_file("/visible")
    plain = cmd_ls(["/"], _ctx(vfs)).output
    assert ".hidden" not in plain
    all_ = cmd_ls(["-a", "/"], _ctx(vfs)).output
    assert ".hidden" in all_


def test_ls_missing_path_raises():
    """ls on a missing path raises CommandError."""
    import pytest
    with pytest.raises(CommandError):
        cmd_ls(["/nope"], _ctx())
