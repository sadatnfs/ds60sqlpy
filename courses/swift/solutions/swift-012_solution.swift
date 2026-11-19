import Foundation

struct Inventory {
  private(set) var stock: Int
  mutating func reserve(_ amount: Int) -> Bool {
    guard amount >= 0, amount <= stock else { return false }
    stock -= amount
    return true
  }
}

@main
struct LessonMain {
  static func main() async throws {
    do {
      var first = Inventory(stock: 5)
      var second = first
      precondition(second.reserve(2))
      precondition(first.stock == 5 && second.stock == 3)
      precondition(first.reserve(0))
    }

    do {
      var inventory = Inventory(stock: 3)
      precondition(!inventory.reserve(4))
      precondition(!inventory.reserve(-1))
      precondition(inventory.stock == 3)
    }

    do {
      // Task 3: Independent construction
      struct BoundedCounter {
        private(set) var value = 0
        let limit: Int
        mutating func increment() -> Bool {
          guard value < limit else { return false }
          value += 1
          return true
        }
      }
      var counter = BoundedCounter(limit: 2)
      precondition(counter.increment() && counter.increment())
      precondition(!counter.increment() && counter.value == 2)
    }
    print("swift-012: passed")
  }
}
