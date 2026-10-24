import Foundation

@main
struct LessonMain {
  static func main() async throws {
    do {
      let values = [2, 4, 6, 8]
      var comparisons = 0
      for value in values {
        comparisons += 1
        if value == 8 { break }
      }
      precondition(comparisons == 4)
    }

    do {
      let index = Set([2, 4, 6, 8])
      precondition(index.contains(8) && !index.contains(9))
      precondition(index.count == 4)
    }
    print("swift-036: passed")
  }
}
