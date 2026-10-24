import Foundation

struct FormState {
  var title: String
  var completed: Bool
  var buttonLabel: String { completed ? "Mark incomplete" : "Mark complete" }
}

@main
struct LessonMain {
  static func main() async throws {
    do {
      let state = FormState(title: "Read", completed: false)
      precondition(state.buttonLabel == "Mark complete")
    }

    do {
      var state = FormState(title: "Read", completed: false)
      state.completed = true
      precondition(state.buttonLabel == "Mark incomplete")
      precondition(state.title == "Read")
    }
    print("swift-040: passed")
  }
}
