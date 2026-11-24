import Foundation

@main
struct LessonMain {
  static func main() async throws {
    do {
      let values = [1, 2, 3]
      let doubled = values.map { value in value * 2 }
      precondition(doubled == [2, 4, 6])
      precondition(values == [1, 2, 3])
    }

    do {
      var factor = 2
      let scale = { [factor] (value: Int) in value * factor }
      factor = 5
      precondition(scale(3) == 6 && factor == 5)
    }

    do {
      // Task 1: Predict and explain
      let values = [1, 2, 3]
      let doubled = values.map { $0 * 2 }
      precondition(doubled == [2, 4, 6])
      precondition(values == [1, 2, 3] && doubled.count == values.count)
    }

    do {
      // Task 2: Guided modification
      let values = [1, 2, 3, 4]
      let evensDoubled = values.filter { $0 % 2 == 0 }.map { $0 * 2 }
      precondition(evensDoubled == [4, 8])
    }

    do {
      // Task 3: Independent construction
      func transformAll(_ values: [Int], _ change: (Int) -> Int) -> [Int] {
        var result: [Int] = []
        for value in values { result.append(change(value)) }
        return result
      }
      let scaled = transformAll([1, 2, 3]) { $0 * 10 }
      precondition(scaled == [10, 20, 30])
    }

    do {
      // Task 4: Diagnose a defect
      var factor = 2
      let live = { (value: Int) in value * factor }
      let frozen = { [factor] (value: Int) in value * factor }
      factor = 5
      precondition(live(3) == 15)
      precondition(frozen(3) == 6)
    }

    do {
      // Task 5: Boundary evidence
      precondition([Int]().map { $0 * 2 }.isEmpty)
      let parsed = ["1", "x", "3"].map { Int($0) }
      precondition(parsed == [1, nil, 3])
      let valid = ["1", "x", "3"].compactMap { Int($0) }
      precondition(valid == [1, 3])
    }
    print("swift-015: passed")
  }
}
