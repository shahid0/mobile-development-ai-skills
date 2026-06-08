#!/usr/bin/env python3
"""Audit reference files for source-backed research and documentation links."""

from __future__ import annotations

import argparse
import pathlib
import re
import sys


URL_RE = re.compile(r"https?://[^\s)>\]]+")
RESEARCH_TERMS = (
    "arxiv.org",
    "developer.apple.com",
    "swift.org",
    "dl.acm.org",
    "doi.org",
)
SOURCE_BACKED_REFERENCES = {
    "animation-metal.md",
    "apple-validation-matrix.md",
    "architecture.md",
    "gap-cases.md",
    "model-control.md",
    "repository-localization.md",
    "skill-mechanics.md",
    "source-grounding.md",
    "swift6-concurrency.md",
    "swiftui-patterns.md",
    "testing-quality.md",
}


def iter_markdown(root: pathlib.Path) -> list[pathlib.Path]:
    if root.is_file():
        return [root] if root.suffix == ".md" else []
    return sorted(path for path in root.rglob("*.md") if path.is_file())


def audit_file(path: pathlib.Path, require_urls: bool) -> list[str]:
    text = path.read_text(encoding="utf-8", errors="replace")
    errors: list[str] = []
    if "TODO" in text:
        errors.append("contains TODO")
    urls = URL_RE.findall(text)
    needs_source_url = path.name in SOURCE_BACKED_REFERENCES
    if (require_urls or needs_source_url) and not urls:
        errors.append("contains no source URLs")
    for url in urls:
        if " " in url or url.endswith("."):
            errors.append(f"suspicious URL formatting: {url}")
    if needs_source_url:
        if not any(any(term in url for term in RESEARCH_TERMS) for url in urls):
            errors.append("source-backed reference lacks expected primary-source domains")
    return errors


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("path", nargs="?", default="references", help="Reference file or directory")
    parser.add_argument("--require-urls", action="store_true", help="Require every scanned markdown file to include at least one URL")
    args = parser.parse_args(argv)
    root = pathlib.Path(args.path).resolve()
    if not root.exists():
        print(f"error: path does not exist: {root}", file=sys.stderr)
        return 2
    files = iter_markdown(root)
    errors: list[str] = []
    for path in files:
        for error in audit_file(path, args.require_urls):
            errors.append(f"{path}: {error}")
    if errors:
        for error in errors:
            print(error, file=sys.stderr)
        return 1
    print(f"Audited {len(files)} markdown reference file(s).")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
