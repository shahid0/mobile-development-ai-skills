#!/usr/bin/env python3
"""Scan Xcode schemes and test plans for validation coverage routing."""

from __future__ import annotations

import argparse
import json
import pathlib
import sys
import xml.etree.ElementTree as ET
from dataclasses import dataclass
from typing import Any


@dataclass(frozen=True)
class Finding:
    path: pathlib.Path
    code: str
    message: str
    severity: str = "advisory"


def iter_files(root: pathlib.Path, suffix: str) -> list[pathlib.Path]:
    if root.is_file():
        return [root] if root.name.endswith(suffix) else []
    ignored = {".build", "DerivedData", ".git", "Pods", "Carthage"}
    files: list[pathlib.Path] = []
    for path in root.rglob(f"*{suffix}"):
        if any(part in ignored for part in path.parts):
            continue
        if path.is_file():
            files.append(path)
    return sorted(files)


def contains_key_or_truthy_value(value: Any, needles: tuple[str, ...]) -> bool:
    folded_needles = tuple(needle.lower() for needle in needles)
    if isinstance(value, dict):
        for key, child in value.items():
            text = str(key).lower()
            if any(needle in text for needle in folded_needles) and truthy(child):
                return True
            if contains_key_or_truthy_value(child, needles):
                return True
    elif isinstance(value, list):
        return any(contains_key_or_truthy_value(child, needles) for child in value)
    return False


def contains_truthy_key(value: Any, keys: tuple[str, ...]) -> bool:
    folded_keys = {key.lower() for key in keys}
    if isinstance(value, dict):
        for key, child in value.items():
            if str(key).lower() in folded_keys and truthy(child):
                return True
            if contains_truthy_key(child, keys):
                return True
    elif isinstance(value, list):
        return any(contains_truthy_key(child, keys) for child in value)
    return False


def contains_key_or_value(value: Any, needles: tuple[str, ...]) -> bool:
    folded_needles = tuple(needle.lower() for needle in needles)
    if isinstance(value, dict):
        for key, child in value.items():
            text = str(key).lower()
            if any(needle in text for needle in folded_needles):
                return True
            if contains_key_or_value(child, needles):
                return True
    elif isinstance(value, list):
        return any(contains_key_or_value(child, needles) for child in value)
    else:
        text = str(value).lower()
        return any(needle in text for needle in folded_needles)
    return False


def truthy(value: Any) -> bool:
    if isinstance(value, bool):
        return value
    if isinstance(value, (int, float)):
        return value != 0
    if value is None:
        return False
    text = str(value).strip().lower()
    return text not in {"", "0", "false", "no", "none", "disabled"}


def scan_test_plan(path: pathlib.Path) -> list[Finding]:
    findings: list[Finding] = []
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as error:
        return [Finding(path, "testplan-parse", f"Could not parse test plan JSON: {error}", "error")]

    configurations = data.get("configurations")
    if not isinstance(configurations, list) or not configurations:
        findings.append(Finding(path, "testplan-no-configurations", "Test plan has no configurations."))
        configurations = []

    if len(configurations) < 2:
        findings.append(Finding(path, "testplan-single-configuration", "Consider multiple configurations for locale, appearance, accessibility, or sanitizer coverage."))

    if not contains_key_or_value(data, ("language", "locale", "region", "application language")):
        findings.append(Finding(path, "testplan-no-localization", "No localization/region signal found. Add long-string and RTL configurations for UI-sensitive flows."))

    if not contains_key_or_value(data, ("dark", "appearance", "uiuserinterfacestyle")):
        findings.append(Finding(path, "testplan-no-appearance", "No appearance signal found. Add light/dark coverage for UI-sensitive flows."))

    if not contains_key_or_value(data, ("dynamic type", "content size", "preferredcontentsizecategory", "accessibility")):
        findings.append(Finding(path, "testplan-no-accessibility-state", "No Dynamic Type/accessibility state signal found. Add accessibility-focused configurations."))

    if not contains_truthy_key(data, ("enableThreadSanitizer", "enableAddressSanitizer", "enableASan", "enableUBSanitizer", "enableMainThreadChecker")):
        findings.append(Finding(path, "testplan-no-sanitizer", "No sanitizer signal found. Add sanitizer configurations for runtime-sensitive changes."))

    return findings


def scan_scheme(path: pathlib.Path) -> list[Finding]:
    findings: list[Finding] = []
    try:
        root = ET.fromstring(path.read_text(encoding="utf-8", errors="replace").lstrip())
    except (OSError, ET.ParseError) as error:
        return [Finding(path, "scheme-parse", f"Could not parse scheme XML: {error}", "error")]

    tags = {element.tag for element in root.iter()}
    if "TestAction" not in tags:
        findings.append(Finding(path, "scheme-no-test-action", "Scheme has no visible TestAction."))

    if not {"LaunchAction", "ProfileAction"}.issubset(tags):
        findings.append(Finding(path, "scheme-weak-run-profile", "Scheme lacks run/profile signal; performance validation may be underspecified."))

    diagnostic_keys = ("enableThreadSanitizer", "enableAddressSanitizer", "enableUBSanitizer", "enableMainThreadChecker")
    has_diagnostics = any(
        truthy(element.attrib.get(key))
        for element in root.iter()
        for key in diagnostic_keys
    )
    if not has_diagnostics:
        findings.append(Finding(path, "scheme-no-diagnostics", "No sanitizer/Main Thread Checker signal found in scheme."))

    return findings


def display(path: pathlib.Path, root: pathlib.Path) -> pathlib.Path:
    try:
        return path.relative_to(root if root.is_dir() else root.parent)
    except ValueError:
        return path


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("path", help="Xcode project/workspace directory or file")
    args = parser.parse_args(argv)
    root = pathlib.Path(args.path).resolve()
    if not root.exists():
        print(f"error: path does not exist: {root}", file=sys.stderr)
        return 2

    findings: list[Finding] = []
    test_plans = iter_files(root, ".xctestplan")
    schemes = iter_files(root, ".xcscheme")
    for path in test_plans:
        findings.extend(scan_test_plan(path))
    for path in schemes:
        findings.extend(scan_scheme(path))

    if not test_plans:
        findings.append(Finding(root, "no-test-plans", "No .xctestplan files found. Consider test plans for matrix validation."))
    if not schemes:
        findings.append(Finding(root, "no-shared-schemes", "No .xcscheme files found. Verify project-native build/test/profile commands manually."))

    for finding in findings:
        print(f"{display(finding.path, root)}: {finding.severity}: {finding.code}: {finding.message}")
    print(f"Scanned {len(test_plans)} test plan(s), {len(schemes)} scheme(s); {len(findings)} finding(s).")
    return 1 if any(finding.severity == "error" for finding in findings) else 0


if __name__ == "__main__":
    raise SystemExit(main())
