#!/usr/bin/env python3
"""Heuristic SwiftUI localization-responsive UI audit.

Flags likely layout/RTL/i18n risks:
- fixed widths near text controls
- one-line limits on user-facing text
- absolute left/right alignment where leading/trailing is usually expected
- directional SF Symbols that may not mirror
- percent/currency/unit string concatenation

False positives are expected. Use as a review queue.
"""

from __future__ import annotations

import argparse
import pathlib
import re
import sys


TEXTISH = re.compile(r"\b(Text|Label|Button|LabeledContent|Picker|Menu)\s*\(")
FIXED_WIDTH = re.compile(r"\.frame\s*\([^)]*\bwidth\s*:")
LINE_LIMIT_ONE = re.compile(r"\.lineLimit\s*\(\s*1\s*\)")
ABS_ALIGN = re.compile(r"\.(multilineTextAlignment|frame)\s*\([^)]*\.(left|right)\b")
PADDING_ABS = re.compile(r"\.padding\s*\(\s*\.(left|right)\b")
SPATIAL_SYMBOL_OK = re.compile(r"text\.align|arrow\.left\.and\.right|chevron\.left\.slash\.chevron\.right")
DIRECTIONAL_SYMBOL = re.compile(r'Image\s*\(\s*systemName:\s*"([^"]*(?:arrow|chevron)[^"]*)"')
CONCAT_PERCENT = re.compile(r'"\s*\+\s*[^\\n]*[%$€£¥]|[%$€£¥][^"\\n]*"\s*\+|Text\s*\(\s*"[^"]*\\\([^)]*\)[^"]*[%$€£¥]')
HSTACK_MANY_TEXT = re.compile(r"HStack\s*\{")


def iter_swift_files(root: pathlib.Path):
    if root.is_file() and root.suffix == ".swift":
        yield root
    elif root.is_dir():
        for path in root.rglob("*.swift"):
            if any(part in {".build", "DerivedData", "Pods", "Carthage"} for part in path.parts):
                continue
            yield path


def nearby_text(lines: list[str], index: int, radius: int = 4) -> bool:
    start = max(0, index - radius)
    end = min(len(lines), index + radius + 1)
    return any(TEXTISH.search(lines[i]) for i in range(start, end))


def audit_file(path: pathlib.Path):
    lines = path.read_text(errors="replace").splitlines()
    findings = []
    for idx, line in enumerate(lines):
        stripped = line.strip()
        if stripped.startswith("//"):
            continue
        line_no = idx + 1

        if FIXED_WIDTH.search(line) and nearby_text(lines, idx):
            findings.append((line_no, "fixed-width-text", "Fixed width near text/control; test double-length and consider flexible/adaptive layout."))

        if LINE_LIMIT_ONE.search(line) and nearby_text(lines, idx):
            findings.append((line_no, "one-line-text", "One-line limit near text/control; verify truncation is intentional in bounded/double-length pseudolanguages."))

        if ABS_ALIGN.search(line) or PADDING_ABS.search(line):
            findings.append((line_no, "absolute-direction", "Uses left/right; prefer leading/trailing unless this is a spatial control."))

        symbol = DIRECTIONAL_SYMBOL.search(line)
        if symbol:
            name = symbol.group(1)
            if (".left" in name or ".right" in name) and not SPATIAL_SYMBOL_OK.search(name):
                findings.append((line_no, "directional-symbol", f"`{name}` may not mirror in RTL; use forward/backward for navigation semantics."))

        if CONCAT_PERCENT.search(line):
            findings.append((line_no, "manual-formatting", "Possible manual percent/currency formatting; prefer FormatStyle/Text format/String(localized:) interpolation."))

        if HSTACK_MANY_TEXT.search(line):
            window = "\n".join(lines[idx : min(len(lines), idx + 12)])
            count = len(TEXTISH.findall(window))
            if count >= 3 and "ViewThatFits" not in window:
                findings.append((line_no, "crowded-horizontal-text", "HStack contains several text controls; consider ViewThatFits/adaptive stack for long translations."))

    return findings


def main() -> int:
    parser = argparse.ArgumentParser(description="Audit SwiftUI layout for localization responsiveness and RTL risks.")
    parser.add_argument("paths", nargs="+", help="Swift file or directory paths")
    parser.add_argument("--quiet", action="store_true")
    args = parser.parse_args()

    all_findings = []
    for raw in args.paths:
        for file in iter_swift_files(pathlib.Path(raw).expanduser()):
            for line, code, msg in audit_file(file):
                all_findings.append((file, line, code, msg))

    if not args.quiet:
        for file, line, code, msg in all_findings:
            print(f"{file}:{line}: [{code}] {msg}")
        print(f"\n{len(all_findings)} finding(s)")

    return 1 if all_findings else 0


if __name__ == "__main__":
    sys.exit(main())
