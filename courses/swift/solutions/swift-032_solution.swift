import Foundation

enum LedgerError: Error { case invalid; case conflict }
actor ImportLedger { private var records: [String: (Int, Int)] = [:]; private(set) var total = 0; func apply(id: String, amount: Int) throws -> Int { guard !id.isEmpty, amount >= 0 else { throw LedgerError.invalid }; if let old = records[id] { guard old.0 == amount else { throw LedgerError.conflict }; return old.1 }; total += amount; records[id] = (amount, total); return total } }

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
            do { _ = try await ledger.apply(id: "one", amount: 4) } catch LedgerError.conflict { conflict = true }
            let total = await ledger.total
            precondition(conflict && total == 3)
        }
        print("swift-032: passed")
    }
}
