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
      // Task 1: Predict and explain
      let seconds: TimeInterval = 5400
      let minutes = seconds / 60
      precondition(minutes == 90)
      precondition(minutes * 60 == seconds)
      let duration = Duration.seconds(5400)
      precondition(duration.components.seconds / 60 == 90)
    }

    do {
      // Task 2: Guided modification
      var calendar = Calendar(identifier: .gregorian)
      calendar.timeZone = TimeZone(identifier: "America/New_York")!
      let start = ISO8601DateFormatter().date(from: "2025-03-08T12:00:00-05:00")!
      let plusSeconds = start.addingTimeInterval(86_400)
      let nextLocalDay = calendar.date(byAdding: .day, value: 1, to: start)!
      precondition(calendar.component(.hour, from: plusSeconds) == 13)
      precondition(calendar.component(.hour, from: nextLocalDay) == 12)
      precondition(nextLocalDay.timeIntervalSince(start) == 82_800)
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

    do {
      // Task 4: Diagnose a defect
      let fixedOffset = TimeZone(secondsFromGMT: -5 * 3600)!
      let newYork = TimeZone(identifier: "America/New_York")!
      let parser = ISO8601DateFormatter()
      let winter = parser.date(from: "2025-01-15T12:00:00Z")!
      let summer = parser.date(from: "2025-07-15T12:00:00Z")!
      precondition(fixedOffset.secondsFromGMT(for: winter) == newYork.secondsFromGMT(for: winter))
      precondition(fixedOffset.secondsFromGMT(for: summer) == -18_000)
      precondition(newYork.secondsFromGMT(for: summer) == -14_400)
    }

    do {
      // Task 5: Boundary evidence
      let parser = ISO8601DateFormatter()
      let late = parser.date(from: "2025-01-01T23:50:00Z")!
      let early = parser.date(from: "2025-01-02T00:10:00Z")!
      precondition(early.timeIntervalSince(late) == 1200)
      precondition(parser.date(from: "not a date") == nil)
      precondition(parser.date(from: "2025-01-01T10:00:00") == nil)
    }
    print("swift-025: passed")
  }
}
