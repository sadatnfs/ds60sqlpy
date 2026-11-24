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
      // Task 1: Predict and explain
      let (stream, continuation) = AsyncStream<Int>.makeStream(bufferingPolicy: .bufferingNewest(5))
      var buffered = -1
      if case .enqueued(let remaining) = continuation.yield(2) { buffered = remaining }
      precondition(buffered == 4)
      continuation.finish()
      var terminated = false
      if case .terminated = continuation.yield(9) { terminated = true }
      precondition(terminated)
      var values: [Int] = []
      for await value in stream { values.append(value) }
      precondition(values == [2])
    }

    do {
      // Task 2: Guided modification
      let stream = AsyncStream<Int>(bufferingPolicy: .bufferingOldest(1)) { continuation in
        continuation.yield(1)
        continuation.yield(2)
        continuation.finish()
      }
      var values: [Int] = []
      for await value in stream { values.append(value) }
      precondition(values == [1])
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

    do {
      // Task 4: Diagnose a defect
      let (stream, continuation) = AsyncStream<Int>.makeStream()
      continuation.yield(1)
      continuation.yield(2)
      continuation.finish()
      var count = 0
      for await _ in stream { count += 1 }
      precondition(count == 2)
    }

    do {
      // Task 5: Boundary evidence
      let (empty, emptyContinuation) = AsyncStream<Int>.makeStream()
      emptyContinuation.finish()
      var none: [Int] = []
      for await value in empty { none.append(value) }
      precondition(none.isEmpty)
      let (stream, continuation) = AsyncStream<Int>.makeStream(bufferingPolicy: .bufferingOldest(2))
      continuation.yield(1)
      continuation.yield(2)
      var dropped: Int?
      if case .dropped(let value) = continuation.yield(3) { dropped = value }
      continuation.finish()
      var kept: [Int] = []
      for await value in stream { kept.append(value) }
      precondition(dropped == 3 && kept == [1, 2])
    }
    print("swift-034: passed")
  }
}
