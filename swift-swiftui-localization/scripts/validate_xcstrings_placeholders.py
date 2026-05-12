#!/usr/bin/env python3
"""Validate placeholder preservation in .xcstrings translations.

This catches common placeholder damage. It is intentionally conservative and
can produce false positives for advanced catalog variation structures.
"""

from __future__ import annotations

import argparse
import json
import pathlib
import re
import sys
from collections import Counter


PLACEHOLDER_RE = re.compile(
    r"%(?:(\d+)\$)?(?:[-+#0 ]*)?(?:\d+|\*)?(?:\.(?:\d+|\*))?(?:hh|h|ll|l|q|L|z|t|j)?[@dDuUxXoOfeEgGcCsSpaAF]"
)


def placeholders(value: str) -> Counter:
    return Counter(match.group(0) for match in PLACEHOLDER_RE.finditer(value or ""))


def walk_units(node):
    if isinstance(node, dict):
        if "stringUnit" in node and isinstance(node["stringUnit"], dict):
            yield node["stringUnit"]
        for value in node.values():
            if isinstance(value, (dict, list)):
                yield from walk_units(value)
    elif isinstance(node, list):
        for value in node:
            yield from walk_units(value)


def main() -> int:
    parser = argparse.ArgumentParser(description="Validate .xcstrings placeholder preservation.")
    parser.add_argument("catalog", help="Path to .xcstrings")
    parser.add_argument("--source-language", help="Override source language")
    args = parser.parse_args()

    path = pathlib.Path(args.catalog).expanduser()
    data = json.loads(path.read_text(encoding="utf-8"))
    source_language = args.source_language or data.get("sourceLanguage")
    strings = data.get("strings", {})
    issues = []

    for key, entry in strings.items():
        localizations = entry.get("localizations", {})
        source_loc = localizations.get(source_language, {})
        source_units = list(walk_units(source_loc))
        source_ph = Counter()
        if source_units:
            for unit in source_units:
                source_ph += placeholders(unit.get("value", ""))
        else:
            source_ph = placeholders(key)

        for locale, localization in localizations.items():
            if locale == source_language:
                continue
            target_ph = Counter()
            for unit in walk_units(localization):
                target_ph += placeholders(unit.get("value", ""))
            if source_ph != target_ph:
                issues.append((key, locale, source_ph, target_ph))

    for key, locale, source_ph, target_ph in issues:
        print(f"{path}: placeholder mismatch [{locale}] {key}")
        print(f"  source: {dict(source_ph)}")
        print(f"  target: {dict(target_ph)}")

    print(f"{len(issues)} placeholder issue(s)")
    return 1 if issues else 0


if __name__ == "__main__":
    sys.exit(main())
