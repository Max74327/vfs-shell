"""Configuration: CLI flags + JSON file, with file taking priority."""
import argparse
import json
import os
from dataclasses import dataclass, field

DEFAULT_CONFIG_PATH = "config.json"
CONFIG_KEY_VFS_PATH = "vfs_path"
CONFIG_KEY_STARTUP = "startup_script"


class ConfigError(Exception):
    """Raised when configuration cannot be read or is malformed."""


@dataclass
class Config:
    """Resolved configuration of the emulator."""

    vfs_path: str = ""
    startup_script: str = ""
    config_path: str = ""
    cli_mode: bool = False
    sources: dict = field(default_factory=dict)


def build_arg_parser() -> argparse.ArgumentParser:
    """Creates the command-line parser with all supported flags."""
    parser = argparse.ArgumentParser(
        prog="vfs-shell",
        description="VFS shell emulator",
    )
    parser.add_argument(
        "--vfs", metavar="PATH",
        help="path to the VFS CSV file",
    )
    parser.add_argument(
        "--startup", metavar="PATH",
        help="path to the startup script",
    )
    parser.add_argument(
        "--config", metavar="PATH",
        help="path to the JSON configuration file",
    )
    parser.add_argument(
        "--cli", action="store_true",
        help="start in console mode (no GUI)",
    )
    return parser


def _read_json(path: str) -> dict:
    """Reads and validates a JSON configuration file."""
    if not os.path.isfile(path):
        raise ConfigError(f"config file not found: {path}")
    try:
        with open(path, "r", encoding="utf-8") as fh:
            data = json.load(fh)
    except json.JSONDecodeError as exc:
        raise ConfigError(f"invalid JSON in {path}: {exc}") from exc
    if not isinstance(data, dict):
        raise ConfigError(f"config root must be an object: {path}")
    return data


def _pick(cli_value, file_value, default=""):
    """Applies priority: file value wins over CLI value."""
    if file_value not in (None, ""):
        return file_value, "file"
    if cli_value not in (None, ""):
        return cli_value, "cli"
    return default, "default"


def resolve_config(argv=None) -> Config:
    """
    Reads CLI flags and the JSON file, applies priority, returns Config.

    Priority rule: values from the JSON file override CLI values.
    """
    args = build_arg_parser().parse_args(argv)
    cfg = Config()

    file_data = {}
    if args.config:
        cfg.config_path = args.config
        file_data = _read_json(args.config)

    cfg.vfs_path, cfg.sources["vfs_path"] = _pick(
        args.vfs, file_data.get(CONFIG_KEY_VFS_PATH),
    )
    cfg.startup_script, cfg.sources["startup_script"] = _pick(
        args.startup, file_data.get(CONFIG_KEY_STARTUP),
    )
    cfg.cli_mode = args.cli
    return cfg


def format_debug(cfg: Config) -> str:
    """Returns a human-readable dump of the resolved configuration."""
    lines = ["Configuration:"]
    lines.append(f"  vfs_path        = {cfg.vfs_path or '(none)'}"
                 f"  [{cfg.sources.get('vfs_path', '-')}]")
    lines.append(f"  startup_script  = {cfg.startup_script or '(none)'}"
                 f"  [{cfg.sources.get('startup_script', '-')}]")
    lines.append(f"  config_path     = {cfg.config_path or '(none)'}")
    lines.append(f"  cli_mode        = {cfg.cli_mode}")
    return "\n".join(lines)
