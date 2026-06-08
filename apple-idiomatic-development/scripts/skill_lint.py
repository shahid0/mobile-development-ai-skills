#!/usr/bin/env python3
"""Deterministic structural lint for the apple-idiomatic-development skill."""

from __future__ import annotations

import argparse
import pathlib
import re
import sys


REQUIRED_FILES = [
    "SKILL.md",
    "agents/openai.yaml",
    "references/gap-cases.md",
    "references/skill-mechanics.md",
    "references/model-control.md",
    "references/repository-localization.md",
    "references/source-grounding.md",
    "references/architecture.md",
    "references/swiftui-patterns.md",
    "references/swift6-concurrency.md",
    "references/animation-metal.md",
    "references/testing-quality.md",
    "references/apple-validation-matrix.md",
    "references/user-feedback/README.md",
    "scripts/feedback_rules.py",
    "scripts/concurrency_settings_scan.py",
    "scripts/compiler_diagnostic_triage.py",
    "scripts/reference_source_audit.py",
    "scripts/goal_audit.py",
    "scripts/skill_lint.py",
    "scripts/self_test.py",
    "scripts/swift_apple_scan.py",
    "scripts/xcode_validation_scan.py",
]

REQUIRED_SKILL_PHRASES = [
    "searchAppleDocumentation",
    "fetchAppleDocumentation",
    "pwm",
    "claude_sonnet",
    "Swift 6",
    "SwiftUI",
    "Observation",
    "Metal",
    "user-feedback",
]

REFERENCE_LINK_RE = re.compile(r"\]\((references/[^)]+)\)")
MARKDOWN_LINK_RE = re.compile(r"\]\((?!https?://|#)([^)]+)\)")
FRONTMATTER_RE = re.compile(r"^---\n(?P<body>.*?)\n---\n", re.DOTALL)


def lint_skill(root: pathlib.Path) -> list[str]:
    errors: list[str] = []
    for relative in REQUIRED_FILES:
        path = root / relative
        if not path.exists():
            errors.append(f"missing required file: {relative}")
    skill_path = root / "SKILL.md"
    if not skill_path.exists():
        return errors
    text = skill_path.read_text(encoding="utf-8")
    frontmatter = FRONTMATTER_RE.match(text)
    if not frontmatter:
        errors.append("SKILL.md must start with YAML frontmatter")
    else:
        body = frontmatter.group("body")
        if "name: apple-idiomatic-development" not in body:
            errors.append("SKILL.md frontmatter must define the skill name")
        if "description:" not in body or "TODO" in body:
            errors.append("SKILL.md frontmatter needs a complete description")
    for phrase in REQUIRED_SKILL_PHRASES:
        if phrase not in text:
            errors.append(f"SKILL.md missing required phrase: {phrase}")
    if "TODO" in text:
        errors.append("SKILL.md contains TODO")
    for link in REFERENCE_LINK_RE.findall(text):
        if not (root / link).exists():
            errors.append(f"SKILL.md links missing reference: {link}")
    for markdown in (root / "references").rglob("*.md"):
        markdown_text = markdown.read_text(encoding="utf-8")
        for link in MARKDOWN_LINK_RE.findall(markdown_text):
            if link.startswith("mailto:"):
                continue
            target = (markdown.parent / link.split("#", 1)[0]).resolve()
            if link.split("#", 1)[0] and not target.exists():
                errors.append(f"{markdown.relative_to(root)} links missing file: {link}")
    if len(text.splitlines()) > 500:
        errors.append("SKILL.md should stay under 500 lines for progressive disclosure")
    return errors


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("root", nargs="?", default=".", help="Skill root")
    args = parser.parse_args(argv)
    root = pathlib.Path(args.root).resolve()
    errors = lint_skill(root)
    if errors:
        for error in errors:
            print(error, file=sys.stderr)
        return 1
    print(f"Skill structure validated: {root}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
