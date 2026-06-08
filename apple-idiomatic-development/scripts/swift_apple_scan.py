#!/usr/bin/env python3
"""Swift/SwiftUI scanner for Apple-idiomatic review routing.

Default mode reports advisory signals for review routing. Use --strict to report
only exact project policy violations that the script can identify mechanically.
"""

from __future__ import annotations

import argparse
import pathlib
import re
import sys
from dataclasses import dataclass


SWIFT_EXTENSIONS = {".swift", ".metal"}


@dataclass(frozen=True)
class Finding:
    path: pathlib.Path
    line: int
    code: str
    message: str
    severity: str


def iter_source_files(root: pathlib.Path) -> list[pathlib.Path]:
    if root.is_file():
        return [root] if root.suffix in SWIFT_EXTENSIONS else []
    ignored = {".build", "DerivedData", ".git", "Pods", "Carthage"}
    files: list[pathlib.Path] = []
    for path in root.rglob("*"):
        if any(part in ignored for part in path.parts):
            continue
        if path.is_file() and path.suffix in SWIFT_EXTENSIONS:
            files.append(path)
    return sorted(files)


def line_number(text: str, index: int) -> int:
    return text.count("\n", 0, index) + 1


def mask_comments(text: str) -> str:
    """Replace comments and string contents with spaces while preserving offsets."""
    chars = list(text)
    index = 0
    block_depth = 0
    in_string = False
    triple_string = False
    while index < len(chars):
        current = chars[index]
        nxt = chars[index + 1] if index + 1 < len(chars) else ""
        third = chars[index + 2] if index + 2 < len(chars) else ""

        if block_depth:
            if current == "/" and nxt == "*":
                chars[index] = " "
                chars[index + 1] = " "
                index += 2
                block_depth += 1
                continue
            if current == "*" and nxt == "/":
                chars[index] = " "
                chars[index + 1] = " "
                index += 2
                block_depth -= 1
                continue
            if current != "\n":
                chars[index] = " "
            index += 1
            continue

        if in_string:
            if not triple_string and current == "\\":
                chars[index] = " "
                if index + 1 < len(chars):
                    chars[index + 1] = " "
                index += 2
                continue
            if triple_string and current == "\"" and nxt == "\"" and third == "\"":
                chars[index] = " "
                chars[index + 1] = " "
                chars[index + 2] = " "
                index += 3
                in_string = False
                triple_string = False
                continue
            if not triple_string and current == "\"":
                chars[index] = " "
                index += 1
                in_string = False
                continue
            if current != "\n":
                chars[index] = " "
            index += 1
            continue

        if current == "\"" and nxt == "\"" and third == "\"":
            chars[index] = " "
            chars[index + 1] = " "
            chars[index + 2] = " "
            in_string = True
            triple_string = True
            index += 3
            continue
        if current == "\"":
            chars[index] = " "
            in_string = True
            index += 1
            continue
        if current == "/" and nxt == "/":
            chars[index] = " "
            chars[index + 1] = " "
            index += 2
            while index < len(chars) and chars[index] != "\n":
                chars[index] = " "
                index += 1
            continue
        if current == "/" and nxt == "*":
            chars[index] = " "
            chars[index + 1] = " "
            index += 2
            block_depth = 1
            continue
        index += 1
    return "".join(chars)


def task_detached_bodies(text: str) -> list[tuple[int, int]]:
    spans: list[tuple[int, int]] = []
    for match in re.finditer(r"Task\.detached\b", text):
        open_brace = text.find("{", match.end(), match.end() + 200)
        if open_brace == -1:
            continue
        depth = 0
        for index in range(open_brace, len(text)):
            char = text[index]
            if char == "{":
                depth += 1
            elif char == "}":
                depth -= 1
                if depth == 0:
                    spans.append((open_brace, index + 1))
                    break
    return spans


def make_finding(path: pathlib.Path, text: str, match: re.Match[str], code: str, message: str, severity: str) -> Finding:
    return Finding(path, line_number(text, match.start()), code, message, severity)


def scan_swift(path: pathlib.Path, text: str, strict: bool) -> list[Finding]:
    findings: list[Finding] = []
    advisory_patterns = [
        (
            "legacy-observation",
            re.compile(r"\b(ObservableObject|@Published|@StateObject|@ObservedObject|@EnvironmentObject)\b"),
            "Legacy Combine observation found. For iOS 17+ code, consider Observation with @Observable, @State ownership, and @Bindable only for bindings.",
        ),
        (
            "navigation-view",
            re.compile(r"\bNavigationView\s*\{"),
            "NavigationView found. Prefer NavigationStack or NavigationSplitView for modern SwiftUI navigation.",
        ),
        (
            "foreground-color",
            re.compile(r"\.foregroundColor\s*\("),
            "foregroundColor found. Prefer foregroundStyle for modern SwiftUI styling unless compatibility requires this API.",
        ),
        (
            "broad-animation",
            re.compile(r"\.animation\s*\(\s*(?!nil\b)[^,\n)]+?\s*\)"),
            "Implicit animation without an explicit value found. Prefer withAnimation or .animation(_:value:) scoped to a specific state value.",
        ),
        (
            "uuid-refresh",
            re.compile(r"\.id\s*\(\s*UUID\s*\(\s*\)\s*\)"),
            "UUID identity refresh found. Use stable identity and fix the state/update model.",
        ),
        (
            "mainactor-service",
            re.compile(r"@MainActor\s+(?:(?:@[A-Za-z_][A-Za-z0-9_]*(?:\([^)]*\))?|public|private|internal|fileprivate|open|final)\s+)*(?:class|struct|actor)\s+\w*(Service|Repository|Client|Decoder|Parser|Worker|Cache)\b"),
            "A service/repository/client/worker is isolated to MainActor. Keep non-UI work off the UI actor unless an Apple API requires UI isolation.",
        ),
        (
            "background-zstack-comment",
            re.compile(r"ZStack\s*\{[\s\S]{0,500}\b(background|Background)\b"),
            "ZStack may be used for view-local background layering. Prefer .background(content:) when the background belongs to one view.",
        ),
        (
            "string-formatting",
            re.compile(r"Text\s*\(\s*String\s*\(\s*format\s*:"),
            "Text(String(format:)) found. Prefer Text(value, format:) or a FormatStyle when presenting values.",
        ),
        (
            "dateformatter-in-view",
            re.compile(r"(?:var\s+body\s*:\s*some\s+View|func\s+\w+.*?->\s*some\s+View)[\s\S]{0,1200}\bDateFormatter\s*\("),
            "DateFormatter is created near SwiftUI view rendering. Prefer Text(date, format:), Text(date, style:), or cached formatting outside body.",
        ),
        (
            "numberformatter-in-view",
            re.compile(r"(?:var\s+body\s*:\s*some\s+View|func\s+\w+.*?->\s*some\s+View)[\s\S]{0,1200}\bNumberFormatter\s*\("),
            "NumberFormatter is created near SwiftUI view rendering. Prefer Text(value, format:) or cached formatting outside body.",
        ),
        (
            "observable-object-mixed",
            re.compile(r"@Observable[\s\S]{0,200}\bObservableObject\b|ObservableObject[\s\S]{0,200}@Observable"),
            "Observation and ObservableObject appear on the same type. Use a single observation model unless compatibility requires a bridge.",
        ),
        (
            "reduce-motion-ternary",
            re.compile(r"reduceMotion\s*\?\s*(?:nil|\.none)|accessibilityReduceMotion\s*\?\s*(?:nil|\.none)"),
            "Local Reduce Motion animation ternary found. Prefer a centralized app-shell or feature-shell transaction policy when broad motion should change.",
        ),
    ]
    strict_patterns = [
        (
            "uuid-refresh",
            re.compile(r"\.id\s*\(\s*UUID\s*\(\s*\)\s*\)"),
            "Unstable UUID identity refresh found. Use stable identity.",
        ),
        (
            "observable-object-mixed",
            re.compile(r"@Observable[\s\S]{0,200}\bObservableObject\b|ObservableObject[\s\S]{0,200}@Observable"),
            "Observation and ObservableObject appear on the same type.",
        ),
        (
            "text-string-format",
            re.compile(r"Text\s*\(\s*String\s*\(\s*format\s*:"),
            "Text(String(format:)) found; project policy prefers Text(value, format:) or FormatStyle for value display.",
        ),
    ]
    selected = strict_patterns if strict else advisory_patterns
    scan_text = mask_comments(text)
    for code, pattern, message in selected:
        for match in pattern.finditer(scan_text):
            findings.append(make_finding(path, text, match, code, message, "error" if strict else "advisory"))
    if not strict:
        for start, end in task_detached_bodies(scan_text):
            body = scan_text[start:end]
            task_match = re.search(r"Task\.detached\b", scan_text[max(0, start - 220):start])
            finding_index = max(0, start - 220) + task_match.start() if task_match else start
            if re.search(r"\bself\.", body):
                findings.append(
                    Finding(
                        path,
                        line_number(text, finding_index),
                        "detached-self",
                        "Task.detached captures self in its closure. Pass Sendable snapshots into detached work and return Sendable values.",
                        "advisory",
                    )
                )
            if "Task.checkCancellation" not in body:
                findings.append(
                    Finding(
                        path,
                        line_number(text, finding_index),
                        "task-detached-no-cancellation",
                        "Task.detached has no cancellation check in its closure. Long or CPU-heavy detached work should check cancellation.",
                        "advisory",
                    )
                )
        bindable_pattern = re.compile(r"@Bindable\s+(?:(?:private|public|internal|fileprivate)\s+)?var\s+(?P<name>[A-Za-z_][A-Za-z0-9_]*)")
        for match in bindable_pattern.finditer(scan_text):
            name = match.group("name")
            window = scan_text[match.end():match.end() + 800]
            if not re.search(rf"\${re.escape(name)}\b", window):
                findings.append(
                    make_finding(
                        path,
                        text,
                        match,
                        "bindable-without-binding-use",
                        "@Bindable appears without nearby binding projection use. Prefer a plain property unless the view passes $model.property bindings.",
                        "advisory",
                    )
                )
    return findings


def scan_metal(path: pathlib.Path, text: str, strict: bool) -> list[Finding]:
    findings: list[Finding] = []
    if strict:
        return findings
    scan_text = mask_comments(text)
    if "[[ stitchable ]]" in scan_text and "#include <SwiftUI/SwiftUI_Metal.h>" not in scan_text:
        findings.append(
            Finding(
                path,
                1,
                "metal-swiftui-include",
                "SwiftUI stitchable shader file should usually include <SwiftUI/SwiftUI_Metal.h> for SwiftUI shader types.",
                "advisory",
            )
        )
    return findings


def scan_file(path: pathlib.Path, strict: bool) -> list[Finding]:
    text = path.read_text(encoding="utf-8", errors="replace")
    if path.suffix == ".swift":
        return scan_swift(path, text, strict)
    if path.suffix == ".metal":
        return scan_metal(path, text, strict)
    return []


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("path", help="Swift project, source directory, or file")
    parser.add_argument("--strict", action="store_true", help="Only report exact policy violations")
    args = parser.parse_args(argv)
    root = pathlib.Path(args.path).resolve()
    if not root.exists():
        print(f"error: path does not exist: {root}", file=sys.stderr)
        return 2
    files = iter_source_files(root)
    findings: list[Finding] = []
    for file_path in files:
        findings.extend(scan_file(file_path, args.strict))
    for finding in findings:
        try:
            display_path = finding.path.relative_to(root if root.is_dir() else root.parent)
        except ValueError:
            display_path = finding.path
        print(f"{display_path}:{finding.line}: {finding.severity}: {finding.code}: {finding.message}")
    print(f"Scanned {len(files)} source file(s); {len(findings)} finding(s).")
    return 1 if findings else 0


if __name__ == "__main__":
    raise SystemExit(main())
