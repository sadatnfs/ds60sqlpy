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
    print("swift-044: passed")
  }
}
