import Foundation

struct CapstoneItem: Equatable, Sendable {
  let id: String
  var complete: Bool
}

@main
struct LessonMain {
  static func main() async throws {
    do {
      let items = [CapstoneItem(id: "a", complete: true), CapstoneItem(id: "b", complete: false)]
      precondition(items.filter(\.complete).count == 1)
      precondition(Set(items.map(\.id)).count == items.count)
    }

    do {
      let original = CapstoneItem(id: "a", complete: false)
      var changed = original
      changed.complete = true
      precondition(changed.id == original.id && !original.complete && changed.complete)
    }

    do {
      // Task 2: Guided modification
      let items = [
        CapstoneItem(id: "a", complete: true),
        CapstoneItem(id: "b", complete: false),
        CapstoneItem(id: "c", complete: true),
      ]
      var progress: String { "\(items.filter(\.complete).count)/\(items.count) complete" }
      precondition(progress == "2/3 complete")
    }

    do {
      // Task 4: Diagnose a defect
      enum CapstoneError: Error { case duplicate }
      func buggyAdd(_ item: CapstoneItem, to items: [CapstoneItem]) -> [CapstoneItem] {
        items + [item]
      }
      func add(_ item: CapstoneItem, to items: [CapstoneItem]) throws -> [CapstoneItem] {
        guard !items.contains(where: { $0.id == item.id }) else { throw CapstoneError.duplicate }
        return items + [item]
      }
      let start = [CapstoneItem(id: "a", complete: false)]
      let broken = buggyAdd(CapstoneItem(id: "a", complete: true), to: start)
      precondition(Set(broken.map(\.id)).count != broken.count)
      precondition((try? add(CapstoneItem(id: "a", complete: true), to: start)) == nil)
    }

    do {
      // Task 5: Boundary evidence
      struct StoredItem: Codable, Equatable {
        let id: String
        let title: String
      }
      func validated(_ items: [StoredItem]) -> Bool {
        Set(items.map(\.id)).count == items.count && items.allSatisfy { !$0.title.isEmpty }
      }
      precondition(validated([]))
      let long = StoredItem(id: "l", title: String(repeating: "word ", count: 200))
      precondition(validated([long]))
      precondition(!validated([StoredItem(id: "x", title: "A"), StoredItem(id: "x", title: "B")]))
      precondition((try? JSONDecoder().decode([StoredItem].self, from: Data("{".utf8))) == nil)
      let saved = try JSONEncoder().encode([long])
      let reloaded = try JSONDecoder().decode([StoredItem].self, from: saved)
      precondition(reloaded == [long])
    }
    print("swift-048: passed")
  }
}
