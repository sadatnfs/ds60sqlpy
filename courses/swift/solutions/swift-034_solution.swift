import Foundation

@main
struct LessonMain {
  static func main() async throws {
    do {
      let stream = AsyncStream<Int> { continuation in
        continuation.yield(2)
        continuation.yield(3)
        continuation.finish()
      }
      var total = 0
      for await value in stream { total += value }
      precondition(total == 5)
    }

    do {
      let stream = AsyncStream<Int>(bufferingPolicy: .bufferingNewest(1)) { continuation in
        continuation.yield(1)
        continuation.yield(2)
        continuation.finish()
      }
      var values: [Int] = []
      for await value in stream { values.append(value) }
      precondition(values == [2])
    }

    do {
      // Task 3: Independent construction
      let (events, continuation) = AsyncStream<String>.makeStream()
      let producer = Task {
        for name in ["start", "progress", "done"] { continuation.yield(name) }
        continuation.finish()
      }
      var received: [String] = []
      for await event in events { received.append(event) }
      await producer.value
      precondition(received == ["start", "progress", "done"])
    }
    print("swift-034: passed")
  }
}
