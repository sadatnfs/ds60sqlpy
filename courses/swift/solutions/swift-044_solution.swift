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
      let identity = "lesson-one"
      let titles = ["en": "Read", "fr": "Lire"]
      precondition(titles["en"] != titles["fr"])
      precondition(identity == "lesson-one")
    }
    print("swift-044: passed")
  }
}
