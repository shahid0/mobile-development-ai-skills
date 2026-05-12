#!/usr/bin/env python3
"""Sync a String Catalog with compiler-emitted .stringsdata files."""

from __future__ import annotations

import argparse
import pathlib
import shutil
import subprocess
import sys


def find_xcstringstool() -> str:
    candidates = [
        "/Applications/Xcode.app/Contents/Developer/usr/bin/xcstringstool",
        shutil.which("xcstringstool"),
    ]
    for candidate in candidates:
        if candidate and pathlib.Path(candidate).exists():
            return str(candidate)
    raise FileNotFoundError("xcstringstool not found. Install/select Xcode.")


def main() -> int:
    parser = argparse.ArgumentParser(description="Run xcstringstool sync for an .xcstrings catalog.")
    parser.add_argument("catalog", help="Path to Localizable.xcstrings")
    parser.add_argument("search_roots", nargs="+", help="Directories or .stringsdata files to include")
    parser.add_argument("--mark-stale", action="store_true", help="Allow stale marking/removal. Default preserves existing entries.")
    args = parser.parse_args()

    catalog = pathlib.Path(args.catalog).expanduser()
    if not catalog.exists() or catalog.suffix != ".xcstrings":
        print(f"Catalog not found or not .xcstrings: {catalog}", file=sys.stderr)
        return 2

    stringsdata: list[str] = []
    for raw in args.search_roots:
        root = pathlib.Path(raw).expanduser()
        if root.is_file() and root.suffix == ".stringsdata":
            stringsdata.append(str(root))
        elif root.is_dir():
            stringsdata.extend(str(p) for p in root.rglob("*.stringsdata"))

    stringsdata = sorted(set(stringsdata))
    if not stringsdata:
        print("No .stringsdata files found.", file=sys.stderr)
        return 1

    cmd = [find_xcstringstool(), "sync", str(catalog)]
    if not args.mark_stale:
        cmd.append("--skip-marking-strings-stale")
    cmd.append("--stringsdata")
    cmd.extend(stringsdata)

    print(f"Syncing {len(stringsdata)} .stringsdata file(s) into {catalog}")
    result = subprocess.run(cmd)
    return result.returncode


if __name__ == "__main__":
    sys.exit(main())
