"""In-memory virtual file system loaded from a CSV description."""
import base64
import csv
import os
from dataclasses import dataclass, field

BASE64_PREFIX = "base64:"
TYPE_FILE = "file"
TYPE_DIR = "dir"
DEFAULT_FILE_MODE = 0o644
DEFAULT_DIR_MODE = 0o755
ROOT_PATH = "/"
CSV_COLUMNS = ("path", "type", "content", "mode")


class VfsError(Exception):
    """Raised when the VFS cannot be loaded or is malformed."""


@dataclass
class Node:
    """A single node in the VFS tree (file or directory)."""

    name: str
    is_dir: bool
    mode: int = DEFAULT_FILE_MODE
    content: str = ""
    binary: bool = False
    children: dict = field(default_factory=dict)
    parent: "Node | None" = None


class Vfs:
    """In-memory virtual file system with a single root."""

    def __init__(self):
        """Creates an empty VFS with a root directory."""
        self.root = Node(name="", is_dir=True, mode=DEFAULT_DIR_MODE)

    # --- navigation -----------------------------------------------------

    def normalize(self, path: str) -> str:
        """Normalises a path: absolute, no trailing slash, no '..'."""
        if not path:
            return ROOT_PATH
        if not path.startswith(ROOT_PATH):
            path = ROOT_PATH + path
        parts = []
        for chunk in path.split(ROOT_PATH):
            if chunk in ("", "."):
                continue
            if chunk == "..":
                if parts:
                    parts.pop()
                continue
            parts.append(chunk)
        return ROOT_PATH + "/".join(parts)

    def find(self, path: str) -> Node:
        """Returns the node at the given path or raises VfsError."""
        norm = self.normalize(path)
        if norm == ROOT_PATH:
            return self.root
        node = self.root
        for part in norm.strip(ROOT_PATH).split(ROOT_PATH):
            if not node.is_dir or part not in node.children:
                raise VfsError(f"no such path: {path}")
            node = node.children[part]
        return node

    # --- mutation -------------------------------------------------------

    def mkdir(self, path: str, mode: int = DEFAULT_DIR_MODE) -> Node:
        """Creates a directory (and its parents) if missing."""
        norm = self.normalize(path)
        if norm == ROOT_PATH:
            return self.root
        node = self.root
        for part in norm.strip(ROOT_PATH).split(ROOT_PATH):
            if not part:
                continue
            child = node.children.get(part)
            if child is None:
                child = Node(name=part, is_dir=True, mode=mode,
                             parent=node)
                node.children[part] = child
            elif not child.is_dir:
                raise VfsError(f"not a directory: {part}")
            node = child
        return node

    def create_file(self, path: str, content: str = "",
                    mode: int = DEFAULT_FILE_MODE,
                    binary: bool = False) -> Node:
        """Creates or replaces a file at the given path."""
        norm = self.normalize(path)
        parent_path, _, name = norm.rpartition(ROOT_PATH)
        parent = self.mkdir(parent_path or ROOT_PATH)
        node = Node(name=name, is_dir=False, mode=mode,
                    content=content, binary=binary, parent=parent)
        parent.children[name] = node
        return node

    # --- listing --------------------------------------------------------

    def listdir(self, path: str) -> list:
        """Returns the sorted children of a directory node."""
        node = self.find(path)
        if not node.is_dir:
            raise VfsError(f"not a directory: {path}")
        return sorted(node.children.values(),
                      key=lambda n: (not n.is_dir, n.name))

    def depth(self, path: str = ROOT_PATH) -> int:
        """Returns the maximum depth below the given path."""
        node = self.find(path)
        if not node.is_dir:
            return 0
        if not node.children:
            return 0
        return 1 + max(self.depth(self._child_path(node, c))
                       for c in node.children.values())

    def _child_path(self, parent: Node, child: Node) -> str:
        """Builds an absolute path from a parent node and a child."""
        parts = [child.name]
        cur = parent
        while cur.parent is not None:
            parts.append(cur.name)
            cur = cur.parent
        return ROOT_PATH + "/".join(reversed([p for p in parts if p]))

    # --- persistence ----------------------------------------------------

    def size(self) -> int:
        """Returns the number of nodes in the tree (excluding root)."""
        return self._count(self.root)

    def _count(self, node: Node) -> int:
        """Recursively counts nodes below the given node."""
        return sum(1 + self._count(c) for c in node.children.values())


def _decode_content(raw: str) -> tuple:
    """Decodes a CSV content cell; returns (text, binary_flag)."""
    if raw.startswith(BASE64_PREFIX):
        payload = raw[len(BASE64_PREFIX):]
        try:
            data = base64.b64decode(payload, validate=True)
        except Exception as exc:
            raise VfsError(
                f"invalid base64 content: {exc}") from exc
        return data.decode("latin-1"), True
    return raw, False


def _parse_mode(raw: str, is_dir: bool) -> int:
    """Parses the octal mode column with a sensible default."""
    if not raw:
        return DEFAULT_DIR_MODE if is_dir else DEFAULT_FILE_MODE
    try:
        return int(raw, 8)
    except ValueError as exc:
        raise VfsError(f"invalid mode: {raw!r}") from exc


def _apply_row(vfs: Vfs, row: dict) -> None:
    """Creates a node in the VFS from a parsed CSV row."""
    path = (row.get("path") or "").strip()
    kind = (row.get("type") or "").strip()
    if not path or kind not in (TYPE_FILE, TYPE_DIR):
        raise VfsError(f"invalid row: {row}")
    mode = _parse_mode((row.get("mode") or "").strip(),
                       kind == TYPE_DIR)
    try:
        if kind == TYPE_DIR:
            vfs.mkdir(path, mode=mode)
        else:
            text, binary = _decode_content(row.get("content") or "")
            vfs.create_file(path, content=text, mode=mode, binary=binary)
    except VfsError:
        raise
    except Exception as exc:
        raise VfsError(f"cannot create {path}: {exc}") from exc


def load_vfs(path: str) -> Vfs:
    """Loads a VFS from a CSV file. Raises VfsError on any problem."""
    if not path:
        raise VfsError("VFS path is not set")
    if not os.path.isfile(path):
        raise VfsError(f"VFS file not found: {path}")
    vfs = Vfs()
    try:
        with open(path, "r", encoding="utf-8", newline="") as fh:
            reader = csv.DictReader(fh)
            if reader.fieldnames is None:
                raise VfsError(f"empty CSV: {path}")
            missing = [c for c in CSV_COLUMNS
                       if c not in reader.fieldnames]
            if missing:
                raise VfsError(
                    f"missing columns in {path}: {missing}")
            for row in reader:
                if not row or not (row.get("path") or "").strip():
                    continue
                if str(row["path"]).lstrip().startswith("#"):
                    continue
                _apply_row(vfs, row)
    except csv.Error as exc:
        raise VfsError(f"CSV parse error: {exc}") from exc
    return vfs
