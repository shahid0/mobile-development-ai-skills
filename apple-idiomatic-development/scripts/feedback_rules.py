#!/usr/bin/env python3
"""Create and validate affirmative user feedback rules for this skill."""

from __future__ import annotations

import argparse
import datetime as dt
import hashlib
import pathlib
import re
import sys
from dataclasses import dataclass


ROOT = pathlib.Path(__file__).resolve().parents[1]
DEFAULT_RULE_DIR = ROOT / "references" / "user-feedback"
GROUP_RE = re.compile(r"^[a-z0-9]+(?:-[a-z0-9]+)*$")
RULE_HEADER_RE = re.compile(r"^## (?P<id>user-rule-[a-z0-9-]+)$", re.MULTILINE)
FIELD_RE = re.compile(r"^\*\*(?P<name>[A-Za-z -]+):\*\* (?P<value>.+)$")
DISCOURAGED_NEGATIVE_RE = re.compile(
    r"\b(don['’‘]?t|do not|avoid|never|stop|instead of|rather than|over|not\b|bad|wrong)\b",
    re.IGNORECASE,
)


@dataclass(frozen=True)
class Rule:
    rule_id: str
    group: str
    feedback: str
    preferred: str
    created: str
    examples: tuple[str, ...] = ()


def slugify(value: str) -> str:
    value = value.strip().lower()
    value = re.sub(r"[^a-z0-9]+", "-", value)
    value = re.sub(r"-+", "-", value).strip("-")
    return value or "rule"


def normalize_group(group: str) -> str:
    normalized = slugify(group)
    if not GROUP_RE.match(normalized):
        raise ValueError(f"Invalid group after normalization: {normalized!r}")
    return normalized


def make_rule_id(group: str, preferred: str) -> str:
    digest = hashlib.sha1(preferred.encode("utf-8")).hexdigest()[:10]
    words = "-".join(slugify(preferred).split("-")[:6])
    return f"user-rule-{group}-{words}-{digest}"


def infer_group(feedback: str, preferred: str) -> str:
    haystack = f"{feedback} {preferred}".lower()
    groups = [
        ("swiftui-animation", ("animation", "motion", "transaction", "gesture", "transition")),
        ("swiftui-text", ("text(", "format", "formatter", "localized", "string(format", "dateformatter")),
        ("swiftui-layout", ("background", "overlay", "zstack", "safearea", "layout", "geometryreader")),
        ("swiftui-observation", ("@observable", "observable", "@bindable", "@stateobject", "@published")),
        ("swift-concurrency", ("sendable", "mainactor", "task.detached", "actor", "async", "await")),
        ("metal-shaders", ("metal", "shader", "layereffect", "coloreffect", "distortioneffect")),
    ]
    for group, needles in groups:
        if any(needle in haystack for needle in needles):
            return group
    return "apple-idioms"


def strip_negative_use_clauses(feedback: str) -> str:
    return re.sub(
        r"\b(?:do not|don['’‘]?t)\s+use\b.*?(?=\buse\b|\bprefer\b|\binstead\b|\brather\b|\bdo this\b|$)",
        "",
        feedback,
        flags=re.IGNORECASE,
    )


def extract_preferred(feedback: str) -> str | None:
    feedback = strip_negative_use_clauses(feedback)
    use_comparison = re.search(
        r"\buse\s+(?P<preferred>.+?)\s+\b(?:not|instead of|rather than|over)\b\s+.+$",
        feedback,
        flags=re.IGNORECASE,
    )
    if use_comparison:
        preferred = use_comparison.group("preferred").strip(" .")
        if preferred:
            return f"Use {preferred}."

    prefer_comparison = re.search(
        r"\bprefer\s+(?P<preferred>.+?)\s+\b(?:to|instead of|rather than|over)\b\s+.+$",
        feedback,
        flags=re.IGNORECASE,
    )
    if prefer_comparison:
        preferred = prefer_comparison.group("preferred").strip(" .")
        if preferred:
            return f"Use {preferred}."

    instead_match = re.search(
        r"\b(?:instead|rather than)\b.*?\buse\s+(?P<preferred>.+)$",
        feedback,
        flags=re.IGNORECASE,
    )
    if instead_match:
        preferred = instead_match.group("preferred").strip(" .")
        if preferred:
            return preferred[0].upper() + preferred[1:] + "."

    use_matches = list(re.finditer(r"\buse\s+(?P<preferred>.+?)(?=\s+\buse\b|$)", feedback, flags=re.IGNORECASE))
    if use_matches:
        preferred = use_matches[-1].group("preferred").strip(" .")
        if preferred:
            return preferred[0].upper() + preferred[1:] + "."

    prefer_matches = list(re.finditer(r"\bprefer\s+(?P<preferred>.+?)(?=\s+\bprefer\b|$)", feedback, flags=re.IGNORECASE))
    if prefer_matches:
        preferred = prefer_matches[-1].group("preferred").strip(" .")
        if preferred:
            return preferred[0].upper() + preferred[1:] + "."

    do_this_match = re.search(r"\bdo this(?: instead)?:\s*(?P<preferred>.+)$", feedback, flags=re.IGNORECASE)
    if do_this_match:
        preferred = do_this_match.group("preferred").strip(" .")
        if preferred:
            return preferred[0].upper() + preferred[1:] + "."
    return None


def clean_positive_guidance(preferred: str) -> str:
    preferred = preferred.strip()
    if not preferred:
        raise ValueError("Preferred guidance is required.")
    if DISCOURAGED_NEGATIVE_RE.search(preferred):
        raise ValueError(
            "Preferred guidance must be affirmative. Rewrite it as what to do."
        )
    if not re.match(r"^(Use|Prefer|Apply|Create|Keep|Centralize|Fetch|Run|Build|Model|Store|Pass|Read|Display|Attach|Present|Isolate|Wrap)\b", preferred):
        preferred = f"Use {preferred}"
    if preferred[0].islower():
        preferred = preferred[0].upper() + preferred[1:]
    if preferred[-1] not in ".!?":
        preferred += "."
    return preferred


def render_rule(rule: Rule) -> str:
    text = (
        f"## {rule.rule_id}\n\n"
        f"**Group:** {rule.group}\n"
        f"**Created:** {rule.created}\n"
        f"**Updated:** {rule.created}\n"
        f"**Guidance:** {rule.preferred}\n"
    )
    for example in rule.examples:
        text += f"**Examples:** {example}\n"
    return text


def add_rule(args: argparse.Namespace) -> int:
    rule_dir = pathlib.Path(args.dir).resolve()
    rule_dir.mkdir(parents=True, exist_ok=True)
    preferred = args.preferred or extract_preferred(args.feedback)
    if preferred is None:
        raise ValueError(
            "Could not extract affirmative guidance. Pass --preferred with what to do next time."
        )
    preferred = clean_positive_guidance(preferred)
    examples = tuple(clean_positive_guidance(example) for example in (args.example or ()))
    group = normalize_group(args.group or infer_group(args.feedback, preferred))
    rule = Rule(
        rule_id=make_rule_id(group, preferred),
        group=group,
        feedback=args.feedback.strip(),
        preferred=preferred,
        created=args.date or dt.date.today().isoformat(),
        examples=examples,
    )
    path = rule_dir / f"user-rules-{group}.md"
    if path.exists():
        text = path.read_text(encoding="utf-8")
    else:
        title = group.replace("-", " ").title()
        text = f"# User Rules: {title}\n\n"
    if f"## {rule.rule_id}\n" in text:
        print(path)
        return 0
    if not text.endswith("\n"):
        text += "\n"
    text += "\n" + render_rule(rule)
    path.write_text(text, encoding="utf-8")
    print(path)
    return 0


def parse_rule_blocks(text: str) -> list[tuple[str, dict[str, list[str]]]]:
    matches = list(RULE_HEADER_RE.finditer(text))
    blocks: list[tuple[str, dict[str, list[str]]]] = []
    for index, match in enumerate(matches):
        start = match.end()
        end = matches[index + 1].start() if index + 1 < len(matches) else len(text)
        fields: dict[str, list[str]] = {}
        for line in text[start:end].splitlines():
            field = FIELD_RE.match(line)
            if field:
                fields.setdefault(field.group("name").lower(), []).append(field.group("value").strip())
        blocks.append((match.group("id"), fields))
    return blocks


def validate_rule_file(path: pathlib.Path) -> list[str]:
    errors: list[str] = []
    text = path.read_text(encoding="utf-8")
    if not path.name.startswith("user-rules-") or path.suffix != ".md":
        if path.name != "README.md":
            errors.append(f"{path}: feedback rule files must be named user-rules-<group>.md")
        return errors
    group = path.stem.removeprefix("user-rules-")
    if not GROUP_RE.match(group):
        errors.append(f"{path}: invalid group slug in filename")
    blocks = parse_rule_blocks(text)
    if not blocks:
        errors.append(f"{path}: no rule blocks found")
    seen: set[str] = set()
    for rule_id, fields in blocks:
        if rule_id in seen:
            errors.append(f"{path}: duplicate rule id {rule_id}")
        seen.add(rule_id)
        if not rule_id.startswith(f"user-rule-{group}-"):
            errors.append(f"{path}: rule id {rule_id} does not match file group {group}")
        for required in ("group", "created", "updated", "guidance"):
            if required not in fields:
                errors.append(f"{path}: {rule_id} missing {required!r}")
        for singular in ("group", "created", "updated", "guidance"):
            if len(fields.get(singular, [])) > 1:
                errors.append(f"{path}: {rule_id} has duplicate {singular!r} fields")
        group_values = fields.get("group", [])
        if group_values and group_values[0] != group:
            errors.append(f"{path}: {rule_id} group field must be {group!r}")
        for guidance in fields.get("guidance", []):
            if DISCOURAGED_NEGATIVE_RE.search(guidance):
                errors.append(f"{path}: {rule_id} guidance must be affirmative")
        for example in fields.get("examples", []):
            if DISCOURAGED_NEGATIVE_RE.search(example):
                errors.append(f"{path}: {rule_id} examples must be affirmative")
    return errors


def validate_rules(args: argparse.Namespace) -> int:
    rule_dir = pathlib.Path(args.dir).resolve()
    if not rule_dir.exists():
        raise ValueError(f"Rule directory does not exist: {rule_dir}")
    errors: list[str] = []
    rule_files = sorted(rule_dir.glob("user-rules-*.md"))
    if not rule_files:
        errors.append(f"{rule_dir}: no feedback rule files found")
    for path in sorted(rule_dir.glob("*.md")):
        errors.extend(validate_rule_file(path))
    if errors:
        for error in errors:
            print(error, file=sys.stderr)
        return 1
    print(f"Validated feedback rules in {rule_dir}")
    return 0


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    subparsers = parser.add_subparsers(dest="command", required=True)

    add = subparsers.add_parser("add", help="Add an affirmative user rule")
    add.add_argument("--group", help="Rule group, e.g. swiftui-layout. Inferred when omitted.")
    add.add_argument("--feedback", required=True, help="Original user correction")
    add.add_argument("--preferred", help="Affirmative guidance to store")
    add.add_argument("--example", action="append", help="Optional affirmative example to store. Can be passed multiple times.")
    add.add_argument("--date", help="ISO date override for tests")
    add.add_argument("--dir", default=str(DEFAULT_RULE_DIR), help="Rule directory")
    add.set_defaults(func=add_rule)

    validate = subparsers.add_parser("validate", help="Validate rule files")
    validate.add_argument("dir", nargs="?", default=str(DEFAULT_RULE_DIR))
    validate.set_defaults(func=validate_rules)
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    try:
        return args.func(args)
    except ValueError as error:
        print(f"error: {error}", file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
