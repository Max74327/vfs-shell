"""Tests for the head command."""
import pytest

from src.commands import CommandContext, CommandError
from src.commands.head import cmd_head
from src.vfs import Vfs


def _ctx(vfs, cwd="/"):
    return CommandContext(vfs=vfs, cwd=cwd)


def test_head_default_ten_lines():
    """head prints up to 10 lines by default."""
    vfs = Vfs()
    content = "\n".join(f"line{i}" for i in range(15))
    vfs.create_file("/f.txt", content=content)
    out = cmd_head(["/f.txt"], _ctx(vfs)).output
    assert out.count("\n") == 9
    assert "line9" in out
    assert "line10" not in out


def test_head_n_flag():
    """head -n 3 prints only 3 lines."""
    vfs = Vfs()
    content = "\n".join(f"l{i}" for i in range(10))
    vfs.create_file("/f.txt", content=content)
    out = cmd_head(["-n", "3", "/f.txt"], _ctx(vfs)).output
    assert out.splitlines() == ["l0", "l1", "l2"]


def test_head_binary_raises():
    """head on a binary file raises CommandError."""
    vfs = Vfs()
    vfs.create_file("/bin", content="\x00\x01", binary=True)
    with pytest.raises(CommandError):
        cmd_head(["/bin"], _ctx(vfs))


def test_head_directory_raises():
    """head on a directory raises CommandError."""
    vfs = Vfs()
    vfs.mkdir("/dir")
    with pytest.raises(CommandError):
        cmd_head(["/dir"], _ctx(vfs))
