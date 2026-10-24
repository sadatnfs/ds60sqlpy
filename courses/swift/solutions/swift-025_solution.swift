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
    print("swift-025: passed")
  }
}
