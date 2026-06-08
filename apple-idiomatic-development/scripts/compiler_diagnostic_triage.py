#!/usr/bin/env python3
"""Classify Swift/Xcode compiler and test diagnostics for repair routing."""

from __future__ import annotations

import argparse
import pathlib
import re
import sys
from dataclasses import dataclass


@dataclass(frozen=True)
class Rule:
    category: str
    pattern: re.Pattern[str]
    route: str


RULES = [
    Rule(
        "concurrency-isolation",
        re.compile(r"\b(MainActor|actor-isolated|nonisolated|Sendable|sending|data race|global actor|isolated|async call|does not support concurrency|concurrent|concurrency)\b", re.I),
        "Inspect default isolation, actor boundary, Sendable crossings, and caller/callee isolation before editing.",
    ),
    Rule(
        "availability",
        re.compile(r"\b(only available in|unavailable|availability|#available|@available|introduced in)\b", re.I),
        "Check deployment target, API availability, and source-backed alternatives.",
    ),
    Rule(
        "protocol-conformance",
        re.compile(r"\b(does not conform|conformance|protocol requirement|witness|associated type)\b", re.I),
        "Inspect protocol isolation, associated types, access level, and extension placement.",
    ),
    Rule(
        "macro-or-generated-code",
        re.compile(r"\b(macro expansion|external macro|generated|@Observable|@Model|SwiftData)\b", re.I),
        "Inspect macro expansion assumptions and generated-code constraints before rewriting user code.",
    ),
    Rule(
        "type-system",
        re.compile(r"\b(cannot convert|extra argument|missing argument|generic parameter|ambiguous|no exact matches|type of expression|has no member|no member|cannot find|cannot infer)\b", re.I),
        "Localize to signature, overload, generic constraint, label, or inferred type mismatch.",
    ),
    Rule(
        "ui-test-or-accessibility",
        re.compile(r"\b(XCUI|accessibility|identifier|label|waitForExistence|element.*not found|Failed to get matching snapshot)\b", re.I),
        "Inspect accessibility identifiers, labels, query stability, locale, and current screen state.",
    ),
    Rule(
        "linking-build-system",
        re.compile(r"\b(linker command failed|ld:|module not found|no such module|library not found|Build input file cannot be found)\b", re.I),
        "Inspect target membership, package/product linkage, generated files, and scheme configuration.",
    ),
]


DIAGNOSTIC_RE = re.compile(
    r"(?P<path>[^:\n]+\.swift):(?P<line>\d+):(?P<column>\d+):\s*(?P<level>error|warning|note):\s*(?P<message>.+)",
    re.I,
)


def classify(message: str) -> tuple[str, str]:
    for rule in RULES:
        if rule.pattern.search(message):
            return rule.category, rule.route
    return "unclassified", "Localize the diagnostic to the smallest symbol, then inspect nearby signatures, imports, and tests."


def parse(text: str) -> list[dict[str, str]]:
    diagnostics: list[dict[str, str]] = []
    for match in DIAGNOSTIC_RE.finditer(text):
        message = match.group("message").strip()
        category, route = classify(message)
        diagnostics.append(
            {
                "path": match.group("path").strip(),
                "line": match.group("line"),
                "column": match.group("column"),
                "level": match.group("level").lower(),
                "message": message,
                "category": category,
                "route": route,
            }
        )
    return diagnostics


def read_input(path: str | None) -> str:
    if path:
        return pathlib.Path(path).read_text(encoding="utf-8", errors="replace")
    return sys.stdin.read()


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("log", nargs="?", help="Build/test log path. Reads stdin when omitted.")
    args = parser.parse_args(argv)
    text = read_input(args.log)
    diagnostics = parse(text)
    if not diagnostics:
        print("No Swift diagnostics found.")
        return 0
    counts: dict[str, int] = {}
    for item in diagnostics:
        counts[item["category"]] = counts.get(item["category"], 0) + 1
        print(
            f"{item['path']}:{item['line']}:{item['column']}: {item['level']}: "
            f"{item['category']}: {item['message']}"
        )
        print(f"  route: {item['route']}")
    print("Summary:")
    for category, count in sorted(counts.items()):
        print(f"  {category}: {count}")
    return 1 if any(item["level"] == "error" for item in diagnostics) else 0


if __name__ == "__main__":
    raise SystemExit(main())
