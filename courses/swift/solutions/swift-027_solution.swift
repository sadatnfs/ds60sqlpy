import Foundation

@main
struct LessonMain {
  static func main() async throws {
    do {
      let cases = [(-2, 0), (0, 0), (3, 3)]
      for (input, expected) in cases { precondition(max(0, input) == expected) }
    }

    do {
      func wrong(_ value: Int) -> Int { value <= 0 ? 1 : value }
      precondition(wrong(0) != max(0, 0))
      precondition(max(0, max(0, -4)) == max(0, -4))
    }
    print("swift-027: passed")
  }
}
