import Foundation

@main
struct LessonMain {
  static func main() async throws {
    do {
      let perBox = 4
      var total = 0
      total += perBox
      total += perBox
      precondition(total == 8 && perBox == 4)
    }

    do {
      let whole = 7 / 2
      let fractional = Double(7) / Double(2)
      precondition(whole == 3)
      precondition(fractional == 3.5)
    }

    do {
      // Task 3: Independent construction
      let total = 7
      let count = 2
      let mean = Double(total) / Double(count)
      precondition(mean == 3.5)
      precondition(total / count == 3)
    }
    print("swift-002: passed")
  }
}
