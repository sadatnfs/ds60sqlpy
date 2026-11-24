import Foundation

@main
struct LessonMain {
  static func main() async throws {
    do {
      func accessibilityText(title: String, complete: Bool) -> String {
        "\(title), \(complete ? "complete" : "incomplete")"
      }
      precondition(accessibilityText(title: "Read", complete: true) == "Read, complete")
    }

    do {
      let titles = ["en": "Read", "fr": "Lire"]
      let saved: [String: Bool] = ["lesson-one": true]
      func row(id: String, language: String) -> String {
        let state = saved[id] == true ? "complete" : "incomplete"
        return "\(titles[language] ?? id): \(state)"
      }
      precondition(row(id: "lesson-one", language: "en") == "Read: complete")
      precondition(row(id: "lesson-one", language: "fr") == "Lire: complete")
    }

    do {
      // Task 1: Predict and explain
      struct ColorOnlyRow {
        let title: String
        let tint: String
      }
      let row = ColorOnlyRow(title: "Read", tint: "green")
      let spoken = row.title
      precondition(!spoken.contains("complete"))
      let labeled = "\(row.title), \(row.tint == "green" ? "complete" : "incomplete")"
      precondition(labeled == "Read, complete")
    }

    do {
      // Task 2: Guided modification
      func rowLabel(title: String, complete: Bool) -> String {
        "\(title), \(complete ? "complete" : "incomplete")"
      }
      func actionLabel(title: String, complete: Bool) -> String {
        complete ? "Mark \(title) incomplete" : "Mark \(title) complete"
      }
      precondition(rowLabel(title: "Read", complete: false) == "Read, incomplete")
      precondition(actionLabel(title: "Read", complete: false) == "Mark Read complete")
    }

    do {
      // Task 4: Diagnose a defect
      let identifier = "row-7"
      let label = "Read a chapter, incomplete"
      precondition(!identifier.contains("Read") && label.contains("Read"))
    }
    print("swift-044: passed")
  }
}
