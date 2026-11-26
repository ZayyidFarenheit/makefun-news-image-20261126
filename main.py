#!/usr/bin/env python3
"""Entry point for the news-image-20261126 entry.

Copies the pre-rendered front page (entry.png, drawn by draw.py) into
the output directory the grader provides. Standard library only.
"""
import hashlib
import os
import shutil
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
SRC = HERE / "entry.png"

MAX_BYTES = 1048576


def _sha256(path):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(65536), b""):
            h.update(chunk)
    return h.hexdigest()


def _resolve_output(argv):
    """Where entry.png goes: argv[1], then MAKEFUN_OUTPUT_DIR, then
    /output if it exists, else output/entry.png under the repo root.
    A directory argument gains the file name; a file argument is used
    as given."""
    if len(argv) > 1:
        dest = Path(argv[1])
        if dest.suffix == ".png" or (dest.exists() and dest.is_file()):
            return dest
        return dest / "entry.png"
    if os.environ.get("MAKEFUN_OUTPUT_DIR"):
        return Path(os.environ["MAKEFUN_OUTPUT_DIR"]) / "entry.png"
    if os.path.isdir("/output"):
        return Path("/output/entry.png")
    return HERE / "output" / "entry.png"


def main():
    if not SRC.is_file():
        raise SystemExit("missing source image: %s" % SRC)
    if SRC.stat().st_size > MAX_BYTES:
        raise SystemExit("entry.png is %d bytes, over the %d-byte limit"
                         % (SRC.stat().st_size, MAX_BYTES))
    dest = _resolve_output(sys.argv)
    dest.parent.mkdir(parents=True, exist_ok=True)
    shutil.copyfile(SRC, dest)
    if _sha256(dest) != _sha256(SRC):
        raise SystemExit("copy mismatch: %s != %s" % (dest, SRC))
    print("copied", SRC, "->", dest, "(%d bytes)" % dest.stat().st_size)


if __name__ == "__main__":
    main()
