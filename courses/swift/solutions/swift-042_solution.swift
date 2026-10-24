import Foundation

struct SavedPlan: Codable {
  let schemaVersion: Int
  let titles: [String]
}
func supported(_ document: SavedPlan) -> Bool {
  document.schemaVersion == 1 && document.titles.allSatisfy { !$0.isEmpty }
}

@main
struct LessonMain {
  static func main() async throws {
    do {
      let document = SavedPlan(schemaVersion: 1, titles: ["Read", "Practice"])
      let data = try JSONEncoder().encode(document)
      let decoded = try JSONDecoder().decode(SavedPlan.self, from: data)
      precondition(decoded.schemaVersion == 1 && decoded.titles.count == 2)
    }

    do {
      let document = SavedPlan(schemaVersion: 99, titles: ["Keep me"])
      precondition(!supported(document))
      precondition(document.titles == ["Keep me"])
    }
    print("swift-042: passed")
  }
}
