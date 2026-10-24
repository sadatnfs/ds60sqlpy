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
    print("swift-016: passed")
  }
}
