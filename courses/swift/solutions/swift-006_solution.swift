import Foundation

@main
struct LessonMain {
  static func main() async throws {
    do {
      func classify(_ score: Int) -> String {
        switch score {
        case 0..<60: return "retry"
        case 60...100: return "pass"
        default: return "invalid"
        }
      }
      precondition(classify(59) == "retry")
      precondition(classify(60) == "pass" && classify(101) == "invalid")
    }

    do {
      func describe(_ text: String?) -> String {
        guard let text, !text.isEmpty else { return "missing" }
        return "value:\(text)"
      }
      precondition(describe(nil) == "missing")
      precondition(describe("") == "missing" && describe("x") == "value:x")
    }

    do {
      // Task 1: Predict and explain
      func classify(_ score: Int) -> String {
        switch score {
        case 0..<60: return "retry"
        case 60...100: return "pass"
        default: return "invalid"
        }
      }
      let predicted = ["retry", "pass", "invalid"]
      precondition([59, 60, 101].map(classify) == predicted)
    }

    do {
      // Task 2: Guided modification
      func classify(_ score: Int) -> String {
        switch score {
        case 0..<70: return "retry"
        case 70...100: return "pass"
        default: return "invalid"
        }
      }
      precondition(classify(69) == "retry" && classify(70) == "pass")
      precondition(classify(60) == "retry" && classify(100) == "pass")
    }

    do {
      // Task 3: Independent construction
      func sign(_ quantity: Int) -> String {
        switch quantity {
        case ..<0: return "negative"
        case 0: return "zero"
        default: return "positive"
        }
      }
      precondition(sign(-2) == "negative" && sign(0) == "zero")
      precondition(sign(7) == "positive")
    }

    do {
      // Task 4: Diagnose a defect
      func overlapping(_ score: Int) -> String {
        switch score {
        case 0...60: return "retry"
        case 60...100: return "pass"
        default: return "invalid"
        }
      }
      func fixed(_ score: Int) -> String {
        switch score {
        case 0..<60: return "retry"
        case 60...100: return "pass"
        default: return "invalid"
        }
      }
      precondition(overlapping(60) == "retry" && fixed(60) == "pass")
      precondition(overlapping(59) == fixed(59))
    }

    do {
      // Task 5: Boundary evidence
      func classify(_ score: Int) -> String {
        switch score {
        case 0..<60: return "retry"
        case 60...100: return "pass"
        default: return "invalid"
        }
      }
      precondition(classify(0) == "retry" && classify(100) == "pass")
      precondition(classify(-1) == "invalid" && classify(101) == "invalid")
    }
    print("swift-006: passed")
  }
}
