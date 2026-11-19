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

    do {
      // Task 3: Independent construction
      let names = ["pear", "apple", "fig"]
      let queries = ["fig", "kiwi", "pear"]
      let scanHits = queries.filter { names.contains($0) }.count
      let index = Set(names)
      let indexHits = queries.filter { index.contains($0) }.count
      precondition(scanHits == 2 && indexHits == scanHits)
    }
    print("swift-036: passed")
  }
}
