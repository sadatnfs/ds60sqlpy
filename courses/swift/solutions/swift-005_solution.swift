import Foundation

@main
struct LessonMain {
  static func main() async throws {
    do {
      let measured: Int? = 0
      let missing: Int? = nil
      precondition(measured != nil && missing == nil)
      if let value = measured {
        precondition(value == 0)
      } else {
        preconditionFailure("present zero")
      }
    }

    do {
      let valid = Int("42")
      let invalid = Int("forty-two")
      precondition(valid == 42 && invalid == nil)
      precondition((invalid ?? -1) == -1)
    }

    do {
      // Task 3: Independent construction
      func parseCount(_ text: String?) -> Int? {
        guard let text, let value = Int(text), value >= 0 else { return nil }
        return value
      }
      precondition(parseCount("12") == 12 && parseCount("0") == 0)
      precondition(parseCount(nil) == nil && parseCount("-3") == nil)
      precondition(parseCount("x") == nil)
    }
    print("swift-005: passed")
  }
}
