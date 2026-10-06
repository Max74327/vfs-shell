# VFS Shell

Emulator of a UNIX-like command shell with an in-memory virtual file
system (VFS), a PyQt6 GUI, a console frontend, JSON configuration and
startup scripts.

---

## 1. Overview

VFS Shell reproduces the look and feel of a UNIX-like command line:

* interactive REPL with a prompt like `user@vfs20:$ `;
* quote-aware argument parser;
* a virtual file system stored entirely in memory and loaded from a
  CSV description (stage 3);
* graphical interface (PyQt6) and a console interface, sharing the
  same core;
* configuration via a JSON file and command-line flags (stage 2);
* startup scripts that are executed at launch, printing both the
  input and the output to imitate a dialogue (stage 2).

The emulator never modifies the physical file system: every operation
on files and directories happens in memory.

### Architecture

```
   ┌──────────────────────────┐
   │        Frontends         │   PyQt6 GUI, console
   │  (src/frontends/*.py)    │
   └────────────┬─────────────┘
                │ Frontend API (write / run / attach)
   ┌────────────▼─────────────┐
   │          Shell           │   REPL, dispatch
   │      (src/shell.py)      │
   └───┬──────────┬───────────┘
       │          │
 ┌─────▼───┐  ┌───▼───────┐
 │ Parser  │  │ Commands  │
 │parser.py│  │commands.py│
 └─────────┘  └────┬──────┘
                   │
              ┌────▼────┐
              │   VFS   │  in-memory tree, loaded from CSV
              │ vfs.py  │  (stage 3)
              └─────────┘

   Configuration (stage 2): src/config.py, src/startup.py
```

* **Core** — knows nothing about how input and output are performed.
* **Frontends** — implement the `Frontend` interface and provide
  either a graphical (PyQt6) or a console REPL.
* **VFS** — a tree of nodes (`Directory`, `File`) kept in memory;
  loaded once from a CSV file, mutated only in memory (stage 3).
* **Configuration** — CLI flags + JSON file, resolved with a strict
  priority rule (file wins over CLI).

### Project layout

```
vfs_shell/
├── README.md
├── .gitignore
├── run.sh                        # launcher (GUI / CLI / tests / lint / clean)
├── configs/
│   └── example.json              # example JSON configuration
├── scripts/
│   ├── run-default.sh            # launcher: no config, CLI mode
│   ├── run-cli.sh                # launcher: CLI with a startup script
│   ├── run-gui.sh                # launcher: GUI with a config file
│   ├── run-override.sh           # launcher: CLI + config, shows priority
│   └── startup-all-commands.sh   # startup script covering all commands
├── src/
│   ├── __init__.py
│   ├── main.py                   # entry point, wires config and frontends
│   ├── parser.py                 # quote-aware tokenizer
│   ├── shell.py                  # REPL core
│   ├── commands.py               # command implementations
│   ├── config.py                 # CLI + JSON configuration
│   ├── startup.py                # startup script runner
│   ├── vfs.py                    # in-memory VFS (stage 3)
│   └── frontends/
│       ├── __init__.py
│       ├── base.py               # Frontend abstraction
│       ├── cli.py                # console frontend
│       └── gui.py                # PyQt6 frontend
└── tests/
    ├── __init__.py
    ├── test_parser.py
    ├── test_commands.py
    ├── test_shell.py
    ├── test_config.py
    └── test_startup.py
```

---

## 2. Modules

### 2.1. `src/parser.py`

* `ParseError` — raised on an unterminated quote.
* `tokenize(line)` — splits a line into tokens:
  * spaces and tabs separate tokens outside quotes;
  * single and double quotes preserve their content as one token;
  * a backslash escapes the next character (outside single quotes);
  * adjacent fragments are concatenated: `ab"cd"ef` → `abcdef`;
  * an empty quote pair `""` produces an empty token;
  * an unterminated quote raises `ParseError`.
* `parse(line)` — returns `(command_name, arguments)`; for an empty
  line — `(None, [])`.

### 2.2. `src/commands.py`

* `cmd_ls(args)` — prints its name and the received arguments.
* `cmd_cd(args)` — prints the target directory; with more than one
  argument returns an error message.
* `cmd_exit(args)` — returns the `EXIT_SENTINEL` marker.
* `COMMANDS` — a dict mapping command names to handlers.

### 2.3. `src/shell.py`

Class `Shell` — the REPL core:

* `Shell(frontend)` — constructor.
* `prompt` — property exposing the frontend prompt.
* `write(text)` — proxies output to the frontend.
* `banner()` — prints the greeting.
* `process(line)` — processes one line; returns `False` when the
  shell should terminate.

### 2.4. `src/config.py`

* `Config` — dataclass with resolved settings:
  * `vfs_path`, `startup_script`, `config_path`, `cli_mode`;
  * `sources` — dict recording where each value came from
    (`file`, `cli`, or `default`).
* `ConfigError` — raised when the config file is missing or malformed.
* `build_arg_parser()` — constructs the `argparse` parser.
* `resolve_config(argv)` — parses CLI flags and JSON file, applies
  priority (file wins over CLI), returns `Config`.
* `format_debug(cfg)` — human-readable dump printed at startup.

### 2.5. `src/startup.py`

* `StartupError` — raised when the script cannot be read.
* `read_script(path)` — reads a startup script, strips comments
  (`#` and `#!`) and blank lines.
* `run_startup(shell, path)` — feeds every line to the shell; prints
  both the input and the output, imitating a dialogue. Returns
  `False` if the shell terminated.

### 2.6. `src/frontends/base.py`

Abstract class `Frontend`:

* `__init__(vfs_name, prompt)` — stores the VFS name and prompt.
* `attach(shell)` — binds the shell core to this frontend.
* `write(text)` — output a line (abstract).
* `run()` — input loop (abstract).

### 2.7. `src/frontends/cli.py`

`CliFrontend` — writes to `stdout`, reads from `stdin`, handles
`Ctrl+C` and `EOF`.

### 2.8. `src/frontends/gui.py`

`GuiFrontend` — a PyQt6 window:

* window title `VFS: <name>`;
* `QPlainTextEdit` for output (read-only, monospaced);
* `QLineEdit` subclass `HistoryLineEdit` for input;
* command history via ↑ / ↓;
* native Wayland support through the Qt platform plugin.

### 2.9. `src/main.py`

* `main(argv)` — resolves the configuration, picks the frontend,
  prints the debug dump, runs the startup script, and enters the
  frontend loop.
* Falls back to the console frontend when PyQt6 is unavailable.

### 2.10. Settings

In `src/main.py`:

* `VFS_NAME = "vfs20"` — name shown in the window title and prompt;
* `PROMPT = "user@vfs20:$ "` — prompt string.

In `src/config.py`:

* `DEFAULT_CONFIG_PATH = "config.json"`;
* `CONFIG_KEY_VFS_PATH = "vfs_path"`;
* `CONFIG_KEY_STARTUP = "startup_script"`.

In `src/commands.py`:

* `MAX_ARGS_CD = 1`;
* `DEFAULT_CD_TARGET = "~"`.

---

## 3. Configuration

### 3.1. Command-line flags

```
--vfs PATH        path to the VFS CSV file
--startup PATH    path to the startup script
--config PATH     path to the JSON configuration file
--cli             start without GUI
```

### 3.2. JSON configuration file

```json
{
  "vfs_path": "data/vfs-minimal.csv",
  "startup_script": "scripts/startup-all-commands.sh"
}
```

### 3.3. Priority rule

Values from the **JSON file override values from the command line**.
If a key is absent in the file, the CLI value is used. If neither
is present, the default (empty) is used.

The debug dump printed at startup shows both the resolved value and
its origin:

```
Configuration:
  vfs_path        = data/vfs-minimal.csv  [file]
  startup_script  = scripts/startup-all-commands.sh  [file]
  config_path     = configs/example.json
  cli_mode        = False
```

Origins: `file`, `cli`, `default`.

### 3.4. Startup scripts

* Executed at launch, one line at a time.
* Lines starting with `#` (including `#!`) and blank lines are
  skipped.
* Both the input line and the output are printed, imitating an
  interactive session.

---

## 4. Requirements

* Python 3.10+;
* `bash` — to run `run.sh` (Linux/macOS; on Windows use WSL or Git Bash);
* `python-pyqt6` — for the GUI (native Wayland on KDE Plasma);
* `pytest` and `pycodestyle` — for tests and PEP 8 checks.

Install on Arch Linux:

```bash
sudo pacman -S python python-pyqt6 bash python-pytest python-pycodestyle
```

Install on Debian/Ubuntu:

```bash
sudo apt install python3 python3-pyqt6 bash python3-pytest python3-pycodestyle
```

If PyQt6 is not installed, the application automatically falls back
to the console frontend.

---

## 5. Build and test commands

```bash
./run.sh          # GUI (PyQt6), no config
./run.sh cli      # console mode, no config
./run.sh test     # run pytest
./run.sh lint     # pycodestyle --max-line-length=80 src tests
./run.sh clean    # remove __pycache__ and .pytest_cache
./run.sh help     # usage message
```

Direct invocation via Python:

```bash
python3 -m src.main
python3 -m src.main --cli
python3 -m src.main --config configs/example.json
python3 -m src.main --cli --startup scripts/startup-all-commands.sh
```

Host-side launchers in `scripts/`:

```bash
./scripts/run-default.sh     # CLI, no config
./scripts/run-cli.sh         # CLI + startup script
./scripts/run-gui.sh         # GUI + JSON config
./scripts/run-override.sh    # CLI + config, demonstrates priority
```

---

## 6. Usage examples

### 6.1. REPL basics

```
user@vfs20:$ ls
ls: stub command
  arguments received: 0
  arguments: []
user@vfs20:$ ls -l /home "my folder"
ls: stub command
  arguments received: 3
  arguments: ['-l', '/home', 'my folder']
user@vfs20:$ cd
cd: stub command
  target directory: '~'
user@vfs20:$ cd "My Documents"
cd: stub command
  target directory: 'My Documents'
```

### 6.2. Error handling

```
user@vfs20:$ cd a b
cd: too many arguments (received 2)
  arguments: ['a', 'b']
user@vfs20:$ ls "unterminated
Parse error: unterminated quote
user@vfs20:$ foo bar
foo: command not found
user@vfs20:$ exit
Bye.
```

### 6.3. Startup script

`scripts/startup-all-commands.sh`:

```bash
# Startup script for stage 2 testing.
ls
ls -l /home "my folder"
cd
cd "My Documents"
cd a b
ls "unterminated
foo bar
exit
```

Running it reproduces a complete dialogue, including errors.

### 6.4. Configuration priority

Given `configs/example.json`:

```json
{
  "vfs_path": "data/vfs-minimal.csv",
  "startup_script": "scripts/startup-all-commands.sh"
}
```

Then:

```bash
python3 -m src.main --vfs ignored.csv \
                    --config configs/example.json
```

resolves to `vfs_path = data/vfs-minimal.csv [file]` — the JSON file
wins over the command line.

### 6.5. Configuration errors

```
$ python3 -m src.main --config /no/such.json
Configuration error: config file not found: /no/such.json
$ echo $?
2
```

```
$ python3 -m src.main --cli --startup /no/such.sh
Startup error: startup script not found: /no/such.sh
user@vfs20:$
```

---

## 7. Roadmap

| Stage | Goal                                                | Status  |
|-------|-----------------------------------------------------|---------|
| 1     | REPL: GUI, parser, stubs, `exit`                    | done    |
| 2     | Configuration: CLI + JSON + startup scripts         | done    |
| 3     | VFS: in-memory tree loaded from CSV                 | planned |
| 4     | Core commands: `ls`, `cd`, `who`, `head`, `tree`    | planned |
| 5     | Extra commands: `mv`, `chmod`                       | planned |

Each stage is committed separately using Conventional Commits, e.g.:

```
feat(frontends): replace tkinter GUI with PyQt6
feat(config): add CLI and JSON configuration with priority
feat(startup): add startup script runner with comments
feat(main): wire configuration and startup scripts
chore(scripts): add host-side launchers and example config
test(config): cover priority rules and script runner
docs: describe stage 2 configuration and startup scripts
```

---

## 8. Repository conventions

* Source code lives in `src/`, tests in `tests/`.
* Launcher is `run.sh`; host-side scripts live in `scripts/`.
* Example configuration lives in `configs/`.
* No archives, binaries, build artefacts, or editor-specific files
  (see `.gitignore`).
* Code style: PEP 8, lines ≤ 80 characters, functions ≤ 40 lines,
  docstrings on every module, class, and public function.
* No magic numbers in comparisons; named constants everywhere.
* Commit messages follow Conventional Commits.

---

## 9. License

Distributed under the MIT License. See `LICENSE` for details.
