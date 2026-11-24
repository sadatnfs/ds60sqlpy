import Foundation

final class Counter {
  private(set) var value = 0
  func increment() { value += 1 }
}

@main
struct LessonMain {
  static func main() async throws {
    do {
      let first = Counter()
      let second = first
      second.increment()
      precondition(first.value == 1)
      precondition(first === second)
    }

    do {
      let first = Counter()
      let second = Counter()
      precondition(first.value == second.value)
      precondition(first !== second)
    }

    do {
      // Task 1: Predict and explain
      let first = Counter()
      let second = first
      precondition(first === second)
      second.increment()
      precondition(first.value == 1)
      precondition(ObjectIdentifier(first) == ObjectIdentifier(second))
    }

    do {
      // Task 2: Guided modification
      let first = Counter()
      let second = Counter()
      second.increment()
      precondition(first.value == 0 && second.value == 1)
      precondition(first !== second)
    }

    do {
      // Task 3: Independent construction
      final class Coordinator {
        var openConnections = 0
      }
      struct Coordinate {
        var x: Int
        var y: Int
      }
      let shared = Coordinator()
      let alias = shared
      alias.openConnections += 1
      let point = Coordinate(x: 1, y: 2)
      var moved = point
      moved.x = 5
      precondition(shared.openConnections == 1 && shared === alias)
      precondition(point.x == 1 && moved.x == 5)
    }

    do {
      // Task 4: Diagnose a defect
      let live = Counter()
      let alias = live
      let snapshot = live.value
      live.increment()
      precondition(alias.value == 1)
      precondition(snapshot == 0)
    }

    do {
      // Task 5: Boundary evidence
      let first = Counter()
      let second = Counter()
      first.increment()
      second.increment()
      precondition(first.value == second.value && first !== second)
      first.increment()
      precondition(first.value == 2 && second.value == 1)
    }
    print("swift-013: passed")
  }
}
