import Foundation

func larger<T: Comparable>(_ left: T, _ right: T) -> T { left >= right ? left : right }
struct Pair<T> {
  let first: T
  let second: T
  func swapped() -> Pair<T> { Pair(first: second, second: first) }
}

@main
struct LessonMain {
  static func main() async throws {
    do {
      precondition(larger(3, 8) == 8)
      precondition(larger("apple", "pear") == "pear")
    }

    do {
      let pair = Pair(first: "left", second: "right")
      let swapped = pair.swapped()
      precondition(swapped.first == "right" && swapped.second == "left")
    }

    do {
      // Task 3: Independent construction
      struct Triple<T> {
        let first: T
        let second: T
        let third: T
        func rotated() -> Triple<T> { Triple(first: second, second: third, third: first) }
      }
      let rotated = Triple(first: 1, second: 2, third: 3).rotated()
      precondition(rotated.first == 2 && rotated.second == 3 && rotated.third == 1)
    }
    print("swift-018: passed")
  }
}
