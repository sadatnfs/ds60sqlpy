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

    do {
      // Task 1: Predict and explain
      let snapshot = Snapshot(name: "pear", quantity: 3)
      let task = Task { Snapshot(name: snapshot.name, quantity: snapshot.quantity * 2) }
      let doubled = await task.value
      precondition(snapshot.quantity == 3)
      precondition(doubled.name == "pear" && doubled.quantity == 6)
    }

    do {
      // Task 2: Guided modification
      struct PricedSnapshot: Sendable {
        let name: String
        let quantity: Int
        let unitPrice: Int
      }
      let snapshot = PricedSnapshot(name: "pear", quantity: 3, unitPrice: 4)
      let cost = await Task { snapshot.quantity * snapshot.unitPrice }.value
      precondition(cost == 12)
    }

    do {
      // Task 3: Independent construction
      struct Summary: Sendable {
        let count: Int
        let total: Int
      }
      let summary = await Task { () -> Summary in
        let values = [2, 3, 4]
        return Summary(count: values.count, total: values.reduce(0, +))
      }.value
      precondition(summary.count == 3 && summary.total == 9)
    }

    do {
      // Task 4: Diagnose a defect
      actor Tally {
        private(set) var count = 0
        func add() { count += 1 }
      }
      let tally = Tally()
      await withTaskGroup(of: Void.self) { group in
        for _ in 0..<100 { group.addTask { await tally.add() } }
      }
      let count = await tally.count
      precondition(count == 100)
    }

    do {
      // Task 5: Boundary evidence
      let none = await withTaskGroup(of: Snapshot.self, returning: [Snapshot].self) { group in
        var collected: [Snapshot] = []
        for await value in group { collected.append(value) }
        return collected
      }
      precondition(none.isEmpty)
      let many = await withTaskGroup(of: Snapshot.self, returning: [String].self) { group in
        for number in 1...4 { group.addTask { Snapshot(name: "p\(number)", quantity: number) } }
        var names: [String] = []
        for await value in group { names.append(value.name) }
        return names.sorted()
      }
      precondition(many == ["p1", "p2", "p3", "p4"])
    }
    print("swift-033: passed")
  }
}
