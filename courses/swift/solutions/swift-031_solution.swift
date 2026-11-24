import Foundation

actor CounterActor {
  private(set) var value = 0
  func increment() { value += 1 }
}
actor InventoryActor {
  private(set) var stock: Int
  init(stock: Int) { self.stock = stock }
  func reserve(_ amount: Int) -> Bool {
    guard amount >= 0 && amount <= stock else { return false }
    stock -= amount
    return true
  }
}
struct StockSnapshot: Sendable, Equatable {
  let stock: Int
}
extension InventoryActor {
  func snapshot() -> StockSnapshot { StockSnapshot(stock: stock) }
}

@main
struct LessonMain {
  static func main() async throws {
    do {
      let counter = CounterActor()
      await withTaskGroup(of: Void.self) { group in
        for _ in 0..<20 { group.addTask { await counter.increment() } }
      }
      let value = await counter.value
      precondition(value == 20)
    }

    do {
      let inventory = InventoryActor(stock: 3)
      let first = await inventory.reserve(2)
      let second = await inventory.reserve(2)
      let remaining = await inventory.stock
      precondition(first && !second && remaining == 1)
    }

    do {
      // Task 1: Predict and explain
      let inventory = InventoryActor(stock: 3)
      let before = await inventory.stock
      let reserved = await inventory.reserve(1)
      let after = await inventory.stock
      precondition(before == 3 && reserved && after == 2)
    }

    do {
      // Task 2: Guided modification
      let inventory = InventoryActor(stock: 3)
      let before = await inventory.snapshot()
      _ = await inventory.reserve(2)
      let after = await inventory.snapshot()
      precondition(before == StockSnapshot(stock: 3) && after.stock == 1)
    }

    do {
      // Task 3: Independent construction
      actor BoundedQueue {
        private var items: [Int] = []
        let capacity: Int
        init(capacity: Int) { self.capacity = capacity }
        func offer(_ item: Int) -> Bool {
          guard items.count < capacity else { return false }
          items.append(item)
          return true
        }
        func take() -> Int? { items.isEmpty ? nil : items.removeFirst() }
      }
      let queue = BoundedQueue(capacity: 2)
      let admitted = [await queue.offer(1), await queue.offer(2), await queue.offer(3)]
      precondition(admitted == [true, true, false])
      let first = await queue.take()
      precondition(first == 1)
    }

    do {
      // Task 4: Diagnose a defect
      actor SplitInventory {
        private(set) var stock = 2
        func canReserve(_ amount: Int) -> Bool { amount <= stock }
        func subtract(_ amount: Int) { stock -= amount }
      }
      let split = SplitInventory()
      let firstCheck = await split.canReserve(2)
      let secondCheck = await split.canReserve(2)
      await split.subtract(2)
      await split.subtract(2)
      let leftover = await split.stock
      precondition(firstCheck && secondCheck && leftover == -2)
      let safe = InventoryActor(stock: 2)
      let one = await safe.reserve(2)
      let two = await safe.reserve(2)
      precondition(one && !two)
    }

    do {
      // Task 5: Boundary evidence
      let inventory = InventoryActor(stock: 3)
      let zero = await inventory.reserve(0)
      let excess = await inventory.reserve(4)
      let exact = await inventory.reserve(3)
      let remaining = await inventory.stock
      precondition(zero && !excess && exact && remaining == 0)
    }
    print("swift-031: passed")
  }
}
