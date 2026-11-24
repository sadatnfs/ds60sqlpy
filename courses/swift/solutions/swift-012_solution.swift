import Foundation

struct Inventory {
  private(set) var stock: Int
  mutating func reserve(_ amount: Int) -> Bool {
    guard amount >= 0, amount <= stock else { return false }
    stock -= amount
    return true
  }
}
extension Inventory {
  mutating func restock(_ amount: Int) -> Bool {
    guard amount > 0 else { return false }
    let result = stock.addingReportingOverflow(amount)
    guard !result.overflow else { return false }
    stock = result.partialValue
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
      // Task 1: Predict and explain
      var first = Inventory(stock: 5)
      var second = first
      precondition(first.stock == 5 && second.stock == 5)
      precondition(second.reserve(2))
      precondition(first.stock == 5 && second.stock == 3)
      precondition(first.reserve(0) && first.stock == 5)
    }

    do {
      // Task 2: Guided modification
      var inventory = Inventory(stock: 3)
      precondition(inventory.restock(4) && inventory.stock == 7)
      precondition(!inventory.restock(0) && !inventory.restock(-2))
      precondition(!inventory.restock(Int.max) && inventory.stock == 7)
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

    do {
      // Task 4: Diagnose a defect
      struct Careless {
        var stock: Int
        mutating func reserve(_ amount: Int) -> Bool {
          stock -= amount
          return stock >= 0
        }
      }
      var careless = Careless(stock: 3)
      precondition(!careless.reserve(4) && careless.stock == -1)
      var inventory = Inventory(stock: 3)
      precondition(!inventory.reserve(4) && inventory.stock == 3)
    }

    do {
      // Task 5: Boundary evidence
      var inventory = Inventory(stock: 3)
      precondition(inventory.reserve(0) && inventory.stock == 3)
      precondition(!inventory.reserve(4) && inventory.stock == 3)
      precondition(inventory.reserve(3) && inventory.stock == 0)
    }
    print("swift-012: passed")
  }
}
