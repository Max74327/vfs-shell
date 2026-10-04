"""Stub commands for stage 1."""

EXIT_SENTINEL = "__EXIT__"
MAX_ARGS_CD = 1
DEFAULT_CD_TARGET = "~"


def cmd_ls(args: list) -> str:
    """Stub for ls: prints its name and the received arguments."""
    return (
        "ls: stub command\n"
        f"  arguments received: {len(args)}\n"
        f"  arguments: {args}"
    )


def cmd_cd(args: list) -> str:
    """Stub for cd: prints the target and validates the arguments."""
    if len(args) > MAX_ARGS_CD:
        return (
            f"cd: too many arguments "
            f"(received {len(args)})\n"
            f"  arguments: {args}"
        )
    target = args[0] if args else DEFAULT_CD_TARGET
    return (
        "cd: stub command\n"
        f"  target directory: {target!r}"
    )


def cmd_exit(args: list) -> str:
    """Signals the shell core to terminate."""
    return EXIT_SENTINEL


COMMANDS = {
    "ls": cmd_ls,
    "cd": cmd_cd,
    "exit": cmd_exit,
}
