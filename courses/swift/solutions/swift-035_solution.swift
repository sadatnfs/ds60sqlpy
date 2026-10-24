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
    print("swift-035: passed")
  }
}
