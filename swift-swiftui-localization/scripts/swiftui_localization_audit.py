#!/usr/bin/env python3
"""Lightweight Swift/SwiftUI localization audit.

Flags likely issues for human review:
- SwiftUI Text/Label/Button calls with non-literal first arguments.
- Stored UI component properties named title/subtitle/message/label/name as String.
- LocalizedError descriptions built without String(localized:).

This is heuristic by design. Treat results as a review queue, not proof.
"""

from __future__ import annotations

import argparse
import pathlib
import re
import sys


UI_NAMES = ("title", "subtitle", "message", "label", "name", "headline", "caption", "placeholder")
STRING_PROP = re.compile(r"\b(?:let|var)\s+(" + "|".join(UI_NAMES) + r")\s*:\s*String\b")
TEXT_VARIABLE = re.compile(r"\b(Text|Label|Button|Picker|Menu)\s*\(\s*([A-Za-z_][A-Za-z0-9_\.]*)")
NAV_TITLE_VARIABLE = re.compile(r"\.navigationTitle\s*\(\s*([A-Za-z_][A-Za-z0-9_\.]*)")
ERROR_DESCRIPTION = re.compile(r"\berrorDescription\s*:\s*String\?")


def iter_swift_files(root: pathlib.Path):
    if root.is_file() and root.suffix == ".swift":
        yield root
    elif root.is_dir():
        for path in root.rglob("*.swift"):
            if any(part in {".build", "DerivedData", "Pods", "Carthage"} for part in path.parts):
                continue
            yield path


def is_probably_literal_or_allowed(arg: str) -> bool:
    return (
        arg.startswith('"')
        or arg.startswith("String(localized:")
        or arg.startswith("LocalizedStringResource(")
        or arg.startswith("verbatim:")
        or arg in {"true", "false"}
    )


def audit_file(path: pathlib.Path) -> list[tuple[int, str, str]]:
    findings: list[tuple[int, str, str]] = []
    text = path.read_text(errors="replace")
    lines = text.splitlines()
    for i, line in enumerate(lines, start=1):
        stripped = line.strip()
        if stripped.startswith("//"):
            continue

        if STRING_PROP.search(line):
            findings.append((i, "ui-string-property", "UI-looking stored property is String; prefer LocalizedStringResource or clearly mark as verbatim/runtime data."))

        for match in TEXT_VARIABLE.finditer(line):
            arg = match.group(2)
            if not is_probably_literal_or_allowed(arg):
                findings.append((i, "swiftui-verbatim-risk", f"{match.group(1)} receives `{arg}`; if this is app UI copy, use LocalizedStringResource."))

        match = NAV_TITLE_VARIABLE.search(line)
        if match:
            findings.append((i, "navigation-title-variable", f"navigationTitle receives `{match.group(1)}`; ensure it is localizable or intentionally verbatim."))

    if ERROR_DESCRIPTION.search(text) and "String(localized:" not in text:
        findings.append((1, "localized-error", "LocalizedError descriptions should usually use String(localized:) for app-owned UI copy."))

    return findings


def main() -> int:
    parser = argparse.ArgumentParser(description="Audit SwiftUI localization patterns.")
    parser.add_argument("paths", nargs="+", help="Swift file or directory paths")
    parser.add_argument("--quiet", action="store_true", help="Only return exit status")
    args = parser.parse_args()

    all_findings = []
    for raw in args.paths:
        root = pathlib.Path(raw).expanduser()
        for path in iter_swift_files(root):
            for line, code, message in audit_file(path):
                all_findings.append((path, line, code, message))

    if not args.quiet:
        for path, line, code, message in all_findings:
            print(f"{path}:{line}: [{code}] {message}")
        print(f"\n{len(all_findings)} finding(s)")

    return 1 if all_findings else 0


if __name__ == "__main__":
    sys.exit(main())
