// swift-030: Cancellation and cleanup in asynchronous work
import Foundation

// Task 1: Separate cancellation request from acknowledged completion.
// Task 2: Add a cancellation check before a simulated state-changing step.
// Task 3: Write a bounded processing loop with cleanup on cancellation.
// Task 4: Diagnose retrying an unknown write merely because its waiter was cancelled.
// Task 5: Test cancellation before work and after an already completed result.
// Task 6: Design a receipt distinguishing success, confirmed cancellation and unknown outcome.

@main
struct LessonMain {
    static func main() async throws {
        fatalError("Implement your own lesson attempt before running.")
    }
}
