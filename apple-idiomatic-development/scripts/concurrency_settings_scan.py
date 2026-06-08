#!/usr/bin/env python3
"""Extract Swift concurrency build-setting declarations from a project."""

from __future__ import annotations

import argparse
import pathlib
import re
import sys
from dataclasses import dataclass


SETTING_NAMES = [
    "SWIFT_VERSION",
    "SWIFT_STRICT_CONCURRENCY",
    "SWIFT_DEFAULT_ACTOR_ISOLATION",
    "SWIFT_UPCOMING_FEATURE_NONISOLATED_NONSENDING_BY_DEFAULT",
    "SWIFT_UPCOMING_FEATURE_INFER_ISOLATED_CONFORMANCES",
    "SWIFT_UPCOMING_FEATURE_GLOBAL_ACTOR_ISOLATED_TYPES_USABILITY",
]


@dataclass(frozen=True)
class Evidence:
    path: pathlib.Path
    line: int
    key: str
    value: str
    source: str


def line_number(text: str, index: int) -> int:
    return text.count("\n", 0, index) + 1


def mask_swift_comments(text: str) -> str:
    chars = list(text)
    index = 0
    block_depth = 0
    in_string = False
    while index < len(chars):
        current = chars[index]
        nxt = chars[index + 1] if index + 1 < len(chars) else ""
        if block_depth:
            if current == "/" and nxt == "*":
                chars[index] = chars[index + 1] = " "
                index += 2
                block_depth += 1
                continue
            if current == "*" and nxt == "/":
                chars[index] = chars[index + 1] = " "
                index += 2
                block_depth -= 1
                continue
            if current != "\n":
                chars[index] = " "
            index += 1
            continue
        if in_string:
            if current == "\\":
                index += 2
                continue
            if current == "\"":
                in_string = False
            index += 1
            continue
        if current == "\"":
            in_string = True
            index += 1
            continue
        if current == "/" and nxt == "/":
            chars[index] = chars[index + 1] = " "
            index += 2
            while index < len(chars) and chars[index] != "\n":
                chars[index] = " "
                index += 1
            continue
        if current == "/" and nxt == "*":
            chars[index] = chars[index + 1] = " "
            index += 2
            block_depth = 1
            continue
        index += 1
    return "".join(chars)


def iter_files(root: pathlib.Path) -> list[pathlib.Path]:
    if root.is_file():
        return [root]
    names = {"Package.swift", "project.pbxproj"}
    suffixes = {".xcconfig"}
    ignored = {".git", ".build", "DerivedData", "Pods", "Carthage"}
    files: list[pathlib.Path] = []
    for path in root.rglob("*"):
        if any(part in ignored for part in path.parts):
            continue
        if path.is_file() and (path.name in names or path.suffix in suffixes):
            files.append(path)
    return sorted(files)


def scan_package(path: pathlib.Path, text: str) -> list[Evidence]:
    findings: list[Evidence] = []
    tools = re.search(r"swift-tools-version:\s*([0-9.]+)", text)
    if tools:
        findings.append(Evidence(path, 1, "swift-tools-version", tools.group(1), "Package.swift"))
    scan_text = mask_swift_comments(text)

    patterns = [
        ("defaultIsolation", re.compile(r"\.defaultIsolation\s*\(\s*(MainActor\.self|nil)\s*\)")),
        ("swiftLanguageMode", re.compile(r"\.swiftLanguageMode\s*\(\s*\.?v?([0-9.]+)\s*\)")),
        ("swiftLanguageVersion", re.compile(r"\.swiftLanguageVersion\s*\(\s*\.?v?([0-9.]+)\s*\)")),
        ("enableUpcomingFeature", re.compile(r"\.enableUpcomingFeature\s*\(\s*\"([A-Za-z0-9_]+)\"")),
        ("enableExperimentalFeature", re.compile(r"\.enableExperimentalFeature\s*\(\s*\"([A-Za-z0-9_=.-]+)\"")),
    ]
    for key, pattern in patterns:
        for match in pattern.finditer(scan_text):
            findings.append(Evidence(path, line_number(text, match.start()), key, match.group(1), "Package.swift"))
    return findings


def scan_build_settings(path: pathlib.Path, text: str) -> list[Evidence]:
    findings: list[Evidence] = []
    scan_text = "\n".join(line.split("//", 1)[0] for line in text.splitlines())
    for name in SETTING_NAMES:
        pattern = re.compile(rf"\b{name}\b(?:\[[^\]\n]+\])?\s*=\s*([^;\n]+)")
        for match in pattern.finditer(scan_text):
            findings.append(
                Evidence(
                    path,
                    line_number(text, match.start()),
                    name,
                    match.group(1).strip().strip('"'),
                    path.suffix or path.name,
                )
            )
    return findings


def setting_enabled(value: str) -> bool:
    return value.strip().strip('"').lower() not in {"", "0", "no", "false", "none", "disabled"}


def summarize(findings: list[Evidence]) -> list[str]:
    values: dict[str, set[str]] = {}
    for finding in findings:
        values.setdefault(finding.key, set()).add(finding.value)

    lines: list[str] = []
    default_values = values.get("SWIFT_DEFAULT_ACTOR_ISOLATION", set()) | values.get("defaultIsolation", set())
    has_mainactor = any(value == "MainActor" or value == "MainActor.self" for value in default_values)
    has_nil = any(value == "nil" for value in default_values)
    if has_mainactor and has_nil:
        lines.append("summary: mixed default actor isolation declarations found: MainActor and nonisolated via nil. Resolve per target before applying annotations.")
    elif has_mainactor:
        lines.append("summary: default actor isolation declares MainActor for at least one target/package setting.")
    elif has_nil:
        lines.append("summary: default actor isolation declares nonisolated via nil for at least one package setting.")
    else:
        lines.append("summary: no default actor isolation declaration found in scanned files; resolve actual build settings before assuming isolation.")

    upcoming = {value for value in values.get("SWIFT_UPCOMING_FEATURE_NONISOLATED_NONSENDING_BY_DEFAULT", set()) if setting_enabled(value)} | {
        value for value in values.get("enableUpcomingFeature", set()) if value == "NonisolatedNonsendingByDefault"
    }
    if upcoming:
        lines.append("summary: NonisolatedNonsendingByDefault is declared; nonisolated async work runs on the caller actor unless marked @concurrent.")
    else:
        lines.append("summary: NonisolatedNonsendingByDefault not declared in scanned files; verify compiler defaults before relying on nonisolated async semantics.")
    return lines


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("path", nargs="?", default=".")
    args = parser.parse_args(argv)
    root = pathlib.Path(args.path).resolve()
    if not root.exists():
        print(f"error: path does not exist: {root}", file=sys.stderr)
        return 2

    files = iter_files(root)
    findings: list[Evidence] = []
    for path in files:
        text = path.read_text(encoding="utf-8", errors="replace")
        if path.name == "Package.swift":
            findings.extend(scan_package(path, text))
        if path.name == "project.pbxproj" or path.suffix == ".xcconfig":
            findings.extend(scan_build_settings(path, text))

    for finding in findings:
        try:
            display = finding.path.relative_to(root if root.is_dir() else root.parent)
        except ValueError:
            display = finding.path
        print(f"{display}:{finding.line}: {finding.key} = {finding.value}")
    for line in summarize(findings):
        print(line)
    print(f"Scanned {len(files)} settings file(s); {len(findings)} declaration(s).")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
