"""Tests for CLI + JSON configuration resolution."""
import json
import os

import pytest

from src.config import ConfigError, resolve_config, format_debug


def _write_config(tmp_path, payload):
    """Helper: writes a JSON config and returns its path."""
    path = tmp_path / "config.json"
    path.write_text(json.dumps(payload), encoding="utf-8")
    return str(path)


def test_defaults_when_nothing_given():
    """No CLI flags and no config yields empty paths."""
    cfg = resolve_config([])
    assert cfg.vfs_path == ""
    assert cfg.startup_script == ""
    assert cfg.cli_mode is False


def test_cli_values_used():
    """CLI values are used when no config file is present."""
    cfg = resolve_config(["--vfs", "a.csv", "--startup", "s.sh"])
    assert cfg.vfs_path == "a.csv"
    assert cfg.startup_script == "s.sh"
    assert cfg.sources["vfs_path"] == "cli"


def test_config_overrides_cli(tmp_path):
    """Values from the JSON file win over CLI values."""
    path = _write_config(tmp_path, {
        "vfs_path": "from_file.csv",
        "startup_script": "from_file.sh",
    })
    cfg = resolve_config([
        "--vfs", "from_cli.csv",
        "--startup", "from_cli.sh",
        "--config", path,
    ])
    assert cfg.vfs_path == "from_file.csv"
    assert cfg.startup_script == "from_file.sh"
    assert cfg.sources["vfs_path"] == "file"


def test_partial_config_falls_back_to_cli(tmp_path):
    """Keys missing in the file fall back to CLI values."""
    path = _write_config(tmp_path, {"vfs_path": "only_vfs.csv"})
    cfg = resolve_config([
        "--vfs", "cli.csv",
        "--startup", "cli.sh",
        "--config", path,
    ])
    assert cfg.vfs_path == "only_vfs.csv"
    assert cfg.startup_script == "cli.sh"
    assert cfg.sources["startup_script"] == "cli"


def test_missing_config_file_raises():
    """A missing config file raises ConfigError."""
    with pytest.raises(ConfigError):
        resolve_config(["--config", "/no/such/file.json"])


def test_invalid_json_raises(tmp_path):
    """Malformed JSON raises ConfigError."""
    path = tmp_path / "broken.json"
    path.write_text("{not json", encoding="utf-8")
    with pytest.raises(ConfigError):
        resolve_config(["--config", str(path)])


def test_debug_dump_contains_sources():
    """The debug dump includes values and their origins."""
    cfg = resolve_config(["--vfs", "a.csv"])
    dump = format_debug(cfg)
    assert "vfs_path" in dump
    assert "a.csv" in dump
    assert "[cli]" in dump
