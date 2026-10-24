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
    print("swift-006: passed")
  }
}
