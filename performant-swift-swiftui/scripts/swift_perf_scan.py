#!/usr/bin/env python3
"""
Swift + SwiftUI performance scanner.

This script flags common AI-generated Swift anti-patterns:
- heavy synchronous work inside plain Task { }
- overbroad @MainActor isolation
- missing Task.detached / @concurrent worker boundaries
- Observation macro misuse
- SwiftUI identity, animation, gesture, and body recomputation smells

It is heuristic. Use it to focus review, not as a compiler or replacement for Instruments.
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from dataclasses import dataclass, asdict
from pathlib import Path
from typing import Iterable, List, Sequence


HEAVY_TERMS = [
    r"JSONDecoder\s*\(",
    r"\.decode\s*\(",
    r"\.sorted\s*(?:\{|\()",
    r"\.sort\s*\(",
    r"\.filter\s*\{",
    r"Data\s*\(\s*contentsOf:",
    r"FileManager\.",
    r"UIImage\s*\(\s*data:",
    r"NSImage\s*\(\s*data:",
    r"CGImageSource",
    r"resize[A-Za-z0-9_]*\s*\(",
    r"downsample[A-Za-z0-9_]*\s*\(",
    r"parse[A-Za-z0-9_]*\s*\(",
    r"build[A-Za-z0-9_]*Index\s*\(",
    r"index[A-Za-z0-9_]*\s*\(",
    r"Compression",
    r"CryptoKit",
    r"SHA256",
    r"SHA512",
]

HEAVY_RE = re.compile("|".join(HEAVY_TERMS))

SUSPICIOUS_MAINACTOR_TYPE_RE = re.compile(
    r"\b(?:final\s+)?(?:class|actor|struct)\s+"
    r"([A-Za-z_][A-Za-z0-9_]*(?:Client|Service|Repository|Repo|Decoder|Parser|Processor|Pipeline|Cache|Database|Storehouse|Indexer|SearchEngine|Loader|SyncManager|FileStore|ImageStore))\b"
)

UI_STATE_IGNORED_RE = re.compile(
    r"@ObservationIgnored\s*(?:private\s+)?(?:var|let)\s+"
    r"(rows|items|query|phase|state|selectedID|selection|isLoading|error|path|route|routes|expandedID)\b"
)


@dataclass
class Finding:
    severity: str
    rule: str
    file: str
    line: int
    message: str
    fix: str
    snippet: str = ""


def read_text(path: Path) -> str:
    try:
        return path.read_text(encoding="utf-8")
    except UnicodeDecodeError:
        return path.read_text(errors="replace")


def iter_swift_files(paths: Sequence[str]) -> Iterable[tuple[str, str]]:
    if not paths:
        data = sys.stdin.read()
        if data.strip():
            yield "<stdin>", data
        return

    for raw in paths:
        if raw == "-":
            data = sys.stdin.read()
            yield "<stdin>", data
            continue

        path = Path(raw)
        if path.is_file() and path.suffix == ".swift":
            yield str(path), read_text(path)
        elif path.is_dir():
            for child in sorted(path.rglob("*.swift")):
                if "/.build/" in str(child) or "/DerivedData/" in str(child):
                    continue
                yield str(child), read_text(child)


def line_number(text: str, index: int) -> int:
    return text.count("\n", 0, index) + 1


def clean_snippet(text: str, max_len: int = 220) -> str:
    text = re.sub(r"\s+", " ", text.strip())
    if len(text) > max_len:
        return text[: max_len - 3] + "..."
    return text


def collect_brace_block(text: str, start: int, max_chars: int = 12000) -> str:
    """Collect a rough Swift brace block starting at or after start."""
    open_at = text.find("{", start)
    if open_at == -1:
        return text[start : start + max_chars]

    depth = 0
    in_string = False
    escape = False
    end_limit = min(len(text), open_at + max_chars)

    for i in range(open_at, end_limit):
        ch = text[i]
        if in_string:
            if escape:
                escape = False
            elif ch == "\\":
                escape = True
            elif ch == '"':
                in_string = False
            continue
        if ch == '"':
            in_string = True
            continue
        if ch == "{":
            depth += 1
        elif ch == "}":
            depth -= 1
            if depth == 0:
                return text[start : i + 1]

    return text[start:end_limit]


def has_heavy_work(block: str) -> bool:
    return HEAVY_RE.search(block) is not None


def add(finding_list: List[Finding], severity: str, rule: str, file: str, line: int, message: str, fix: str, snippet: str = "") -> None:
    finding_list.append(Finding(severity, rule, file, line, message, fix, clean_snippet(snippet)))


def scan_file(file_name: str, text: str) -> List[Finding]:
    findings: List[Finding] = []
    lines = text.splitlines()

    # Observation mixing.
    if "@Observable" in text and "ObservableObject" in text:
        idx = text.find("ObservableObject")
        add(
            findings,
            "high",
            "observation-mixed-observableobject",
            file_name,
            line_number(text, idx),
            "@Observable is mixed with ObservableObject. This is usually an old/new Observation model mix.",
            "For iOS 17+ Observation code, remove ObservableObject and @Published; use @State for ownership, plain properties for read-only child views, and @Bindable only for bindings.",
            text[idx : idx + 180],
        )

    if "@Observable" in text and "@Published" in text:
        idx = text.find("@Published")
        add(
            findings,
            "high",
            "observation-mixed-published",
            file_name,
            line_number(text, idx),
            "@Published appears in a file using @Observable.",
            "Do not use @Published inside new @Observable stores. Stored vars are tracked by Observation unless ignored.",
            text[idx : idx + 180],
        )

    # Suspicious @MainActor types.
    for match in re.finditer(r"@MainActor", text):
        window = text[match.start() : match.start() + 500]
        type_match = SUSPICIOUS_MAINACTOR_TYPE_RE.search(window)
        if type_match:
            add(
                findings,
                "high",
                "broad-mainactor-type",
                file_name,
                line_number(text, match.start()),
                f"Suspicious @MainActor on non-UI type '{type_match.group(1)}'.",
                "Keep @MainActor at the UI boundary. Move services/workers off MainActor and return final values to the UI store.",
                window,
            )

    # Heavy work inside plain Task blocks.
    for match in re.finditer(r"\bTask\s*(?:<[^>]+>)?\s*(?:\([^)]*\))?\s*\{", text):
        prefix = text[max(0, match.start() - 30) : match.start()]
        if "detached" in prefix or "Task.detached" in text[max(0, match.start() - 60) : match.start() + 60]:
            continue
        block = collect_brace_block(text, match.start())
        if has_heavy_work(block):
            add(
                findings,
                "high",
                "heavy-work-in-plain-task",
                file_name,
                line_number(text, match.start()),
                "Synchronous heavy work appears inside plain Task { }. This may still run on the caller actor, including MainActor from SwiftUI.",
                "Move heavy work into Task.detached(priority: .userInitiated) { ... }.value or a @concurrent worker function. The Task may remain only as the UI orchestration shell.",
                block[:500],
            )

    # Heavy work inside MainActor.run.
    for match in re.finditer(r"MainActor\.run\s*\{", text):
        block = collect_brace_block(text, match.start())
        if has_heavy_work(block):
            add(
                findings,
                "critical",
                "heavy-work-in-mainactor-run",
                file_name,
                line_number(text, match.start()),
                "Heavy work appears inside MainActor.run.",
                "Only final UI state mutation belongs in MainActor.run. Move decode/sort/parse/image work to Task.detached or @concurrent first.",
                block[:500],
            )

    # Heavy work inside DispatchQueue.main.async.
    for match in re.finditer(r"DispatchQueue\.main\.async\s*\{", text):
        block = collect_brace_block(text, match.start())
        if has_heavy_work(block):
            add(
                findings,
                "critical",
                "heavy-work-in-dispatch-main",
                file_name,
                line_number(text, match.start()),
                "Heavy work appears inside DispatchQueue.main.async.",
                "Do not move CPU or I/O work to the main queue. Move work off-main, then publish final UI results on MainActor.",
                block[:500],
            )

    # Heavy work in SwiftUI body.
    for match in re.finditer(r"var\s+body\s*:\s*some\s+View\s*\{", text):
        block = collect_brace_block(text, match.start(), max_chars=16000)
        if has_heavy_work(block):
            add(
                findings,
                "high",
                "heavy-work-in-view-body",
                file_name,
                line_number(text, match.start()),
                "Potential expensive work appears inside a SwiftUI body.",
                "Precompute rows/results in a Swift worker or store. Keep body as cheap rendering from state.",
                block[:500],
            )

    # Global missing boundary hint for files with heavy operations but no explicit off-actor worker.
    if has_heavy_work(text) and "Task.detached" not in text and "@concurrent" not in text:
        add(
            findings,
            "medium",
            "no-explicit-cpu-worker-boundary",
            file_name,
            1,
            "File contains likely CPU-heavy synchronous operations but no Task.detached or @concurrent worker boundary.",
            "Verify where the work executes. If triggered from SwiftUI/MainActor, add Task.detached(priority: .userInitiated) or @concurrent worker APIs.",
            "",
        )

    # @ObservationIgnored on probable UI state.
    for match in UI_STATE_IGNORED_RE.finditer(text):
        add(
            findings,
            "high",
            "observationignored-ui-state",
            file_name,
            line_number(text, match.start()),
            f"@ObservationIgnored is applied to probable UI state '{match.group(1)}'.",
            "Only ignore implementation details such as task handles, debouncers, loggers, caches, and service references. Do not ignore state SwiftUI reads.",
            text[match.start() : match.start() + 180],
        )

    # SwiftUI identity and animation smells.
    for i, line in enumerate(lines, start=1):
        if re.search(r"\.id\s*\(\s*UUID\s*\(\s*\)\s*\)", line):
            add(
                findings,
                "high",
                "unstable-id-uuid",
                file_name,
                i,
                ".id(UUID()) destroys identity and can break lists, transitions, and matched geometry.",
                "Use stable Identifiable IDs. Do not force refresh by changing identity every render.",
                line,
            )

        if re.search(r"ForEach\s*\([^\n]*\.indices\s*,\s*id:\s*\\\.self", line):
            add(
                findings,
                "medium",
                "foreach-index-identity",
                file_name,
                i,
                "ForEach over indices with id: \\.self is suspicious for mutable/reorderable collections.",
                "Prefer ForEach(items) with stable Identifiable models.",
                line,
            )

        if "matchedGeometryEffect" in line and re.search(r"id:\s*UUID\s*\(", line):
            add(
                findings,
                "high",
                "matched-geometry-unstable-id",
                file_name,
                i,
                "matchedGeometryEffect uses UUID() as an ID.",
                "Use a stable ID and the same namespace for source and destination.",
                line,
            )

        if ".animation(" in line:
            local = "\n".join(lines[max(0, i - 1) : min(len(lines), i + 3)])
            if "value:" not in local and "transaction" not in local:
                add(
                    findings,
                    "medium",
                    "broad-animation-scope",
                    file_name,
                    i,
                    "Implicit animation may be broad or unscoped.",
                    "Prefer withAnimation around a specific state mutation or .animation(..., value: specificValue).",
                    local,
                )

        if re.search(r"@StateObject\b", line):
            add(
                findings,
                "info",
                "stateobject-check",
                file_name,
                i,
                "@StateObject found. This is correct for ObservableObject, but not for new @Observable stores.",
                "If this object uses @Observable, own it with @State instead. If it is ObservableObject for compatibility, this may be fine.",
                line,
            )

        if re.search(r"@ObservedObject\b", line):
            add(
                findings,
                "info",
                "observedobject-check",
                file_name,
                i,
                "@ObservedObject found. This is old ObservableObject style.",
                "For new @Observable stores, pass read-only stores as plain properties and use @Bindable only for bindings.",
                line,
            )

    return findings


def severity_rank(severity: str) -> int:
    return {"critical": 4, "high": 3, "medium": 2, "info": 1}.get(severity, 0)


def format_markdown(findings: Sequence[Finding]) -> str:
    if not findings:
        return "# Swift performance scan\n\nNo findings. Still verify with Instruments and code review."

    counts = {}
    for f in findings:
        counts[f.severity] = counts.get(f.severity, 0) + 1

    parts = ["# Swift performance scan", ""]
    parts.append(
        "Summary: "
        + ", ".join(f"{sev}={counts[sev]}" for sev in ["critical", "high", "medium", "info"] if sev in counts)
    )
    parts.append("")

    for f in sorted(findings, key=lambda x: (-severity_rank(x.severity), x.file, x.line, x.rule)):
        parts.append(f"## {f.severity.upper()} {f.rule}")
        parts.append(f"File: `{f.file}` line {f.line}")
        parts.append(f"Message: {f.message}")
        parts.append(f"Fix: {f.fix}")
        if f.snippet:
            parts.append("")
            parts.append("```swift")
            parts.append(f.snippet)
            parts.append("```")
        parts.append("")

    return "\n".join(parts).rstrip() + "\n"


def main() -> int:
    parser = argparse.ArgumentParser(description="Scan Swift files for SwiftUI performance and concurrency anti-patterns.")
    parser.add_argument("paths", nargs="*", help="Swift files or directories. Use '-' or omit paths to read stdin.")
    parser.add_argument("--json", action="store_true", help="Emit JSON instead of markdown.")
    parser.add_argument(
        "--fail-on",
        choices=["critical", "high", "medium", "info", "never"],
        default="never",
        help="Exit nonzero when findings at or above severity are present.",
    )
    args = parser.parse_args()

    findings: List[Finding] = []
    for file_name, text in iter_swift_files(args.paths):
        findings.extend(scan_file(file_name, text))

    if args.json:
        print(json.dumps([asdict(f) for f in findings], indent=2))
    else:
        print(format_markdown(findings))

    if args.fail_on != "never":
        threshold = severity_rank(args.fail_on)
        if any(severity_rank(f.severity) >= threshold for f in findings):
            return 2
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
