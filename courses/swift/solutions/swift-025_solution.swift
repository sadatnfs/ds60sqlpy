import Foundation

@main
struct LessonMain {
  static func main() async throws {
    do {
      let start = Date(timeIntervalSince1970: 0)
      let end = start.addingTimeInterval(90 * 60)
      precondition(end.timeIntervalSince(start) == 5400)
    }

    do {
      let formatter = ISO8601DateFormatter()
      let first = formatter.date(from: "2025-01-01T12:00:00+02:00")
      let second = formatter.date(from: "2025-01-01T10:00:00Z")
      precondition(first != nil && first == second)
    }

    do {
      // Task 3: Independent construction
      let formatter = ISO8601DateFormatter()
      let start = formatter.date(from: "2025-03-01T22:30:00Z")!
      let end = formatter.date(from: "2025-03-02T01:15:00Z")!
      let minutes = Int(end.timeIntervalSince(start) / 60)
      let report = "\(minutes) minutes from \(formatter.string(from: start))"
      precondition(report == "165 minutes from 2025-03-01T22:30:00Z")
    }
    print("swift-025: passed")
  }
}
