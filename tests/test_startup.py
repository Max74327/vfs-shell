"""Tests for the startup script runner."""
import pytest

from src.startup import StartupError, read_script, run_startup


class FakeShell:
    """Minimal shell stub that records the lines it receives."""

    def __init__(self, stop_after=None):
        """Creates a stub that stops after the given line."""
        self.lines = []
        self.stop_after = stop_after

    def process(self, line):
        """Records the line and reports whether to continue."""
        self.lines.append(line)
        if self.stop_after is not None and line == self.stop_after:
            return False
        return True


def test_read_script_strips_comments(tmp_path):
    """Comments and blank lines are skipped."""
    path = tmp_path / "s.sh"
    path.write_text(
        "# a comment\n"
        "ls\n"
        "\n"
        "# another comment\n"
        "cd /tmp\n",
        encoding="utf-8",
    )
    assert read_script(str(path)) == ["ls", "cd /tmp"]


def test_read_script_missing_raises(tmp_path):
    """A missing script raises StartupError."""
    with pytest.raises(StartupError):
        read_script(str(tmp_path / "missing.sh"))


def test_run_startup_feeds_lines(tmp_path):
    """run_startup forwards every line to the shell."""
    path = tmp_path / "s.sh"
    path.write_text("ls\ncd\n", encoding="utf-8")
    shell = FakeShell()
    assert run_startup(shell, str(path)) is True
    assert shell.lines == ["ls", "cd"]


def test_run_startup_stops_on_exit(tmp_path):
    """run_startup stops as soon as the shell returns False."""
    path = tmp_path / "s.sh"
    path.write_text("ls\nexit\ncd\n", encoding="utf-8")
    shell = FakeShell(stop_after="exit")
    assert run_startup(shell, str(path)) is False
    assert shell.lines == ["ls", "exit"]
