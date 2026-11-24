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
      // Task 1: Predict and explain
      let wrappedZero: Int? = 0
      let absent: Int? = nil
      precondition(wrappedZero != absent)
      precondition(wrappedZero.map { $0 + 1 } == 1 && absent.map { $0 + 1 } == nil)
      precondition((wrappedZero ?? 99) == 0 && (absent ?? 99) == 99)
    }

    do {
      // Task 2: Guided modification
      func display(_ reading: Int?) -> String { reading.map { "\($0)" } ?? "unknown" }
      precondition(display(Int("42")) == "42")
      precondition(display(Int("forty-two")) == "unknown")
      precondition(display(0) == "0")
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

    do {
      // Task 4: Diagnose a defect
      let external = "forty-two"
      let parsed = Int(external)
      precondition(parsed == nil)
      let outcome: String
      if let value = parsed { outcome = "value:\(value)" } else { outcome = "rejected:\(external)" }
      precondition(outcome == "rejected:forty-two")
    }

    do {
      // Task 5: Boundary evidence
      func parseCount(_ text: String?) -> Int? {
        guard let text, let value = Int(text), value >= 0 else { return nil }
        return value
      }
      precondition(parseCount("") == nil)
      precondition(parseCount("0") == 0)
      precondition(parseCount("-1") == nil)
      precondition(parseCount("9223372036854775807") == Int.max)
      precondition(parseCount("9223372036854775808") == nil)
    }
    print("swift-005: passed")
  }
}
