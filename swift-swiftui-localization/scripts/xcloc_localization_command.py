#!/usr/bin/env python3
"""Print xcodebuild export/import localization commands.

This avoids retyping fragile command shapes. It prints commands rather than
executing them so the caller can review paths and options first.
"""

from __future__ import annotations

import argparse
import shlex


def quote(parts: list[str]) -> str:
    return " ".join(shlex.quote(part) for part in parts)


def main() -> int:
    parser = argparse.ArgumentParser(description="Generate xcodebuild localization export/import commands.")
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument("--project", help=".xcodeproj path")
    group.add_argument("--workspace", help=".xcworkspace path")
    parser.add_argument("--scheme", help="Scheme name, required for most workspace exports")
    parser.add_argument("--localization-path", required=True, help="Output folder for export or .xcloc path for import")
    parser.add_argument("--language", action="append", help="Language to export; may be repeated")
    parser.add_argument("--include-screenshots", action="store_true")
    parser.add_argument("--mode", choices=("export", "import"), default="export")
    args = parser.parse_args()

    cmd = ["xcodebuild"]
    if args.mode == "export":
        cmd.append("-exportLocalizations")
    else:
        cmd.append("-importLocalizations")

    if args.project:
        cmd += ["-project", args.project]
    else:
        cmd += ["-workspace", args.workspace]
    if args.scheme:
        cmd += ["-scheme", args.scheme]
    cmd += ["-localizationPath", args.localization_path]

    if args.mode == "export":
        for language in args.language or []:
            cmd += ["-exportLanguage", language]
        if args.include_screenshots:
            cmd.append("-includeScreenshots")

    print(quote(cmd))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
