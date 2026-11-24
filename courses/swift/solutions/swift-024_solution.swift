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

    do {
      // Task 1: Predict and explain
      let manager = FileManager.default
      func useOwnedDirectory() throws -> URL {
        let root = manager.temporaryDirectory.appendingPathComponent(
          UUID().uuidString, isDirectory: true)
        try manager.createDirectory(at: root, withIntermediateDirectories: true)
        defer { try? manager.removeItem(at: root) }
        let file = root.appendingPathComponent("trace.txt")
        try Data("used".utf8).write(to: file)
        precondition(manager.fileExists(atPath: file.path))
        return root
      }
      let root = try useOwnedDirectory()
      precondition(!manager.fileExists(atPath: root.path))
    }

    do {
      // Task 2: Guided modification
      let manager = FileManager.default
      let root = manager.temporaryDirectory.appendingPathComponent(
        UUID().uuidString, isDirectory: true)
      try manager.createDirectory(at: root, withIntermediateDirectories: true)
      defer { try? manager.removeItem(at: root) }
      let first = root.appendingPathComponent("a.txt")
      let second = root.appendingPathComponent("b.txt")
      try Data("alpha".utf8).write(to: first)
      try Data("beta".utf8).write(to: second)
      let firstText = try String(contentsOf: first, encoding: .utf8)
      let secondText = try String(contentsOf: second, encoding: .utf8)
      precondition(firstText == "alpha" && secondText == "beta")
    }

    do {
      // Task 3: Independent construction
      struct Stock: Codable, Equatable {
        let name: String
        let quantity: Int
      }
      let manager = FileManager.default
      let folder = manager.temporaryDirectory.appendingPathComponent(
        UUID().uuidString, isDirectory: true)
      try manager.createDirectory(at: folder, withIntermediateDirectories: true)
      defer { try? manager.removeItem(at: folder) }
      let file = folder.appendingPathComponent("stock.json")
      let saved = Stock(name: "pear", quantity: 3)
      try JSONEncoder().encode(saved).write(to: file)
      let restored = try JSONDecoder().decode(Stock.self, from: Data(contentsOf: file))
      precondition(restored == saved && restored.quantity >= 0)
    }

    do {
      // Task 5: Boundary evidence
      let manager = FileManager.default
      let root = manager.temporaryDirectory.appendingPathComponent(
        UUID().uuidString, isDirectory: true)
      try manager.createDirectory(at: root, withIntermediateDirectories: true)
      defer { try? manager.removeItem(at: root) }
      let blank = root.appendingPathComponent("blank.bin")
      try Data().write(to: blank)
      let blankBytes = try Data(contentsOf: blank)
      precondition(blankBytes.isEmpty)
      var missingFailed = false
      do { _ = try Data(contentsOf: root.appendingPathComponent("absent.bin")) } catch {
        missingFailed = true
      }
      precondition(missingFailed)
    }
    print("swift-024: passed")
  }
}
