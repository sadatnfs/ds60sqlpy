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

    do {
      // Task 1: Predict and explain
      let cases = [(-2, 0), (0, 0), (3, 3)]
      func passes(_ candidate: (Int) -> Int) -> Bool {
        cases.allSatisfy { candidate($0.0) == $0.1 }
      }
      precondition(passes { max(0, $0) })
      precondition(!passes { $0 })
      precondition(!passes { abs($0) })
      precondition(!passes { _ in 0 })
    }

    do {
      // Task 2: Guided modification
      precondition(max(0, Int.min) == 0)
      precondition(Int.min.magnitude == UInt(Int.max) + 1)
      precondition(Int.min.addingReportingOverflow(-1).overflow)
    }

    do {
      // Task 4: Diagnose a defect
      func wrongClamp(_ value: Int) -> Int { value <= 0 ? 1 : value }
      precondition(wrongClamp(0) == wrongClamp(0))
      precondition(wrongClamp(0) != 0)
    }

    do {
      // Task 5: Boundary evidence
      func clampAll(_ texts: [String]) -> [Int]? {
        var result: [Int] = []
        for text in texts {
          guard let value = Int(text) else { return nil }
          result.append(max(0, value))
        }
        return result
      }
      precondition(clampAll([]) == [])
      precondition(clampAll(["-1", "-1"]) == [0, 0])
      precondition(clampAll(["2", "x"]) == nil)
    }
    print("swift-027: passed")
  }
}
