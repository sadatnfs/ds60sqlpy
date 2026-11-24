import Foundation

@resultBuilder enum SectionBuilder {
  static func buildExpression(_ value: String) -> [String] { [value] }
  static func buildBlock(_ components: [String]...) -> [String] { components.flatMap { $0 } }
  static func buildOptional(_ component: [String]?) -> [String] { component ?? [] }
}
func sections(@SectionBuilder _ content: () -> [String]) -> [String] { content() }
@resultBuilder enum LoopingSectionBuilder {
  static func buildExpression(_ value: String) -> [String] { [value] }
  static func buildBlock(_ components: [String]...) -> [String] { components.flatMap { $0 } }
  static func buildArray(_ components: [[String]]) -> [String] { components.flatMap { $0 } }
}
func loopingSections(@LoopingSectionBuilder _ content: () -> [String]) -> [String] { content() }

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
      // Task 1: Predict and explain
      let manual = SectionBuilder.buildBlock(
        SectionBuilder.buildExpression("Overview"),
        SectionBuilder.buildExpression("Details"))
      let built = sections {
        "Overview"
        "Details"
      }
      precondition(manual == built && manual == ["Overview", "Details"])
    }

    do {
      // Task 2: Guided modification
      let include = false
      let report = sections {
        "Overview"
        if include { "Diagnostics" }
      }
      precondition(report == ["Overview"])
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

    do {
      // Task 4: Diagnose a defect
      let names = ["North", "South"]
      let report = loopingSections {
        "Overview"
        for name in names { "Region \(name)" }
      }
      precondition(report == ["Overview", "Region North", "Region South"])
    }

    do {
      // Task 5: Boundary evidence
      let empty = sections {}
      precondition(empty.isEmpty)
      let show = false
      let hidden = sections {
        if show { "Hidden" }
      }
      precondition(hidden.isEmpty)
    }
    print("swift-038: passed")
  }
}
