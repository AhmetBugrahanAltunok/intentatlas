from __future__ import annotations

import os
import stat
from pathlib import Path


def read_bounded_regular_file(path: Path, max_bytes: int) -> bytes | None:
    """Read one stable regular-file handle without following a final symbolic link."""

    if max_bytes < 0:
        return None
    flags = os.O_RDONLY
    if hasattr(os, "O_BINARY"):
        flags |= os.O_BINARY
    if hasattr(os, "O_NOFOLLOW"):
        flags |= os.O_NOFOLLOW
    if hasattr(os, "O_NONBLOCK"):
        flags |= os.O_NONBLOCK
    try:
        descriptor = os.open(path, flags)
        with os.fdopen(descriptor, "rb") as handle:
            opened = os.fstat(handle.fileno())
            current = path.stat(follow_symlinks=False)
            if (
                not stat.S_ISREG(opened.st_mode)
                or opened.st_size > max_bytes
                or not os.path.samestat(opened, current)
            ):
                return None
            value = handle.read(max_bytes + 1)
            after = path.stat(follow_symlinks=False)
            if not os.path.samestat(opened, after):
                return None
    except OSError:
        return None
    return value if len(value) <= max_bytes else None
