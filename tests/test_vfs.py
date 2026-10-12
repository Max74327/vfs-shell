"""Tests for the in-memory VFS and the CSV loader."""
import base64

import pytest

from src.vfs import (
    Vfs, VfsError, Node, load_vfs, BASE64_PREFIX,
    DEFAULT_DIR_MODE, DEFAULT_FILE_MODE,
)


def _write(tmp_path, text, name="vfs.csv"):
    """Helper: writes CSV text and returns the file path."""
    path = tmp_path / name
    path.write_text(text, encoding="utf-8")
    return str(path)


def test_empty_vfs_has_root():
    """A fresh VFS has a single root directory."""
    vfs = Vfs()
    assert vfs.root.is_dir is True
    assert vfs.root.children == {}


def test_mkdir_creates_parents():
    """mkdir creates missing parent directories."""
    vfs = Vfs()
    node = vfs.mkdir("/a/b/c")
    assert node.is_dir is True
    assert vfs.find("/a").is_dir is True
    assert vfs.find("/a/b").is_dir is True
    assert vfs.find("/a/b/c") is node


def test_create_file_under_missing_parents():
    """Creating a file under missing parents auto-creates them."""
    vfs = Vfs()
    node = vfs.create_file("/x/y/z.txt", content="hi")
    assert node.is_dir is False
    assert node.content == "hi"
    assert vfs.find("/x/y/z.txt") is node


def test_find_missing_raises():
    """Finding a missing path raises VfsError."""
    vfs = Vfs()
    with pytest.raises(VfsError):
        vfs.find("/nope")


def test_normalize():
    """Paths are normalised: absolute, no '.', resolves '..'."""
    vfs = Vfs()
    assert vfs.normalize("a/b") == "/a/b"
    assert vfs.normalize("/a//b/./c") == "/a/b/c"
    assert vfs.normalize("/a/b/../c") == "/a/c"
    assert vfs.normalize("/a/../../b") == "/b"


def test_listdir_sorted_dirs_first():
    """listdir puts directories before files, alphabetically."""
    vfs = Vfs()
    vfs.mkdir("/z-dir")
    vfs.create_file("/b.txt")
    vfs.create_file("/a.txt")
    names = [n.name for n in vfs.listdir("/")]
    assert names == ["z-dir", "a.txt", "b.txt"]


def test_listdir_on_file_raises():
    """listdir on a file is an error."""
    vfs = Vfs()
    vfs.create_file("/a.txt")
    with pytest.raises(VfsError):
        vfs.listdir("/a.txt")


def test_size_counts_all_nodes():
    """size counts every node below the root."""
    vfs = Vfs()
    vfs.mkdir("/a/b")
    vfs.create_file("/a/b/c.txt")
    assert vfs.size() == 3


def test_load_minimal(tmp_path):
    """Minimal CSV loads a single directory and file."""
    path = _write(tmp_path,
                  "path,type,content,mode\n"
                  "/etc,dir,,755\n"
                  "/etc/hostname,file,vfs20,644\n")
    vfs = load_vfs(path)
    assert vfs.find("/etc/hostname").content == "vfs20"
    assert vfs.find("/etc").mode == 0o755
    assert vfs.find("/etc/hostname").mode == 0o644


def test_load_nested_creates_parents(tmp_path):
    """Nested paths create intermediate directories."""
    path = _write(tmp_path,
                  "path,type,content,mode\n"
                  "/a/b/c/d.txt,file,deep,644\n")
    vfs = load_vfs(path)
    assert vfs.find("/a/b/c/d.txt").content == "deep"


def test_load_base64(tmp_path):
    """base64: prefix marks binary content."""
    payload = base64.b64encode(b"\x00\x01\x02").decode("ascii")
    path = _write(tmp_path,
                  "path,type,content,mode\n"
                  f"/bin/data,file,{BASE64_PREFIX}{payload},644\n")
    vfs = load_vfs(path)
    node = vfs.find("/bin/data")
    assert node.binary is True
    assert node.content == "\x00\x01\x02"


def test_load_skips_comments_and_blanks(tmp_path):
    """Blank lines and # lines are ignored."""
    path = _write(tmp_path,
                  "path,type,content,mode\n"
                  "\n"
                  "# a comment\n"
                  "/x,dir,,755\n")
    vfs = load_vfs(path)
    assert vfs.find("/x").is_dir is True


def test_load_missing_file_raises():
    """Missing file raises VfsError."""
    with pytest.raises(VfsError):
        load_vfs("/no/such/file.csv")


def test_load_missing_columns_raises(tmp_path):
    """CSV without the required columns raises VfsError."""
    path = _write(tmp_path, "path,type\n/x,dir\n")
    with pytest.raises(VfsError):
        load_vfs(path)


def test_load_invalid_type_raises(tmp_path):
    """An unknown type value raises VfsError."""
    path = _write(tmp_path,
                  "path,type,content,mode\n"
                  "/x,weird,,644\n")
    with pytest.raises(VfsError):
        load_vfs(path)


def test_load_invalid_mode_raises(tmp_path):
    """A non-octal mode raises VfsError."""
    path = _write(tmp_path,
                  "path,type,content,mode\n"
                  "/x,dir,,not-octal\n")
    with pytest.raises(VfsError):
        load_vfs(path)


def test_load_invalid_base64_raises(tmp_path):
    """Invalid base64 payload raises VfsError."""
    path = _write(tmp_path,
                  "path,type,content,mode\n"
                  "/x,file,base64:***,644\n")
    with pytest.raises(VfsError):
        load_vfs(path)


def test_load_shipped_datasets():
    """All shipped datasets load without errors."""
    for name in ("vfs-minimal.csv",
                 "vfs-several-files.csv",
                 "vfs-nested.csv"):
        vfs = load_vfs(f"data/{name}")
        assert vfs.size() > 0


def test_nested_depth_at_least_three():
    """The nested dataset really has depth ≥ 3."""
    vfs = load_vfs("data/vfs-nested.csv")
    assert vfs.depth() >= 3
