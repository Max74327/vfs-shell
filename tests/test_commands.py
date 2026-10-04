"""Tests for the stub commands."""
from src.commands import cmd_ls, cmd_cd, cmd_exit, EXIT_SENTINEL


def test_ls_no_args():
    """ls with no arguments reports zero arguments."""
    out = cmd_ls([])
    assert "stub command" in out
    assert "arguments received: 0" in out


def test_ls_with_args():
    """ls with arguments prints them."""
    out = cmd_ls(["-l", "/home"])
    assert "'-l'" in out
    assert "'/home'" in out


def test_cd_default():
    """cd with no arguments goes to the home directory."""
    assert "target directory: '~'" in cmd_cd([])


def test_cd_target():
    """cd with one argument uses it as the target."""
    assert "target directory: 'My Documents'" in cmd_cd(["My Documents"])


def test_cd_too_many():
    """cd with two arguments returns an error."""
    out = cmd_cd(["a", "b"])
    assert "too many arguments" in out


def test_exit_sentinel():
    """exit returns the sentinel marker."""
    assert cmd_exit([]) == EXIT_SENTINEL
