"""Shell core: parsing, dispatch, output via a Frontend."""
from src.parser import parse, ParseError
from src.commands import (
    COMMANDS, CommandContext, CommandResult, CommandError,
)
from src.frontends.base import Frontend
from src.vfs import Vfs

ROOT_PATH = "/"


class Shell:
    """REPL core independent of any concrete presentation."""

    def __init__(self, frontend: Frontend):
        """Creates the core on top of the given frontend."""
        self.fe = frontend
        self.vfs = Vfs()
        self.cwd = ROOT_PATH

    def attach_vfs(self, vfs) -> None:
        """Attaches the loaded VFS to the shell."""
        self.vfs = vfs

    @property
    def prompt(self) -> str:
        """Prompt string used by the frontend."""
        return self.fe.prompt

    def write(self, text: str) -> None:
        """Proxies output to the frontend."""
        self.fe.write(text)

    def banner(self) -> None:
        """Prints the greeting on startup."""
        self.write(f"Welcome to VFS: {self.fe.vfs_name}")
        self.write("Type 'exit' to quit.\n")

    def process(self, line: str) -> bool:
        """Processes one line; False means the shell should stop."""
        self.write(self.prompt + line)
        try:
            name, args = parse(line)
        except ParseError as exc:
            self.write(f"Parse error: {exc}")
            return True

        if name is None:
            return True

        handler = COMMANDS.get(name)
        if handler is None:
            self.write(f"{name}: command not found")
            return True

        ctx = CommandContext(vfs=self.vfs, cwd=self.cwd)
        try:
            result = handler(args, ctx)
        except CommandError as exc:
            self.write(str(exc))
            return True

        if not isinstance(result, CommandResult):
            result = CommandResult(output=str(result))

        if result.output:
            self.write(result.output)
        if result.new_cwd is not None:
            self.cwd = result.new_cwd
        if result.exit:
            self.write("Bye.")
            return False
        return True
