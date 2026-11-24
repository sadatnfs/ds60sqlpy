import Foundation

@main
struct LessonMain {
  static func main() async throws {
    do {
      func summary(completed: Int, total: Int) -> String { "\(completed)/\(total) complete" }
      precondition(summary(completed: 2, total: 3) == "2/3 complete")
    }

    do {
      let capabilities = Set(["portable-core", "foundation-files"])
      precondition(capabilities.contains("portable-core"))
      precondition(!capabilities.contains("swiftui-linux"))
    }

    do {
      // Task 1: Predict and explain
      struct PortablePlan {
        let completed: Int
        let total: Int
        var summary: String { "\(completed)/\(total) complete" }
      }
      let plan = PortablePlan(completed: 1, total: 2)
      precondition(plan.summary == "1/2 complete")
    }

    do {
      // Task 2: Guided modification
      func percentComplete(completed: Int, total: Int) -> Int {
        guard total > 0 else { return 0 }
        return completed * 100 / total
      }
      precondition(percentComplete(completed: 1, total: 4) == 25)
      precondition(percentComplete(completed: 0, total: 0) == 0)
    }

    do {
      // Task 5: Boundary evidence
      let capabilities: Set<String> = ["portable-core", "foundation-files"]
      func runAction(_ capability: String) -> String {
        capabilities.contains(capability)
          ? "Running \(capability)" : "\(capability) is not available on this platform"
      }
      precondition(runAction("portable-core") == "Running portable-core")
      precondition(
        runAction("swiftui-preview") == "swiftui-preview is not available on this platform")
    }
    print("swift-047: passed")
  }
}
