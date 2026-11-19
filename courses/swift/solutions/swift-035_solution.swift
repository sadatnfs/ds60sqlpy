import Foundation

@main
struct LessonMain {
  static func main() async throws {
    do {
      let values = [2, 3, 4]
      let total = values.withUnsafeBufferPointer { buffer in buffer.reduce(0, +) }
      precondition(total == 9)
    }

    do {
      let values: [Int] = []
      let count = values.withUnsafeBufferPointer { buffer in buffer.count }
      precondition(count == 0)
    }

    do {
      // Task 3: Independent construction
      /// Returns the sum of the values; the buffer pointer never escapes this call.
      func total(of values: [Int]) -> Int {
        values.withUnsafeBufferPointer { buffer in
          var sum = 0
          for value in buffer { sum += value }
          return sum
        }
      }
      precondition(total(of: [2, 3, 4]) == 9 && total(of: []) == 0)
    }
    print("swift-035: passed")
  }
}
