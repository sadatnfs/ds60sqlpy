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
    print("swift-047: passed")
  }
}
