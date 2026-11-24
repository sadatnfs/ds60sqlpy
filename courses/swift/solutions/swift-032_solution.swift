import Foundation

enum LedgerError: Error {
  case invalid
  case conflict
}
actor ImportLedger {
  private var records: [String: (Int, Int)] = [:]
  private(set) var total = 0
  func apply(id: String, amount: Int) throws -> Int {
    guard !id.isEmpty, amount >= 0 else { throw LedgerError.invalid }
    if let old = records[id] {
      guard old.0 == amount else { throw LedgerError.conflict }
      return old.1
    }
    total += amount
    records[id] = (amount, total)
    return total
  }
}

@main
struct LessonMain {
  static func main() async throws {
    do {
      let ledger = ImportLedger()
      let first = try await ledger.apply(id: "one", amount: 3)
      let repeated = try await ledger.apply(id: "one", amount: 3)
      let total = await ledger.total
      precondition(first == 3 && repeated == 3 && total == 3)
    }

    do {
      let ledger = ImportLedger()
      _ = try await ledger.apply(id: "one", amount: 3)
      var conflict = false
      do { _ = try await ledger.apply(id: "one", amount: 4) } catch LedgerError.conflict {
        conflict = true
      }
      let total = await ledger.total
      precondition(conflict && total == 3)
    }

    do {
      // Task 1: Predict and explain
      let ledger = ImportLedger()
      let firstReceipt = try await ledger.apply(id: "a", amount: 5)
      let afterFirst = await ledger.total
      let repeatReceipt = try await ledger.apply(id: "a", amount: 5)
      let afterRepeat = await ledger.total
      precondition(firstReceipt == 5 && afterFirst == 5)
      precondition(repeatReceipt == 5 && afterRepeat == 5)
    }

    do {
      // Task 2: Guided modification
      let ledger = ImportLedger()
      _ = try await ledger.apply(id: "one", amount: 3)
      let receipt = try await ledger.apply(id: "two", amount: 4)
      let total = await ledger.total
      precondition(receipt == 7 && total == 7)
    }

    do {
      // Task 3: Independent construction
      actor ReceiptLedger {
        private var receipts: [String: Int] = [:]
        private(set) var executions = 0
        func apply(id: String, amount: Int) -> Int {
          if let receipt = receipts[id] { return receipt }
          executions += 1
          receipts[id] = amount
          return amount
        }
        func receipt(for id: String) -> Int? { receipts[id] }
      }
      let ledger = ReceiptLedger()
      _ = await ledger.apply(id: "one", amount: 3)
      let found = await ledger.receipt(for: "one")
      let missing = await ledger.receipt(for: "two")
      let executions = await ledger.executions
      precondition(found == 3 && missing == nil && executions == 1)
    }

    do {
      // Task 4: Diagnose a defect
      actor CarelessLedger {
        private var receipts: [String: Int] = [:]
        private(set) var total = 0
        func apply(id: String, amount: Int) -> Int {
          total += amount
          if let receipt = receipts[id] { return receipt }
          receipts[id] = total
          return total
        }
      }
      let careless = CarelessLedger()
      _ = await careless.apply(id: "one", amount: 3)
      _ = await careless.apply(id: "one", amount: 3)
      let carelessTotal = await careless.total
      let ledger = ImportLedger()
      _ = try await ledger.apply(id: "one", amount: 3)
      _ = try await ledger.apply(id: "one", amount: 3)
      let safeTotal = await ledger.total
      precondition(carelessTotal == 6 && safeTotal == 3)
    }

    do {
      // Task 5: Boundary evidence
      let ledger = ImportLedger()
      var invalid = false
      do { _ = try await ledger.apply(id: "neg", amount: -1) } catch LedgerError.invalid {
        invalid = true
      }
      precondition(invalid)
      let receipts = try await withThrowingTaskGroup(of: Int.self, returning: [Int].self) { group in
        for _ in 0..<5 { group.addTask { try await ledger.apply(id: "same", amount: 2) } }
        var collected: [Int] = []
        for try await receipt in group { collected.append(receipt) }
        return collected
      }
      let total = await ledger.total
      precondition(receipts == [2, 2, 2, 2, 2] && total == 2)
    }
    print("swift-032: passed")
  }
}
