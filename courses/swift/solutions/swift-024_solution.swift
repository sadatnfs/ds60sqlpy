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
    print("swift-024: passed")
  }
}
