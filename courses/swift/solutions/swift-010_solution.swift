import Foundation

@main
struct LessonMain {
  static func main() async throws {
    do {
      let counts = ["pear": 0]
      precondition(counts["pear"] == 0)
      precondition(counts["apple"] == nil)
    }

    do {
      var tags: Set<String> = ["red"]
      precondition(!tags.insert("red").inserted)
      precondition(tags.insert("blue").inserted)
      precondition(tags.sorted() == ["blue", "red"])
    }

    do {
      // Task 3: Independent construction
      let rows = ["pear", "apple", "pear", "", "fig"]
      let names = Set(rows.filter { !$0.isEmpty }).sorted()
      precondition(names == ["apple", "fig", "pear"])
    }
    print("swift-010: passed")
  }
}
