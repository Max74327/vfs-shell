"""Frontend interface. The shell core talks to it only through this."""
from abc import ABC, abstractmethod


class Frontend(ABC):
    """
    Contract between the shell core and a presentation.

    The core calls write(); the input loop lives in the frontend
    (method run) and forwards lines to Shell.process().
    """

    def __init__(self, vfs_name: str, prompt: str):
        """Stores the VFS name and the prompt string."""
        self.vfs_name = vfs_name
        self.prompt = prompt
        self.shell = None

    def attach(self, shell) -> None:
        """Attaches the shell core to this frontend."""
        self.shell = shell

    @abstractmethod
    def write(self, text: str) -> None:
        """Writes a line of text (without a trailing newline)."""

    @abstractmethod
    def run(self) -> None:
        """Runs the input loop."""
