import Foundation

@main
struct LessonMain {
  static func main() async throws {
    do {
      func total(_ values: [Int]) -> Int { values.reduce(0, +) }
      precondition(total([2, 3]) == 5)
      precondition(total([]) == 0)
    }

    do {
      func render(_ total: Int) -> String { "total=\(total)" }
      precondition(render(5) == "total=5")
    }

    do {
      // Task 1: Predict and explain
      func total(_ values: [Int]) -> Int { values.reduce(0, +) }
      func render(_ total: Int) -> String { "total=\(total)" }
      let sum = total([4, 6])
      precondition(sum == 10)
      precondition(render(sum) == "total=10")
    }
    print("swift-026: passed")
  }
}
