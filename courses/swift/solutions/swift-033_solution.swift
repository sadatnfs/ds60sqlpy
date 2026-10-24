import Foundation

struct Snapshot: Sendable {
  let name: String
  let quantity: Int
}

@main
struct LessonMain {
  static func main() async throws {
    do {
      let snapshot = Snapshot(name: "pear", quantity: 3)
      let task = Task { snapshot.quantity * 2 }
      let result = await task.value
      precondition(result == 6)
    }

    do {
      let result = await withTaskGroup(of: Snapshot.self, returning: [Snapshot].self) { group in
        group.addTask { Snapshot(name: "b", quantity: 2) }
        group.addTask { Snapshot(name: "a", quantity: 1) }
        var snapshots: [Snapshot] = []
        for await value in group { snapshots.append(value) }
        return snapshots.sorted { $0.name < $1.name }
      }
      precondition(result.map(\.name) == ["a", "b"])
    }
    print("swift-033: passed")
  }
}
