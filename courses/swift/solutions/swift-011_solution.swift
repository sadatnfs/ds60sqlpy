import Foundation

enum Outcome {
  case value(Int)
  case invalid(String)
}

@main
struct LessonMain {
  static func main() async throws {
    do {
      let summary = (accepted: 3, rejected: 2)
      precondition(summary.accepted + summary.rejected == 5)
    }

    do {
      let outcomes: [Outcome] = [.value(4), .invalid("negative")]
      let rendered = outcomes.map { outcome in
        switch outcome {
        case .value(let count): return "count:\(count)"
        case .invalid(let reason): return "error:\(reason)"
        }
      }
      precondition(rendered == ["count:4", "error:negative"])
    }

    do {
      // Task 3: Independent construction
      enum Load {
        case loading
        case ready(Int)
        case failed(String)
      }
      func label(_ state: Load) -> String {
        switch state {
        case .loading: return "loading"
        case .ready(let count): return "ready:\(count)"
        case .failed(let reason): return "failed:\(reason)"
        }
      }
      precondition(label(.loading) == "loading" && label(.ready(3)) == "ready:3")
      precondition(label(.failed("offline")) == "failed:offline")
    }
    print("swift-011: passed")
  }
}
