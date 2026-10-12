"""Tests for the chmod command."""
import pytest

from src.commands import CommandContext, CommandError
from src.commands.chmod import cmd_chmod
from src.vfs import Vfs


def _ctx(vfs=None, cwd="/"):
    vfs = vfs or Vfs()
    return CommandContext(vfs=vfs, cwd=cwd)


def test_chmod_octal():
    """chmod with an octal mode sets the mode directly."""
    vfs = Vfs()
    vfs.create_file("/a.txt")
    cmd_chmod(["600", "/a.txt"], _ctx(vfs))
    assert vfs.find("/a.txt").mode == 0o600


def test_chmod_octal_with_special_bits():
    """chmod accepts sticky bit (1xxx)."""
    vfs = Vfs()
    vfs.mkdir("/tmp")
    cmd_chmod(["1777", "/tmp"], _ctx(vfs))
    assert vfs.find("/tmp").mode == 0o1777


def test_chmod_symbolic_add():
    """chmod u+x adds execute for the owner."""
    vfs = Vfs()
    vfs.create_file("/a.txt", mode=0o644)
    cmd_chmod(["u+x", "/a.txt"], _ctx(vfs))
    assert vfs.find("/a.txt").mode == 0o744


def test_chmod_symbolic_remove():
    """chmod go-w removes write for group and other."""
    vfs = Vfs()
    vfs.create_file("/a.txt", mode=0o666)
    cmd_chmod(["go-w", "/a.txt"], _ctx(vfs))
    assert vfs.find("/a.txt").mode == 0o644


def test_chmod_symbolic_assign():
    """chmod a=r resets every group to read-only."""
    vfs = Vfs()
    vfs.create_file("/a.txt", mode=0o755)
    cmd_chmod(["a=r", "/a.txt"], _ctx(vfs))
    assert vfs.find("/a.txt").mode == 0o444


def test_chmod_multiple_targets():
    """chmod applies to every listed target."""
    vfs = Vfs()
    vfs.create_file("/a.txt")
    vfs.create_file("/b.txt")
    cmd_chmod(["600", "/a.txt", "/b.txt"], _ctx(vfs))
    assert vfs.find("/a.txt").mode == 0o600
    assert vfs.find("/b.txt").mode == 0o600


def test_chmod_invalid_mode():
    """An invalid mode raises CommandError."""
    vfs = Vfs()
    vfs.create_file("/a.txt")
    with pytest.raises(CommandError):
        cmd_chmod(["9x9", "/a.txt"], _ctx(vfs))


def test_chmod_missing_target():
    """chmod on a missing path raises CommandError."""
    with pytest.raises(CommandError):
        cmd_chmod(["644", "/nope"], _ctx())
