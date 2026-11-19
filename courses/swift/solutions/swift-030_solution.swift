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
    print("swift-030: passed")
  }
}
