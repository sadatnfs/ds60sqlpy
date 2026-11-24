import Foundation

struct SavedPlan: Codable {
  let schemaVersion: Int
  let titles: [String]
}
func supported(_ document: SavedPlan) -> Bool {
  document.schemaVersion == 1 && document.titles.allSatisfy { !$0.isEmpty }
}

@main
struct LessonMain {
  static func main() async throws {
    do {
      let document = SavedPlan(schemaVersion: 1, titles: ["Read", "Practice"])
      let data = try JSONEncoder().encode(document)
      let decoded = try JSONDecoder().decode(SavedPlan.self, from: data)
      precondition(decoded.schemaVersion == 1 && decoded.titles.count == 2)
    }

    do {
      let document = SavedPlan(schemaVersion: 99, titles: ["Keep me"])
      precondition(!supported(document))
      precondition(document.titles == ["Keep me"])
    }

    do {
      // Task 1: Predict and explain
      let future = Data(#"{"schemaVersion":99,"titles":["Keep"]}"#.utf8)
      let decoded = try JSONDecoder().decode(SavedPlan.self, from: future)
      precondition(decoded.schemaVersion == 99 && !supported(decoded))
      let blank = SavedPlan(schemaVersion: 1, titles: [""])
      precondition(!supported(blank))
    }

    do {
      // Task 2: Guided modification
      struct SavedPlanWithNote: Codable {
        let schemaVersion: Int
        let titles: [String]
        let note: String?
      }
      let old = Data(#"{"schemaVersion":1,"titles":["Read"]}"#.utf8)
      let decoded = try JSONDecoder().decode(SavedPlanWithNote.self, from: old)
      precondition(decoded.note == nil && decoded.titles == ["Read"])
    }

    do {
      // Task 4: Diagnose a defect
      enum LoadResult: Equatable {
        case loaded([String])
        case blocked(original: Data)
      }
      func load(_ data: Data) -> LoadResult {
        guard let plan = try? JSONDecoder().decode(SavedPlan.self, from: data), supported(plan)
        else { return .blocked(original: data) }
        return .loaded(plan.titles)
      }
      let unreadable = Data("{".utf8)
      precondition(load(unreadable) == .blocked(original: unreadable))
    }

    do {
      // Task 5: Boundary evidence
      let decoder = JSONDecoder()
      precondition((try? decoder.decode(SavedPlan.self, from: Data())) == nil)
      precondition((try? decoder.decode(SavedPlan.self, from: Data("[1,".utf8))) == nil)
      let future = try decoder.decode(
        SavedPlan.self, from: Data(#"{"schemaVersion":2,"titles":[]}"#.utf8))
      precondition(!supported(future))
    }
    print("swift-042: passed")
  }
}
