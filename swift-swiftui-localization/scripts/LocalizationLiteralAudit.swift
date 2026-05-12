#!/usr/bin/env swift
import Foundation

let arguments = CommandLine.arguments.dropFirst()
guard !arguments.isEmpty else {
    FileHandle.standardError.write(Data("Usage: LocalizationLiteralAudit.swift <swift-file-or-directory> [...]\n".utf8))
    exit(2)
}

let uiPropertyPattern = #"\b(let|var)\s+(title|subtitle|message|label|name|headline|caption|placeholder)\s*:\s*String\b"#
let textVariablePattern = #"\b(Text|Label|Button|Picker|Menu)\s*\(\s*([A-Za-z_][A-Za-z0-9_\.]*)"#

func regex(_ pattern: String) -> NSRegularExpression {
    try! NSRegularExpression(pattern: pattern)
}

let uiPropertyRegex = regex(uiPropertyPattern)
let textVariableRegex = regex(textVariablePattern)
var findingCount = 0

func swiftFiles(at url: URL) -> [URL] {
    var isDirectory: ObjCBool = false
    guard FileManager.default.fileExists(atPath: url.path, isDirectory: &isDirectory) else { return [] }
    if !isDirectory.boolValue {
        return url.pathExtension == "swift" ? [url] : []
    }
    guard let enumerator = FileManager.default.enumerator(at: url, includingPropertiesForKeys: nil) else { return [] }
    return enumerator.compactMap { item in
        guard let file = item as? URL, file.pathExtension == "swift" else { return nil }
        let path = file.path
        if path.contains("/.build/") || path.contains("/DerivedData/") || path.contains("/Pods/") {
            return nil
        }
        return file
    }
}

func report(file: URL, line: Int, code: String, message: String) {
    findingCount += 1
    print("\(file.path):\(line): [\(code)] \(message)")
}

for raw in arguments {
    let root = URL(fileURLWithPath: NSString(string: raw).expandingTildeInPath)
    for file in swiftFiles(at: root) {
        guard let content = try? String(contentsOf: file) else { continue }
        let lines = content.components(separatedBy: .newlines)
        for (index, line) in lines.enumerated() {
            let range = NSRange(line.startIndex..<line.endIndex, in: line)
            if uiPropertyRegex.firstMatch(in: line, range: range) != nil {
                report(file: file, line: index + 1, code: "ui-string-property", message: "UI-looking stored property is String; prefer LocalizedStringResource or intentional verbatim data.")
            }
            if let match = textVariableRegex.firstMatch(in: line, range: range),
               match.numberOfRanges >= 3,
               let argRange = Range(match.range(at: 2), in: line) {
                let arg = String(line[argRange])
                report(file: file, line: index + 1, code: "swiftui-verbatim-risk", message: "SwiftUI call receives `\(arg)`; verify this is not app-owned localizable copy.")
            }
        }
    }
}

print("\n\(findingCount) finding(s)")
exit(findingCount == 0 ? 0 : 1)
