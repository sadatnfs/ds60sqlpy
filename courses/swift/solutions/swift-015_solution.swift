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
      // Task 3: Independent construction
      func transformAll(_ values: [Int], _ change: (Int) -> Int) -> [Int] {
        var result: [Int] = []
        for value in values { result.append(change(value)) }
        return result
      }
      let scaled = transformAll([1, 2, 3]) { $0 * 10 }
      precondition(scaled == [10, 20, 30])
    }
    print("swift-015: passed")
  }
}
