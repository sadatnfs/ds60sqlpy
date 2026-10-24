import Foundation

@main
struct LessonMain {
  static func main() async throws {
    do {
      let manager = FileManager.default
      let root = manager.temporaryDirectory.appendingPathComponent(
        UUID().uuidString, isDirectory: true)
      try manager.createDirectory(at: root, withIntermediateDirectories: true)
      defer { try? manager.removeItem(at: root) }
      let file = root.appendingPathComponent("note.txt")
      let expected = Data("café".utf8)
      try expected.write(to: file)
      let actual = try Data(contentsOf: file)
      precondition(actual == expected)
    }

    do {
      let file = URL(fileURLWithPath: "/tmp/example.txt")
      let remote = URL(string: "https://example.invalid/data")!
      precondition(file.isFileURL && !remote.isFileURL)
    }
    print("swift-024: passed")
  }
}
