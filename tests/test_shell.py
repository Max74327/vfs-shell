"""Tests for the Shell core using a fake frontend."""
from src.frontends.base import Frontend
from src.shell import Shell


class FakeFrontend(Frontend):
    """Collects all output into a list for assertions."""

    def __init__(self):
        """Initialises an empty output log."""
        super().__init__("test", "user@test:$ ")
        self.lines = []

    def write(self, text: str) -> None:
        """Records a line."""
        self.lines.append(text)

    def run(self) -> None:
        """Not used in tests."""

    def joined(self) -> str:
        """Returns the whole output as a single string."""
        return "\n".join(self.lines)


def _make_shell():
    """Creates a Shell with a fake frontend."""
    fe = FakeFrontend()
    return Shell(fe), fe


def test_empty_line_keeps_running():
    """An empty line does not terminate the shell."""
    shell, _ = _make_shell()
    assert shell.process("") is True


def test_unknown_command():
    """An unknown command prints an error."""
    shell, fe = _make_shell()
    shell.process("foo bar")
    assert "foo: command not found" in fe.joined()


def test_parse_error_reported():
    """A parser error is shown to the user."""
    shell, fe = _make_shell()
    shell.process('ls "unterminated')
    assert "Parse error" in fe.joined()


def test_exit_stops_shell():
    """exit returns False from process."""
    shell, fe = _make_shell()
    assert shell.process("exit") is False
    assert "Bye." in fe.joined()


def test_ls_dispatch():
    """ls is routed to the stub command."""
    shell, fe = _make_shell()
    shell.process('ls "a b"')
    assert "ls: stub command" in fe.joined()
    assert "'a b'" in fe.joined()
