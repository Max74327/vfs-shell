# VFS Shell

A teaching-oriented emulator of a UNIX-like command shell written in
Python 3.10+.

Stage 1 — minimal REPL prototype: interactive dialogue, an argument
parser with quote handling, stub commands `ls`, `cd`, and the `exit`
command. The GUI is isolated in a separate module, so the application
runs without it as well.

---

## 1. Overview

VFS Shell is split into a core and one of several presentations:

* **Core** (`src/shell.py`, `src/parser.py`, `src/commands.py`) — knows
  nothing about how input and output are performed.
* **Frontends** (`src/frontends/`) — implement the `Frontend` interface
  and provide either a graphical interface (PyQt6, native Wayland) or
  a console REPL.

Because of this separation the application can run without a GUI:
just pass `--cli`, or run it in an environment where `tkinter` is not
available — the launcher automatically falls back to the console
frontend.

### Project layout

```
vfs_shell/
├── README.md
├── .gitignore
├── run.sh              # launcher (GUI / CLI / tests / lint / clean)
├── src/
│   ├── __init__.py
│   ├── parser.py
│   ├── commands.py
│   ├── shell.py
│   ├── main.py
│   └── frontends/
│       ├── __init__.py
│       ├── base.py
│       ├── cli.py
│       └── gui.py
└── tests/
    ├── __init__.py
    ├── test_parser.py
    ├── test_commands.py
    └── test_shell.py
```

---

## 2. Modules, functions, and settings

### 2.1. `src/parser.py`

* `ParseError` — exception raised on an unterminated quote.
* `tokenize(line: str) -> list[str]` — splits a line into tokens.
  Rules:
  * spaces and tabs separate tokens outside quotes;
  * single and double quotes preserve their content as one token,
    including spaces;
  * a backslash escapes the next character (outside single quotes);
  * adjacent fragments are concatenated: `ab"cd"ef` → `abcdef`;
  * an empty quote pair `""` produces an empty token;
  * an unterminated quote raises `ParseError`.
* `parse(line: str) -> (str | None, list[str])` — returns
  `(command_name, arguments)`; for an empty line — `(None, [])`.

### 2.2. `src/commands.py`

* `cmd_ls(args)` — prints the command name and the received arguments.
* `cmd_cd(args)` — prints the target directory; with more than one
  argument returns an error message.
* `cmd_exit(args)` — returns the `EXIT_SENTINEL` marker.
* `COMMANDS` — a dict mapping command names to their handlers.
* Constants: `MAX_ARGS_CD = 1`, `DEFAULT_CD_TARGET = "~"`.

### 2.3. `src/shell.py`

Class `Shell` — the REPL core. Methods:

* `Shell(frontend)` — constructor.
* `prompt` — property exposing the frontend's prompt string.
* `write(text)` — proxies output to the frontend.
* `banner()` — prints the greeting.
* `process(line) -> bool` — processes a single line; `False` means the
  shell should terminate.

### 2.4. `src/frontends/base.py`

Abstract class `Frontend`:

* `__init__(vfs_name, prompt)` — stores the VFS name and the prompt.
* `write(text)` — output a line (abstract).
* `run()` — input loop (abstract).

### 2.5. `src/frontends/cli.py`

`CliFrontend` — writes to `stdout`, reads from `stdin`, gracefully
handles `Ctrl+C` and `EOF`.


### 2.6. `src/frontends/gui.py`

```markdown
`GuiFrontend` — a PyQt6 window:

* window title `VFS: <name>`;
* `QPlainTextEdit` for output (read-only, monospaced);
* `QLineEdit` subclass `HistoryLineEdit` for input;
* command history via ↑ / ↓ arrow keys;
* native Wayland support through the Qt platform plugin.

### 2.7. `src/main.py`

* `main(argv=None) -> int` — entry point, parses arguments.
* Flag `--cli` — start without a GUI.
* Flag `-h/--help` — show help.

### 2.8. Settings

In `src/main.py`:

* `VFS_NAME = "vfs20"` — virtual FS name (used in the window title);
* `PROMPT = "user@vfs20:$ "` — prompt string.

In `src/frontends/gui.py`:

* `WINDOW_W`, `WINDOW_H` — window size;
* `FONT_FAMILY`, `FONT_SIZE` — font settings;
* `BG_COLOR`, `FG_COLOR` — colour scheme.

In `src/commands.py`:

* `MAX_ARGS_CD = 1` — maximum number of arguments for `cd`;
* `DEFAULT_CD_TARGET = "~"` — default `cd` target.

---

## 3. Build and test commands

* Python 3.10+;
* `bash` — to run `run.sh` (Linux/macOS; on Windows use WSL or Git Bash);
* `python-pyqt6` — for the GUI (native Wayland on KDE Plasma);
* `pytest` and `pycodestyle` — for tests and PEP8 checks.

Install:

```bash
sudo pacman -S python python-pyqt6 bash python-pytest python-pycodestyle
```

### 3.2. Running the application

```bash
./run.sh          # GUI
./run.sh cli      # console mode
```

Or directly, without the launcher:

```bash
python3 -m src.main
python3 -m src.main --cli
```

### 3.3. Tests, lint, cleanup

```bash
./run.sh test     # run pytest tests
./run.sh lint     # pycodestyle --max-line-length=80 src tests
./run.sh clean    # remove __pycache__ and .pytest_cache
./run.sh help     # usage message
```
