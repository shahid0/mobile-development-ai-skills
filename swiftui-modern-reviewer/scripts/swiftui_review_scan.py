#!/usr/bin/env python3
"""AIO preflight scanner for the swiftui-modern-reviewer skill.

The scanner is intentionally heuristic. It reduces false positives by ignoring
comments/strings, tracking rough SwiftUI scopes, checking nearby context, and
emitting confidence plus caveats. It should route review attention, not replace
manual code review or Instruments profiling. It can produce false positives and
false negatives.
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from collections import Counter, defaultdict
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Iterable, Sequence


REFERENCE_BY_TOPIC = {
    "observation": "references/observation.md",
    "concurrency-lifecycle": "references/concurrency-lifecycle.md",
    "concurrency-worker-boundaries": "references/concurrency-worker-boundaries.md",
    "dependency-injection-previews": "references/dependency-injection-previews.md",
    "performance-formatting": "references/performance-formatting.md",
    "swiftdata": "references/swiftdata.md",
    "accessibility": "references/accessibility.md",
    "animation-performance": "references/animation-performance.md",
    "animation-patterns": "references/animation-patterns.md",
    "gesture-patterns": "references/gesture-patterns.md",
    "layout-performance": "references/layout-performance.md",
    "navigation-coordination": "references/navigation-coordination.md",
    "presentation-state": "references/presentation-state.md",
    "loading-empty-error": "references/loading-empty-error.md",
    "component-surface-review": "references/component-surface-review.md",
    "search-focus-input": "references/search-focus-input.md",
    "responsive-text-layout": "references/responsive-text-layout.md",
    "review-checklist": "references/review-checklist.md",
    "charts-review": "references/charts-review.md",
    "macos-multiplatform": "references/macos-multiplatform.md",
    "testing-hygiene": "references/testing-hygiene.md",
    "modern-api": "references/modern-api.md",
    "image-performance": "references/image-performance.md",
    "localization-text": "references/localization-text.md",
    "source-grounding": "references/source-grounding.md",
}


@dataclass(frozen=True)
class Finding:
    file: str
    line: int
    severity: str
    confidence: str
    code: str
    topic: str
    message: str
    snippet: str
    caveat: str
    reference: str


@dataclass(frozen=True)
class Line:
    number: int
    raw: str
    code: str
    scope: str


@dataclass(frozen=True)
class Rule:
    code: str
    severity: str
    confidence: str
    topic: str
    pattern: re.Pattern[str]
    message: str
    caveat: str
    scopes: tuple[str, ...] = ("swiftui",)
    window: int = 0
    require_any: tuple[str, ...] = ()
    reject_any: tuple[str, ...] = ()
    search_raw: bool = False


RULES: tuple[Rule, ...] = (
    Rule("OBS001", "P2", "high", "observation", re.compile(r"\bObservableObject\b"), "Legacy ObservableObject in a SwiftUI/Observation review target.", "May be valid for older deployment targets, Combine publisher contracts, or incremental migration.", ("any",)),
    Rule("OBS002", "P2", "high", "observation", re.compile(r"@Published\b"), "Legacy @Published property; @Observable tracks stored properties by default.", "May be valid while a type still intentionally conforms to ObservableObject.", ("any",)),
    Rule("OBS003", "P2", "high", "observation", re.compile(r"@(StateObject|ObservedObject|EnvironmentObject)\b"), "Legacy SwiftUI observation wrapper in modern code.", "May be valid for compatibility or unmigrated Combine-backed dependencies.", ("swiftui",)),
    Rule("OBS004", "P3", "medium", "observation", re.compile(r"@(Observable|Bindable|ObservationIgnored)\b"), "Observation signal; inspect ownership, binding projection, and ignored fields.", "Informational routing signal.", ("any",)),
    Rule("CON001", "P1", "high", "concurrency-lifecycle", re.compile(r"\bTask\.detached\s*\{"), "Task.detached in or near SwiftUI code.", "May be valid only behind a clear actor/service boundary that never mutates UI state directly.", ("swiftui",)),
    Rule("CON002", "P2", "medium", "concurrency-lifecycle", re.compile(r"\bTask\s*\{"), "Task started near onAppear/onDisappear; prefer .task for lifecycle-bound work.", "Event-handler Task can be valid; inspect lifecycle and cancellation.", ("swiftui",), 5, (".onAppear", ".onDisappear")),
    Rule("CON003", "P2", "medium", "concurrency-lifecycle", re.compile(r"\bDispatchQueue\b"), "DispatchQueue in SwiftUI/UI model context.", "May be valid at platform adapter boundaries; prefer actors/async-await in UI code.", ("swiftui",)),
    Rule("CON004", "P2", "medium", "concurrency-lifecycle", re.compile(r"\btry\?\s+await\b|\bcatch\s*\{\s*\}"), "Potentially swallowed async error.", "May be valid for best-effort non-user-visible work; inspect user impact.", ("swiftui", "observable")),
    Rule("WRK001", "P2", "medium", "concurrency-worker-boundaries", re.compile(r"\b(JSONDecoder|PropertyListDecoder)\s*\("), "Decoder allocation/use near SwiftUI or @MainActor context.", "Can be fine for tiny inputs or one-time setup; risk rises in view bodies, main-actor models, and repeated row work.", ("swiftui", "observable", "mainactor")),
    Rule("WRK002", "P1", "high", "concurrency-worker-boundaries", re.compile(r"@MainActor\b.*\b(class|actor)\s+\w*(Service|Repository|Decoder|Processor|Cache)\b|\b(class|actor)\s+\w*(Service|Repository|Decoder|Processor|Cache)\b.*@MainActor\b|\b(class|actor)\s+\w*(Service|Repository|Decoder|Processor|Cache)\b"), "@MainActor worker-like type.", "UI-facing coordinators can be main-actor isolated; CPU, decoding, cache, repository, and IO work usually need a non-UI boundary.", ("any",), 3, ("@MainActor",)),
    Rule("WRK003", "P1", "high", "concurrency-worker-boundaries", re.compile(r"\bTask\.detached\s*\{"), "Task.detached may capture self.", "Only a capture risk if the detached closure actually references self or implicitly uses instance members; inspect Sendable and actor isolation.", ("swiftui", "observable", "mainactor"), 8, ("self",)),
    Rule("DEP001", "P1", "medium", "dependency-injection-previews", re.compile(r"\b[A-Za-z_][A-Za-z0-9_]*\.shared\b"), "Singleton/global access in SwiftUI context.", "May be a harmless static namespace or singleton intentionally injected elsewhere; inspect dependency boundary.", ("swiftui",)),
    Rule("DEP002", "P1", "high", "dependency-injection-previews", re.compile(r"\bUIApplication\.shared\b|\bUserDefaults\.standard\b|\bNotificationCenter\.default\b"), "Direct app/system global state access from SwiftUI context.", "May belong in a platform adapter, app scene, or coordinator rather than the view.", ("swiftui",)),
    Rule("DEP003", "P3", "medium", "dependency-injection-previews", re.compile(r"#Preview\b|PreviewProvider\b"), "Preview exists; verify it uses fake dependencies and covers key states.", "Informational routing signal.", ("any",)),
    Rule("PERF001", "P1", "high", "performance-formatting", re.compile(r"\.id\s*\(\s*(UUID|Date)\s*\("), "Unstable view identity.", "Usually a real problem in frequently rendered views; valid only for deliberate state reset.", ("swiftui",)),
    Rule("PERF002", "P2", "high", "performance-formatting", re.compile(r"\b(DateFormatter|NumberFormatter|MeasurementFormatter|RelativeDateTimeFormatter)\s*\("), "Formatter allocation in SwiftUI context.", "May be fine in static properties or initializers; inspect whether it runs per render/row.", ("swiftui",)),
    Rule("PERF003", "P3", "medium", "performance-formatting", re.compile(r"\b(List|ForEach|ScrollView|LazyVStack|LazyHStack|LazyVGrid|LazyHGrid)\b"), "Collection/rendering signal.", "Informational. Inspect identity, row body cost, eager work, and animation scope.", ("swiftui",)),
    Rule("PERF004", "P2", "medium", "performance-formatting", re.compile(r"\.(sorted|filter|map)\s*[\(\{]"), "Collection transform in a SwiftUI hot path.", "False positive if this is cached, precomputed, or outside body/list row evaluation; inspect body, ForEach, and List context.", ("swiftui",), 8, ("body", "ForEach", "List")),
    Rule("DAT001", "P3", "medium", "swiftdata", re.compile(r"@Model\b|@Query\b|@ModelActor\b|\bModelContext\b|\bSwiftData\b"), "SwiftData signal.", "Informational routing signal. Inspect model isolation, query ownership, undo/save timing, and main-actor assumptions.", ("any",)),
    Rule("A11Y001", "P3", "medium", "accessibility", re.compile(r"\.accessibility(Label|Action|Representation)\s*\("), "Accessibility semantic modifier signal.", "Informational. Verify labels/actions are meaningful, localized, and do not mask native control semantics.", ("swiftui",)),
    Rule("ANIM001", "P1", "high", "animation-performance", re.compile(r"\.animation\s*\("), "Possibly broad implicit animation.", "False positive if value: is hidden beyond the scanned call window or produced by unusual formatting.", ("swiftui",), 4, (), ("value:", ".animation(nil")),
    Rule("ANIM002", "P2", "medium", "animation-performance", re.compile(r"\bwithAnimation\s*\{|\bwithAnimation\s*\("), "Explicit animation transaction.", "Often valid. Inspect mutation scope, bulk data changes, and main-actor context.", ("swiftui", "observable")),
    Rule("ANIM003", "P2", "medium", "animation-performance", re.compile(r"\bmatchedGeometryEffect\s*\("), "matchedGeometryEffect usage.", "Inspect stable IDs, single active source, modifier order, clipping, and navigation boundaries.", ("swiftui",)),
    Rule("ANIM004", "P2", "medium", "animation-performance", re.compile(r"\b(PhaseAnimator|KeyframeAnimator|TimelineView|Canvas)\b"), "Modern or continuous animation/drawing API.", "Often valid. Inspect state mutation per tick, body churn, and reduce-motion behavior.", ("swiftui",)),
    Rule("ANIM005", "P2", "high", "animation-performance", re.compile(r"\b(Timer\.scheduledTimer|CADisplayLink)\b"), "Timer/display-link driven updates.", "Review carefully if it mutates SwiftUI state or drives animation at frame rate.", ("swiftui", "observable")),
    Rule("ANIM006", "P2", "medium", "animation-performance", re.compile(r"\.(blur|shadow|mask|drawingGroup|compositingGroup)\s*\("), "Potentially expensive visual effect or compositing.", "Static use can be fine. Risk rises when animated, repeated in lists, or applied to large surfaces.", ("swiftui",)),
    Rule("ANIM007", "P3", "medium", "animation-performance", re.compile(r"\.(transition|contentTransition|symbolEffect)\s*\("), "Transition/effect signal.", "Inspect identity stability, reduce-motion handling, and layout isolation.", ("swiftui",)),
    Rule("ANIM008", "P2", "medium", "animation-performance", re.compile(r"\.(onChanged|onEnded|updating)\s*\{"), "Gesture hot path.", "Inspect closure body for main-thread work, large model writes, and per-frame animation.", ("swiftui",)),
    Rule("ANIM009", "P3", "medium", "animation-performance", re.compile(r"accessibilityReduceMotion"), "Reduce-motion signal.", "Informational. Verify nonessential motion is actually gated.", ("swiftui",)),
    Rule("ANIM010", "P3", "low", "animation-performance", re.compile(r"\.(frame|padding|font|lineLimit|layoutPriority)\s*\("), "Layout-affecting modifier.", "Very common and not a bug alone. Inspect only if animated, gesture-driven, or repeated in hot rows.", ("swiftui",)),
    Rule("ANIM011", "P2", "medium", "animation-performance", re.compile(r"\.(material|background|overlay)\s*\("), "Layering/material/overlay signal.", "Common and often fine. Risk rises with nested transparent layers, blur/material, and animation.", ("swiftui",)),
    Rule("GEST001", "P2", "medium", "gesture-patterns", re.compile(r"\.onTapGesture\s*(\(|\{)"), "Tap gesture used as an action.", "May be fine for decorative/simple views; prefer Button or an accessibility action for semantic, keyboard, and assistive behavior.", ("swiftui",)),
    Rule("LAY001", "P3", "medium", "layout-performance", re.compile(r"\b(GeometryReader|PreferenceKey|ViewThatFits|AnyLayout)\b|\.onGeometryChange\s*\("), "Layout measurement/adaptation signal.", "Informational. Inspect invalidation scope, measurement feedback loops, and whether simpler layout APIs would work.", ("swiftui",)),
    Rule("LAY002", "P3", "medium", "layout-performance", re.compile(r"\b(struct|class)\s+\w+\s*:\s*Layout\b|\bfunc\s+sizeThatFits\s*\(|\bfunc\s+placeSubviews\s*\("), "Custom Layout protocol signal.", "Informational. Inspect cache use, proposal handling, and repeated subview measurement.", ("any",)),
    Rule("NAV001", "P2", "high", "navigation-coordination", re.compile(r"\bNavigationView\b"), "NavigationView in modern SwiftUI code.", "May be retained for old deployment targets.", ("swiftui",)),
    Rule("NAV002", "P3", "medium", "navigation-coordination", re.compile(r"\bNavigationLink\s*\(\s*destination\s*:"), "Destination-based NavigationLink.", "May be fine for simple flows; value-driven routing scales better.", ("swiftui",)),
    Rule("NAV003", "P3", "medium", "navigation-coordination", re.compile(r"\bNavigationStack\b|\bNavigationPath\b|\.navigationDestination\b|\.sheet\s*\("), "Navigation/modal signal.", "Informational. Inspect route ownership and presentation state.", ("swiftui",)),
    Rule("PRS001", "P2", "medium", "presentation-state", re.compile(r"\.sheet\s*\(\s*isPresented\s*:"), "Boolean-driven sheet presentation.", "Can be fine for one simple modal. Risk rises when multiple booleans encode mutually exclusive routes or associated data.", ("swiftui",)),
    Rule("PRS002", "P3", "low", "presentation-state", re.compile(r"@State\s+(?:private\s+)?var\s+(?:is|show|shows|showing|present|presents|presenting)\w*(?:Sheet|Alert|Dialog|Popover|Modal|Editor|Picker)\w*\s*=\s*false"), "Boolean presentation state signal.", "Heuristic only. Multiple nearby presentation booleans may indicate route state that should be modeled as an enum or item.", ("swiftui",)),
    Rule("PRS003", "P3", "medium", "presentation-state", re.compile(r"\.sheet\s*\(\s*item\s*:"), "Item-driven sheet presentation.", "Usually a better direction than booleans; inspect item identity, dismissal mutation, and associated data ownership.", ("swiftui",)),
    Rule("PRS004", "P3", "medium", "presentation-state", re.compile(r"\.presentationDetents\s*\("), "Presentation detents signal.", "Informational. Inspect content sizing, default detent, scroll interaction, and compact-size behavior.", ("swiftui",)),
    Rule("PRS005", "P2", "medium", "presentation-state", re.compile(r"\.interactiveDismissDisabled\s*\("), "Interactive dismissal is disabled.", "Often valid for unsaved changes or required flows; verify escape paths, confirmation, and accessibility.", ("swiftui",)),
    Rule("PRS006", "P3", "medium", "presentation-state", re.compile(r"\.(alert|confirmationDialog|popover)\s*\("), "Alert/dialog/popover presentation signal.", "Informational. Inspect source of truth, stale captures, button roles, platform adaptation, and localization.", ("swiftui",)),
    Rule("LDE001", "P3", "medium", "loading-empty-error", re.compile(r"\bProgressView\b|\.redacted\s*\(|\bContentUnavailableView\b"), "Loading, skeleton, or empty-state signal.", "Informational. Verify cancellation, retry, error messaging, accessibility labels, and whether loading/empty/error states are mutually exclusive.", ("swiftui",)),
    Rule("CMP001", "P3", "medium", "component-surface-review", re.compile(r"\b(public|open)\s+struct\s+\w+(?:\s*<[^>]+>)?\s*:\s*View\b|\b@Binding\b|\binit\s*\([^)]*(?:Binding<|@ViewBuilder)"), "Reusable component surface signal.", "Informational. Inspect initializer shape, binding ownership, environment assumptions, generic constraints, and preview coverage.", ("swiftui",)),
    Rule("INP001", "P3", "medium", "search-focus-input", re.compile(r"\.searchable\s*\(|\bsearchScopes\s*\("), "Search UI signal.", "Informational. Inspect debounce/cancellation, scope resets, empty queries, keyboard behavior, and result identity.", ("swiftui",)),
    Rule("INP002", "P3", "medium", "search-focus-input", re.compile(r"@FocusState\b|\.focused\s*\(|\.onSubmit\s*\("), "Focus or submit flow signal.", "Informational. Verify focus ownership, default focus timing, validation, keyboard submit labels, and accessibility.", ("swiftui",)),
    Rule("TXT001", "P3", "low", "responsive-text-layout", re.compile(r"\.(lineLimit|minimumScaleFactor|allowsTightening|fixedSize|truncationMode|dynamicTypeSize)\s*\("), "Responsive text/layout signal.", "Common and often fine. Inspect long localized text, Dynamic Type, truncation, and stable layout constraints.", ("swiftui",)),
    Rule("CHT001", "P3", "medium", "charts-review", re.compile(r"\bChart\s*\(|\b(BarMark|LineMark|SectorMark)\s*\(|\bChartProxy\b|\.chartXSelection\s*\("), "Swift Charts signal.", "Informational. Inspect mark identity, axis readability, selection state, ChartProxy coordinate assumptions, accessibility, and data volume.", ("swiftui", "any")),
    Rule("MAC001", "P3", "medium", "macos-multiplatform", re.compile(r"\b(MenuBarExtra|Settings|WindowGroup|Window|UtilityWindow|Table|HSplitView|VSplitView|NSViewRepresentable)\b|\.fileImporter\s*\(|\.fileExporter\s*\("), "macOS or multiplatform API signal.", "Informational. Inspect scene ownership, command/menu behavior, selection models, AppKit bridge lifecycle, sandboxing, and platform availability.", ("swiftui", "any")),
    Rule("API001", "P3", "medium", "modern-api", re.compile(r"\.foregroundColor\s*\("), "foregroundColor usage in modern SwiftUI code.", "Often still works; review whether foregroundStyle is the better semantic/style API for the target OS.", ("swiftui",)),
    Rule("API002", "P3", "medium", "modern-api", re.compile(r"\.accentColor\s*\("), "accentColor usage in modern SwiftUI code.", "May be needed for older targets; tint is generally the modern control tinting API.", ("swiftui",)),
    Rule("API003", "P2", "high", "modern-api", re.compile(r"\bNavigationView\b"), "NavigationView modern API signal.", "May be retained for old deployment targets; otherwise prefer NavigationStack/SplitView routing.", ("swiftui",)),
    Rule("IMG001", "P2", "medium", "image-performance", re.compile(r"\bUIImage\s*\(\s*data\s*:"), "UIImage(data:) decoding signal.", "May be fine off the main actor for small images; inspect downsampling, caching, and whether decode happens during render.", ("swiftui", "observable", "mainactor")),
    Rule("IMG002", "P2", "medium", "image-performance", re.compile(r"\bCGImageSource\w*\b"), "CGImageSource image decoding/downsampling signal.", "Often the right tool. Inspect where it runs, thumbnail options, memory pressure, and caching.", ("swiftui", "observable", "mainactor", "any")),
    Rule("LOC001", "P3", "medium", "localization-text", re.compile(r"\bText\s*\(\s*\"[^\"]+\"\s*\)"), "Hard-coded Text string.", "SwiftUI may localize string literals automatically; inspect interpolation, comments-only matches, product names, debug text, and localization policy.", ("swiftui",), 0, (), (), True),
    Rule("LOC002", "P3", "medium", "localization-text", re.compile(r"\bText\s*\(\s*[A-Za-z_][A-Za-z0-9_\.]*\s*\)"), "Text initialized from a variable.", "May intentionally be verbatim dynamic text; inspect whether the value is user content, already localized, or should use LocalizedStringResource.", ("swiftui",), 0, (), (), True),
    Rule("LOC003", "P3", "medium", "localization-text", re.compile(r"\bLocalizedStringResource\b|\bString\s*\(\s*localized\s*:"), "Explicit localization API signal.", "Informational. Verify keys, interpolation, tables/bundles, and extraction behavior.", ("any",)),
    Rule("TST001", "P3", "medium", "testing-hygiene", re.compile(r"\bSelf\._(?:printChanges|logChanges)\s*\("), "SwiftUI change logging signal.", "Debug-only instrumentation. Ensure it does not ship unintentionally and use it to guide state invalidation review.", ("swiftui", "any")),
    Rule("TST002", "P3", "low", "testing-hygiene", re.compile(r"\bprint\s*\("), "Debug print in body-ish SwiftUI context.", "High false-positive risk. Only actionable when it runs during rendering, repeated callbacks, previews, or tests without a logging policy.", ("swiftui",), 12, ("body", "var body", "some View", "ForEach", "List", "#Preview")),
)


def strip_comments_and_strings(text: str) -> str:
    result: list[str] = []
    i = 0
    in_block = 0
    in_string = False
    in_line_comment = False
    while i < len(text):
        ch = text[i]
        nxt = text[i + 1] if i + 1 < len(text) else ""

        if in_line_comment:
            if ch == "\n":
                in_line_comment = False
                result.append(ch)
            else:
                result.append(" ")
            i += 1
            continue

        if in_block:
            if ch == "/" and nxt == "*":
                in_block += 1
                result.extend("  ")
                i += 2
            elif ch == "*" and nxt == "/":
                in_block -= 1
                result.extend("  ")
                i += 2
            else:
                result.append("\n" if ch == "\n" else " ")
                i += 1
            continue

        if in_string:
            if ch == "\\":
                result.extend("  ")
                i += 2
            elif ch == "\"":
                in_string = False
                result.append(" ")
                i += 1
            else:
                result.append("\n" if ch == "\n" else " ")
                i += 1
            continue

        if ch == "/" and nxt == "/":
            in_line_comment = True
            result.extend("  ")
            i += 2
        elif ch == "/" and nxt == "*":
            in_block = 1
            result.extend("  ")
            i += 2
        elif ch == "\"":
            in_string = True
            result.append(" ")
            i += 1
        else:
            result.append(ch)
            i += 1
    return "".join(result)


def iter_swift_files(paths: Iterable[Path]) -> Iterable[Path]:
    ignored_parts = {
        ".build",
        ".git",
        ".swiftpm",
        "Carthage",
        "DerivedData",
        "Pods",
        "SourcePackages",
        "build",
    }
    for path in paths:
        if path.is_file() and path.suffix == ".swift":
            yield path
        elif path.is_dir():
            for child in path.rglob("*.swift"):
                if ignored_parts.isdisjoint(child.parts):
                    yield child


def classify_scope(code_lines: Sequence[str], index: int, imports_swiftui: bool) -> str:
    start = max(0, index - 100)
    window = "\n".join(code_lines[start : index + 1])
    if re.search(r"(@Observable\b|:\s*ObservableObject\b)", window):
        return "observable"
    swiftui_signals = list(
        re.finditer(
            r"\b(struct|class)\s+\w+[^{}:]*:\s*View\b|\bvar\s+body\s*:\s*some\s+View\b|#Preview\b|PreviewProvider\b",
            window,
        )
    )
    mainactor_signals = list(re.finditer(r"@MainActor\b", window))
    latest_swiftui = swiftui_signals[-1].start() if swiftui_signals else -1
    latest_mainactor = mainactor_signals[-1].start() if mainactor_signals else -1
    if latest_mainactor > latest_swiftui:
        return "mainactor"
    if imports_swiftui and latest_swiftui >= 0:
        return "swiftui"
    if imports_swiftui:
        return "swiftui"
    return "any"


def build_lines(path: Path) -> list[Line]:
    raw_text = path.read_text(encoding="utf-8", errors="replace")
    code_text = strip_comments_and_strings(raw_text)
    raw_lines = raw_text.splitlines()
    code_lines = code_text.splitlines()
    imports_swiftui = any(re.search(r"^\s*import\s+SwiftUI\b", line) for line in code_lines)
    line_count = max(len(raw_lines), len(code_lines))
    lines: list[Line] = []
    for index in range(line_count):
        raw = raw_lines[index] if index < len(raw_lines) else ""
        code = code_lines[index] if index < len(code_lines) else ""
        lines.append(Line(index + 1, raw, code, classify_scope(code_lines, index, imports_swiftui)))
    return lines


def scope_matches(rule: Rule, scope: str) -> bool:
    return "any" in rule.scopes or scope in rule.scopes


def context(lines: Sequence[Line], index: int, window: int) -> str:
    if window <= 0:
        return lines[index].code
    start = max(0, index - window)
    end = min(len(lines), index + window + 1)
    return "\n".join(line.code for line in lines[start:end])


def forward_call_context(lines: Sequence[Line], index: int, max_lines: int = 8) -> str:
    selected: list[str] = []
    balance = 0
    started = False
    for line in lines[index : min(len(lines), index + max_lines)]:
        selected.append(line.code)
        for ch in line.code:
            if ch == "(":
                balance += 1
                started = True
            elif ch == ")":
                balance -= 1
        if started and balance <= 0:
            break
    return "\n".join(selected)


def scan_file(path: Path) -> list[Finding]:
    lines = build_lines(path)
    findings: list[Finding] = []
    seen: set[tuple[str, int, str]] = set()

    for index, line in enumerate(lines):
        if not line.code.strip():
            continue

        for rule in RULES:
            if not scope_matches(rule, line.scope):
                continue
            searchable_line = line.raw if rule.search_raw else line.code
            if not rule.pattern.search(searchable_line):
                continue

            ctx = context(lines, index, rule.window)
            if rule.require_any and not any(token in ctx for token in rule.require_any):
                continue
            reject_context = forward_call_context(lines, index) if rule.code == "ANIM001" else ctx
            if rule.reject_any and any(token in reject_context for token in rule.reject_any):
                continue

            key = (rule.code, line.number, line.raw.strip())
            if key in seen:
                continue
            seen.add(key)
            findings.append(
                Finding(
                    file=str(path),
                    line=line.number,
                    severity=rule.severity,
                    confidence=rule.confidence,
                    code=rule.code,
                    topic=rule.topic,
                    message=rule.message,
                    snippet=line.raw.strip(),
                    caveat=rule.caveat,
                    reference=REFERENCE_BY_TOPIC[rule.topic],
                )
            )

    return findings


def severity_allowed(severity: str, minimum: str) -> bool:
    rank = {"P0": 0, "P1": 1, "P2": 2, "P3": 3}
    return rank[severity] <= rank[minimum]


def summarize(findings: Sequence[Finding]) -> dict[str, object]:
    by_topic = Counter(f.topic for f in findings)
    by_severity = Counter(f.severity for f in findings)
    references = sorted({f.reference for f in findings})
    return {
        "total": len(findings),
        "by_severity": dict(sorted(by_severity.items())),
        "by_topic": dict(sorted(by_topic.items())),
        "suggested_references": references,
    }


def print_markdown(findings: Sequence[Finding]) -> None:
    summary = summarize(findings)
    print("# SwiftUI Modern Reviewer Preflight")
    print()
    print(f"Total hotspots: {summary['total']}")
    if summary["suggested_references"]:
        print()
        print("Suggested references:")
        for ref in summary["suggested_references"]:
            print(f"- {ref}")
    print()

    if not findings:
        print("No hotspots found for the selected filters.")
        return

    grouped: dict[str, list[Finding]] = defaultdict(list)
    for finding in findings:
        grouped[finding.topic].append(finding)

    for topic in sorted(grouped):
        print(f"## {topic}")
        for finding in grouped[topic]:
            print(f"- `{finding.file}:{finding.line}` {finding.severity} {finding.code} ({finding.confidence})")
            print(f"  - {finding.message}")
            print(f"  - Snippet: `{finding.snippet}`")
            print(f"  - Caveat: {finding.caveat}")
        print()


def print_text(findings: Sequence[Finding]) -> None:
    if not findings:
        print("No SwiftUI reviewer hotspots found for the selected filters.")
        return
    for finding in findings:
        print(f"{finding.file}:{finding.line}: {finding.severity} {finding.code} [{finding.topic}] confidence={finding.confidence}")
        print(f"  {finding.message}")
        print(f"  {finding.snippet}")
        print(f"  caveat: {finding.caveat}")
        print(f"  reference: {finding.reference}")


def main() -> int:
    parser = argparse.ArgumentParser(
        description="AIO heuristic preflight scanner for SwiftUI modern-reviewer hotspots. Output can include false positives and false negatives."
    )
    parser.add_argument("paths", nargs="+", type=Path, help="Swift file or directory paths to scan.")
    parser.add_argument("--topic", choices=sorted(REFERENCE_BY_TOPIC), help="Only show one topic.")
    parser.add_argument("--min-severity", choices=("P0", "P1", "P2", "P3"), default="P3", help="Lowest severity to show.")
    parser.add_argument("--format", choices=("text", "markdown", "json"), default="text", help="Output format.")
    parser.add_argument("--summary", action="store_true", help="Only print summary data.")
    args = parser.parse_args()

    swift_files = sorted(set(iter_swift_files(args.paths)))
    findings: list[Finding] = []
    for swift_file in swift_files:
        findings.extend(scan_file(swift_file))

    filtered = [
        finding
        for finding in findings
        if severity_allowed(finding.severity, args.min_severity)
        and (args.topic is None or finding.topic == args.topic)
    ]

    if args.summary:
        print(json.dumps(summarize(filtered), indent=2, sort_keys=True))
    elif args.format == "json":
        print(json.dumps({"summary": summarize(filtered), "findings": [asdict(f) for f in filtered]}, indent=2, sort_keys=True))
    elif args.format == "markdown":
        print_markdown(filtered)
    else:
        print_text(filtered)

    return 0


if __name__ == "__main__":
    sys.exit(main())
