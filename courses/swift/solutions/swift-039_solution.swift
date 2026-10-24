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
    print("swift-039: passed")
  }
}
