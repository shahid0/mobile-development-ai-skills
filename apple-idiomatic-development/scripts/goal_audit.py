#!/usr/bin/env python3
"""Audit this skill against the original user objective."""

from __future__ import annotations

import argparse
import pathlib
import re
import subprocess
import sys


REQUIRED_EVIDENCE = {
    "skill frontmatter": ["SKILL.md", "name: apple-idiomatic-development", "description:"],
    "pwm claude sonnet detailed": ["SKILL.md", "pwm", "claude_sonnet", "--intent detailed"],
    "sosumi apple docs": ["SKILL.md", "searchAppleDocumentation", "fetchAppleDocumentation"],
    "web/current source grounding": ["references/source-grounding.md", "Apple Developer Documentation", "Swift.org", "pwm"],
    "research backed mechanics": ["references/skill-mechanics.md", "SWE-agent", "Agentless", "AutoCodeRover", "SWE-Bench+", "Self-Repair", "Retrieval-Augmented Generation", "feedback rules"],
    "model steering mechanics": ["references/skill-mechanics.md", "cannot retrain model weights", "localize before editing", "external feedback", "repository-level behavior", "phase gates"],
    "model control research": ["references/model-control.md", "Control Stack", "Self-Consistency", "ReAct", "Direct Preference Optimization", "Hallucination Guard"],
    "repository localization": ["references/repository-localization.md", "Localization Protocol", "Typed Diagnostic Loop", "compiler_diagnostic_triage.py", "CoSIL"],
    "gap filling guidance": ["references/gap-cases.md", "Default Isolation Is A Project Fact", "NonisolatedNonsendingByDefault", "@concurrent", "render-scope"],
    "swiftui guidance": ["references/swiftui-patterns.md", "Text(value, format: style)", ".background(alignment:content:)", "@Bindable"],
    "swiftui source coverage": ["references/swiftui-patterns.md", "Sources", "https://developer.apple.com/documentation/swiftui/text/init(_:format:)", "https://developer.apple.com/documentation/foundation/formatstyle"],
    "swift 6 guidance": ["references/swift6-concurrency.md", "Swift 6", "SWIFT_DEFAULT_ACTOR_ISOLATION", "NonisolatedNonsendingByDefault", "Task.detached"],
    "swift 6 source coverage": ["references/swift6-concurrency.md", "Sources", "https://www.swift.org/migration/documentation/swift-6-concurrency-migration-guide/", "https://developer.apple.com/documentation/packagedescription/swiftsetting/defaultisolation(_:_:)" ],
    "metal shaders guidance": ["references/animation-metal.md", "ShaderLibrary", "colorEffect", "distortionEffect", "layerEffect"],
    "animation guidance": ["references/animation-metal.md", "transaction(_:)", "accessibilityReduceMotion", "PhaseAnimator"],
    "animation source coverage": ["references/animation-metal.md", "Sources", "https://developer.apple.com/documentation/swiftui/view/transaction(_:)", "https://developer.apple.com/documentation/swiftui/shader"],
    "architecture guidance": ["references/architecture.md", "SwiftUI views render state", "Services", "Workers"],
    "architecture source coverage": ["references/architecture.md", "Sources", "https://developer.apple.com/documentation/swiftui/app-organization"],
    "quality gate guidance": ["references/testing-quality.md", "Build", "accessibility", "performance"],
    "quality source coverage": ["references/testing-quality.md", "Sources", "https://developer.apple.com/documentation/xcode/organizing-tests-to-improve-feedback"],
    "advanced validation matrix": ["references/apple-validation-matrix.md", "performAccessibilityAudit", "XCTApplicationLaunchMetric", "SwiftUI Instruments", "metamorphic"],
    "feedback readme": ["references/user-feedback/README.md", "affirmative", "feedback_rules.py"],
    "background user rule": ["references/user-feedback/user-rules-swiftui-layout.md", ".background"],
    "text format user rule": ["references/user-feedback/user-rules-swiftui-text.md", "Text(value, format:)"],
    "reduce motion user rule": ["references/user-feedback/user-rules-swiftui-animation.md", "narrowest transaction or motion-policy scope"],
    "feedback style user rule": ["references/user-feedback/user-rules-feedback-style.md", "direct affirmative rules", "Use Text(value, format:) for localized value display."],
    "feedback metadata": ["references/user-feedback/user-rules-swiftui-layout.md", "**Created:**", "**Updated:**", "**Examples:**"],
    "feedback script": ["scripts/feedback_rules.py", "extract_preferred", "infer_group", "validate"],
    "concurrency settings scanner": ["scripts/concurrency_settings_scan.py", "SWIFT_DEFAULT_ACTOR_ISOLATION", "defaultIsolation", "NonisolatedNonsendingByDefault", "[^\\]\\n]+"],
    "compiler diagnostic triage": ["scripts/compiler_diagnostic_triage.py", "concurrency-isolation", "availability", "protocol-conformance"],
    "reference source audit": ["scripts/reference_source_audit.py", "arxiv.org", "developer.apple.com", "source-backed"],
    "swift scanner": ["scripts/swift_apple_scan.py", "--strict", "advisory", "text-string-format"],
    "xcode validation scanner": ["scripts/xcode_validation_scan.py", "xctestplan", "sanitizer", "localization"],
    "self tests": ["scripts/self_test.py", "test_feedback_rules", "test_swift_scanner", "test_compiler_diagnostic_triage", "test_xcode_validation_scan", "test_reference_source_audit", "SpacedFormat", "disabledDiagnostics", "duplicate-examples"],
}
NEGATIVE_RULE_RE = re.compile(
    r"\b(don['’‘]?t|do not|avoid|never|stop|instead of|rather than|over|not\b|bad|wrong)\b",
    re.IGNORECASE,
)


def read(root: pathlib.Path, relative: str) -> str:
    path = root / relative
    if not path.exists():
        raise FileNotFoundError(relative)
    return path.read_text(encoding="utf-8")


def audit_files(root: pathlib.Path) -> list[str]:
    errors: list[str] = []
    for label, evidence in REQUIRED_EVIDENCE.items():
        relative, *needles = evidence
        try:
            text = read(root, relative)
        except FileNotFoundError:
            errors.append(f"{label}: missing {relative}")
            continue
        folded = text.lower()
        for needle in needles:
            if needle.lower() not in folded:
                errors.append(f"{label}: {relative} missing {needle!r}")
    return errors


def audit_positive_rule_store(root: pathlib.Path) -> list[str]:
    errors: list[str] = []
    for path in sorted((root / "references" / "user-feedback").glob("user-rules-*.md")):
        text = path.read_text(encoding="utf-8")
        if "User wording:" in text:
            errors.append(f"{path.relative_to(root)} stores raw user wording; store affirmative guidance only")
        if "**Updated:**" not in text:
            errors.append(f"{path.relative_to(root)} missing updated metadata")
        if "**Examples:**" not in text:
            errors.append(f"{path.relative_to(root)} missing an affirmative example")
        for line in text.splitlines():
            if line.startswith(("**Guidance:**", "**Examples:**")) and NEGATIVE_RULE_RE.search(line):
                errors.append(f"{path.relative_to(root)} guidance/example contains negative wording")
    return errors


def run(root: pathlib.Path, command: list[str]) -> tuple[int, str, str]:
    result = subprocess.run(command, cwd=root, text=True, capture_output=True, check=False)
    return result.returncode, result.stdout, result.stderr


def audit_commands(root: pathlib.Path) -> list[str]:
    errors: list[str] = []
    commands = [
        [sys.executable, "scripts/skill_lint.py", "."],
        [sys.executable, "scripts/reference_source_audit.py", "references"],
        [sys.executable, "scripts/feedback_rules.py", "validate", "references/user-feedback"],
        [sys.executable, "scripts/self_test.py"],
    ]
    for command in commands:
        code, stdout, stderr = run(root, command)
        if code != 0:
            errors.append(
                f"command failed: {' '.join(command)}\nstdout:\n{stdout}\nstderr:\n{stderr}"
            )
    return errors


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("root", nargs="?", default=".")
    args = parser.parse_args(argv)
    root = pathlib.Path(args.root).resolve()
    errors = audit_files(root)
    errors.extend(audit_positive_rule_store(root))
    errors.extend(audit_commands(root))
    if errors:
        for error in errors:
            print(error, file=sys.stderr)
        return 1
    print(f"Goal audit passed: {root}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
