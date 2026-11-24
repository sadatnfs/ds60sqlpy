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
      // Task 1: Predict and explain
      let summary = (accepted: 3, rejected: 2)
      precondition(summary.0 == summary.accepted && summary.1 == summary.rejected)
      precondition(summary.accepted + summary.rejected == 5)
    }

    do {
      // Task 2: Guided modification
      let summary = (accepted: 3, rejected: 2, skipped: 1)
      let seen = summary.accepted + summary.rejected + summary.skipped
      precondition(seen == 6)
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

    do {
      // Task 4: Diagnose a defect
      struct LoosePage {
        var isLoading: Bool
        var count: Int?
        var error: String?
      }
      let contradictory = LoosePage(isLoading: true, count: 3, error: "offline")
      precondition(contradictory.isLoading && contradictory.count != nil)
      precondition(contradictory.error != nil)
      enum PageState: Equatable {
        case loading
        case ready(Int)
        case failed(String)
      }
      precondition(PageState.ready(3) != .failed("offline"))
    }

    do {
      // Task 5: Boundary evidence
      enum Load {
        case loading
        case ready(Int)
        case failed(String)
        case cancelled
      }
      func label(_ state: Load) -> String {
        switch state {
        case .loading: return "loading"
        case .ready(let count): return "ready:\(count)"
        case .failed(let reason): return "failed:\(reason)"
        case .cancelled: return "cancelled"
        }
      }
      precondition(label(.cancelled) == "cancelled" && label(.ready(2)) == "ready:2")
    }
    print("swift-011: passed")
  }
}
