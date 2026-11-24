import Foundation

@main
struct LessonMain {
  static func main() async throws {
    do {
      let task = Task {
        while !Task.isCancelled { await Task.yield() }
        do {
          try Task.checkCancellation()
          return false
        } catch is CancellationError { return true } catch { return false }
      }
      task.cancel()
      let acknowledged = await task.value
      precondition(acknowledged)
    }

    do {
      let task = Task { 9 }
      task.cancel()
      let value = await task.value
      precondition(value == 9)
    }

    do {
      // Task 1: Predict and explain
      let task = Task { () -> String in
        while !Task.isCancelled { await Task.yield() }
        return "acknowledged"
      }
      precondition(!task.isCancelled)
      task.cancel()
      precondition(task.isCancelled)
      let reply = await task.value
      precondition(reply == "acknowledged")
    }

    do {
      // Task 2: Guided modification
      func commit(_ log: [String]) async -> [String] {
        if Task.isCancelled { return log + ["skipped write"] }
        return log + ["wrote"]
      }
      let task = Task { () -> [String] in
        while !Task.isCancelled { await Task.yield() }
        return await commit(["read"])
      }
      task.cancel()
      let cancelledLog = await task.value
      precondition(cancelledLog == ["read", "skipped write"])
      let normalLog = await commit(["read"])
      precondition(normalLog == ["read", "wrote"])
    }

    do {
      // Task 3: Independent construction
      func process(_ items: [Int], isCancelled: () -> Bool) -> (done: [Int], cleanedUp: Bool) {
        var done: [Int] = []
        var cleanedUp = false
        do {
          defer { cleanedUp = true }
          for item in items {
            if isCancelled() { break }
            done.append(item)
          }
        }
        return (done, cleanedUp)
      }
      var checks = 0
      let stopped = process([1, 2, 3, 4, 5]) {
        checks += 1
        return checks > 3
      }
      precondition(stopped.done == [1, 2, 3] && stopped.cleanedUp)
      let task = Task { process([1, 2]) { Task.isCancelled } }
      let full = await task.value
      precondition(full.done == [1, 2] && full.cleanedUp)
    }

    do {
      // Task 5: Boundary evidence
      let started = await withTaskGroup(of: Int.self, returning: Bool.self) { group in
        group.cancelAll()
        return group.addTaskUnlessCancelled { 1 }
      }
      precondition(!started)
      let finished = Task { 5 }
      let first = await finished.value
      finished.cancel()
      let again = await finished.value
      precondition(first == 5 && again == 5)
    }
    print("swift-030: passed")
  }
}
