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
    print("swift-030: passed")
  }
}
