"""PyQt6 GUI frontend. Imported only when GUI is requested."""
import sys

from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont, QKeyEvent
from PyQt6.QtWidgets import (
    QApplication,
    QLineEdit,
    QMainWindow,
    QPlainTextEdit,
    QVBoxLayout,
    QWidget,
)

from src.frontends.base import Frontend

WINDOW_W = 820
WINDOW_H = 520
FONT_FAMILY = "Monospace"
FONT_SIZE = 11
BG_COLOR = "#1e1e1e"
FG_COLOR = "#d4d4d4"
CLOSE_DELAY_MS = 50


class HistoryLineEdit(QLineEdit):
    """Input field with up/down history navigation."""

    def __init__(self, parent=None):
        """Stores the parent and prepares the history buffer."""
        super().__init__(parent)
        self.history: list = []
        self.hist_idx = 0

    def remember(self, line: str) -> None:
        """Appends a non-empty line to history."""
        if line.strip():
            self.history.append(line)
        self.hist_idx = len(self.history)

    def key_press_event(self, event: QKeyEvent) -> None:
        """Handles arrow keys for history navigation."""
        key = event.key()
        if key == Qt.Key.Key_Up:
            self._hist_prev()
            return
        if key == Qt.Key.Key_Down:
            self._hist_next()
            return
        super().keyPressEvent(event)

    def _hist_prev(self) -> None:
        """Moves to the previous command in history."""
        if self.history and self.hist_idx > 0:
            self.hist_idx -= 1
            self.setText(self.history[self.hist_idx])

    def _hist_next(self) -> None:
        """Moves to the next command in history."""
        if self.hist_idx < len(self.history) - 1:
            self.hist_idx += 1
            self.setText(self.history[self.hist_idx])
        else:
            self.hist_idx = len(self.history)
            self.clear()


class GuiFrontend(Frontend):
    """Qt-based frontend implementing the Frontend interface."""

    def __init__(self, vfs_name: str, prompt: str):
        """Creates the window, output area, and input field."""
        super().__init__(vfs_name, prompt)
        self.app = QApplication.instance() or QApplication(sys.argv)

        self.window = QMainWindow()
        self.window.setWindowTitle(f"VFS: {vfs_name}")
        self.window.resize(WINDOW_W, WINDOW_H)

        central = QWidget()
        layout = QVBoxLayout(central)
        layout.setContentsMargins(6, 6, 6, 6)
        layout.setSpacing(6)

        font = QFont(FONT_FAMILY, FONT_SIZE)

        self.output = QPlainTextEdit()
        self.output.setReadOnly(True)
        self.output.setFont(font)
        self.output.setStyleSheet(
            f"background:{BG_COLOR}; color:{FG_COLOR};"
        )
        layout.addWidget(self.output)

        self.entry = HistoryLineEdit()
        self.entry.setFont(font)
        self.entry.setStyleSheet(
            f"background:{BG_COLOR}; color:{FG_COLOR};"
        )
        self.entry.returnPressed.connect(self._on_enter)
        layout.addWidget(self.entry)

        self.window.setCentralWidget(central)

    def write(self, text: str) -> None:
        """Appends a line to the output area."""
        self.output.appendPlainText(text)

    def run(self) -> None:
        """Shows the window and enters the Qt event loop."""
        self.shell.banner()
        self.window.show()
        self.window.raise_()
        self.window.activateWindow()
        self.entry.setFocus(Qt.FocusReason.OtherFocusReason)
        self.app.exec()

    def _on_enter(self) -> None:
        """Handles Enter: sends the line to the shell core."""
        line = self.entry.text()
        self.entry.clear()
        self.entry.remember(line)
        if not self.shell.process(line):
            self.app.quit()
