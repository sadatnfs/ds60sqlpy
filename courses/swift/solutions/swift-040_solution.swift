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

    do {
      // Task 1: Predict and explain
      var state = FormState(title: "Read", completed: false)
      precondition(state.buttonLabel == "Mark complete")
      state.completed.toggle()
      precondition(state.buttonLabel == "Mark incomplete")
    }

    do {
      // Task 2: Guided modification
      struct EditableForm {
        var title: String
        var completed: Bool
        var saveDisabled: Bool { title.trimmingCharacters(in: .whitespaces).isEmpty }
      }
      var form = EditableForm(title: "Read", completed: false)
      precondition(!form.saveDisabled)
      form.title = "  "
      precondition(form.saveDisabled)
    }

    do {
      // Task 4: Diagnose a defect
      final class Model { var title = "Read" }
      struct StaleChild {
        var copy: String
        init(model: Model) { copy = model.title }
      }
      struct LiveChild {
        let model: Model
        var shown: String { model.title }
      }
      let model = Model()
      let stale = StaleChild(model: model)
      let live = LiveChild(model: model)
      model.title = "Review"
      precondition(stale.copy == "Read" && live.shown == "Review")
    }

    do {
      // Task 5: Boundary evidence
      struct Draft {
        var title: String
        func commit(into saved: inout String) { saved = title }
      }
      var saved = "Read"
      var edit = Draft(title: saved)
      edit.title = "Review"
      edit.commit(into: &saved)
      precondition(saved == "Review")
      var cancelled = Draft(title: saved)
      cancelled.title = "Discard me"
      precondition(saved == "Review")
    }
    print("swift-040: passed")
  }
}
