#!/usr/bin/env python3
"""Print localization-related Xcode build settings for a project/workspace."""

from __future__ import annotations

import argparse
import pathlib
import subprocess
import sys


KEYS = {
    "SWIFT_EMIT_LOC_STRINGS",
    "LOCALIZATION_PREFERS_STRING_CATALOGS",
    "LOCALIZED_STRING_SWIFTUI_SUPPORT",
    "STRING_CATALOG_GENERATE_SYMBOLS",
    "DEVELOPMENT_LANGUAGE",
}


def main() -> int:
    parser = argparse.ArgumentParser(description="Inspect Xcode localization build settings.")
    parser.add_argument("container", help=".xcodeproj or .xcworkspace path")
    parser.add_argument("scheme", nargs="?", help="Scheme name")
    parser.add_argument("--configuration", default="Debug")
    args = parser.parse_args()

    container = pathlib.Path(args.container).expanduser()
    if container.suffix == ".xcworkspace":
        cmd = ["xcodebuild", "-workspace", str(container)]
    elif container.suffix == ".xcodeproj":
        cmd = ["xcodebuild", "-project", str(container)]
    else:
        print("container must be .xcodeproj or .xcworkspace", file=sys.stderr)
        return 2

    if args.scheme:
        cmd += ["-scheme", args.scheme]
    cmd += ["-configuration", args.configuration, "-showBuildSettings"]

    result = subprocess.run(cmd, text=True, capture_output=True)
    if result.returncode != 0:
        sys.stderr.write(result.stderr)
        return result.returncode

    seen = False
    for line in result.stdout.splitlines():
        stripped = line.strip()
        if " = " not in stripped:
            continue
        key = stripped.split(" = ", 1)[0]
        if key in KEYS:
            print(stripped)
            seen = True

    if not seen:
        print("No localization build settings found in xcodebuild output.")
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
