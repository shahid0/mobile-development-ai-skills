#!/usr/bin/env python3
"""Inspect .xcstrings locale coverage, states, stale entries, and metadata.

Heuristic reporting only; it does not replace Xcode's catalog editor.
"""

from __future__ import annotations

import argparse
import json
import pathlib
import sys
from collections import Counter, defaultdict


def load(path: pathlib.Path) -> dict:
    with path.open(encoding="utf-8") as f:
        return json.load(f)


def string_state(unit: dict | None) -> str:
    if not unit:
        return "missing"
    return unit.get("state", "unknown")


def walk_string_units(node):
    if isinstance(node, dict):
        if "stringUnit" in node and isinstance(node["stringUnit"], dict):
            yield node["stringUnit"]
        for value in node.values():
            yield from walk_string_units(value)
    elif isinstance(node, list):
        for value in node:
            yield from walk_string_units(value)


def main() -> int:
    parser = argparse.ArgumentParser(description="Inspect an Xcode String Catalog.")
    parser.add_argument("catalog", help="Path to .xcstrings")
    parser.add_argument("--show-keys", action="store_true", help="Print keys with missing/new/review/stale states")
    args = parser.parse_args()

    path = pathlib.Path(args.catalog).expanduser()
    if not path.exists():
        print(f"Missing catalog: {path}", file=sys.stderr)
        return 2

    data = load(path)
    strings = data.get("strings", {})
    source_language = data.get("sourceLanguage", "unknown")

    locales = set()
    state_counts: dict[str, Counter] = defaultdict(Counter)
    extraction_counts = Counter()
    should_not_translate = []
    issue_keys = []

    for key, entry in strings.items():
        if entry.get("shouldTranslate") is False:
            should_not_translate.append(key)
        extraction = entry.get("extractionState", "unknown")
        extraction_counts[extraction] += 1
        if extraction == "stale":
            issue_keys.append((key, "stale", "source no longer found"))

        localizations = entry.get("localizations", {})
        locales.update(localizations.keys())
        for locale, localization in localizations.items():
            units = list(walk_string_units(localization))
            if not units:
                state_counts[locale]["missing"] += 1
                issue_keys.append((key, locale, "missing stringUnit"))
                continue
            for unit in units:
                state = string_state(unit)
                state_counts[locale][state] += 1
                if state in {"new", "needs_review"}:
                    issue_keys.append((key, locale, state))

    print(f"Catalog: {path}")
    print(f"Source language: {source_language}")
    print(f"Keys: {len(strings)}")
    print(f"Locales: {', '.join(sorted(locales)) if locales else '(none)'}")
    print("\nExtraction states:")
    for state, count in sorted(extraction_counts.items()):
        print(f"  {state}: {count}")
    print(f"shouldTranslate=false: {len(should_not_translate)}")

    if state_counts:
        print("\nLocalization states:")
        for locale in sorted(state_counts):
            total = sum(state_counts[locale].values())
            translated = state_counts[locale].get("translated", 0)
            pct = (translated / total * 100) if total else 0
            details = ", ".join(f"{k}={v}" for k, v in sorted(state_counts[locale].items()))
            print(f"  {locale}: {translated}/{total} translated ({pct:.1f}%) [{details}]")

    if args.show_keys and issue_keys:
        print("\nReview keys:")
        for key, locale, reason in issue_keys:
            print(f"  [{locale}] {reason}: {key}")

    return 1 if issue_keys else 0


if __name__ == "__main__":
    sys.exit(main())
