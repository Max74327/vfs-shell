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
* **VFS** — a tree of nodes (`Node`) kept in memory; loaded once from
  a CSV file, mutated only in memory (stage 3).
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
├── data/
│   ├── vfs-minimal.csv           # one directory and one file
│   ├── vfs-several-files.csv     # several files at the same level
│   └── vfs-nested.csv            # at least three levels + binary
├── scripts/
│   ├── run-default.sh            # launcher: no config, CLI mode
│   ├── run-cli.sh                # launcher: CLI with a startup script
│   ├── run-gui.sh                # launcher: GUI with a config file
│   ├── run-override.sh           # launcher: CLI + config, shows priority
│   ├── run-vfs-minimal.sh        # launcher: minimal VFS
│   ├── run-vfs-several.sh        # launcher: several-files VFS
│   ├── run-vfs-nested.sh         # launcher: nested VFS
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
    ├── test_startup.py
    └── test_vfs.py
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
* `attach_vfs(vfs)` — binds the loaded VFS to the shell.
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
  priority (file wins over CLI), returns `Config`. Falls back to
  `DEFAULT_VFS_PATH = "data/vfs-minimal.csv"` when nothing is given.
* `format_debug(cfg)` — human-readable dump printed at startup.

### 2.5. `src/startup.py`

* `StartupError` — raised when the script cannot be read.
* `read_script(path)` — reads a startup script, strips comments
  (`#` and `#!`) and blank lines.
* `run_startup(shell, path)` — feeds every line to the shell; prints
  both the input and the output, imitating a dialogue. Returns
  `False` if the shell terminated.

### 2.6. `src/vfs.py`

* `Node` — a single node in the VFS tree:
  * `name` — segment name, empty for the root;
  * `is_dir` — true for directories;
  * `mode` — POSIX mode bits as an integer (e.g. `0o644`);
  * `content` — text for files; Latin-1 string for binary files;
  * `binary` — true when the content was decoded from base64;
  * `children` — dict mapping child name to `Node`;
  * `parent` — back-reference to the parent `Node` (or `None` for
    the root).
* `Vfs` — in-memory tree with a single root:
  * `normalize(path)` — returns an absolute path, collapses repeated
    slashes, resolves `.` and `..`, and always starts with `/`;
  * `find(path)` — returns the `Node` at `path` or raises `VfsError`;
  * `mkdir(path, mode)` — creates a directory and any missing parents;
    a no-op for the root; never creates an empty-named child;
  * `create_file(path, content, mode, binary)` — creates or replaces
    a file at `path`, creating parents as needed;
  * `listdir(path)` — returns children sorted directories-first, then
    alphabetically; raises `VfsError` if the path is not a directory;
  * `depth(path)` — maximum nesting depth below a node; `0` for a
    file or an empty directory;
  * `size()` — total number of nodes below the root (root itself is
    not counted).
* `VfsError` — raised on any load or navigation problem.
* `load_vfs(path)` — loads a VFS from a CSV file; raises `VfsError`
  when the file is missing, the header is incomplete, the mode is not
  octal, the base64 payload is malformed, or a node cannot be created.

### 2.7. CSV format

Columns (header is mandatory):

| Column | Required | Description |
|---|---|---|
| `path` | yes | absolute path, `/` as a separator |
| `type` | yes | `file` or `dir` |
| `content` | files only | text, or `base64:<payload>` for binary data |
| `mode` | no | octal, defaults to `644` (file) / `755` (dir) |

Rules:

* Nesting is encoded by the `path` column; intermediate directories
  are created automatically. It is legal to describe only leaves
  (e.g. `/a/b/c/d.txt`) and let the loader build the chain.
* Blank lines and lines whose `path` starts with `#` are ignored.
* Creating a file at an existing path replaces the previous node;
  creating a directory at an existing path reuses it.
* Invalid values raise `VfsError` with a human-readable message:
  * missing required columns in the header;
  * unknown `type` (anything other than `file` or `dir`);
  * non-octal `mode`;
  * malformed base64 payload — validated strictly, so `***` and other
    non-alphabet characters are rejected instead of being silently
    dropped;
  * a file path where a directory with the same name already exists.
* Binary content is marked with a `base64:` prefix. After decoding,
  the bytes are stored as a Latin-1 string in `Node.content` and the
  `Node.binary` flag is set to `True`. `base64.b64decode` is called
  with `validate=True`, so garbage after the prefix is an error and
  not an empty buffer.
* `mode` accepts special bits — setuid (`4xxx`), setgid (`2xxx`) and
  sticky (`1xxx`) — for example `1777` for a shared temporary
  directory. The value is stored as an integer in `Node.mode` and
  rendered by future commands such as `ls -l` and `chmod`.

### 2.8. `src/frontends/base.py`

Abstract class `Frontend`:

* `__init__(vfs_name, prompt)` — stores the VFS name and prompt.
* `attach(shell)` — binds the shell core to this frontend.
* `write(text)` — output a line (abstract).
* `run()` — input loop (abstract).

The frontend is responsible only for input and output. Startup
messages (banner, debug dump, VFS report) are printed once by
`main.py`.

### 2.9. `src/frontends/cli.py`

`CliFrontend` — writes to `stdout`, reads from `stdin`, handles
`Ctrl+C` and `EOF`.

### 2.10. `src/frontends/gui.py`

`GuiFrontend` — a PyQt6 window:

* window title `VFS: <name>`;
* `QPlainTextEdit` for output (read-only, monospaced);
* `QLineEdit` subclass `HistoryLineEdit` for input;
* command history via ↑ / ↓;
* native Wayland support through the Qt platform plugin.

### 2.11. `src/main.py`

* `main(argv)` — resolves the configuration, picks the frontend,
  prints the debug dump, loads the VFS, runs the startup script, and
  enters the frontend loop.
* On a VFS load error, prints `VFS error: ...` and continues with an
  empty VFS, so the shell stays usable.
* Falls back to the console frontend when PyQt6 is unavailable.

### 2.12. Settings

In `src/main.py`:

* `VFS_NAME = "vfs20"` — name shown in the window title and prompt;
* `PROMPT = "user@vfs20:$ "` — prompt string.

In `src/config.py`:

* `DEFAULT_CONFIG_PATH = "config.json"`;
* `DEFAULT_VFS_PATH = "data/vfs-minimal.csv"`;
* `CONFIG_KEY_VFS_PATH = "vfs_path"`;
* `CONFIG_KEY_STARTUP = "startup_script"`.

In `src/vfs.py`:

* `BASE64_PREFIX = "base64:"`;
* `TYPE_FILE = "file"`, `TYPE_DIR = "dir"`;
* `DEFAULT_FILE_MODE = 0o644`, `DEFAULT_DIR_MODE = 0o755`;
* `ROOT_PATH = "/"`.

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
  "vfs_path": "data/vfs-nested.csv",
  "startup_script": "scripts/startup-all-commands.sh"
}
```

### 3.3. Priority rule

Values from the **JSON file override values from the command line**.
If a key is absent in the file, the CLI value is used. If neither
is present, the default is used.

The debug dump printed at startup shows both the resolved value and
its origin:

```
Configuration:
  vfs_path        = data/vfs-nested.csv  [file]
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

### 3.5. VFS CSV datasets

| File | Contents |
|---|---|
| `data/vfs-minimal.csv` | one directory and one file |
| `data/vfs-several-files.csv` | several files at the same level |
| `data/vfs-nested.csv` | at least three levels of nesting plus a binary file encoded with base64 |

Loading is strict: a missing file, an unknown `type`, a non-octal
`mode`, or a broken base64 payload all abort the load with a
`VFS error: ...` message, after which the shell continues with an
empty VFS.

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
python3 -m src.main --cli --vfs data/vfs-nested.csv
```

Host-side launchers in `scripts/`:

```bash
./scripts/run-default.sh     # CLI, no config
./scripts/run-cli.sh         # CLI + startup script
./scripts/run-gui.sh         # GUI + JSON config
./scripts/run-override.sh    # CLI + config, demonstrates priority
./scripts/run-vfs-minimal.sh # CLI + minimal VFS
./scripts/run-vfs-several.sh # CLI + several-files VFS
./scripts/run-vfs-nested.sh  # CLI + nested VFS
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

### 6.6. VFS datasets

Successful load:

```
$ python3 -m src.main --cli --vfs data/vfs-nested.csv
Configuration:
  vfs_path        = data/vfs-nested.csv  [cli]
  ...
VFS loaded: 11 nodes
Welcome to VFS: vfs20
Type 'exit' to quit.

user@vfs20:$
```

Missing file:

```
$ python3 -m src.main --cli --vfs /no/such/file.csv
VFS error: VFS file not found: /no/such/file.csv
VFS empty: running without files
Welcome to VFS: vfs20
Type 'exit' to quit.

user@vfs20:$
```

Malformed base64:

```
$ printf 'path,type,content,mode\n/x,file,base64:***,644\n' > /tmp/bad.csv
$ python3 -m src.main --cli --vfs /tmp/bad.csv
VFS error: invalid base64 content: Only base64 data is allowed
VFS empty: running without files
user@vfs20:$
```

---

## 7. Roadmap

| Stage | Goal                                                | Status  |
|-------|-----------------------------------------------------|---------|
| 1     | REPL: GUI, parser, stubs, `exit`                    | done    |
| 2     | Configuration: CLI + JSON + startup scripts         | done    |
| 3     | VFS: in-memory tree loaded from CSV                 | done    |
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
feat(vfs): add in-memory VFS and CSV loader
feat(shell): attach a VFS instance to the shell
feat(main): load VFS at startup and report errors
chore(data): add minimal, several-files and nested VFS datasets
test(vfs): cover loading, navigation and error handling
docs: describe VFS format, datasets and error handling
```

---

## 8. Repository conventions

* Source code lives in `src/`, tests in `tests/`.
* Launcher is `run.sh`; host-side scripts live in `scripts/`.
* Example configuration lives in `configs/`; VFS datasets in `data/`.
* No archives, binaries, build artefacts, or editor-specific files
  (see `.gitignore`).
* Code style: PEP 8, lines ≤ 80 characters, functions ≤ 40 lines,
  docstrings on every module, class, and public function.
* No magic numbers in comparisons; named constants everywhere.
* The banner and startup diagnostics are emitted once, from
  `main.py`. Frontends must not call `Shell.banner()` themselves.
* Commit messages follow Conventional Commits.

---

## 9. License

Distributed under the MIT License. See `LICENSE` for details.
