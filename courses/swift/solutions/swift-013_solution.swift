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
    print("swift-013: passed")
  }
}
