import Foundation

@resultBuilder enum SectionBuilder {
  static func buildExpression(_ value: String) -> [String] { [value] }
  static func buildBlock(_ components: [String]...) -> [String] { components.flatMap { $0 } }
  static func buildOptional(_ component: [String]?) -> [String] { component ?? [] }
}
func sections(@SectionBuilder _ content: () -> [String]) -> [String] { content() }

@main
struct LessonMain {
  static func main() async throws {
    do {
      let report = sections {
        "Overview"
        "Details"
      }
      precondition(report == ["Overview", "Details"])
    }

    do {
      let include = true
      let report = sections {
        "Overview"
        if include { "Diagnostics" }
      }
      precondition(report == ["Overview", "Diagnostics"])
    }

    do {
      // Task 3: Independent construction
      let hasWarnings = false
      let report = sections {
        "Summary"
        "Totals"
        if hasWarnings { "Warnings" }
      }
      precondition(report == ["Summary", "Totals"])
    }
    print("swift-038: passed")
  }
}
