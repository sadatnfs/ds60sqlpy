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
      // Task 1: Predict and explain
      let values = [2, 3, 4]
      let byteCount = values.withUnsafeBytes { bytes in bytes.count }
      precondition(byteCount == values.count * MemoryLayout<Int>.stride)
      let total = values.withUnsafeBufferPointer { buffer in buffer.reduce(0, +) }
      precondition(total == 9)
    }

    do {
      // Task 2: Guided modification
      func largest(_ values: [Int]) -> Int? {
        values.withUnsafeBufferPointer { buffer in
          guard let first = buffer.first else { return nil }
          return buffer.reduce(first, max)
        }
      }
      precondition(largest([]) == nil)
      precondition(largest([3, 9, 2]) == 9)
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

    do {
      // Task 4: Diagnose a defect
      let values = [5, 6]
      let copied = values.withUnsafeBufferPointer { buffer in Array(buffer) }
      precondition(copied == [5, 6])
    }

    do {
      // Task 5: Boundary evidence
      func bufferSum(_ values: [Int]) -> Int {
        values.withUnsafeBufferPointer { buffer in buffer.reduce(0, +) }
      }
      precondition(bufferSum([]) == 0)
      precondition(bufferSum([7]) == 7)
      precondition(bufferSum([1, 2, 3, 4]) == 10)
    }
    print("swift-035: passed")
  }
}
