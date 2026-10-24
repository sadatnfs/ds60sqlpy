// swift-042: App persistence, migrations and recoverable saves
import Foundation

// Task 1: Identify the schema and domain validation boundaries.
// Task 2: Add a version-one optional field while preserving old decoding behavior.
// Task 3: Inspect JourneyApp save and load errors with an owned test file.
// Task 4: Diagnose replacing an unreadable saved file with an empty default automatically.
// Task 5: Test empty data, malformed data and an unknown future version.
// Task 6: Design a version-one to version-two migration with backup, rollback and verification steps.

@main
struct LessonMain {
  static func main() async throws {
    fatalError("Implement your own lesson attempt before running.")
  }
}
