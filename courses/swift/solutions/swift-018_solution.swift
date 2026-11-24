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
      // Task 1: Predict and explain
      let number = larger(3, 8)
      let word = larger("apple", "pear")
      let pair = Pair(first: "left", second: "right")
      precondition(type(of: number) == Int.self)
      precondition(type(of: word) == String.self)
      precondition(type(of: pair) == Pair<String>.self)
    }

    do {
      // Task 2: Guided modification
      precondition(larger(2.5, 1.5) == 2.5)
      let tie = larger(2.0, 2.0)
      precondition(tie == 2.0 && type(of: tie) == Double.self)
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

    do {
      // Task 4: Diagnose a defect
      func describe<T: CustomStringConvertible>(_ value: T) -> String {
        "value: \(value.description)"
      }
      precondition(describe(7) == "value: 7")
      precondition(describe("pear") == "value: pear")
    }

    do {
      // Task 5: Boundary evidence
      struct Ranked: Comparable {
        let rank: Int
        let tag: String
        static func < (left: Ranked, right: Ranked) -> Bool { left.rank < right.rank }
        static func == (left: Ranked, right: Ranked) -> Bool { left.rank == right.rank }
      }
      let winner = larger(Ranked(rank: 1, tag: "left"), Ranked(rank: 1, tag: "right"))
      precondition(winner.tag == "left")
    }
    print("swift-018: passed")
  }
}
