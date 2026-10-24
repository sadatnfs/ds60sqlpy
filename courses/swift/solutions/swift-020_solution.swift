import Foundation

@main
struct LessonMain {
  static func main() async throws {
    do {
      let values = [10, 20, 30, 40]
      let slice = values[1...2]
      precondition(slice.startIndex == 1)
      precondition(slice.map { $0 / 10 } == [2, 3])
    }

    do {
      let transformed = [1, 2, 3].lazy.filter { $0 > 1 }.map { $0 * 10 }
      precondition(Array(transformed) == [20, 30])
      precondition([Int]().reduce(0, +) == 0)
    }
    print("swift-020: passed")
  }
}
