import Foundation

func importRows(_ lines: [String]) -> (counts: [String: Int], rejected: Int) {
  var counts: [String: Int] = [:]
  var rejected = 0
  for line in lines {
    let fields = line.split(separator: ",", omittingEmptySubsequences: false)
    guard fields.count == 2, !fields[0].isEmpty, let quantity = Int(fields[1]), quantity >= 0 else {
      rejected += 1
      continue
    }
    counts[String(fields[0]), default: 0] += quantity
  }
  return (counts, rejected)
}

@main
struct LessonMain {
  static func main() async throws {
    do {
      let result = importRows(["pear,2", "apple,3", "pear,4"])
      precondition(result.counts == ["pear": 6, "apple": 3])
      precondition(result.rejected == 0)
    }

    do {
      let result = importRows(["pear,0", "bad", "apple,-1", "pear,no"])
      precondition(result.counts == ["pear": 0])
      precondition(result.rejected == 3)
      precondition(importRows([]).counts.isEmpty)
    }

    do {
      // Task 1: Predict and explain
      let lines = ["pear,2", "bad", ",3", "pear,x", "pear,-1", "apple,3"]
      let verdicts = lines.map { importRows([$0]).rejected == 0 ? "ok" : "rejected" }
      precondition(verdicts == ["ok", "rejected", "rejected", "rejected", "rejected", "ok"])
    }

    do {
      // Task 2: Guided modification
      let result = importRows(["pear,2", "apple,3", "pear,4", "apple,1"])
      precondition(result.counts == ["pear": 6, "apple": 4])
      precondition(result.rejected == 0)
    }

    do {
      // Task 3: Independent construction
      let result = importRows(["pear,2", "apple,3", "bad", "pear,1"])
      var lines = result.counts.keys.sorted().map { "\($0): \(result.counts[$0]!)" }
      lines.append("rejected: \(result.rejected)")
      precondition(lines.joined(separator: "\n") == "apple: 3\npear: 3\nrejected: 1")
    }

    do {
      // Task 4: Diagnose a defect
      func lenientQuantity(_ text: Substring) -> Int { Int(text) ?? 0 }
      precondition(lenientQuantity("no") == lenientQuantity("0"))
      let result = importRows(["pear,0", "pear,no"])
      precondition(result.counts == ["pear": 0] && result.rejected == 1)
    }

    do {
      // Task 5: Boundary evidence
      precondition(importRows([",2"]).rejected == 1)
      precondition(importRows(["pear,2,extra"]).rejected == 1)
      precondition(importRows(["pear,0"]).counts == ["pear": 0])
      let empty = importRows([])
      precondition(empty.counts.isEmpty && empty.rejected == 0)
    }
    print("swift-016: passed")
  }
}
