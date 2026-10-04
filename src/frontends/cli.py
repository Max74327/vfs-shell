"""Console frontend — works without GUI and without tkinter."""
import sys

from src.frontends.base import Frontend


class CliFrontend(Frontend):
    """REPL over standard input/output."""

    def write(self, text: str) -> None:
        """Prints a line to stdout."""
        sys.stdout.write(text + "\n")
        sys.stdout.flush()

    def run(self) -> None:
        """Runs the input loop until exit or EOF."""
        self.shell.banner()
        try:
            while True:
                try:
                    line = input(self.shell.prompt)
                except EOFError:
                    self.shell.write("")
                    break
                if not self.shell.process(line):
                    break
        except KeyboardInterrupt:
            self.shell.write("")
