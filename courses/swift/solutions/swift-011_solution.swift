import Foundation

enum Outcome { case value(Int); case invalid(String) }

@main
struct LessonMain {
    static func main() async throws {
        do {
            let summary = (accepted: 3, rejected: 2)
            precondition(summary.accepted + summary.rejected == 5)
        }

        do {
            let outcomes: [Outcome] = [.value(4), .invalid("negative")]
            let rendered = outcomes.map { outcome in switch outcome { case .value(let count): return "count:\(count)"; case .invalid(let reason): return "error:\(reason)" } }
            precondition(rendered == ["count:4", "error:negative"])
        }
        print("swift-011: passed")
    }
}
