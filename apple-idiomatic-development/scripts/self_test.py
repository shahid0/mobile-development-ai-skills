#!/usr/bin/env python3
"""Self-tests for the apple-idiomatic-development helper scripts."""

from __future__ import annotations

import pathlib
import subprocess
import sys
import tempfile


ROOT = pathlib.Path(__file__).resolve().parents[1]


def run(command: list[str], cwd: pathlib.Path = ROOT) -> subprocess.CompletedProcess[str]:
    return subprocess.run(command, cwd=cwd, text=True, capture_output=True, check=False)


def assert_success(result: subprocess.CompletedProcess[str]) -> None:
    if result.returncode != 0:
        raise AssertionError(
            f"command failed: {' '.join(result.args)}\nstdout:\n{result.stdout}\nstderr:\n{result.stderr}"
        )


def assert_failure(result: subprocess.CompletedProcess[str]) -> None:
    if result.returncode == 0:
        raise AssertionError(f"command unexpectedly succeeded: {' '.join(result.args)}")


def test_feedback_rules() -> None:
    with tempfile.TemporaryDirectory() as directory:
        rule_dir = pathlib.Path(directory)
        add = run(
            [
                sys.executable,
                "scripts/feedback_rules.py",
                "add",
                "--feedback",
                "For prices dont use String(format:) use Text(value, format: .currency(code: code))",
                "--example",
                "Use localized prices with Text(price, format: .currency(code: code))",
                "--dir",
                str(rule_dir),
                "--date",
                "2026-05-29",
            ]
        )
        assert_success(add)
        validate = run([sys.executable, "scripts/feedback_rules.py", "validate", str(rule_dir)])
        assert_success(validate)
        text = (rule_dir / "user-rules-swiftui-text.md").read_text(encoding="utf-8")
        assert "Text(value, format: .currency(code: code))." in text
        assert "**Updated:** 2026-05-29" in text
        assert "**Examples:** Use localized prices with Text(price, format: .currency(code: code))." in text
        if "User wording" in text:
            raise AssertionError("stored feedback rules should keep affirmative guidance only")
        if "String(format:)" in text.split("**Guidance:**", maxsplit=1)[1]:
            raise AssertionError("negative source pattern leaked into affirmative guidance")

        comparative = run(
            [
                sys.executable,
                "scripts/feedback_rules.py",
                "add",
                "--feedback",
                "Prefer Text(value, format:) over String(format:)",
                "--dir",
                str(rule_dir),
                "--date",
                "2026-05-29",
            ]
        )
        assert_success(comparative)
        comparative_text = (rule_dir / "user-rules-swiftui-text.md").read_text(encoding="utf-8")
        if "Prefer Text(value, format:)" in comparative_text:
            raise AssertionError("comparative feedback should store direct affirmative guidance, not Prefer X to Y wording")
        if "String(format:)" in comparative_text.rsplit("**Guidance:**", maxsplit=1)[1]:
            raise AssertionError("comparative negative source pattern leaked into affirmative guidance")

        not_comparison = run(
            [
                sys.executable,
                "scripts/feedback_rules.py",
                "add",
                "--feedback",
                "Use .background(content:) not ZStack for attached backgrounds",
                "--dir",
                str(rule_dir),
                "--date",
                "2026-05-29",
            ]
        )
        assert_success(not_comparison)
        layout_text = (rule_dir / "user-rules-swiftui-layout.md").read_text(encoding="utf-8")
        if "ZStack" in layout_text.rsplit("**Guidance:**", maxsplit=1)[1]:
            raise AssertionError("not-comparison negative source pattern leaked into affirmative guidance")

        prefer_to = run(
            [
                sys.executable,
                "scripts/feedback_rules.py",
                "add",
                "--feedback",
                "Prefer Text(value, format:) to String(format:)",
                "--dir",
                str(rule_dir),
                "--date",
                "2026-05-29",
            ]
        )
        assert_success(prefer_to)
        prefer_to_text = (rule_dir / "user-rules-swiftui-text.md").read_text(encoding="utf-8")
        if "Prefer Text(value, format:)" in prefer_to_text:
            raise AssertionError("prefer-to feedback should be rewritten as direct Use guidance")

        rejected = run(
            [
                sys.executable,
                "scripts/feedback_rules.py",
                "add",
                "--group",
                "bad-rule",
                "--feedback",
                "No clear preferred action",
                "--dir",
                str(rule_dir),
            ]
        )
        assert_failure(rejected)

        inverted = run(
            [
                sys.executable,
                "scripts/feedback_rules.py",
                "add",
                "--feedback",
                "Do not use GeometryReader for ordinary background layout",
                "--dir",
                str(rule_dir),
            ]
        )
        assert_failure(inverted)

        empty_dir = pathlib.Path(directory) / "empty"
        empty_dir.mkdir()
        empty = run([sys.executable, "scripts/feedback_rules.py", "validate", str(empty_dir)])
        assert_failure(empty)


def test_swift_scanner() -> None:
    with tempfile.TemporaryDirectory() as directory:
        root = pathlib.Path(directory)
        source = root / "LegacyView.swift"
        source.write_text(
            """
import SwiftUI

final class Store: ObservableObject {
    @Published var title = "Hi"
}

struct LegacyView: View {
    @Environment(\\.accessibilityReduceMotion) private var reduceMotion

    var body: some View {
        NavigationView {
            Text(String(format: "%d", 42))
                .foregroundColor(.red)
                .animation(reduceMotion ? nil : .easeInOut)
        }
    }
}
""",
            encoding="utf-8",
        )
        result = run([sys.executable, "scripts/swift_apple_scan.py", str(root)])
        assert_failure(result)
        for expected in [
            "legacy-observation",
            "navigation-view",
            "foreground-color",
            "broad-animation",
            "string-formatting",
            "reduce-motion-ternary",
        ]:
            if expected not in result.stdout:
                raise AssertionError(f"expected scanner finding {expected!r}\n{result.stdout}")
        strict_result = run([sys.executable, "scripts/swift_apple_scan.py", "--strict", str(root)])
        assert_failure(strict_result)
        if "text-string-format" not in strict_result.stdout:
            raise AssertionError(f"expected strict text-string-format finding\n{strict_result.stdout}")
        if "legacy-observation" in strict_result.stdout:
            raise AssertionError(f"strict mode should not include advisory findings\n{strict_result.stdout}")

        comments = root / "CommentsOnly.swift"
        comments.write_text(
            """
// Text(String(format: "%d", 42))
// .id(UUID())
// @Observable final class Store: ObservableObject {}
""",
            encoding="utf-8",
        )
        comments_result = run([sys.executable, "scripts/swift_apple_scan.py", "--strict", str(comments)])
        assert_success(comments_result)
        if "finding(s)" not in comments_result.stdout or "0 finding(s)" not in comments_result.stdout:
            raise AssertionError(f"comments should not trigger strict findings\n{comments_result.stdout}")

        string_literals = root / "StringLiterals.swift"
        string_literals.write_text(
            """
import SwiftUI
let sample = "Text(String(format: \\"%d\\", 42)) .id(UUID())"
let multiline = \"\"\"
Text(String(format: "%d", 42))
.id(UUID())
\"\"\"
struct LiteralView: View { var body: some View { Text("ok") } }
""",
            encoding="utf-8",
        )
        literal_result = run([sys.executable, "scripts/swift_apple_scan.py", "--strict", str(string_literals)])
        assert_success(literal_result)
        if "text-string-format" in literal_result.stdout or "uuid-refresh" in literal_result.stdout:
            raise AssertionError(f"string literals should not trigger strict findings\n{literal_result.stdout}")

        spaced_label = root / "SpacedFormat.swift"
        spaced_label.write_text(
            """
import SwiftUI
struct SpacedFormatView: View {
    var body: some View {
        Text(String(format : "%d", 42))
    }
}
""",
            encoding="utf-8",
        )
        spaced_result = run([sys.executable, "scripts/swift_apple_scan.py", "--strict", str(spaced_label)])
        assert_failure(spaced_result)
        if "text-string-format" not in spaced_result.stdout:
            raise AssertionError(f"format label with whitespace should be detected\n{spaced_result.stdout}")

        bindable = root / "BindableView.swift"
        bindable.write_text(
            """
import SwiftUI
@Observable final class Model { var title = "" }
struct Editor: View {
    @Bindable var model: Model
    var body: some View {
        TextField("Title", text: $model.title)
    }
}
""",
            encoding="utf-8",
        )
        bindable_result = run([sys.executable, "scripts/swift_apple_scan.py", str(bindable)])
        assert_success(bindable_result)
        if "bindable-without-binding-use" in bindable_result.stdout:
            raise AssertionError(f"valid @Bindable use should not be flagged\n{bindable_result.stdout}")

        main_actor_service = root / "ImageService.swift"
        main_actor_service.write_text("@MainActor public final class ImageService {}\n", encoding="utf-8")
        service_result = run([sys.executable, "scripts/swift_apple_scan.py", str(main_actor_service)])
        assert_failure(service_result)
        if "mainactor-service" not in service_result.stdout:
            raise AssertionError(f"public MainActor service should be flagged\n{service_result.stdout}")

        stacked_service = root / "StackedImageService.swift"
        stacked_service.write_text("@MainActor @Observable public final class StackedImageService {}\n", encoding="utf-8")
        stacked_result = run([sys.executable, "scripts/swift_apple_scan.py", str(stacked_service)])
        assert_failure(stacked_result)
        if "mainactor-service" not in stacked_result.stdout:
            raise AssertionError(f"MainActor service with stacked attributes should be flagged\n{stacked_result.stdout}")

        detached_comment = root / "Detached.swift"
        detached_comment.write_text(
            """
func run() {
    Task.detached {
        // Task.checkCancellation()
        crunch()
    }
}
func crunch() {}
""",
            encoding="utf-8",
        )
        detached_result = run([sys.executable, "scripts/swift_apple_scan.py", str(detached_comment)])
        assert_failure(detached_result)
        if "task-detached-no-cancellation" not in detached_result.stdout:
            raise AssertionError(f"commented cancellation should not suppress detached finding\n{detached_result.stdout}")

        detached_unrelated = root / "DetachedUnrelated.swift"
        detached_unrelated.write_text(
            """
func run() {
    Task.detached {
        crunch()
    }
    try? Task.checkCancellation()
}
func crunch() {}
""",
            encoding="utf-8",
        )
        unrelated_result = run([sys.executable, "scripts/swift_apple_scan.py", str(detached_unrelated)])
        assert_failure(unrelated_result)
        if "task-detached-no-cancellation" not in unrelated_result.stdout:
            raise AssertionError(f"unrelated cancellation outside detached closure should not suppress finding\n{unrelated_result.stdout}")


def test_concurrency_settings_scanner() -> None:
    with tempfile.TemporaryDirectory() as directory:
        root = pathlib.Path(directory)
        package = root / "Package.swift"
        package.write_text(
            """
// swift-tools-version: 6.2
import PackageDescription

let package = Package(
    name: "Demo",
    targets: [
        .target(
            name: "Demo",
            swiftSettings: [
                .defaultIsolation(MainActor.self),
                .enableUpcomingFeature("NonisolatedNonsendingByDefault"),
                .enableUpcomingFeature("InferIsolatedConformances")
            ]
        )
    ]
)
""",
            encoding="utf-8",
        )
        result = run([sys.executable, "scripts/concurrency_settings_scan.py", str(root)])
        assert_success(result)
        for expected in [
            "swift-tools-version = 6.2",
            "defaultIsolation = MainActor.self",
            "enableUpcomingFeature = NonisolatedNonsendingByDefault",
            "summary: default actor isolation declares MainActor",
        ]:
            if expected not in result.stdout:
                raise AssertionError(f"expected settings output {expected!r}\n{result.stdout}")

        package.write_text(
            """
// swift-tools-version: 6.2
import PackageDescription
let package = Package(
    name: "Demo",
    targets: [
        .target(name: "Core", swiftSettings: [.defaultIsolation(nil)])
    ]
)
""",
            encoding="utf-8",
        )
        nil_result = run([sys.executable, "scripts/concurrency_settings_scan.py", str(root)])
        assert_success(nil_result)
        if "summary: default actor isolation declares nonisolated via nil" not in nil_result.stdout:
            raise AssertionError(f"expected nil default isolation summary\n{nil_result.stdout}")

        package.write_text(
            """
// swift-tools-version: 6.2
import PackageDescription
let package = Package(
    name: "Demo",
    targets: [
        .target(name: "UI", swiftSettings: [.defaultIsolation(MainActor.self)]),
        .target(name: "Core", swiftSettings: [.defaultIsolation(nil)])
    ]
)
""",
            encoding="utf-8",
        )
        mixed_result = run([sys.executable, "scripts/concurrency_settings_scan.py", str(root)])
        assert_success(mixed_result)
        if "mixed default actor isolation declarations found" not in mixed_result.stdout:
            raise AssertionError(f"expected mixed default isolation summary\n{mixed_result.stdout}")

        package.write_text(
            """
// swift-tools-version: 6.2
import PackageDescription
let package = Package(
    name: "Demo",
    targets: [
        .target(name: "Demo", swiftSettings: [
            // .defaultIsolation(MainActor.self),
            // .enableUpcomingFeature("NonisolatedNonsendingByDefault")
        ])
    ]
)
""",
            encoding="utf-8",
        )
        commented_result = run([sys.executable, "scripts/concurrency_settings_scan.py", str(root)])
        assert_success(commented_result)
        if "defaultIsolation =" in commented_result.stdout or "enableUpcomingFeature =" in commented_result.stdout:
            raise AssertionError(f"commented settings should not be reported\n{commented_result.stdout}")

        xcconfig = root / "App.xcconfig"
        xcconfig.write_text(
            """
SWIFT_VERSION = 6.0;
SWIFT_DEFAULT_ACTOR_ISOLATION[sdk=iphoneos*] = MainActor;
SWIFT_UPCOMING_FEATURE_NONISOLATED_NONSENDING_BY_DEFAULT[config=Debug] = YES;
""",
            encoding="utf-8",
        )
        scoped_result = run([sys.executable, "scripts/concurrency_settings_scan.py", str(xcconfig)])
        assert_success(scoped_result)
        for expected in [
            "SWIFT_DEFAULT_ACTOR_ISOLATION = MainActor",
            "SWIFT_UPCOMING_FEATURE_NONISOLATED_NONSENDING_BY_DEFAULT = YES",
            "summary: default actor isolation declares MainActor",
            "summary: NonisolatedNonsendingByDefault is declared",
        ]:
            if expected not in scoped_result.stdout:
                raise AssertionError(f"expected scoped Xcode setting output {expected!r}\n{scoped_result.stdout}")

        disabled_xcconfig = root / "NoUpcoming.xcconfig"
        disabled_xcconfig.write_text("SWIFT_UPCOMING_FEATURE_NONISOLATED_NONSENDING_BY_DEFAULT = NO;\n", encoding="utf-8")
        disabled_result = run([sys.executable, "scripts/concurrency_settings_scan.py", str(disabled_xcconfig)])
        assert_success(disabled_result)
        if "NonisolatedNonsendingByDefault is declared" in disabled_result.stdout:
            raise AssertionError(f"disabled upcoming feature should not be summarized as enabled\n{disabled_result.stdout}")


def test_compiler_diagnostic_triage() -> None:
    with tempfile.TemporaryDirectory() as directory:
        root = pathlib.Path(directory)
        log = root / "build.log"
        log.write_text(
            """
/tmp/Demo/ViewModel.swift:12:8: error: main actor-isolated property 'title' can not be referenced from a nonisolated context
/tmp/Demo/ModernView.swift:20:10: warning: 'glassEffect' is only available in iOS 26.0 or newer
/tmp/Demo/Thing.swift:4:15: error: type 'Thing' does not conform to protocol 'Identifiable'
""",
            encoding="utf-8",
        )
        result = run([sys.executable, "scripts/compiler_diagnostic_triage.py", str(log)])
        assert_failure(result)
        for expected in ["concurrency-isolation", "availability", "protocol-conformance"]:
            if expected not in result.stdout:
                raise AssertionError(f"expected triage category {expected!r}\n{result.stdout}")

        extra_log = root / "extra.log"
        extra_log.write_text(
            """
/tmp/Demo/ViewModel.swift:12:9: error: 'async' call in a function that does not support concurrency
/tmp/Demo/View.swift:7:15: error: value of type 'User' has no member 'displayName'
""",
            encoding="utf-8",
        )
        extra = run([sys.executable, "scripts/compiler_diagnostic_triage.py", str(extra_log)])
        assert_failure(extra)
        for expected in ["concurrency-isolation", "type-system"]:
            if expected not in extra.stdout:
                raise AssertionError(f"expected extra triage category {expected!r}\n{extra.stdout}")


def test_xcode_validation_scan() -> None:
    with tempfile.TemporaryDirectory() as directory:
        root = pathlib.Path(directory)
        plan = root / "App.xctestplan"
        plan.write_text(
            """
{
  "configurations": [
    {
      "name": "English Light",
      "options": {
        "language": "en",
        "region": "US",
        "userInterfaceStyle": "light"
      }
    },
    {
      "name": "Arabic Dark Accessibility",
      "options": {
        "language": "ar",
        "region": "SA",
        "userInterfaceStyle": "dark",
        "preferredContentSizeCategory": "accessibilityExtraExtraExtraLarge",
        "enableThreadSanitizer": true
      }
    }
  ]
}
""",
            encoding="utf-8",
        )
        result = run([sys.executable, "scripts/xcode_validation_scan.py", str(root)])
        assert_success(result)
        if "Scanned 1 test plan(s)" not in result.stdout:
            raise AssertionError(f"expected test plan scan summary\n{result.stdout}")
        if "testplan-no-localization" in result.stdout:
            raise AssertionError(f"localization signal should be detected\n{result.stdout}")
        if "testplan-no-sanitizer" in result.stdout:
            raise AssertionError(f"sanitizer signal should be detected\n{result.stdout}")

        plan.write_text(
            """
{
  "configurations": [
    {
      "name": "No Sanitizer",
      "options": {
        "language": "en",
        "region": "US",
        "userInterfaceStyle": "dark",
        "preferredContentSizeCategory": "accessibilityExtraExtraExtraLarge",
        "enableThreadSanitizer": false
      }
    }
  ]
}
""",
            encoding="utf-8",
        )
        disabled = run([sys.executable, "scripts/xcode_validation_scan.py", str(root)])
        assert_success(disabled)
        if "testplan-no-sanitizer" not in disabled.stdout:
            raise AssertionError(f"disabled sanitizer should not count as coverage\n{disabled.stdout}")

        plan.write_text(
            """
{
  "configurations": [
    {
      "name": "Thread Sanitizer Disabled",
      "options": {
        "language": "en",
        "region": "US",
        "userInterfaceStyle": "dark",
        "preferredContentSizeCategory": "accessibilityExtraExtraExtraLarge",
        "enableThreadSanitizer": false
      }
    },
    {
      "name": "Disabled Diagnostics",
      "options": {
        "language": "en",
        "region": "US",
        "userInterfaceStyle": "dark",
        "preferredContentSizeCategory": "accessibilityExtraExtraExtraLarge",
        "disabledDiagnostics": ["Thread Sanitizer"]
      }
    }
  ]
}
""",
            encoding="utf-8",
        )
        disabled_name = run([sys.executable, "scripts/xcode_validation_scan.py", str(root)])
        assert_success(disabled_name)
        if "testplan-no-sanitizer" not in disabled_name.stdout:
            raise AssertionError(f"disabled sanitizer names should not count as coverage\n{disabled_name.stdout}")

        scheme_dir = root / "Demo.xcodeproj" / "xcshareddata" / "xcschemes"
        scheme_dir.mkdir(parents=True)
        scheme = scheme_dir / "Demo.xcscheme"
        scheme.write_text(
            """
<?xml version="1.0" encoding="UTF-8"?>
<Scheme LastUpgradeVersion="1600" version="1.7">
   <BuildAction/>
   <TestAction enableThreadSanitizer="YES"/>
   <LaunchAction selectedDebuggerIdentifier="Xcode.DebuggerFoundation.Debugger.LLDB"/>
   <ProfileAction/>
</Scheme>
""",
            encoding="utf-8",
        )
        scheme_result = run([sys.executable, "scripts/xcode_validation_scan.py", str(scheme)])
        assert_success(scheme_result)
        for unexpected in ["scheme-no-test-action", "scheme-weak-run-profile", "scheme-no-diagnostics"]:
            if unexpected in scheme_result.stdout:
                raise AssertionError(f"valid XML scheme should not trigger {unexpected}\n{scheme_result.stdout}")

        scheme.write_text(
            """
<Scheme LastUpgradeVersion="1600" version="1.7">
   <BuildAction/>
   <TestAction enableThreadSanitizer="YES"/>
   <LaunchAction enableThreadSanitizer="NO"/>
   <ProfileAction/>
</Scheme>
""",
            encoding="utf-8",
        )
        overwritten = run([sys.executable, "scripts/xcode_validation_scan.py", str(scheme)])
        assert_success(overwritten)
        if "scheme-no-diagnostics" in overwritten.stdout:
            raise AssertionError(f"later false diagnostic attribute should not override earlier true signal\n{overwritten.stdout}")


def test_reference_source_audit() -> None:
    with tempfile.TemporaryDirectory() as directory:
        root = pathlib.Path(directory)
        refs = root / "references"
        refs.mkdir()
        source_backed = refs / "model-control.md"
        source_backed.write_text(
            """
# Model Control

Use source-backed model-control rules.

Source: https://arxiv.org/abs/2210.03629
""",
            encoding="utf-8",
        )
        result = run([sys.executable, "scripts/reference_source_audit.py", str(refs)])
        assert_success(result)

        source_backed.write_text("# Model Control\n\nSource needed.\n", encoding="utf-8")
        failed = run([sys.executable, "scripts/reference_source_audit.py", str(refs), "--require-urls"])
        assert_failure(failed)
        if "contains no source URLs" not in failed.stderr:
            raise AssertionError(f"expected missing source URL failure\n{failed.stdout}\n{failed.stderr}")

        source_backed.write_text("# Model Control\n\ndeveloper.apple.com\n", encoding="utf-8")
        plain_domain = run([sys.executable, "scripts/reference_source_audit.py", str(refs)])
        assert_failure(plain_domain)
        if "contains no source URLs" not in plain_domain.stderr:
            raise AssertionError(f"plain domain text should not satisfy source audit\n{plain_domain.stdout}\n{plain_domain.stderr}")

        source_backed.write_text(
            "# Model Control\n\nSource: https://arxiv.org/abs/2210.03629\n",
            encoding="utf-8",
        )
        swift_reference = refs / "swift6-concurrency.md"
        swift_reference.write_text("# Swift 6\n\nSource needed.\n", encoding="utf-8")
        expanded = run([sys.executable, "scripts/reference_source_audit.py", str(refs)])
        assert_failure(expanded)
        if "swift6-concurrency.md" not in expanded.stderr:
            raise AssertionError(f"source-sensitive Swift reference should require URLs\n{expanded.stdout}\n{expanded.stderr}")

        rules = root / "rules"
        rules.mkdir()
        rule_file = rules / "user-rules-swiftui-text.md"
        rule_file.write_text(
            """
# User Rules: Swiftui Text

## user-rule-swiftui-text-curly

**Group:** swiftui-text
**Created:** 2026-05-30
**Updated:** 2026-05-30
**Guidance:** Don’t use String(format:) for value display.
""",
            encoding="utf-8",
        )
        curly = run([sys.executable, "scripts/feedback_rules.py", "validate", str(rules)])
        assert_failure(curly)
        if "guidance must be affirmative" not in curly.stderr:
            raise AssertionError(f"curly apostrophe negative guidance should fail\n{curly.stdout}\n{curly.stderr}")

        rule_file.write_text(
            """
# User Rules: Swiftui Text

## user-rule-swiftui-text-duplicate-examples

**Group:** swiftui-text
**Created:** 2026-05-30
**Updated:** 2026-05-30
**Guidance:** Use Text(value, format: style).
**Examples:** Do not use String(format:).
**Examples:** Use Text(price, format: .currency(code: code)).
""",
            encoding="utf-8",
        )
        duplicate_negative = run([sys.executable, "scripts/feedback_rules.py", "validate", str(rules)])
        assert_failure(duplicate_negative)
        if "examples must be affirmative" not in duplicate_negative.stderr:
            raise AssertionError(f"negative duplicate example should fail validation\n{duplicate_negative.stdout}\n{duplicate_negative.stderr}")


def main() -> int:
    test_feedback_rules()
    test_swift_scanner()
    test_concurrency_settings_scanner()
    test_compiler_diagnostic_triage()
    test_xcode_validation_scan()
    test_reference_source_audit()
    print("Self-tests passed.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
