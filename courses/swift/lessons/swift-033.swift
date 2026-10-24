// swift-033: Sendable and strict concurrency boundaries
import Foundation

// Task 1: Identify the owner of every value crossing a task boundary.
// Task 2: Add another immutable field to the snapshot.
// Task 3: Replace a shared mutable result class with a sendable value result.
// Task 4: Diagnose an unchecked Sendable annotation hiding unsynchronized mutable state.
// Task 5: Test empty snapshots and multiple concurrent producers.
// Task 6: Design data exchange between a UI model and a background actor using immutable snapshots.

@main
struct LessonMain {
  static func main() async throws {
    fatalError("Implement your own lesson attempt before running.")
  }
}
