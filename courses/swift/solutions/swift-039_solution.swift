import Foundation

struct PlannerItem: Equatable, Sendable {
  let id: String
  let title: String
  var completed: Bool
}
func toggled(_ item: PlannerItem) -> PlannerItem {
  var result = item
  result.completed.toggle()
  return result
}

@main
struct LessonMain {
  static func main() async throws {
    do {
      let original = PlannerItem(id: "one", title: "Read", completed: false)
      let changed = toggled(original)
      precondition(changed.completed && !original.completed)
    }

    do {
      let original = PlannerItem(id: "one", title: "Read", completed: false)
      let changed = toggled(original)
      precondition(changed.id == original.id && changed.title == original.title)
    }

    do {
      // Task 1: Predict and explain
      let item = PlannerItem(id: "one", title: "Read", completed: false)
      let updated = toggled(item)
      let rowText = "\(updated.title): \(updated.completed ? "done" : "open")"
      precondition(updated.completed && rowText == "Read: done")
    }

    do {
      // Task 2: Guided modification
      enum RenameError: Error { case emptyTitle }
      func renamed(_ item: PlannerItem, to title: String) throws -> PlannerItem {
        let trimmed = title.trimmingCharacters(in: .whitespacesAndNewlines)
        guard !trimmed.isEmpty else { throw RenameError.emptyTitle }
        return PlannerItem(id: item.id, title: trimmed, completed: item.completed)
      }
      let item = PlannerItem(id: "one", title: "Read", completed: true)
      let changed = try renamed(item, to: " Review ")
      precondition(changed.id == "one" && changed.title == "Review" && changed.completed)
      precondition((try? renamed(item, to: "   ")) == nil)
    }

    do {
      // Task 4: Diagnose a defect
      struct PlanSnapshot {
        let titles: [String]
        var count: Int { titles.count }
      }
      func loadPlan(from storage: [String: [String]], key: String) -> PlanSnapshot {
        PlanSnapshot(titles: storage[key] ?? [])
      }
      let storage = ["plan": ["Read", "Practice"]]
      let plan = loadPlan(from: storage, key: "plan")
      precondition(plan.count == 2 && plan.count == 2)
    }

    do {
      // Task 5: Boundary evidence
      enum AdmitError: Error { case duplicate, unknown }
      func admit(_ item: PlannerItem, into items: [PlannerItem]) throws -> [PlannerItem] {
        guard !items.contains(where: { $0.id == item.id }) else { throw AdmitError.duplicate }
        return items + [item]
      }
      func toggle(id: String, in items: [PlannerItem]) throws -> [PlannerItem] {
        guard let index = items.firstIndex(where: { $0.id == id }) else { throw AdmitError.unknown }
        var result = items
        result[index] = toggled(result[index])
        return result
      }
      let items = try admit(PlannerItem(id: "a", title: "Read", completed: false), into: [])
      precondition(
        (try? admit(PlannerItem(id: "a", title: "Copy", completed: false), into: items)) == nil)
      precondition((try? toggle(id: "missing", in: items)) == nil)
      let toggledItems = try toggle(id: "a", in: items)
      precondition(toggledItems[0].completed)
    }
    print("swift-039: passed")
  }
}
