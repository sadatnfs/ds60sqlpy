import Foundation

@main
struct LessonMain {
  static func main() async throws {
    do {
      let evidence: Set<String> = ["domain-tests", "package-build"]
      precondition(!evidence.contains("ui-tested"))
      precondition(!evidence.contains("device-signed"))
    }

    do {
      let required: Set<String> = ["domain-tests", "ui-smoke", "save-reload"]
      let observed: Set<String> = ["domain-tests", "ui-smoke"]
      precondition(required.subtracting(observed) == ["save-reload"])
    }

    do {
      // Task 2: Guided modification
      var observed: Set<String> = ["domain-tests", "ui-smoke"]
      let saved = Data(#"{"titles":["Read"]}"#.utf8)
      let reloaded = try JSONDecoder().decode([String: [String]].self, from: saved)
      if reloaded["titles"] == ["Read"] { observed.insert("save-reload") }
      let required: Set<String> = ["domain-tests", "ui-smoke", "save-reload"]
      precondition(required.subtracting(observed).isEmpty)
    }

    do {
      // Task 4: Diagnose a defect
      let archiveEvidence: Set<String> = ["compiled", "archived"]
      precondition(!archiveEvidence.contains("voiceover-checked"))
    }

    do {
      // Task 5: Boundary evidence
      var disk: [String: Data] = [:]
      func launch() -> (titles: [String], blocked: Bool) {
        guard let data = disk["plan"] else { return ([], false) }
        guard let titles = try? JSONDecoder().decode([String].self, from: data) else {
          return ([], true)
        }
        return (titles, false)
      }
      precondition(launch().titles.isEmpty && !launch().blocked)
      disk["plan"] = try JSONEncoder().encode(["Read"])
      precondition(launch().titles == ["Read"])
      disk["plan"] = Data("{".utf8)
      precondition(launch().blocked && disk["plan"] == Data("{".utf8))
    }
    print("swift-046: passed")
  }
}
