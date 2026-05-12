#!/usr/bin/env python3
"""Heuristic Flutter/Dart performance linter.

Scans Dart files for common agent-generated Flutter/Dart performance mistakes and
prints findings with concrete suggested fixes. This is intentionally lightweight
and uses only the Python standard library so it can run inside a Skill without
extra dependencies.

Usage:
  python scripts/flutter_dart_perf_lint.py /path/to/flutter/project
  python scripts/flutter_dart_perf_lint.py lib/main.dart --json
  python scripts/flutter_dart_perf_lint.py . --fail-on high
"""

from __future__ import annotations

import argparse
import json
import os
import re
import sys
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Iterable, Iterator, Sequence


@dataclass(frozen=True)
class Finding:
    severity: str
    rule: str
    path: str
    line: int
    column: int
    message: str
    suggestion: str
    snippet: str


SEVERITY_ORDER = {"high": 3, "medium": 2, "low": 1}
SKIP_DIR_NAMES = {
    ".dart_tool",
    ".git",
    ".idea",
    ".vscode",
    "build",
    "coverage",
    "ios",
    "android",
    "macos",
    "windows",
    "linux",
}
SKIP_PATH_SEQUENCES = {
    ("web", "build"),
}
GENERATED_SUFFIXES = (
    ".g.dart",
    ".freezed.dart",
    ".gr.dart",
    ".mocks.dart",
    ".gen.dart",
    ".config.dart",
)
LIFECYCLE_TYPES = {
    "AnimationController": "dispose",
    "TextEditingController": "dispose",
    "ScrollController": "dispose",
    "PageController": "dispose",
    "TabController": "dispose",
    "FocusNode": "dispose",
    "StreamController": "close",
    "StreamSubscription": "cancel",
    "Timer": "cancel",
}
SERVICE_CLASS_RE = re.compile(r"\bclass\s+(\w*(?:Repository|Service|Client|Parser|Mapper|Cache|Database))\b")
CONTROLLER_CLASS_RE = re.compile(r"\bclass\s+(\w*(?:Controller|Notifier|Bloc|Cubit|ViewModel))\b")
CLASS_RE = re.compile(r"\bclass\s+(\w+)\b([^\{]*)")
STATE_CLASS_RE = re.compile(r"\bclass\s+(\w+)\s+extends\s+State\s*<")
FIELD_RE_TEMPLATE = r"\b(?:late\s+)?(?:final\s+)?{typ}(?:<[^>]+>)?\s+(_?\w+)\b"


def is_generated(path: Path) -> bool:
    name = path.name
    return name.endswith(GENERATED_SUFFIXES)


def has_path_sequence(parts: Sequence[str], sequence: Sequence[str]) -> bool:
    """Return True when a path contains an exact sequence of components."""
    if not sequence or len(sequence) > len(parts):
        return False
    last_start = len(parts) - len(sequence)
    return any(tuple(parts[start : start + len(sequence)]) == tuple(sequence) for start in range(last_start + 1))


def should_skip(path: Path) -> bool:
    """Skip generated/platform directories by exact path component, not substring.

    This avoids false skips for project folders such as `my_android_tools`,
    `linux_notes`, or `buildkite_scripts`, while still ignoring normal Flutter
    platform/generated output directories.
    """
    parts = tuple(part.lower() for part in path.parts)
    if any(part in SKIP_DIR_NAMES for part in parts):
        return True
    return any(has_path_sequence(parts, sequence) for sequence in SKIP_PATH_SEQUENCES)


def iter_dart_files(inputs: Sequence[Path]) -> Iterator[Path]:
    for input_path in inputs:
        if input_path.is_file() and input_path.suffix == ".dart" and not is_generated(input_path):
            yield input_path
        elif input_path.is_dir():
            for root, dirs, files in os.walk(input_path):
                root_path = Path(root)
                dirs[:] = [d for d in dirs if not should_skip(root_path / d)]
                for file_name in files:
                    path = root_path / file_name
                    if path.suffix == ".dart" and not is_generated(path) and not should_skip(path):
                        yield path


def line_col(line: str, token: str) -> int:
    index = line.find(token)
    return max(index + 1, 1)


def add(
    findings: list[Finding],
    severity: str,
    rule: str,
    path: Path,
    line_no: int,
    line: str,
    message: str,
    suggestion: str,
    token: str = "",
) -> None:
    findings.append(
        Finding(
            severity=severity,
            rule=rule,
            path=str(path),
            line=line_no,
            column=line_col(line, token) if token else 1,
            message=message,
            suggestion=suggestion,
            snippet=line.strip(),
        )
    )


def find_block_end(lines: list[str], start_index: int) -> int:
    """Return inclusive end line index for a Dart-ish brace block."""
    depth = 0
    seen_open = False
    for index in range(start_index, len(lines)):
        line = strip_line_comment(lines[index])
        for char in line:
            if char == "{":
                depth += 1
                seen_open = True
            elif char == "}":
                depth -= 1
                if seen_open and depth <= 0:
                    return index
    return min(len(lines) - 1, start_index + 80)


def strip_line_comment(line: str) -> str:
    """Remove // comments while preserving // inside simple string literals.

    This is still a heuristic scanner, not a Dart parser. It intentionally does
    not try to fully parse block comments, raw strings, interpolation, or every
    valid Dart literal. The goal is to avoid common false positives such as
    `https://example.com` while keeping the scanner dependency-free.
    """
    in_single = False
    in_double = False
    escaped = False
    i = 0

    while i < len(line):
        char = line[i]
        next_char = line[i + 1] if i + 1 < len(line) else ""

        if escaped:
            escaped = False
            i += 1
            continue

        if char == "\\" and (in_single or in_double):
            escaped = True
            i += 1
            continue

        if char == "'" and not in_double:
            in_single = not in_single
            i += 1
            continue

        if char == '"' and not in_single:
            in_double = not in_double
            i += 1
            continue

        if char == "/" and next_char == "/" and not in_single and not in_double:
            return line[:i]

        i += 1

    return line


def window(lines: list[str], start: int, size: int) -> str:
    return "\n".join(lines[start : min(len(lines), start + size)])



def is_likely_nested_callback(block_lines: list[str], offset: int) -> bool:
    """Detect constructor calls that are probably inside a nested callback body.

    The scanner should still flag persistent UI owners created directly in
    build(), but nested callbacks and builder closures are noisier. This helper
    lowers severity for those cases instead of treating every lexical occurrence
    inside build() as equally serious.
    """
    callback_re = re.compile(
        r"\b(?:on[A-Z]\w*|listener|builder|itemBuilder|separatorBuilder|pageBuilder|routeBuilder|transitionBuilder)\s*:\s*(?:\([^)]*\)\s*)?(?:async\s*)?(?:=>|\{)"
    )
    brace_depth = 0
    seen_callback = False

    for line in block_lines[: offset + 1]:
        clean = strip_line_comment(line)
        if callback_re.search(clean):
            seen_callback = True
            brace_depth = 0

        if seen_callback:
            brace_depth += clean.count("{")
            brace_depth -= clean.count("}")
            if brace_depth > 0:
                return True
            if ";" in clean and "=>" in clean:
                return True

    return False


def scan_line_rules(path: Path, lines: list[str], findings: list[Finding]) -> None:
    for i, raw_line in enumerate(lines):
        line_no = i + 1
        line = strip_line_comment(raw_line)
        stripped = line.strip()
        if not stripped:
            continue

        if "UniqueKey(" in line:
            add(
                findings,
                "high",
                "unstable-identity",
                path,
                line_no,
                raw_line,
                "Unstable UniqueKey detected. Random identity destroys subtree state and hurts list/Hero animation continuity.",
                "Use a stable domain key such as ValueKey(model.id), or remove the key if no stable identity is needed.",
                "UniqueKey(",
            )

        if re.search(r"ValueKey\s*\(\s*(DateTime\.now|Random\s*\(|Uuid\s*\(|UniqueKey\s*\()", line):
            add(
                findings,
                "high",
                "unstable-identity",
                path,
                line_no,
                raw_line,
                "Changing ValueKey detected. Timestamp/random keys force Flutter to recreate state instead of preserving identity.",
                "Use ValueKey(model.id), ObjectKey(stableObject) only when object identity is stable, or no key.",
                "ValueKey",
            )

        if "Hero(" in line:
            block = window(lines, i, 12)
            if re.search(r"tag\s*:\s*(UniqueKey\s*\(|DateTime\.now|Random\s*\(|Uuid\s*\()", block):
                add(
                    findings,
                    "high",
                    "unstable-hero-tag",
                    path,
                    line_no,
                    raw_line,
                    "Hero uses an unstable tag. Hero transitions require stable matching tags across routes.",
                    "Use a stable domain value such as row.id for both source and destination Hero widgets.",
                    "Hero(",
                )

        if "FutureBuilder" in line:
            block = window(lines, i, 16)
            if re.search(r"future\s*:\s*[^,;\n]+\([^\n]*\)", block) and not re.search(r"future\s*:\s*(_\w+|\w+Future)\b", block):
                add(
                    findings,
                    "high",
                    "unstable-futurebuilder",
                    path,
                    line_no,
                    raw_line,
                    "FutureBuilder appears to create a new Future from a method call during build.",
                    "Create the Future once in initState, a provider, or a controller, then pass the stable Future to FutureBuilder.",
                    "FutureBuilder",
                )

        if "StreamBuilder" in line:
            block = window(lines, i, 16)
            if re.search(r"stream\s*:\s*[^,;\n]+\([^\n]*\)", block):
                add(
                    findings,
                    "medium",
                    "unstable-streambuilder",
                    path,
                    line_no,
                    raw_line,
                    "StreamBuilder appears to create/acquire a stream during build.",
                    "Create or watch the stream from a stable owner such as initState, provider, bloc, or repository field.",
                    "StreamBuilder",
                )

        if "compute(" in line and re.search(r"compute\s*\(\s*(\(|async\s*\(|\(.*\)\s*=>|\w+\s*=>)", line):
            add(
                findings,
                "high",
                "invalid-compute-callback",
                path,
                line_no,
                raw_line,
                "compute() appears to receive a closure. Closures often capture non-sendable UI objects and cannot be sent to an isolate reliably.",
                "Use a top-level or static function for compute(), and pass only isolate-sendable data such as String, int, List, Map, or typed value snapshots.",
                "compute(",
            )

        if re.search(r"class\s+\w*(Repository|Service|Client|Parser|Mapper|Cache|Database)\s+extends\s+ChangeNotifier", line):
            add(
                findings,
                "high",
                "changenotifier-service",
                path,
                line_no,
                raw_line,
                "A service/repository/parser/cache extends ChangeNotifier. This mixes non-UI work with UI invalidation.",
                "Keep services/repositories as plain Dart classes. Put UI state in a small controller/notifier that calls the service.",
                "ChangeNotifier",
            )

        if "@immutable" in line and i + 1 < len(lines):
            next_lines = window(lines, i, 4)
            if "extends ChangeNotifier" in next_lines:
                add(
                    findings,
                    "medium",
                    "immutable-mutable-controller",
                    path,
                    line_no,
                    raw_line,
                    "@immutable is applied to a mutable ChangeNotifier/controller.",
                    "Use @immutable for value models/widgets with final fields, not for mutable UI controllers.",
                    "@immutable",
                )

        if "@JsonSerializable" in line and i + 1 < len(lines):
            next_lines = window(lines, i, 6)
            if re.search(r"class\s+\w*(Controller|Notifier|Bloc|Cubit|Service|Repository|Widget)\b", next_lines):
                add(
                    findings,
                    "medium",
                    "json-serializable-wrong-layer",
                    path,
                    line_no,
                    raw_line,
                    "@JsonSerializable appears to be applied outside the DTO/json model layer.",
                    "Apply JsonSerializable to DTO/value models only, and keep controllers/services free of serialization codegen annotations.",
                    "@JsonSerializable",
                )

        if "Image.network" in line:
            block = window(lines, i, 14)
            missing_size = "width:" not in block or "height:" not in block
            missing_cache = "cacheWidth:" not in block and "cacheHeight:" not in block
            if missing_size or missing_cache:
                add(
                    findings,
                    "medium",
                    "oversized-network-image",
                    path,
                    line_no,
                    raw_line,
                    "Image.network may decode/display an oversized image because target dimensions or cache dimensions are missing.",
                    "Provide width, height, fit, and cacheWidth/cacheHeight for thumbnails and scrolling lists.",
                    "Image.network",
                )

        if "ListView(" in line:
            block = window(lines, i, 30)
            if "children:" in block and ".map(" in block:
                add(
                    findings,
                    "medium",
                    "eager-large-list",
                    path,
                    line_no,
                    raw_line,
                    "ListView with children generated by map() eagerly builds widgets and can hurt long-list performance.",
                    "Use ListView.builder, SliverList, pagination, or a small static list if the collection is truly tiny.",
                    "ListView(",
                )

        if any(token in line for token in ("BackdropFilter", "ImageFilter.blur", "Clip.antiAliasWithSaveLayer")):
            add(
                findings,
                "medium",
                "expensive-render-layer",
                path,
                line_no,
                raw_line,
                "Potentially expensive rendering layer detected in a widget tree.",
                "Avoid expensive filters/clips in scrolling or animated regions; pre-render/cache when possible and profile in DevTools.",
                stripped.split("(", 1)[0].strip(),
            )

        if re.search(r"\bBuildContext\b", line):
            nearby = "\n".join(lines[max(0, i - 8) : min(len(lines), i + 4)])
            if SERVICE_CLASS_RE.search(nearby) or re.search(r"(repository|service|client|parser|cache|database)", str(path).lower()):
                add(
                    findings,
                    "high",
                    "buildcontext-in-service",
                    path,
                    line_no,
                    raw_line,
                    "BuildContext is used in a service/repository-style layer.",
                    "Keep BuildContext in widgets/controllers. Pass plain values such as Locale, ThemeData-derived values, ids, or config into services.",
                    "BuildContext",
                )


def scan_build_methods(path: Path, lines: list[str], findings: list[Finding]) -> None:
    for i, line in enumerate(lines):
        if re.search(r"\bWidget\s+build\s*\(\s*BuildContext\s+context\s*\)", line):
            end = find_block_end(lines, i)
            block_lines = lines[i : end + 1]
            for offset, raw in enumerate(block_lines):
                line_no = i + offset + 1
                clean = strip_line_comment(raw)
                if "jsonDecode(" in clean:
                    add(
                        findings,
                        "high",
                        "cpu-work-in-build",
                        path,
                        line_no,
                        raw,
                        "jsonDecode() inside build() blocks the UI isolate during rendering.",
                        "Move parsing to a repository/worker and use compute() or Isolate.run for large payloads.",
                        "jsonDecode",
                    )
                if re.search(r"\.(sort|where|map|fold|reduce)\s*\(", clean) and ("toList" in clean or ".sort" in clean or "sort(" in clean):
                    add(
                        findings,
                        "medium",
                        "derived-work-in-build",
                        path,
                        line_no,
                        raw,
                        "Sorting/filtering/mapping collection data inside build() can repeat on every rebuild.",
                        "Precompute derived rows in a controller/provider/repository when inputs change, then render the prepared list.",
                        ".",
                    )
                nested_callback = is_likely_nested_callback(block_lines, offset)
                lifecycle_ctor = re.search(
                    r"\b(TextEditingController|ScrollController|PageController|TabController|AnimationController|FocusNode|StreamController|ChangeNotifier)\s*\(",
                    clean,
                )
                if lifecycle_ctor:
                    add(
                        findings,
                        "low" if nested_callback else "medium",
                        "lifecycle-object-in-build",
                        path,
                        line_no,
                        raw,
                        (
                            "A lifecycle object is created in a nested build callback; verify it is short-lived and not a persistent UI owner."
                            if nested_callback
                            else "A lifecycle object is created directly inside build(); verify it is not recreated on rebuilds and leaking resources."
                        ),
                        (
                            "Prefer creating persistent controllers/nodes/subscriptions in State.initState, provider setup, or dependency injection; dispose/cancel them."
                            if nested_callback
                            else "Move persistent controllers/nodes/subscriptions to State.initState, provider setup, or dependency injection, and dispose/cancel them."
                        ),
                        lifecycle_ctor.group(1),
                    )
                ui_owner_ctor = re.search(r"\b\w*(Controller|Notifier|Bloc|Cubit)\s*\(", clean)
                if not lifecycle_ctor and ui_owner_ctor:
                    add(
                        findings,
                        "low" if nested_callback else "medium",
                        "ui-state-owner-in-build",
                        path,
                        line_no,
                        raw,
                        (
                            "A controller/notifier/bloc appears in a nested build callback; verify it is not persistent UI state recreated by rebuilds."
                            if nested_callback
                            else "A controller/notifier/bloc appears to be created directly inside build(); verify it is not a persistent UI state owner."
                        ),
                        "Create persistent UI state owners outside build(), such as in initState, route/provider construction, or dependency injection.",
                        "Controller",
                    )
                if re.search(r"\b(repo|repository|service|api|client)\w*\.\w+\s*\(", clean):
                    add(
                        findings,
                        "medium",
                        "service-call-in-build",
                        path,
                        line_no,
                        raw,
                        "A service/repository/API call appears inside build().",
                        "Start work from initState, a stable provider/controller, or an event handler; render existing state in build().",
                        ".",
                    )


def scan_controller_cpu_work(path: Path, lines: list[str], findings: list[Finding]) -> None:
    for i, line in enumerate(lines):
        match = CONTROLLER_CLASS_RE.search(line)
        extends_notifier = "extends ChangeNotifier" in line
        if not match and not extends_notifier:
            continue
        end = find_block_end(lines, i)
        for j in range(i, end + 1):
            clean = strip_line_comment(lines[j])
            line_no = j + 1
            if "jsonDecode(" in clean:
                add(
                    findings,
                    "high",
                    "cpu-work-in-controller",
                    path,
                    line_no,
                    lines[j],
                    "jsonDecode() inside a controller/notifier keeps CPU parsing in the UI state layer.",
                    "Move parsing to a repository worker and use compute() or Isolate.run for large payloads.",
                    "jsonDecode",
                )
            if re.search(r"\.(sort|where|map|fold|reduce)\s*\(", clean) and ("large" in clean.lower() or "rows" in clean or "items" in clean or "toList" in clean or ".sort" in clean):
                add(
                    findings,
                    "medium",
                    "derived-work-in-controller",
                    path,
                    line_no,
                    lines[j],
                    "Collection transformation inside a controller may block UI state updates if the collection is large.",
                    "Move heavy transforms to a repository/worker and emit final immutable state snapshots from the controller.",
                    ".",
                )


def scan_high_frequency_callbacks(path: Path, lines: list[str], findings: list[Finding]) -> None:
    callback_re = re.compile(r"\b(onPanUpdate|onScaleUpdate|onHorizontalDragUpdate|onVerticalDragUpdate|addListener)\b")
    for i, line in enumerate(lines):
        if not callback_re.search(line):
            continue
        block = window(lines, i, 12)
        if "notifyListeners()" in block:
            add(
                findings,
                "medium",
                "broad-notify-in-high-frequency-callback",
                path,
                i + 1,
                lines[i],
                "notifyListeners() is called from a high-frequency callback.",
                "Keep drag/animation/scroll state local, or ensure the listening subtree is tiny and intentionally scoped.",
                "notifyListeners",
            )


def scan_state_lifecycle(path: Path, lines: list[str], findings: list[Finding]) -> None:
    for i, line in enumerate(lines):
        if not STATE_CLASS_RE.search(line):
            continue
        end = find_block_end(lines, i)
        class_text = "\n".join(lines[i : end + 1])
        for typ, cleanup in LIFECYCLE_TYPES.items():
            field_re = re.compile(FIELD_RE_TEMPLATE.format(typ=re.escape(typ)))
            for field_match in field_re.finditer(class_text):
                name = field_match.group(1)
                if name.startswith("_") or name.isidentifier():
                    cleanup_call = f"{name}.{cleanup}("
                    if cleanup_call not in class_text:
                        line_offset = class_text[: field_match.start()].count("\n")
                        source_line = lines[i + line_offset]
                        add(
                            findings,
                            "high" if typ.endswith("Controller") or typ == "FocusNode" else "medium",
                            "missing-dispose",
                            path,
                            i + line_offset + 1,
                            source_line,
                            f"Owned {typ} field '{name}' is not cleaned up with {cleanup}().",
                            f"Override dispose() and call {name}.{cleanup}() before super.dispose().",
                            name,
                        )


METHOD_START_RE = re.compile(
    r"^\s*(?:@override\s*)?(?:Future(?:<[^>]+>)?|Stream(?:<[^>]+>)?|Widget|void|[A-Za-z_][A-Za-z0-9_<>?]*)\s+\w+\s*\("
)


def bounded_lookahead(lines: list[str], start_index: int, class_end: int, max_lines: int = 10) -> str:
    collected: list[str] = []
    for k in range(start_index + 1, min(class_end + 1, start_index + 1 + max_lines)):
        clean = strip_line_comment(lines[k])
        if k > start_index + 1 and (clean.strip().startswith("@override") or METHOD_START_RE.search(clean)):
            break
        collected.append(clean)
    return "\n".join(collected)


def scan_mounted_after_await(path: Path, lines: list[str], findings: list[Finding]) -> None:
    state_spans: list[tuple[int, int]] = []
    for i, line in enumerate(lines):
        if STATE_CLASS_RE.search(line):
            state_spans.append((i, find_block_end(lines, i)))
    for start, end in state_spans:
        j = start
        while j <= end:
            if "await " not in strip_line_comment(lines[j]):
                j += 1
                continue
            joined = bounded_lookahead(lines, j, end, max_lines=10)
            uses_ui = re.search(r"\b(context|setState\s*\(|Navigator\.|ScaffoldMessenger\.|showDialog\s*\(|showModalBottomSheet\s*\()", joined)
            has_mounted = re.search(r"\bmounted\b", joined)
            if uses_ui and not has_mounted:
                add(
                    findings,
                    "medium",
                    "missing-mounted-check",
                    path,
                    j + 1,
                    lines[j],
                    "A State method awaits and then appears to use UI/context without a mounted check.",
                    "After await, check if (!mounted) return; before context, Navigator, ScaffoldMessenger, showDialog, or setState.",
                    "await",
                )
            j += 1


def scan_async_cpu_after_await(path: Path, lines: list[str], findings: list[Finding]) -> None:
    for i, raw_line in enumerate(lines):
        if "await " not in strip_line_comment(raw_line):
            continue
        look = bounded_lookahead(lines, i, len(lines) - 1, max_lines=16)
        if "compute(" in look or "Isolate.run" in look:
            continue
        risky = re.search(r"jsonDecode\s*\(|\.sort\s*\(|\.where\s*\(|\.map\s*\([^\n]*\)\s*\.toList\s*\(", look, flags=re.DOTALL)
        if risky:
            add(
                findings,
                "medium",
                "sync-cpu-after-await",
                path,
                i + 1,
                raw_line,
                "Synchronous parsing/sorting/filtering appears after await. async/await does not move CPU work off the current isolate.",
                "Move heavy CPU work to compute(), Isolate.run, or a top-level/static worker and return immutable results to UI state.",
                "await",
            )


def scan_file(path: Path) -> list[Finding]:
    try:
        text = path.read_text(encoding="utf-8")
    except UnicodeDecodeError:
        text = path.read_text(encoding="utf-8", errors="replace")
    lines = text.splitlines()
    findings: list[Finding] = []
    scan_line_rules(path, lines, findings)
    scan_build_methods(path, lines, findings)
    scan_controller_cpu_work(path, lines, findings)
    scan_high_frequency_callbacks(path, lines, findings)
    scan_state_lifecycle(path, lines, findings)
    scan_async_cpu_after_await(path, lines, findings)
    scan_mounted_after_await(path, lines, findings)
    return dedupe_findings(findings)


def dedupe_findings(findings: Iterable[Finding]) -> list[Finding]:
    seen: set[tuple[str, str, int, str]] = set()
    unique: list[Finding] = []
    for finding in findings:
        key = (finding.rule, finding.path, finding.line, finding.message)
        if key in seen:
            continue
        seen.add(key)
        unique.append(finding)
    return sorted(unique, key=lambda f: (-SEVERITY_ORDER[f.severity], f.path, f.line, f.rule))


def render_markdown(findings: list[Finding], scanned_count: int) -> str:
    high = sum(1 for f in findings if f.severity == "high")
    medium = sum(1 for f in findings if f.severity == "medium")
    low = sum(1 for f in findings if f.severity == "low")
    out = [
        "# Flutter/Dart performance lint report",
        "",
        f"Scanned Dart files: {scanned_count}",
        f"Findings: {len(findings)} high={high} medium={medium} low={low}",
        "",
    ]
    if not findings:
        out.append("No high-confidence Flutter/Dart performance anti-patterns found by this heuristic scanner.")
        out.append("Still review architecture manually: build cost, rebuild scope, isolate boundaries, keys, gestures, animation, images, and lifecycle.")
        return "\n".join(out)

    for idx, finding in enumerate(findings, start=1):
        out.extend(
            [
                f"## {idx}. {finding.severity.upper()} - {finding.rule}",
                "",
                f"Location: `{finding.path}:{finding.line}:{finding.column}`",
                "",
                f"Problem: {finding.message}",
                "",
                "Snippet:",
                "```dart",
                finding.snippet,
                "```",
                "",
                f"Suggested fix: {finding.suggestion}",
                "",
            ]
        )
    return "\n".join(out)


def severity_threshold(value: str) -> int:
    if value == "none":
        return 999
    return SEVERITY_ORDER[value]


def parse_args(argv: Sequence[str]) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Scan Flutter/Dart code for performance anti-patterns and suggested fixes.")
    parser.add_argument("paths", nargs="+", type=Path, help="Dart files or directories to scan")
    parser.add_argument("--json", action="store_true", help="Emit JSON instead of markdown")
    parser.add_argument("--max-findings", type=int, default=200, help="Maximum findings to print, default 200")
    parser.add_argument(
        "--fail-on",
        choices=["none", "low", "medium", "high"],
        default="none",
        help="Exit non-zero if a finding at or above this severity is present. Default: none",
    )
    return parser.parse_args(argv)


def main(argv: Sequence[str]) -> int:
    args = parse_args(argv)
    dart_files = sorted(set(iter_dart_files(args.paths)))
    all_findings: list[Finding] = []
    for file_path in dart_files:
        all_findings.extend(scan_file(file_path))
    all_findings = dedupe_findings(all_findings)
    limited = all_findings[: max(args.max_findings, 0)]

    if args.json:
        payload = {
            "scanned_files": len(dart_files),
            "finding_count": len(all_findings),
            "truncated": len(limited) < len(all_findings),
            "findings": [asdict(f) for f in limited],
        }
        print(json.dumps(payload, indent=2))
    else:
        print(render_markdown(limited, len(dart_files)))
        if len(limited) < len(all_findings):
            print(f"\nReport truncated: showing {len(limited)} of {len(all_findings)} findings. Use --max-findings to adjust.")

    threshold = severity_threshold(args.fail_on)
    if any(SEVERITY_ORDER[f.severity] >= threshold for f in all_findings):
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
