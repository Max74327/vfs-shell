"""Shell core: parsing, command dispatch, output via Frontend."""
from src.parser import parse, ParseError
from src.commands import COMMANDS, EXIT_SENTINEL
from src.frontends.base import Frontend


class Shell:
    """REPL core independent of any concrete presentation."""

    def __init__(self, frontend: Frontend):
        """Creates the core on top of the given frontend."""
        self.fe = frontend

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
        """
        Processes a single line.

        Returns False if the shell is terminating, otherwise True.
        """
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

        result = handler(args)
        if result == EXIT_SENTINEL:
            self.write("Bye.")
            return False

        self.write(result)
        return True
