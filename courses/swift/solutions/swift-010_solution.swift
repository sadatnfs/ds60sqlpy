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
    print("swift-010: passed")
  }
}
